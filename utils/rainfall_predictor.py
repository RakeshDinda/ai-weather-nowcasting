"""
Rainfall risk inference module using final_rainfall_model.pkl.

The model was trained on temporal lag features derived from IMD daily rainfall:
  - rainfall_lag1        (previous day rainfall — same district)
  - rainfall_lag2        (2 days before — same district)
  - rainfall_rolling_avg (3-day trailing average — same district)
  - month                (calendar month)

At inference time we have no district history, so we approximate lags using
the current rainfall estimate (from OpenWeather API). This is the best
available signal and is consistent with how the training features behave
in steady-state monsoon conditions.

Output:
  risk_label     : int   (0=LOW, 1=MODERATE, 2=HIGH)
  rainfall_level : str   ("LOW" / "MODERATE" / "HIGH")
  confidence     : float (max class probability, 0.0–1.0)
"""

import os
import joblib
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "final_rainfall_model.pkl")

_clf = None   # Lazy-loaded once

LABEL_MAP = {0: "LOW", 1: "MODERATE", 2: "HIGH"}


def _load_model():
    global _clf
    if _clf is None:
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(f"Model not found: {_MODEL_PATH}")
        _clf = joblib.load(_MODEL_PATH)
    return _clf


def predict_rainfall_risk(
    rainfall: float,
    temperature: float,
    humidity: float,
    wind_speed: float,
    pressure: float,
    month: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run rainfall risk prediction for a single location.

    Args:
        rainfall   : Estimated/observed rainfall in mm (from API or generator)
        temperature: Air temperature in Celsius
        humidity   : Relative humidity %
        wind_speed : Wind speed in m/s
        pressure   : Atmospheric pressure in hPa
        month      : Calendar month (1-12). Defaults to current month.

    Returns:
        {
          "risk_label"     : 0 | 1 | 2,
          "rainfall_level" : "LOW" | "MODERATE" | "HIGH",
          "confidence"     : float,
          "probabilities"  : {"LOW": f, "MODERATE": f, "HIGH": f}
        }
    """
    clf = _load_model()

    if month is None:
        month = datetime.now().month

    # Approximate lag features using current rainfall
    # Rationale: in steady-state conditions, yesterday ≈ today.
    # This is conservative and avoids hallucinating values we don't have.
    lag1    = float(rainfall)
    lag2    = float(rainfall)
    rolling = float(rainfall)

    # Features must match training order exactly:
    # ["rainfall_lag1", "rainfall_lag2", "rainfall_rolling_avg", "month"]
    X = np.array([[lag1, lag2, rolling, float(month)]], dtype="float32")

    proba = clf.predict_proba(X)[0]          # shape: (3,)
    risk_label = int(np.argmax(proba))
    confidence = float(np.max(proba))

    return {
        "risk_label": risk_label,
        "rainfall_level": LABEL_MAP[risk_label],
        "confidence": round(confidence, 3),
        "probabilities": {
            "LOW":      round(float(proba[0]), 3),
            "MODERATE": round(float(proba[1]), 3),
            "HIGH":     round(float(proba[2]), 3),
        },
    }


def batch_predict_rainfall_risk(
    weather_records: list,
    month: Optional[int] = None,
) -> list:
    """
    Vectorized batch prediction for all locations in /predict-all.

    Args:
        weather_records: list of dicts, each with keys:
            rainfall, temperature, humidity, wind_speed, pressure
        month: calendar month (defaults to current)

    Returns:
        List of prediction dicts (same order as input).
    """
    clf = _load_model()

    if month is None:
        month = datetime.now().month

    n = len(weather_records)
    if n == 0:
        return []

    lags  = np.array([float(r.get("rainfall", 0.0)) for r in weather_records], dtype="float32")
    months = np.full(n, float(month), dtype="float32")

    # Feature matrix: [lag1, lag2, rolling_avg, month]
    X = np.column_stack([lags, lags, lags, months])   # shape: (n, 4)

    proba_matrix = clf.predict_proba(X)               # shape: (n, 3)
    labels       = np.argmax(proba_matrix, axis=1)

    results = []
    for i in range(n):
        p   = proba_matrix[i]
        lbl = int(labels[i])
        results.append({
            "risk_label":     lbl,
            "rainfall_level": LABEL_MAP[lbl],
            "confidence":     round(float(np.max(p)), 3),
            "probabilities": {
                "LOW":      round(float(p[0]), 3),
                "MODERATE": round(float(p[1]), 3),
                "HIGH":     round(float(p[2]), 3),
            },
        })
    return results
