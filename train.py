"""
train.py — Run this ONCE to train the ML model.
Usage:  python train.py --dataset your_dataset.csv
"""
import os, re, argparse
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from scipy.sparse import hstack

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
VEC_PATH   = os.path.join(DATA_DIR, "vectorizer.pkl")

def extract_features(text):
    links = len(re.findall(r'http[s]?://', text))
    sus_w = len(re.findall(r'(free|win|urgent|offer|click|bank|verify|password)', text.lower()))
    return [links, sus_w, len(text)]

def train(csv_path):
    os.makedirs(DATA_DIR, exist_ok=True)

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    text_col = next((c for c in df.columns if c in ['text','email','message','content']), None)
    label_col= next((c for c in df.columns if c in ['label','spam','category','class']), None)

    if not text_col or not label_col:
        raise Exception("❌ CSV must have text & label columns")

    df.rename(columns={text_col:'text', label_col:'label'}, inplace=True)
    df['label'] = df['label'].astype(str).str.lower().str.strip()
    df['label'] = df['label'].map({'spam':1,'ham':0,'safe':0,'malicious':1,'1':1,'0':0})
    df.dropna(inplace=True)
    print(f"✅ Dataset loaded: {df.shape}")

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_text = vectorizer.fit_transform(df["text"])
    extra  = np.array([extract_features(t) for t in df["text"]])
    X      = hstack((X_text, extra))
    y      = df["label"]

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X, y)

    joblib.dump(model,      MODEL_PATH)
    joblib.dump(vectorizer, VEC_PATH)
    print(f"✅ Model saved → {MODEL_PATH}")
    print(f"✅ Vectorizer  → {VEC_PATH}")
    print("🎉 Training complete! Now run: python app.py")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True, help='Path to CSV dataset')
    args = parser.parse_args()
    train(args.dataset)
