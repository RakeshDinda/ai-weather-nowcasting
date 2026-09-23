"""
Build FINAL TRAINING DATASET with real weather features.

Strategy:
  - IMD dataset has 728 unique districts
  - Call OpenWeather Geo API once per district (deduped) to get coordinates
  - Call OpenWeather Weather API once per unique (lat,lon) pair
  - Broadcast weather features back to all 24,005 rows
  - Compute derived features, save final_training_data.csv

This respects the 60 req/min free tier by:
  - Using in-memory deduplication (one API call per distinct location)
  - Throttling at 45 calls/min (1.33s sleep between calls)
  - Batching in chunks with progress reporting
"""

import os, sys, time, json
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, "backend", ".env"))
load_dotenv()

DATA_PATH    = os.path.join(PROJECT_ROOT, "data", "processed", "imd_cleaned.csv")
OUT_PATH     = os.path.join(PROJECT_ROOT, "data", "processed", "final_training_data.csv")
CACHE_PATH   = os.path.join(PROJECT_ROOT, "data", "processed", "weather_cache.json")

API_KEY      = os.getenv("OPENWEATHER_API_KEY")
SLEEP_SECS   = 1.4   # ~43 req/min — safely under 60/min limit

# ── Load existing weather cache (so re-runs skip already-fetched locations) ──
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        weather_cache = json.load(f)
    print(f"[Cache] Loaded {len(weather_cache)} cached locations")
else:
    weather_cache = {}

def save_cache():
    with open(CACHE_PATH, "w") as f:
        json.dump(weather_cache, f, indent=2)

