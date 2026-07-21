import os
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

from features import extract_features, FEATURES

# --- config ---
MODEL_PATH = os.getenv("MODEL_PATH", "../models/phishing_model.pkl")

# --- load secrets and configure the LLM ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- load the trained model ONCE, at startup (not per request!) ---
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Phishing URL Detector API")


# --- request/response schemas (FastAPI validates these automatically) ---
class URLRequest(BaseModel):
    url: str


# --- endpoints ---
@app.get("/health")
def health():
    """Liveness check - Kubernetes will use this later."""
    return {"status": "ok"}


@app.post("/predict")
def predict(request: URLRequest):
    """Classify a URL and explain the verdict."""
    url = request.url

    # 1. extract the same 7 features the model was trained on
    feats = extract_features(url)

    # 2. the model expects a 2D structure with columns in the right order
    X = pd.DataFrame([feats])[FEATURES]

    # 3. predict: 0 = legitimate, 1 = phishing
    prediction = int(model.predict(X)[0])

    # 4. ask the LLM to explain
    explanation = explain_url(url, feats)

    return {
        "url": url,
        "prediction": "phishing" if prediction == 1 else "legitimate",
        "features": feats,
        "explanation": explanation,
    }


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