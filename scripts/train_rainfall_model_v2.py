"""
Train a real ML model WITHOUT data leakage.
Features : month, day, State (encoded), District (encoded)
Target   : risk_label  (0=LOW, 1=MODERATE, 2=HIGH)
Output   : models/rainfall_model_v2.pkl
Note     : season is constant (Monsoon only) in the IMD dataset -> not useful.
           State + District provide genuine geographic signal.
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
DATA_PATH  = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "rainfall_model_v2.pkl")
META_PATH  = os.path.join(PROJECT_ROOT, "models", "rainfall_model_v2_meta.pkl")

print("=" * 62)
print("STEP 1 - Loading dataset")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["month","day","State","District","risk_label"])
print(f"  Rows: {len(df):,}  |  Unique states: {df['State'].nunique()}  |  Districts: {df['District'].nunique()}")

print("\nClass distribution:")
vc = df["risk_label"].value_counts().sort_index()
for lbl, cnt in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(lbl),str(lbl))
    print(f"  Class {int(lbl)} ({name:8s}): {cnt:,}  ({cnt/len(df)*100:.1f}%)")

if len(vc) < 3:
    print("ERROR: Need all 3 classes."); sys.exit(1)

print("\nSTEP 2 - Encoding categorical features")
le_state    = LabelEncoder()
le_district = LabelEncoder()
df["state_enc"]    = le_state.fit_transform(df["State"])
df["district_enc"] = le_district.fit_transform(df["District"])
print(f"  States encoded    : {len(le_state.classes_)}")
print(f"  Districts encoded : {len(le_district.classes_)}")

FEATURES = ["month", "day", "state_enc", "district_enc"]
TARGET   = "risk_label"
print(f"\n  Features used (NO rainfall!): {FEATURES}")

X = df[FEATURES].values.astype("float32")
y = df[TARGET].values.astype("int32")

print("\nSTEP 3 - 80/20 stratified split")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")

print("\nSTEP 4 - Training RandomForestClassifier")
print("  n_estimators=200  max_depth=8  class_weight=balanced")
clf = RandomForestClassifier(
    n_estimators=200, max_depth=8,
    class_weight="balanced",
    min_samples_leaf=5,
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

print("Feature importances:")
for name, imp in sorted(zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1]):
    print(f"  {name:15s}: {imp:.4f}")

print(f"\nSTEP 6 - Saving to {MODEL_PATH}")
joblib.dump(clf, MODEL_PATH)
meta = {"le_state": le_state, "le_district": le_district, "features": FEATURES}
joblib.dump(meta, META_PATH)
print("  Model saved -> rainfall_model_v2.pkl")
print("  Meta  saved -> rainfall_model_v2_meta.pkl")
print("=" * 62)
print("  TRAINING COMPLETE")
print("=" * 62)