# ── Geo API: get (lat,lon) for a district ─────────────────────────────────────
def get_coords(district, state):
    key = f"{district}|{state}".lower()
    if key in weather_cache and "lat" in weather_cache[key]:
        return weather_cache[key]["lat"], weather_cache[key]["lon"]

    queries = [
        f"{district},{state},IN",
        f"{district},IN",
        f"{district}",
    ]
    for q in queries:
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={q}&limit=1&appid={API_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data:
                    lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
                    if key not in weather_cache:
                        weather_cache[key] = {}
                    weather_cache[key]["lat"] = lat
                    weather_cache[key]["lon"] = lon
                    return lat, lon
        except Exception as e:
            pass
        time.sleep(SLEEP_SECS)

    if key not in weather_cache:
        weather_cache[key] = {}
    weather_cache[key]["lat"] = None
    weather_cache[key]["lon"] = None
    return None, None

# ── Weather API: get weather for (lat,lon) ───────────────────────────────────
def get_weather(lat, lon, district, state):
    key = f"{district}|{state}".lower()
    if key in weather_cache and "temperature" in weather_cache[key]:
        c = weather_cache[key]
        return c["temperature"], c["humidity"], c["wind_speed"], c["pressure"]

    if lat is None or lon is None:
        return None, None, None, None

    try:
        url = (f"http://api.openweathermap.org/data/2.5/weather"
               f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            temp     = float(d["main"]["temp"])
            humidity = float(d["main"]["humidity"])
            wind     = float(d["wind"]["speed"])
            pressure = float(d["main"].get("pressure", 1013.0))

            weather_cache[key].update({
                "temperature": temp,
                "humidity": humidity,
                "wind_speed": wind,
                "pressure": pressure
            })
            time.sleep(SLEEP_SECS)
            return temp, humidity, wind, pressure
    except Exception as e:
        pass

    return None, None, None, None

# ── 1. Load IMD data ──────────────────────────────────────────────────────────
print("=" * 62)
print("STEP 1 - Loading IMD dataset")
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["rainfall","month","risk_label"])
print(f"  Rows: {len(df):,}  |  States: {df['State'].nunique()}  |  Districts: {df['District'].nunique()}")

# Unique locations to query
unique_locs = df[["District","State"]].drop_duplicates().reset_index(drop=True)
total       = len(unique_locs)
print(f"  Unique locations to query: {total}")

# ── 2. Fetch coords + weather for each unique district ────────────────────────
print(f"\nSTEP 2 - Fetching coordinates + weather for {total} districts")
print(f"  Rate limit: ~{int(60/SLEEP_SECS)} calls/min (safe under 60/min)")
print()

loc_results = {}   # key: "District|State" -> dict of weather values
fetched, cached_hits, failed = 0, 0, 0

for i, row in unique_locs.iterrows():
    dist  = row["District"]
    state = row["State"]
    key   = f"{dist}|{state}".lower()

    # Check if fully cached already
    wc = weather_cache.get(key, {})
    if "temperature" in wc:
        loc_results[key] = {
            "temperature": wc["temperature"],
            "humidity":    wc["humidity"],
            "wind_speed":  wc["wind_speed"],
            "pressure":    wc["pressure"],
        }
        cached_hits += 1
        if (i+1) % 50 == 0:
            print(f"  [{i+1}/{total}] Cache hits so far: {cached_hits}")
        continue

    # Geo lookup
    lat, lon = get_coords(dist, state)
    time.sleep(SLEEP_SECS)

    # Weather lookup
    temp, hum, wind, pres = get_weather(lat, lon, dist, state)

    if temp is not None:
        loc_results[key] = {
            "temperature": temp,
            "humidity":    hum,
            "wind_speed":  wind,
            "pressure":    pres,
        }
        fetched += 1
    else:
        loc_results[key] = None
        failed += 1

    if (i+1) % 20 == 0 or (i+1) == total:
        print(f"  [{i+1}/{total}] fetched={fetched} cached={cached_hits} failed={failed}")
        save_cache()

save_cache()
print(f"\n  Done. fetched={fetched}, cached={cached_hits}, failed={failed}")

# ── 3. Merge weather features into main dataframe ────────────────────────────
print("\nSTEP 3 - Merging weather features into IMD dataset")
temps, hums, winds, presses = [], [], [], []

for _, row in df.iterrows():
    key = f"{row['District']}|{row['State']}".lower()
    w   = loc_results.get(key)
    if w:
        temps.append(w["temperature"])
        hums.append(w["humidity"])
        winds.append(w["wind_speed"])
        presses.append(w["pressure"])
    else:
        temps.append(None)
        hums.append(None)
        winds.append(None)
        presses.append(None)

df["temperature"] = temps
df["humidity"]    = hums
df["wind_speed"]  = winds
df["pressure"]    = presses

# ── 4. Fill any remaining nulls with state-level medians, then global median ──
print("STEP 4 - Filling any remaining nulls with state-level medians")
for col in ["temperature","humidity","wind_speed","pressure"]:
    state_med = df.groupby("State")[col].transform("median")
    df[col] = df[col].fillna(state_med)
    global_med = df[col].median()
    df[col] = df[col].fillna(global_med)

# ── 5. Derived features ───────────────────────────────────────────────────────
print("STEP 5 - Computing derived features")
df["moisture_index"]    = df["humidity"]    * df["rainfall"]
df["instability_index"] = df["temperature"] * df["humidity"]
df["pressure_drop"]     = 1013.0            - df["pressure"]
df["rain_intensity"]    = df["rainfall"]    * df["wind_speed"]

# ── 6. Build final dataset ────────────────────────────────────────────────────
print("STEP 6 - Building final training dataset")
FINAL_COLS = [
    "rainfall", "temperature", "humidity", "wind_speed", "pressure",
    "moisture_index", "instability_index", "pressure_drop", "rain_intensity",
    "risk_label"
]
final_df = df[FINAL_COLS].copy()
final_df = final_df.dropna()

# ── 7. Save ───────────────────────────────────────────────────────────────────
print(f"STEP 7 - Saving to {OUT_PATH}")
final_df.to_csv(OUT_PATH, index=False)
print(f"  Saved: {len(final_df):,} rows")

# ── 8. Validation ─────────────────────────────────────────────────────────────
print("\nSTEP 8 - Validation")
print(f"  Shape: {final_df.shape}")
print(f"\n  Null values per column:")
nulls = final_df.isnull().sum()
for col, n in nulls.items():
    print(f"    {col:20s}: {n}")

print(f"\n  Sample rows:")
print(final_df.head(5).to_string(index=False))

print(f"\n  Descriptive statistics:")
print(final_df.describe().round(2).to_string())

print(f"\n  Risk label distribution:")
vc = final_df["risk_label"].value_counts().sort_index()
for lbl, cnt in vc.items():
    name = {0:"LOW",1:"MODERATE",2:"HIGH"}.get(int(lbl), str(lbl))
    print(f"    Class {int(lbl)} ({name:8s}): {cnt:,}  ({cnt/len(final_df)*100:.1f}%)")

print("\n" + "=" * 62)
print("  FINAL TRAINING DATASET READY")
print("=" * 62)
