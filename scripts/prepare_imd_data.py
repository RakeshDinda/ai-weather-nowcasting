"""
IMD Rainfall Dataset Preparation Script
---------------------------------------
Cleans and prepares real Indian Meteorological Department (IMD) daily district-wise rainfall
data for ML training and future multi-source API integration.

Pipeline Steps:
1. Load raw dataset: data/raw/rainfall_districtwise_daily_imd.csv
2. Keep core columns: State, District, Date, Daily Actual -> rainfall
3. Clean and convert Date to datetime, drop nulls and invalid values
4. Feature Engineering: month, day, season (Monsoon, Winter, Summer)
5. Create Target Labels: rainfall_level (LOW, MODERATE, HIGH) & risk_label (0, 1, 2)
6. Add Future-Ready Placeholders: temperature, humidity, wind (NULL/NaN)
7. Save cleaned data: data/processed/imd_cleaned.csv
8. Validate and output statistics
"""

import os
import sys
import pandas as pd
import numpy as np

# Path configurations
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "rainfall_districtwise_daily_imd.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_DATA_PATH = os.path.join(PROCESSED_DIR, "imd_cleaned.csv")


def load_raw_data(file_path: str) -> pd.DataFrame:
    """Reads raw IMD daily rainfall CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw IMD data file not found at: {file_path}")
    print(f"Loading raw IMD data from: {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Raw dataset loaded: {df.shape[0]:,} rows, {df.shape[1]} columns.")
    return df


def clean_imd_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters core columns, renames Daily Actual to rainfall,
    parses datetime, and drops invalid or missing records.
    """
    print("\n--- Cleaning Data ---")
    required_cols = ["State", "District", "Date", "Daily Actual"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns in input CSV: {missing}")

    # 1. Keep only required columns
    df_clean = df[required_cols].copy()

    # 2. Rename 'Daily Actual' -> 'rainfall'
    df_clean.rename(columns={"Daily Actual": "rainfall"}, inplace=True)

    # 3. Clean string columns
    df_clean["State"] = df_clean["State"].astype(str).str.strip()
    df_clean["District"] = df_clean["District"].astype(str).str.strip()

    # 4. Convert Date to datetime format
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")

    # 5. Ensure rainfall is numeric float
    df_clean["rainfall"] = pd.to_numeric(df_clean["rainfall"], errors="coerce")

    initial_len = len(df_clean)

    # 6. Drop null values across core fields
    df_clean = df_clean.dropna(subset=["State", "District", "Date", "rainfall"])

    # 7. Drop invalid negative rainfall values
    df_clean = df_clean[df_clean["rainfall"] >= 0.0].copy()

    dropped_count = initial_len - len(df_clean)
    print(f"Cleaned records: {len(df_clean):,} valid rows (dropped {dropped_count} invalid/null rows).")
    return df_clean


def engineer_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts month, day, and categorizes meteorological season:
      - Monsoon: Jun (6) - Sep (9)
      - Winter:  Oct (10) - Feb (2)
      - Summer:  Mar (3) - May (5)
    """
    print("\n--- Feature Engineering ---")
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    def map_season(month: int) -> str:
        if 6 <= month <= 9:
            return "Monsoon"
        elif month in [10, 11, 12, 1, 2]:
            return "Winter"
        else:
            return "Summer"

    df["season"] = df["month"].apply(map_season)
    print(f"Generated features: 'month', 'day', 'season'")
    print(f"Season counts:\n{df['season'].value_counts().to_string()}")
    return df


def create_target_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates rainfall hazard classifications and risk labels:
      - LOW (< 2.0 mm)             -> risk_label = 0
      - MODERATE (2.0 <= r < 20.0) -> risk_label = 1
      - HIGH (>= 20.0 mm)          -> risk_label = 2
    """
    print("\n--- Creating Target Labels ---")
    conditions = [
        (df["rainfall"] < 2.0),
        (df["rainfall"] >= 2.0) & (df["rainfall"] < 20.0),
        (df["rainfall"] >= 20.0)
    ]
    levels = ["LOW", "MODERATE", "HIGH"]
    labels = [0, 1, 2]

    df["rainfall_level"] = np.select(conditions, levels, default="LOW")
    df["risk_label"] = np.select(conditions, labels, default=0).astype(int)

    print("Rainfall Level & Risk Label Distribution:")
    counts = df.groupby(["rainfall_level", "risk_label"]).size().reset_index(name="count")
    print(counts.to_string(index=False))
    return df


def add_future_api_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds placeholder columns for temperature, humidity, and wind
    for future live API merging without altering training schemas.
    """
    print("\n--- Adding Future-Ready Placeholders ---")
    df["temperature"] = 0.0
    df["humidity"] = 0.0
    df["wind"] = 0.0
    print("Added placeholders: 'temperature', 'humidity', 'wind' (initialized to 0.0)")
    return df


def save_processed_data(df: pd.DataFrame, output_path: str) -> None:
    """Saves processed dataframe to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nSaved processed dataset to: {output_path} ({file_size_mb:.2f} MB)")


def validate_dataset(df: pd.DataFrame) -> None:
    """Prints mandatory validation metrics and sample rows."""
    print("\n" + "=" * 60)
    print("MANDATORY VALIDATION METRICS")
    print("=" * 60)
    print(f"Total Rows:       {len(df):,}")
    print(f"Unique Districts: {df['District'].nunique():,}")
    print(f"Unique States:    {df['State'].nunique():,}")
    print(f"Date Range:       {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    print("\nSample 5 Rows:")
    sample_df = df.head(5)
    # Configure pandas display for full column printing
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(sample_df)
    print("=" * 60)


def main():
    try:
        # 1. Load Data
        df = load_raw_data(RAW_DATA_PATH)

        # 2. Clean Data
        df_cleaned = clean_imd_data(df)

        # 3. Feature Engineering
        df_featured = engineer_temporal_features(df_cleaned)

        # 4. Create Target Labels
        df_labeled = create_target_labels(df_featured)

        # 5. Add Placeholders
        df_final = add_future_api_placeholders(df_labeled)

        # 6. Save Processed Data
        save_processed_data(df_final, OUTPUT_DATA_PATH)

        # 7. Validation
        validate_dataset(df_final)
        print("\nPipeline completed successfully! Dataset is ready for ML training.")

    except Exception as e:
        print(f"\nError during IMD data preparation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
