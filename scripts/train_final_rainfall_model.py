"""
FINAL IMPROVED MODEL — Lag features, zero leakage.

Root cause of 100% accuracy: risk_label is a pure step-function of
today's rainfall. Including rainfall (or extreme_flag which is also
derived from rainfall) directly encodes the answer.

SOLUTION: Use ONLY lag/rolling features (past days) + month.
The model must predict TODAY's risk from YESTERDAY's conditions.
This is the genuine early-warning use case.

Features:
  rainfall_lag1        - yesterday rainfall (same district)
  rainfall_lag2        - 2 days ago (same district)
  rainfall_rolling_avg - 3-day trailing average (same district)
  month                - calendar month

Note: extreme_flag also dropped (= f(today's rainfall) -> leakage)
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH    = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")
MODEL_PATH   = os.path.join(PROJECT_ROOT, "models", "final_rainfall_model.pkl")

print("=" * 65)
print("  FINAL RAINFALL MODEL — Pure Lag Features (No Leakage)")
print("=" * 65)

# STEP 1: Load
print("\nSTEP 1 - Loading dataset")
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
df = df.dropna(subset=["rainfall", "month", "risk_label", "Date"])
df = df.sort_values(["District", "Date"]).reset_index(drop=True)
print(f"  Rows: {len(df):,}  Districts: {df['District'].nunique()}")
print(f"  Date range: {df['Date'].min().date()} -> {df['Date'].max().date()}")

# STEP 2: Lag features (all past-only, computed per district)
print("\nSTEP 2 - Computing lag features per District group")
grp = df.groupby("District")["rainfall"]

df["rainfall_lag1"]        = grp.shift(1)
df["rainfall_lag2"]        = grp.shift(2)
df["rainfall_rolling_avg"] = grp.transform(
    lambda x: x.shift(1).rolling(3, min_periods=1).mean()
)

print(f"  lag1 valid        : {df['rainfall_lag1'].notna().sum():,}")
print(f"  lag2 valid        : {df['rainfall_lag2'].notna().sum():,}")
print(f"  rolling_avg valid : {df['rainfall_rolling_avg'].notna().sum():,}")

FEATURES = [
    "rainfall_lag1",
    "rainfall_lag2",
    "rainfall_rolling_avg",
    "month",
]
TARGET = "risk_label"

df_model = df[FEATURES + [TARGET, "Date"]].dropna().copy()
print(f"\n  Rows after dropping NaN rows: {len(df_model):,}")

print("\nClass distribution:")
vc = df_model[TARGET].value_counts().sort_index()
for lbl, cnt in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(lbl),str(lbl))
    print(f"  Class {int(lbl)} ({name:8s}): {cnt:,}  ({cnt/len(df_model)*100:.1f}%)")

# STEP 3: Chronological split
print("\nSTEP 3 - Chronological 80/20 split (no future leakage)")
df_model = df_model.sort_values("Date").reset_index(drop=True)
split_idx = int(len(df_model) * 0.80)

train_df = df_model.iloc[:split_idx]
test_df  = df_model.iloc[split_idx:]
print(f"  Train: {len(train_df):,}  ({train_df['Date'].min().date()} -> {train_df['Date'].max().date()})")
print(f"  Test : {len(test_df):,}  ({test_df['Date'].min().date()} -> {test_df['Date'].max().date()})")

X_train = train_df[FEATURES].values.astype("float32")
y_train = train_df[TARGET].values.astype("int32")
X_test  = test_df[FEATURES].values.astype("float32")
y_test  = test_df[TARGET].values.astype("int32")

print("\n  Test class distribution:")
for lbl in [0,1,2]:
    cnt = (y_test == lbl).sum()
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}[lbl]
    print(f"    Class {lbl} ({name:8s}): {cnt}")

# STEP 4: Train
print("\nSTEP 4 - Training RandomForestClassifier")
print("  n_estimators=300  max_depth=12  class_weight=balanced")
clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=4,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
clf.fit(X_train, y_train)
print("  Training complete")

# STEP 5: Evaluate
print("\nSTEP 5 - Evaluation")
y_pred = clf.predict(X_test)

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
rec  = recall_score(y_test, y_pred, average="macro", zero_division=0)
f1   = f1_score(y_test, y_pred, average="macro", zero_division=0)

print(f"\n  Accuracy          : {acc:.4f}")
print(f"  Precision (macro) : {prec:.4f}")
print(f"  Recall    (macro) : {rec:.4f}")
print(f"  F1 Score  (macro) : {f1:.4f}")
print()
print(classification_report(
    y_test, y_pred,
    target_names=["LOW(0)","MODERATE(1)","HIGH(2)"],
    zero_division=0,
))

print("Feature importances:")
for name, imp in sorted(zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1]):
    print(f"  {name:25s}: {imp:.4f}")

# STEP 6: Save
print(f"\nSTEP 6 - Saving")
joblib.dump(clf, MODEL_PATH)
meta = {"features": FEATURES, "target": TARGET}
joblib.dump(meta, MODEL_PATH.replace(".pkl", "_meta.pkl"))
size_kb = os.path.getsize(MODEL_PATH) // 1024
print(f"  Saved: final_rainfall_model.pkl  ({size_kb:,} KB)")
print(f"  Saved: final_rainfall_model_meta.pkl")

print("\n" + "=" * 65)
print("  TRAINING COMPLETE — ZERO DATA LEAKAGE")
print("=" * 65)
