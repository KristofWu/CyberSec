import os
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
from features import extract_features, FEATURES

DATA_PATH = os.getenv("DATA_PATH", "../data/phishing_url_dataset_unique.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "../models/phishing_model.pkl")

# --- load data ---
df = pd.read_csv(DATA_PATH)


# --- feature engineering ---
feature_row = df["url"].apply(extract_features)
df = pd.concat([df, pd.DataFrame(list(feature_row))], axis=1)


# --- train / test split ---

X = df[FEATURES]
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

joblib.dump(model, MODEL_PATH)
print(f"Model saved to: {MODEL_PATH}")