# 🎣 Phishing URL Detector (ML + LLM)

A machine-learning classifier that flags phishing URLs from their structure, with an LLM layer (Google Gemini) that explains *why* a URL is suspicious in plain language. The model decides; the LLM interprets.

## 🎯 Overview

Phishing URLs differ from legitimate ones in measurable ways — they tend to be longer, packed with digits, use raw IP addresses instead of domains, and skip HTTPS. The script:

1. Loads a labeled dataset of URLs.
2. Engineers numeric features from each raw URL.
3. Trains a Random Forest classifier and evaluates it.
4. Uses Gemini to explain a sample prediction in analyst-style language.

Everything lives in a single script: `phishing_url_detector.py`.

## 📊 Results

Trained on ~48,800 labeled URLs, evaluated on a 20% held-out test set:

| Metric | Score |
|---|---|
| Accuracy | **99.76%** |
| Phishing recall | **~1.00** (18 missed out of 4,977) |
| False positives | 5 out of 4,786 legitimate |

In a security context recall is the priority — missing a phishing URL is costlier than a false alarm.

Confusion matrix (test set):
```
                 pred: legit   pred: phishing
actual: legit       4781             5
actual: phishing      18          4959
```

## 🧩 Features

Seven features extracted from each raw URL:

| Feature | Signal (legit vs phishing avg) |
|---|---|
| `digit_count` | 0.14 vs 11.54 — strongest signal |
| `has_ip` | 0.00 vs 0.71 — legit never uses raw IPs |
| `has_https` | 1.00 vs 0.23 — legit almost always encrypted |
| `url_length` | 20 vs 36 — phishing URLs run longer |
| `dot_count` | 1.1 vs 3.2 — phishing stacks subdomains |
| `hyphen_count` | 0.08 vs 0.14 — weak but kept |
| `has_suspicious` | weak on this dataset (see note) |

> **Note on `has_suspicious`:** keyword bait (`login`, `verify`, `secure`...) barely separated the classes here, because this dataset skews toward *technical* phishing (malware URLs, raw IPs) rather than *brand-impersonation* phishing. Kept in the model but documented as a finding — not every intuitive feature works on every dataset.

## 🤖 LLM explanation

The model outputs phishing/legitimate; Gemini then explains the verdict given the URL and its features:

```
URL:        http://110.37.26.193:54956/bin.sh
Prediction: phishing
LLM:        Uses a raw IP instead of a domain (a major red flag), lacks HTTPS
            (unencrypted), and the /bin.sh path suggests script execution — a
            common malware delivery pattern.
```

The LLM interprets; it does not override the model's decision.

## 🚀 Setup & run

1. **Install dependencies**
   ```bash
   pip install pandas scikit-learn google-generativeai python-dotenv
   ```

2. **Dataset** — a CSV with `url` and `label` columns (0 = legitimate, 1 = phishing). The script reads the path from the `DATA_PATH` environment variable, falling back to `../data/phishing_url_dataset_unique.csv` when run from `src/`. Override it if your file lives elsewhere:
   ```bash
   DATA_PATH=/path/to/your.csv python phishing_url_detector.py
   ```

