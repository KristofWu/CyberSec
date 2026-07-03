# ☁️ Cloud Network Security Monitor (AWS)

An event-driven security monitor for AWS network traffic. Real VPC Flow Logs land in S3, a Lambda function analyses each file as it arrives, and SNS sends an email alert when blocked-connection activity crosses a threshold — a serverless mini-SOC built on real traffic.

## 🎯 Overview

A live EC2 instance with a public IP attracts constant internet background scanning (bots probing SSH, Telnet, RDP...). VPC Flow Logs capture every connection — source, destination, port, and whether it was `ACCEPT`ed or `REJECT`ed. This project turns that raw traffic into actionable security insight:

1. **VPC Flow Logs → S3** — real network traffic captured to object storage.
2. **Lambda analysis** — reads each gzip-compressed log file, counts REJECTed connections, identifies top attackers.
3. **SNS alerts** — emails a summary when blocked attempts cross a threshold.
4. **Event-driven** — an S3 trigger invokes the Lambda automatically as new logs arrive.

## 🏗️ Architecture

```
   EC2 (public IP)                       bots scan it 24/7
        │ traffic
        ▼
   ┌─────────┐
   │   VPC   │  Flow Logs capture every connection (ACCEPT / REJECT)
   └─────────┘
        │  .log.gz
        ▼
   ┌─────────┐   S3 "object created" → automatic trigger
   │   S3    │ ───────────────────────────────┐
   └─────────┘                                │
                                              ▼
                                        ┌───────────┐
                                        │  Lambda   │ decompress gzip,
                                        │ (Python)  │ parse, count REJECTs
                                        └───────────┘
                                              │ if REJECTs ≥ threshold
                                              ▼
                                        ┌───────────┐
                                        │    SNS    │ → 📧 email alert
                                        └───────────┘
```

## 🧩 AWS services

- **VPC Flow Logs** — capture all traffic (ACCEPT + REJECT) in the VPC, delivered to S3.
- **S3** — stores the gzip-compressed flow log files; the create event triggers analysis.
- **Lambda (Python)** — reads from S3, decompresses gzip, parses the default flow-log format, counts blocked connections, publishes alerts.
- **SNS** — email delivery of alerts.
- **EC2** — a `t3.micro` instance whose public IP generates realistic traffic (mostly hostile scans).
- **IAM** — the Lambda role has exactly what it needs: S3 read, SNS publish.

## 📊 What the analysis finds

Real findings from captured traffic (one server, short window):

- **~54% of traffic was REJECTed** — over half the connections were blocked scan attempts.
- **125 unique attacker IPs** — most probe once, a few are persistent (one IP tried 15+ times).
- **Telnet (port 23) dominated** — classic IoT-botnet behaviour (Mirai-style bots hunting devices with default credentials).
- **Subnet `85.217.140.x`** — multiple IPs from one subnet running a coordinated scan, each hitting several ports. Individually they look minor; grouped, they reveal one adversary across many addresses.

## 🔌 VPC Flow Log format

Default format, space-separated fields (the parser uses field positions):

```
2 <account> <eni> <srcaddr> <dstaddr> <srcport> <dstport> <proto> <packets> <bytes> <start> <end> <action> <status>
                      [3]       [4]               [6]                                                  [12]
```

The Lambda reads positions 3 (srcaddr), 6 (dstport), and 12 (action) — enough to count and attribute blocked connections.

## 🗂️ Project structure

```
cloud-network-security-monitor/
├── README.md
├── Dockerfile               # containerizes the local analyzer
├── job.yaml                 # Kubernetes Job manifest
├── src/
│   ├── lambda_function.py   # the deployed Lambda (S3 → analyse → SNS)
│   └── flow_analysis.py     # local exploration (top IPs, ports, scanners, stats)
└── data/                    # sample flow logs (not committed)
```

## 🐳 Run the analyzer in Docker / Kubernetes

The AWS pipeline above is the production path — Lambda runs the analysis serverlessly in response to S3 events. For **local development and offline analysis**, the same detection logic (`flow_analysis.py`) also runs as a standalone container. This is a separate execution path from the Lambda: no AWS account, no S3, no credentials — just a log file in, a report out.

> Only `flow_analysis.py` is containerized. `lambda_function.py` stays AWS-native (it depends on S3/SNS events and `boto3`), so it isn't part of the image.

### Why it's a lean image
`flow_analysis.py` uses only the Python standard library (`sys`, `collections`) — no third-party packages. That means **no `requirements.txt` and no `pip install` step**: the Dockerfile just copies the code and data and sets the run command.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY src/ ./src/
COPY data/ ./data/
CMD ["python", "src/flow_analysis.py", "data/logs.log"]
```

The log path is baked into `CMD` as an argument (the script reads `sys.argv[1]`), so there's nothing to configure at runtime.

### Docker
```bash
docker build -t flow-analyzer .
docker run flow-analyzer
```
No flags needed — no secrets, no environment variables. The report prints straight to stdout.

### Kubernetes (local, Minikube)
The analyzer runs once to completion, so it's modeled as a **Job**, not a Deployment.

```bash
# make the locally built image available to the cluster
minikube image load flow-analyzer

# run it
kubectl apply -f job.yaml

# inspect
kubectl get pods
kubectl logs <pod-name>

# clean up
kubectl delete -f job.yaml
```

The manifest (`job.yaml`) carries no `env` or `Secret` block — unlike a service that needs API keys, this batch job needs only the image and its baked-in argument:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: flow-analyzer
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: flow-analyzer
          image: flow-analyzer:latest
          imagePullPolicy: Never
  backoffLimit: 2
```

`imagePullPolicy: Never` tells Kubernetes to use the image loaded into Minikube instead of pulling from a remote registry.

## 🚀 Deployment (summary)

1. **Enable VPC Flow Logs** on your VPC → destination an S3 bucket, filter `All`.
2. **Launch a t3.micro EC2** with a public IP (free tier) to generate traffic; restrict SSH to your own IP.
3. **Create the Lambda** (`lambda_function.py`), Python runtime.
4. **Attach IAM policies** to the Lambda role: S3 read, SNS publish.
5. **Create an SNS topic**, subscribe your email, confirm the subscription.
6. **Add an S3 trigger** (all object-create events) so the Lambda runs automatically.
7. **Set an AWS Budgets alert** as a cost safety net.

## 🔐 Security & cost notes

- **Least privilege** — the Lambda role is limited to S3 read + SNS publish.
- **SSH restricted to a single IP** — the EC2 is exposed enough to attract (and log) scans, but not open to SSH from the world. Blocked attempts still appear as `REJECT` in the logs.
- **Loop safety** — the Lambda only *reads* from the bucket that triggers it; it never writes back, so there's no infinite invocation loop.
- **Free tier** — Flow Logs, S3 (5 GB), Lambda (1M requests), SNS, and one `t3.micro` (750 h/month) stay within always-free limits. **Stop or terminate the EC2 instance when done** to avoid consuming free-tier hours.

## 🛠️ Tech stack

Python · boto3 · AWS VPC Flow Logs · S3 · Lambda · SNS · EC2 · IAM · Docker · Kubernetes (Minikube)

## 📌 Possible extensions

- Port the full local analysis (port scanners, subnet grouping) into the Lambda alert.
- Add the Security Group auditor (boto3 scan for `0.0.0.0/0` on sensitive ports).
- Aggregate attackers by `/24` subnet to surface coordinated scans automatically.
- Persist findings (DynamoDB) for trend analysis over time.
