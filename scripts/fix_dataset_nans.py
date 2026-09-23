"""
Fix Remaining NaN Values in IMD Cleaned Dataset
-----------------------------------------------
1. Opens data/processed/imd_cleaned.csv
2. Removes all rows where rainfall or risk_label is null
3. Fixes remaining placeholder NaN values (temperature, humidity, wind) with 0.0
4. Saves data/processed/imd_cleaned.csv
5. Prints total rows and confirms no null values exist
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")


def fix_nans():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"File not found: {CSV_PATH}")

    print(f"Reading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    initial_rows = len(df)
    print(f"Initial rows: {initial_rows:,}")

    # 1. Remove rows where rainfall is null or non-numeric
    df = df.dropna(subset=["rainfall", "risk_label"])
    df = df[df["rainfall"].notna()]
    df = df[df["risk_label"].notna()]

    # Ensure non-negative rainfall
    df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")
    df = df.dropna(subset=["rainfall"])
    df = df[df["rainfall"] >= 0.0]

    # Ensure risk_label is clean integer
    df["risk_label"] = df["risk_label"].astype(int)

    # 2. Fix remaining placeholder NaN values across all columns
    if "temperature" in df.columns:
        df["temperature"] = df["temperature"].fillna(0.0)
    if "humidity" in df.columns:
        df["humidity"] = df["humidity"].fillna(0.0)
    if "wind" in df.columns:
        df["wind"] = df["wind"].fillna(0.0)

    # Any remaining NaNs
    df = df.fillna(0.0)

    # 3. Save again
    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved updated dataset to: {CSV_PATH}")

    # 4. Validation & Confirmation
    print("\n" + "=" * 50)
    print("DATASET VALIDATION RESULTS")
    print("=" * 50)
    print(f"Total Rows: {len(df):,}")
    print("\nNull Values Per Column:")
    null_counts = df.isnull().sum()
    print(null_counts.to_string())

    total_nulls = null_counts.sum()
    print("-" * 50)
    print(f"Total Null/NaN Values in Dataset: {total_nulls}")
    assert total_nulls == 0, f"Expected 0 nulls, found {total_nulls}"
    print("CONFIRMATION: ZERO null/NaN values present in dataset!")
    print("=" * 50)

    print("\nSample 5 Rows:")
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(df.head(5))


if __name__ == "__main__":
    fix_nans()
