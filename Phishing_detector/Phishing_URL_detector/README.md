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

2. **Dataset** — a CSV with `url` and `label` columns (0 = legitimate, 1 = phishing). Update the path at the top of the script to point to your file.

3. **Gemini API key** (free from [Google AI Studio](https://aistudio.google.com)) — create a `.env` file next to the script:
   ```
   GEMINI_API_KEY=your_key_here
   ```

4. **Run**
   ```bash
   python phishing_url_detector.py
   ```

## 🔐 Security note

The Gemini API key is loaded from a `.env` file via `python-dotenv` and never hardcoded. Add `.env` to `.gitignore` so the secret never reaches the repository.

## 🛠️ Tech stack

Python · pandas · scikit-learn (Random Forest) · Google Gemini API · python-dotenv
