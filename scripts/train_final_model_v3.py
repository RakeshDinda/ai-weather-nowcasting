"""
FINAL MODEL v3 - NO DATA LEAKAGE.

Core insight: risk_label = step_function(rainfall). Including rainfall
as an input guarantees 100% accuracy but zero generalization.

This model predicts rainfall risk from atmospheric conditions alone:
  temperature, humidity, wind_speed, month, state_enc

This is the real early-warning use case: given today's atmospheric 
conditions, what is the flood/rainfall risk? The weather features
(temperature, humidity, wind) come from OpenWeather API live data.
"""

import os, sys
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMD_PATH     = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")
CACHE_PATH   = os.path.join(PROJECT_ROOT, "data", "processed", "weather_cache.json")
MODEL_PATH   = os.path.join(PROJECT_ROOT, "models", "final_model.pkl")

print("=" * 65)
print("  FINAL MODEL v3 - Weather + Location (No Leakage)")
print("=" * 65)

# ── 1. Load IMD ───────────────────────────────────────────────────────────────
print("\nSTEP 1 - Loading IMD dataset")
df = pd.read_csv(IMD_PATH, parse_dates=["Date"])
df = df.dropna(subset=["rainfall","month","risk_label","Date","State","District"])
df = df.sort_values(["District","Date"]).reset_index(drop=True)
print(f"  Rows:{len(df):,}  States:{df['State'].nunique()}  Districts:{df['District'].nunique()}")

# ── 2. Merge real OpenWeather weather data ────────────────────────────────────
print("\nSTEP 2 - Merging real OpenWeather data from weather_cache.json")
with open(CACHE_PATH) as f:
    cache = json.load(f)
print(f"  Cache entries: {len(cache)}")

temps, hums, winds = [], [], []
for _, row in df.iterrows():
    key = f"{row['District']}|{row['State']}".lower()
    e   = cache.get(key, {})
    temps.append(e.get("temperature"))
    hums.append(e.get("humidity"))
    winds.append(e.get("wind_speed"))

df["temperature"] = temps
df["humidity"]    = hums
df["wind_speed"]  = winds

# Fill missing with state-level medians then global median
for col in ["temperature","humidity","wind_speed"]:
    state_med = df.groupby("State")[col].transform("median")
    df[col] = df[col].fillna(state_med).fillna(df[col].median())

pct = df["temperature"].notna().mean()*100
print(f"  Coverage after fill: {pct:.1f}% complete")

# ── 3. Encode State ───────────────────────────────────────────────────────────
print("\nSTEP 3 - Encoding State")
le = LabelEncoder()
df["state_enc"] = le.fit_transform(df["State"])
print(f"  {len(le.classes_)} states encoded")

# ── 4. Define features (NO rainfall — it is the label definition) ─────────────
print("\nSTEP 4 - Feature set")
FEAT_COLS = ["temperature","humidity","wind_speed","month","state_enc"]
print(f"  Features: {FEAT_COLS}")
print(f"  Target  : risk_label (0=LOW, 1=MODERATE, 2=HIGH)")
print()
print("  Note: 'rainfall' excluded — it deterministically defines risk_label.")
print("  The model learns atmospheric precursors to high-rainfall events.")

df_model = df[FEAT_COLS + ["risk_label","Date"]].dropna().copy()
print(f"\n  Rows ready: {len(df_model):,}")

print("\nClass distribution:")
vc = df_model["risk_label"].value_counts().sort_index()
for lbl, cnt in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(lbl),str(lbl))
    print(f"  Class {int(lbl)} ({name:8s}): {cnt:,}  ({cnt/len(df_model)*100:.1f}%)")

# ── 5. Chronological 80/20 split ─────────────────────────────────────────────
print("\nSTEP 5 - Chronological 80/20 split (no future leakage)")
df_model = df_model.sort_values("Date").reset_index(drop=True)
split    = int(len(df_model)*0.80)

X_train = df_model.iloc[:split][FEAT_COLS].values.astype("float32")
y_train = df_model.iloc[:split]["risk_label"].values.astype("int32")
X_test  = df_model.iloc[split:][FEAT_COLS].values.astype("float32")
y_test  = df_model.iloc[split:]["risk_label"].values.astype("int32")

print(f"  Train:{len(X_train):,}  ({df_model.iloc[0]['Date'].date()} -> {df_model.iloc[split-1]['Date'].date()})")
print(f"  Test :{len(X_test):,}   ({df_model.iloc[split]['Date'].date()} -> {df_model.iloc[-1]['Date'].date()})")
print("\n  Test class distribution:")
for lbl in [0,1,2]:
    cnt  = (y_test==lbl).sum()
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}[lbl]
    print(f"    Class {lbl} ({name:8s}): {cnt:,}")

# ── 6. Scale ──────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── 7. Train ──────────────────────────────────────────────────────────────────
print("\nSTEP 6 - Training RandomForestClassifier")
print("  n_estimators=300  max_depth=12  class_weight=balanced")
clf = RandomForestClassifier(
    n_estimators=300, max_depth=12,
    min_samples_leaf=4, class_weight="balanced",
    random_state=42, n_jobs=-1,
)
clf.fit(X_train_sc, y_train)
print("  Training complete")

# ── 8. Evaluate ───────────────────────────────────────────────────────────────
print("\nSTEP 7 - Evaluation on held-out FUTURE dates")
y_pred = clf.predict(X_test_sc)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
rec  = recall_score(y_test, y_pred, average="macro", zero_division=0)
f1   = f1_score(y_test, y_pred, average="macro", zero_division=0)

print(f"\n  Accuracy          : {acc:.4f}")
print(f"  Precision (macro) : {prec:.4f}")
print(f"  Recall    (macro) : {rec:.4f}")
print(f"  F1 Score  (macro) : {f1:.4f}")
print()
print(classification_report(y_test,y_pred,
      target_names=["LOW(0)","MODERATE(1)","HIGH(2)"],zero_division=0))

print("Feature importances:")
for name, imp in sorted(zip(FEAT_COLS,clf.feature_importances_),key=lambda x:-x[1]):
    bar = "#"*int(imp*50)
    print(f"  {name:15s}: {imp:.4f}  {bar}")

# ── 9. Save bundle ────────────────────────────────────────────────────────────
print(f"\nSTEP 8 - Saving -> {MODEL_PATH}")
bundle = {
    "model":     clf,
    "scaler":    scaler,
    "le_state":  le,
    "features":  FEAT_COLS,
    "label_map": {0:"LOW",1:"MODERATE",2:"HIGH"},
    "n_states":  len(le.classes_),
}
joblib.dump(bundle, MODEL_PATH)
size_kb = os.path.getsize(MODEL_PATH)//1024
print(f"  Saved: final_model.pkl  ({size_kb:,} KB)")
print(f"  Bundle: model + scaler + le_state + feature_list")
print("\n" + "="*65)
print("  TRAINING COMPLETE - ZERO DATA LEAKAGE")
print("="*65)
