"""
AWS Lambda — VPC Flow Log Analyzer
==================================
Triggered when a new VPC Flow Log file lands in S3. Reads the (gzip-compressed)
log, counts REJECTed connections, identifies the top source IPs, and publishes
an SNS alert if the number of blocked attempts crosses a threshold.

Wyzwalana, gdy nowy plik VPC Flow Log trafi do S3. Czyta (skompresowany gzip)
log, liczy odrzucone (REJECT) połączenia, wyłania top źródłowe IP i publikuje
alert SNS, jeśli liczba zablokowanych prób przekroczy próg.
"""

import gzip
import boto3
from collections import Counter

SNS_TOPIC_ARN = "arn:aws:sns:eu-central-1:458207137259:Firewall-alerts"
REJECT_THRESHOLD = 20   # alert if a single flow-log file has this many REJECTs

# VPC Flow Log default format — field positions (0-indexed)
SRCADDR = 3
DSTPORT = 6
ACTION = 12


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    sns = boto3.client("sns")

    # 1. Resolve the file that triggered this invocation
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    # 2. Download and decompress the gzip-ed flow log
    response = s3.get_object(Bucket=bucket, Key=key)
    content = gzip.decompress(response["Body"].read()).decode("utf-8")

    # 3. Parse and count REJECTed connections per source IP
    attacker_ips = Counter()
    rejects = 0
    for line in content.splitlines():
        parts = line.split()
        if len(parts) < 14:          # skip header / malformed lines
            continue
        if parts[ACTION] == "REJECT":
            rejects += 1
            attacker_ips[parts[SRCADDR]] += 1

    # 4. Alert via SNS if the threshold is crossed
    if rejects >= REJECT_THRESHOLD:
        message = f"VPC Flow Log Alert: {rejects} REJECT (blocked) connections.\nTop attackers:\n"
        for ip, count in attacker_ips.most_common(5):
            message += f"  {ip}: {count} attempts\n"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="VPC Flow Log Alert",
            Message=message,
        )

    return {"statusCode": 200, "rejects": rejects}
