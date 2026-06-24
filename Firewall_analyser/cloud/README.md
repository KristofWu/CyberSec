# ☁️ Firewall Log Analyzer — Phase 3: Cloud (AWS)

> Phase 3 takes the local analyser into the cloud: a log uploaded to S3 automatically triggers a Lambda function that analyses it and sends an email alert via SNS — a fully serverless, event-driven security pipeline.
>
> Faza 3 przenosi lokalny analizator do chmury: log wrzucony do S3 automatycznie wyzwala funkcję Lambda, która go analizuje i wysyła alert mailowy przez SNS — w pełni serverless, sterowany zdarzeniami pipeline bezpieczeństwa.

🇬🇧 [English](#-english) | 🇵🇱 [Polski](#-polski)

---

## 🇬🇧 English

### 🎯 What this phase adds

Phases 1–2 run on your own machine. Phase 3 puts the pipeline in **AWS**, so it runs without your computer and reacts automatically to new logs.

### 🏗️ Architecture

```
   firewall_big.log
        │  upload
        ▼
   ┌─────────┐   S3 "object created" event (automatic trigger)
   │   S3    │ ─────────────────────────────────────────┐
   │ bucket  │                                           │
   └─────────┘                                           ▼
                                                   ┌───────────┐
                                                   │  Lambda   │  reads log (boto3),
                                                   │ (Python)  │  counts DROP lines
                                                   └───────────┘
                                                         │ if DROPs > threshold
                                                         ▼  publish
                                                   ┌───────────┐
                                                   │    SNS    │  topic "Firewall-alerts"
                                                   │   topic   │
                                                   └───────────┘
                                                         │ email subscription
                                                         ▼
                                                   📧 email alert
```

### 🧩 The AWS services used

- **S3 (Simple Storage Service)** — object storage. The firewall log lives in a bucket (`kris-firewall-logs`) instead of on a local disk.
- **Lambda** — serverless compute. A Python function runs *on demand* (no server to manage), reads the log from S3 with `boto3`, and analyses it.
- **SNS (Simple Notification Service)** — pub/sub notifications. The Lambda publishes to a topic; an email subscription delivers the alert.
- **IAM** — permissions. The Lambda's execution role is granted exactly what it needs: read S3, publish SNS.
- **AWS Budgets** — a cost alert set *before* anything was deployed, as a safety net.

### ⚡ Event-driven: the automatic trigger

The Lambda is wired to the S3 bucket: **uploading a file automatically invokes the function** — no manual "Test" click. This is the *event-driven* model real systems use: an event (new log) triggers an action (analysis + alert).

> ⚠️ **Loop safety:** a Lambda must never *write* a file into the same bucket that triggers it — that creates an infinite invoke loop (and a bill). This function only *reads* from S3, so it's safe.

### 🔐 Security choices

- **Least privilege** — the role uses `AmazonS3ReadOnlyAccess` (read, not write) because the function only reads the log. (`AmazonSNSFullAccess` is used for simplicity; in production this would be narrowed to `sns:Publish` on the single topic ARN.)
- **Private bucket** — "Block all public access" stays on; the log is never public.
- **Budget alert first** — a $1 cost budget was created before deploying anything, so any unexpected spend triggers an email immediately.

### 🛠️ Why pure Python (no pandas/sklearn) in the cloud

The full ML analyser (Phases 1–2) uses pandas and scikit-learn. Those are heavy to package into a vanilla Lambda (size limits, layers/containers needed). This cloud function is a deliberately lightweight, pure-Python version that demonstrates the **S3 → Lambda → SNS** mechanics cleanly. Porting the full ML pipeline (via Lambda layers or a container image) is a natural next step.

### 📋 Deployment steps (summary)

1. Create an S3 bucket; upload the log.
2. Create a Lambda function (Python); paste `lambda_function.py`.
3. Attach IAM policies to the Lambda role: S3 read, SNS publish.
4. Create an SNS topic; subscribe your email; **confirm** the subscription.
5. Set the Lambda timeout to ~30s (S3 + SNS calls need more than the default 3s).
6. Add an S3 trigger (all object-create events) for automatic invocation.
7. Set an AWS Budgets cost alert.

---

## 🇵🇱 Polski

### 🎯 Co dodaje ta faza

Fazy 1–2 działają na Twoim komputerze. Faza 3 umieszcza pipeline w **AWS**, więc działa bez Twojego komputera i reaguje automatycznie na nowe logi.

### 🏗️ Architektura

```
   firewall_big.log
        │  upload
        ▼
   ┌─────────┐   zdarzenie S3 "obiekt utworzony" (automatyczny trigger)
   │   S3    │ ─────────────────────────────────────────┐
   │ bucket  │                                           │
   └─────────┘                                           ▼
                                                   ┌───────────┐
                                                   │  Lambda   │  czyta log (boto3),
                                                   │ (Python)  │  liczy linie DROP
                                                   └───────────┘
                                                         │ jeśli DROP > próg
                                                         ▼  publish
                                                   ┌───────────┐
                                                   │    SNS    │  temat "Firewall-alerts"
                                                   │   temat   │
                                                   └───────────┘
                                                         │ subskrypcja email
                                                         ▼
                                                   📧 alert mailowy
```

### 🧩 Użyte usługi AWS

- **S3 (Simple Storage Service)** — magazyn obiektów. Log firewalla mieszka w buckecie (`kris-firewall-logs`) zamiast na lokalnym dysku.
- **Lambda** — obliczenia serverless. Funkcja Pythona uruchamia się *na żądanie* (bez serwera do zarządzania), czyta log z S3 przez `boto3` i analizuje go.
- **SNS (Simple Notification Service)** — powiadomienia pub/sub. Lambda publikuje do tematu; subskrypcja email dostarcza alert.
- **IAM** — uprawnienia. Rola wykonawcza Lambdy dostaje dokładnie to, czego potrzebuje: odczyt S3, publikacja SNS.
- **AWS Budgets** — alert kosztowy ustawiony *przed* wdrożeniem czegokolwiek, jako siatka bezpieczeństwa.

### ⚡ Event-driven: automatyczny trigger

Lambda jest podpięta do bucketa S3: **wrzucenie pliku automatycznie uruchamia funkcję** — bez ręcznego „Test". To model *sterowany zdarzeniami*, którego używają prawdziwe systemy: zdarzenie (nowy log) wyzwala akcję (analiza + alert).

> ⚠️ **Bezpieczeństwo pętli:** Lambda nigdy nie może *zapisywać* pliku do tego samego bucketa, który ją wyzwala — to tworzy nieskończoną pętlę wywołań (i rachunek). Ta funkcja tylko *czyta* z S3, więc jest bezpieczna.

### 🔐 Decyzje bezpieczeństwa

- **Najmniejsze uprawnienia** — rola używa `AmazonS3ReadOnlyAccess` (odczyt, nie zapis), bo funkcja tylko czyta log. (`AmazonSNSFullAccess` użyte dla uproszczenia; w produkcji zawęziłoby się do `sns:Publish` na jednym ARN tematu.)
- **Prywatny bucket** — „Block all public access" pozostaje włączone; log nigdy nie jest publiczny.
- **Najpierw alert budżetowy** — budżet kosztowy 1$ utworzony przed wdrożeniem czegokolwiek, więc każdy nieoczekiwany wydatek natychmiast wyzwala maila.

### 🛠️ Czemu czysty Python (bez pandas/sklearn) w chmurze

Pełny analizator ML (Fazy 1–2) używa pandas i scikit-learn. Te są ciężkie do spakowania w zwykłą Lambdę (limity rozmiaru, potrzebne warstwy/kontenery). Ta funkcja chmurowa to celowo lekka, czysto-pythonowa wersja, która czysto demonstruje mechanikę **S3 → Lambda → SNS**. Przeniesienie pełnego pipeline ML (przez warstwy Lambda albo obraz kontenera) to naturalny kolejny krok.

### 📋 Kroki wdrożenia (podsumowanie)

1. Stwórz bucket S3; wrzuć log.
2. Stwórz funkcję Lambda (Python); wklej `lambda_function.py`.
3. Podłącz polityki IAM do roli Lambdy: odczyt S3, publikacja SNS.
4. Stwórz temat SNS; zasubskrybuj swój email; **potwierdź** subskrypcję.
5. Ustaw timeout Lambdy na ~30s (wywołania S3 + SNS potrzebują więcej niż domyślne 3s).
6. Dodaj trigger S3 (wszystkie zdarzenia create) dla automatycznego uruchamiania.
7. Ustaw alert kosztowy AWS Budgets.
