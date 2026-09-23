"""
Train a RandomForestClassifier for rainfall risk prediction using the cleaned IMD dataset.
Features : rainfall, month, season (encoded)
Target   : risk_label  (0=LOW, 1=MODERATE, 2=HIGH)
Output   : models/rainfall_model.pkl
"""

import os, sys
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH    = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")
MODEL_PATH   = os.path.join(PROJECT_ROOT, "models", "rainfall_model.pkl")
ENC_PATH     = os.path.join(PROJECT_ROOT, "models", "season_encoder.pkl")

print("="*60)
print("STEP 1 - Loading dataset")
df = pd.read_csv(DATA_PATH)
print(f"  Rows loaded : {len(df):,}")

df = df.dropna(subset=["rainfall","month","season","risk_label"])
print(f"  After drop  : {len(df):,} rows")

print("\nRisk-label distribution:")
vc = df["risk_label"].value_counts().sort_index()
for label, count in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(label), str(label))
    print(f"  Class {int(label)} ({name:8s}): {count:,}  ({count/len(df)*100:.1f}%)")

if len(vc) < 3:
    print("ERROR: Not all 3 classes present."); sys.exit(1)

print("\nSTEP 2 - Encoding season")
le = LabelEncoder()
df["season_enc"] = le.fit_transform(df["season"])
print(f"  Mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")
joblib.dump(le, ENC_PATH)
print(f"  Encoder saved -> {ENC_PATH}")

X = df[["rainfall","month","season_enc"]].values.astype("float32")
y = df["risk_label"].values.astype("int32")

print("\nSTEP 3 - 80/20 stratified split")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")

print("\nSTEP 4 - Training RandomForest (200 trees, depth=10)")
clf = RandomForestClassifier(n_estimators=200, max_depth=10,
                              class_weight="balanced", random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)
print("  Training complete")

print("\nSTEP 5 - Evaluation")
y_pred = clf.predict(X_test)
print(f"  Accuracy          : {accuracy_score(y_test,y_pred):.4f}")
print(f"  Precision (macro) : {precision_score(y_test,y_pred,average='macro',zero_division=0):.4f}")
print(f"  Recall    (macro) : {recall_score(y_test,y_pred,average='macro',zero_division=0):.4f}")
print(f"  F1 Score  (macro) : {f1_score(y_test,y_pred,average='macro',zero_division=0):.4f}")
print("\nClassification Report:")
print(classification_report(y_test,y_pred,
      target_names=["LOW(0)","MODERATE(1)","HIGH(2)"],zero_division=0))

importances = clf.feature_importances_
print("Feature importances:")
for n, i in zip(["rainfall","month","season_enc"], importances):
    print(f"  {n:12s}: {i:.4f}")

print(f"\nSTEP 6 - Saving model -> {MODEL_PATH}")
joblib.dump(clf, MODEL_PATH)
print("  Model saved successfully")
print("="*60)
print("TRAINING COMPLETE")
print("="*60)