3. **Gemini API key** (free from [Google AI Studio](https://aistudio.google.com)) — create a `.env` file next to the script:
   ```
   GEMINI_API_KEY=your_key_here
   ```

4. **Run**
   ```bash
   python phishing_url_detector.py
   ```

## 🐳 Run with Docker

The project is fully containerized — no need to install Python or any dependencies locally. Anyone with Docker can build and run it identically on any machine.

### Prerequisites
- Docker installed ([install guide](https://docs.docker.com/engine/install/))
- A `.env` file with your `GEMINI_API_KEY` (see step 3 above)
- The dataset CSV in `data/`

### Build the image
From the project root (where the `Dockerfile` lives):
```bash
docker build -t phishing-detector .
```

### Run the container
```bash
docker run --env-file .env -e DATA_PATH=data/phishing_url_dataset_unique.csv phishing-detector
```

- `--env-file .env` injects the Gemini API key **at runtime** — the key is never baked into the image, so the image is safe to push to a registry.
- `-e DATA_PATH=data/...` points the script at the dataset's location *inside* the container (`/app/data/`), without changing any code.

### Design notes

**Layer caching.** The `Dockerfile` copies `requirements.txt` and installs dependencies *before* copying the application code. Since dependencies change rarely and code changes often, Docker caches the (slow) `pip install` layer and only rebuilds the fast code-copy step on each edit — turning a ~37s rebuild into ~1s.

**Secrets stay out of the image.** The API key is passed at runtime via `--env-file`, never via `COPY`. As a second safeguard, `.env` is listed in `.dockerignore`, so it can't end up in the image even accidentally.

**Portable data path.** The same `DATA_PATH` environment variable handles both environments: it defaults to a relative path for local runs and is overridden at `docker run` time for the container — one code path, zero changes between environments.

**Lean build context.** A `.dockerignore` excludes `venv/`, `.git/`, `notebooks/`, and Python caches, keeping the build context small and builds fast.

## ☸️ Run on Kubernetes

The detector runs as a Kubernetes **Job** on a local [Minikube](https://minikube.sigs.k8s.io/) cluster. A Job is the right primitive here: the script runs once to completion (train → evaluate → explain) and exits — unlike a long-running service, which would use a Deployment.

### Prerequisites
- `kubectl` and `minikube` installed
- A running cluster: `minikube start --driver=docker`

### 1. Make the image available to the cluster
Minikube keeps its own image store, separate from the local Docker daemon. Load the locally built image into it:
```bash
minikube image load phishing-detector
```

### 2. Store the API key as a Secret
The Gemini key is kept in a Kubernetes `Secret`, created directly from the existing `.env` file — the value lives in the cluster, never in the manifest:
```bash
kubectl create secret generic gemini-secret --from-env-file=.env
```

### 3. Run the Job
```bash
kubectl apply -f job.yaml
```

### 4. Inspect the result
```bash
kubectl get pods                 # wait for STATUS: Completed
kubectl logs <pod-name>          # view training output + LLM explanation
```

### 5. Clean up
```bash
kubectl delete -f job.yaml
```

### The manifest (`job.yaml`)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: phishing-detector
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: phishing-detector
          image: phishing-detector:latest
          imagePullPolicy: Never
          env:
            - name: DATA_PATH
              value: "data/phishing_url_dataset_unique.csv"
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-secret
                  key: GEMINI_API_KEY
  backoffLimit: 2
```

### Design notes

**Job, not Deployment.** The workload is a batch task that terminates on success. A Deployment would treat the exiting container as a crash and restart it endlessly (`CrashLoopBackOff`). `restartPolicy: Never` + a Job match the actual lifecycle.

**Secrets via `secretKeyRef`, not plaintext.** `GEMINI_API_KEY` is pulled from the `gemini-secret` object with `valueFrom.secretKeyRef` — the manifest holds only a *reference*, so `job.yaml` is safe to commit. (Note: Kubernetes Secrets are base64-encoded, not encrypted; real protection comes from RBAC and etcd encryption at rest.)

**Local image, no registry pull.** `imagePullPolicy: Never` forces Kubernetes to use the image loaded into Minikube instead of trying to pull from a remote registry — required when the image only exists locally.

**Same env-var contract as Docker.** `DATA_PATH` and `GEMINI_API_KEY` are the same variables the container already expects, so the image runs unchanged whether started by `docker run` or by Kubernetes — only the *source* of the values differs.

## 🔐 Security note

The Gemini API key is loaded from a `.env` file via `python-dotenv` and never hardcoded. Add `.env` to `.gitignore` so the secret never reaches the repository.

## 🛠️ Tech stack

Python · pandas · scikit-learn (Random Forest) · Google Gemini API · python-dotenv · Docker · Kubernetes (Minikube)
