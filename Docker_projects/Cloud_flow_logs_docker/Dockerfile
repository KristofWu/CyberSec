FROM python:3.12-slim

WORKDIR /app

COPY src/ ./src/

COPY data/ ./data/

CMD ["python", "src/flow_analysis.py", "data/logs.log"]

