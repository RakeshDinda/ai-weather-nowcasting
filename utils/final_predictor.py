"""
Inference module for final_model.pkl.

Features: temperature, humidity, wind_speed, month, state_enc
Bundle:   model + scaler + le_state (all in one .pkl)
"""
import os, joblib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, List

_BUNDLE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "models", "final_model.pkl")
_bundle = None

LABEL_MAP = {0: "LOW", 1: "MODERATE", 2: "HIGH"}
ALERT_MAP = {
    0: {"severity":"LOW",      "status":"SAFE",    "color":"#22cc44", "icon":"safe",
        "message":"Low rainfall risk. Conditions appear stable."},
    1: {"severity":"MODERATE", "status":"CAUTION", "color":"#ffaa00", "icon":"caution",
        "message":"Moderate rainfall expected. Stay alert for changing conditions."},
    2: {"severity":"HIGH",     "status":"WARNING", "color":"#ff4444", "icon":"warning",
        "message":"High rainfall risk. Potential flooding or waterlogging likely."},
}


def _load():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(_BUNDLE_PATH)
    return _bundle


def _encode_state(le, state: Optional[str]) -> int:
    if not state:
        return len(le.classes_) // 2          # median fallback
    s = str(state).upper().strip()
    if s in le.classes_:
        return int(le.transform([s])[0])
    # Partial match
    for cls in le.classes_:
        if s in cls or cls in s:
            return int(le.transform([cls])[0])
    return len(le.classes_) // 2


def predict_final(
    temperature: float,
    humidity:    float,
    wind_speed:  float,
    state:       Optional[str] = None,
    month:       Optional[int] = None,
) -> Dict[str, Any]:
    """Single-location prediction using live weather features."""
    b = _load()
    m = month if month is not None else datetime.now().month
    s_enc = _encode_state(b["le_state"], state)

    X = np.array([[temperature, humidity, wind_speed, float(m), float(s_enc)]],
                 dtype="float32")
    X_sc = b["scaler"].transform(X)
    proba = b["model"].predict_proba(X_sc)[0]
    lbl   = int(np.argmax(proba))

    return {
        "risk_label":    lbl,
        "risk_level":    LABEL_MAP[lbl],
        "confidence":    round(float(np.max(proba)), 3),
        "probabilities": {
            "LOW":      round(float(proba[0]), 3),
            "MODERATE": round(float(proba[1]), 3),
            "HIGH":     round(float(proba[2]), 3),
        },
    }


def batch_predict_final(
    weather_records: List[Dict[str, Any]],
    states:          List[Optional[str]],
    month:           Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Vectorized batch prediction for /predict-all."""
    b = _load()
    n = len(weather_records)
    if n == 0:
        return []

    m = float(month if month is not None else datetime.now().month)

    temps  = np.array([float(r.get("temperature", 30.0)) for r in weather_records], dtype="float32")
    hums   = np.array([float(r.get("humidity",    65.0)) for r in weather_records], dtype="float32")
    winds  = np.array([float(r.get("wind_speed",   3.0)) for r in weather_records], dtype="float32")
    months = np.full(n, m, dtype="float32")
    s_encs = np.array([float(_encode_state(b["le_state"], s)) for s in states], dtype="float32")

    X    = np.column_stack([temps, hums, winds, months, s_encs])
    X_sc = b["scaler"].transform(X)
    proba_matrix = b["model"].predict_proba(X_sc)
    labels       = np.argmax(proba_matrix, axis=1)

    return [{
        "risk_label":    int(labels[i]),
        "risk_level":    LABEL_MAP[int(labels[i])],
        "confidence":    round(float(np.max(proba_matrix[i])), 3),
        "probabilities": {
            "LOW":      round(float(proba_matrix[i][0]), 3),
            "MODERATE": round(float(proba_matrix[i][1]), 3),
            "HIGH":     round(float(proba_matrix[i][2]), 3),
        },
    } for i in range(n)]


def get_alert(pred: Dict[str, Any]) -> Dict[str, Any]:
    """Structured alert dict from prediction output."""
    lbl   = int(pred.get("risk_label", 0))
    alert = dict(ALERT_MAP.get(lbl, ALERT_MAP[0]))
    alert["risk_level"]    = LABEL_MAP.get(lbl, "LOW")
    alert["confidence"]    = pred.get("confidence", 0.0)
    alert["probabilities"] = pred.get("probabilities", {})
    # Legacy-compatible keys for existing frontend
    p = pred.get("probabilities", {})
    alert["flood"]        = _rstr(p.get("HIGH",     0.0))
    alert["thunderstorm"] = _rstr(p.get("MODERATE", 0.0))
    alert["cloudburst"]   = _rstr(p.get("HIGH",     0.0))
    return alert


def _rstr(p: float) -> str:
    if p >= 0.6: return "HIGH RISK"
    if p >= 0.35: return "MODERATE RISK"
    return "LOW RISK"
