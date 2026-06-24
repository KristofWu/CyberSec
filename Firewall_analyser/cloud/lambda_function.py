"""
AWS Lambda — Firewall Log Analyzer (Phase 3, cloud)
===================================================
Triggered automatically when a log file is uploaded to the S3 bucket.
Reads the log from S3, counts blocked (DROP) connections, and — if a
threshold is exceeded — publishes an alert to an SNS topic (which emails
the subscriber).

Uruchamiana automatycznie, gdy plik logu trafi do bucketa S3.
Czyta log z S3, liczy zablokowane (DROP) polaczenia i — jesli prog jest
przekroczony — publikuje alert do tematu SNS (ktory wysyla maila subskrybentowi).

This is a deliberately simple, pure-Python version (no pandas/sklearn) so it
fits in a vanilla Lambda runtime with no extra layers. The full ML analyser
(Phases 1-2) runs locally; this cloud function demonstrates the S3 -> Lambda
-> SNS event-driven pipeline.
"""

import json
import boto3

# --- configuration ---
BUCKET = "kris-firewall-logs"
KEY = "firewall_big.log"
SNS_TOPIC_ARN = "arn:aws:sns:eu-central-1:458207137259:Firewall-alerts"
DROP_THRESHOLD = 50   # alert if more than this many DROP lines


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    sns = boto3.client("sns")

    # 1. Read the log file from S3
    response = s3.get_object(Bucket=BUCKET, Key=KEY)
    content = response["Body"].read().decode("utf-8")
    lines = content.splitlines()

    # 2. Count blocked (DROP) connections
    dropped = 0
    for line in lines:
        if "ACTION=DROP" in line:
            dropped += 1

    # 3. If the threshold is exceeded, publish an alert to SNS
    if dropped >= DROP_THRESHOLD:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Many drops in firewall log",
            Message=f"We have {dropped} actions blocked: DROP in {len(lines)} lines"
        )

    # 4. Return a summary
    return {
        "statusCode": 200,
        "body": json.dumps(f"We have {dropped} actions blocked: DROP in {len(lines)} lines")
    }
