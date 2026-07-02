import os
import re
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


# --- load data ---
df = pd.read_csv(r'C:\Users\Krzychu\Documents\Python\Phishing_URL_detector\data\phishing_url_dataset_unique.csv')


# --- feature engineering ---
df["url_length"] = df["url"].str.len()
df["dot_count"] = df["url"].str.count(r"\.")
df["hyphen_count"] = df["url"].str.count("-")
df["digit_count"] = df["url"].str.count(r"\d")
df["has_https"] = df["url"].str.startswith("https").astype(int)


def has_ip(url):
    if re.search(r"https?://\d+\.\d+\.\d+\.\d+", url):
        return 1
    else:
        return 0


df["has_ip"] = df["url"].apply(has_ip)


def has_suspicious(url):
    suspicious = ["login", "verify", "secure", "account", "bank", "update"]
    url_lower = url.lower()
    for word in suspicious:
        if word in url_lower:
            return 1
    return 0


df["has_suspicious"] = df["url"].apply(has_suspicious)


# --- train / test split ---
features = ["url_length", "dot_count", "hyphen_count", "digit_count", "has_https", "has_ip", "has_suspicious"]

X = df[features]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Train:", X_train.shape, "Test:", y_test.shape)


# --- train model ---
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

print("Model trained.")


# --- evaluate ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy: ", accuracy)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))


# --- LLM explanation ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def explain_url(url, features):
    prompt = f""" You are a security researcher.

Analyse following URL in terms of phishing
URL: {url}

Features:

-URL length: {features['url_length']}
-Digits: {features['digit_count']}
-uses IP instead of domain: {'yes' if features['has_ip'] else 'no'}
-uses https: {'yes' if features['has_https'] else 'no'}
-dots: {features['dot_count']}

Explain shortly why following URL might be phishing"""
    llm = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = llm.generate_content(prompt)
    return response.text


row = df[df['label'] == 1].iloc[0]
print("URL:", row['url'])
print(explain_url(row['url'], row))
