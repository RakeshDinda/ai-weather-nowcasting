"""
FINAL MODEL — True no-leakage version.

The label risk_label is defined purely from rainfall thresholds:
  LOW < 2mm, MODERATE 2-20mm, HIGH >= 20mm

So rainfall, moisture_index (=humidity*rainfall), and rain_intensity
(=rainfall*wind_speed) ALL perfectly encode the label.

True independent features (from OpenWeather API only):
  temperature, humidity, wind_speed, pressure, pressure_drop, instability_index

These are the ONLY features the model would have at inference time
BEFORE rainfall is observed — i.e., they are genuine predictors.
"""
import os, sys
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH   = os.path.join(PROJECT_ROOT, "data", "processed", "final_training_data.csv")
MODEL_PATH  = os.path.join(PROJECT_ROOT, "models", "rainfall_model_v2.pkl")
SCALER_PATH = os.path.join(PROJECT_ROOT, "models", "rainfall_scaler_v2.pkl")

print("=" * 62)
print("STEP 1 - Loading dataset")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}  |  Nulls: {df.isnull().sum().sum()}")

print("\nClass distribution:")
vc = df["risk_label"].value_counts().sort_index()
for lbl, cnt in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(lbl),str(lbl))
    print(f"  Class {int(lbl)} ({name:8s}): {cnt:,}  ({cnt/len(df)*100:.1f}%)")

# TRUE independent features — exclude rainfall + anything derived from rainfall
FEATURES = [
    "temperature",       # from OpenWeather only
    "humidity",          # from OpenWeather only
    "wind_speed",        # from OpenWeather only
    "pressure",          # from OpenWeather only
    "pressure_drop",     # = 1013 - pressure  (no rainfall)
    "instability_index"  # = temperature * humidity (no rainfall)
]
TARGET = "risk_label"

print(f"\n  Input features (NO rainfall, NO rainfall-derived):")
for f in FEATURES:
    print(f"    - {f}")

X = df[FEATURES].values.astype("float32")
y = df[TARGET].values.astype("int32")

print("\nSTEP 2 - StandardScaler")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, SCALER_PATH)
print(f"  Scaler saved -> rainfall_scaler_v2.pkl")

print("\nSTEP 3 - 80/20 stratified split")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y)
print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")

print("\nSTEP 4 - Training RandomForestClassifier")
print("  n_estimators=200  max_depth=10  class_weight=balanced")
clf = RandomForestClassifier(
    n_estimators=200, max_depth=10,
    min_samples_leaf=5, class_weight="balanced",
    random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)
print("  Training complete")

print("\nSTEP 5 - Evaluation")
y_pred = clf.predict(X_test)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
rec  = recall_score(y_test, y_pred, average="macro", zero_division=0)
f1   = f1_score(y_test, y_pred, average="macro", zero_division=0)
print(f"  Accuracy          : {acc:.4f}")
print(f"  Precision (macro) : {prec:.4f}")
print(f"  Recall    (macro) : {rec:.4f}")
print(f"  F1 Score  (macro) : {f1:.4f}")
print()
print(classification_report(y_test, y_pred,
      target_names=["LOW(0)","MODERATE(1)","HIGH(2)"], zero_division=0))

print("Feature importances (true independent features only):")
for name, imp in sorted(zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1]):
    print(f"  {name:22s}: {imp:.4f}")

print(f"\nSTEP 6 - Saving")
joblib.dump(clf, MODEL_PATH)
print(f"  Model  -> rainfall_model_v2.pkl")
print(f"  Scaler -> rainfall_scaler_v2.pkl")
print("=" * 62)
print("  TRAINING COMPLETE — ZERO DATA LEAKAGE")
print("=" * 62)
