"""
Recalculate Rainfall Level & Risk Label
---------------------------------------
Updates label distribution in data/processed/imd_cleaned.csv using:
  - LOW:      rainfall < 2.0 mm       -> risk_label = 0
  - MODERATE: 2.0 <= rainfall < 20.0  -> risk_label = 1
  - HIGH:     rainfall >= 20.0 mm     -> risk_label = 2
"""

import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")


def recalculate_labels():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"File not found: {CSV_PATH}")

    print(f"Loading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Total Rows: {len(df):,}")

    # Define thresholds
    conditions = [
        (df["rainfall"] < 2.0),
        (df["rainfall"] >= 2.0) & (df["rainfall"] < 20.0),
        (df["rainfall"] >= 20.0)
    ]
    levels = ["LOW", "MODERATE", "HIGH"]
    labels = [0, 1, 2]

    # Recalculate
    df["rainfall_level"] = np.select(conditions, levels, default="LOW")
    df["risk_label"] = np.select(conditions, labels, default=0).astype(int)

    # Save
    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved updated dataset to: {CSV_PATH}")

    # Validation
    print("\n" + "=" * 50)
    print("VALIDATION: UPDATED RISK LABEL DISTRIBUTION")
    print("=" * 50)
    counts = df["risk_label"].value_counts().sort_index()
    print("risk_label value_counts:")
    print(counts.to_string())

    percentages = (df["risk_label"].value_counts(normalize=True).sort_index() * 100)
    print("\nrisk_label percentages:")
    for label, pct in percentages.items():
        name = "LOW (<2mm)" if label == 0 else "MODERATE (2-20mm)" if label == 1 else "HIGH (>=20mm)"
        print(f"  Class {label} ({name}): {counts[label]:,} rows ({pct:.2f}%)")

    # Ensure all 3 classes exist
    unique_classes = set(df["risk_label"].unique())
    assert unique_classes == {0, 1, 2}, f"Missing classes! Found: {unique_classes}"
    print("-" * 50)
    print("SUCCESS: All 3 risk classes (0, 1, 2) exist and are well-distributed!")
    print("=" * 50)

    print("\nSample 5 Rows:")
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(df.head(5))


if __name__ == "__main__":
    recalculate_labels()
