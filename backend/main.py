"""
Real-Time Weather AI System — FastAPI Backend v7.0
============================================================
Pipeline:
  1. Live Weather API: OpenWeatherMap (temperature, humidity, rainfall, wind_speed)
  2. Leak-Free ML Model: rainfall_model_v2.pkl (month, day, state_enc, district_enc)
  3. Hybrid Risk Logic:
       IF rainfall >= 20 mm  -> HIGH (2)
       ELIF rainfall >= 5 mm -> MODERATE (1)
       ELSE                  -> ML prediction
  4. Response: structured weather metrics + hybrid risk prediction
============================================================
"""
from dotenv import load_dotenv
import os
import sys

load_dotenv()

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio, time, hashlib
from typing import Optional, List, Dict, Any, Tuple
import httpx
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Ensure project root .env and backend/.env are loaded regardless of execution CWD
load_dotenv(os.path.join(project_root, "backend", ".env"))
load_dotenv(os.path.join(project_root, ".env"))
load_dotenv()

from utils.api_fetcher import (
    get_coordinates, get_weather_by_coords, get_fallback_mock,
    fetch_weather, async_fetch_weather, _GEO_CACHE,
)
from utils.locations_manager import (
    get_india_locations, get_sampled_locations, find_location_by_name,
)
from utils.v2_predictor import (
    predict_v2, batch_predict_v2, compute_hybrid_risk, get_alert,
)

app = FastAPI(title="Real-Time Weather AI System API", version="7.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup warm-up
print("Loading rainfall_model_v2.pkl & LabelEncoders...")
try:
    _test = predict_v2(state="MAHARASHTRA", district="MUMBAI")
    print(f"  ML Ready: {_test['risk_level']} (conf={_test['confidence']})")
except Exception as e:
    print(f"  WARNING during model warm-up: {e}")

_CACHE: Dict[str, Tuple[Any, float]] = {}
CACHE_TTL = 300.0  # 300 seconds cache for sub-50ms repeat responses


class PredictionRequest(BaseModel):
    city: Optional[str] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "7.0.0",
        "system": "Real-Time Weather AI System",
        "model": "rainfall_model_v2.pkl",
        "logic": "Hybrid (Live Weather Rule Override + ML Inference)",
        "features": ["month", "day", "state_enc", "district_enc"],
        "total_india_locations": len(get_india_locations()),
        "cached_geo_points": len(_GEO_CACHE),
    }


@app.get("/locations")
def get_locations():
    return get_india_locations()


def calculate_rule_risk(rainfall: float, humidity: float, wind_speed: float) -> Tuple[str, int]:
    """
    Core Intelligence Risk Evaluation:
    HIGH if: rainfall > 20 OR humidity > 90 OR wind_speed > 10
    MODERATE if: rainfall > 5 OR humidity > 70
    LOW otherwise
    """
    rain = float(rainfall if rainfall is not None else 0.0)
    hum = float(humidity if humidity is not None else 0.0)
    wind = float(wind_speed if wind_speed is not None else 0.0)

    if rain > 20.0 or hum > 90.0 or wind > 10.0:
        return "HIGH", 2
    elif rain > 5.0 or hum > 70.0:
        return "MODERATE", 1
    else:
        return "LOW", 0


def generate_explainable_reason(rainfall: float, humidity: float, wind_speed: float, risk_level: str = "LOW") -> str:
    """
    Explainable AI (XAI) Rule Engine:
    - rainfall > 20 -> "Heavy rainfall indicates flood risk"
    - humidity > 90 -> "High humidity supports storm formation"
    - wind_speed > 10 -> "Strong wind indicates thunderstorm"
    - Combine reasons if multiple
    """
    reasons = []
    rain = float(rainfall if rainfall is not None else 0.0)
    hum = float(humidity if humidity is not None else 0.0)
    wind = float(wind_speed if wind_speed is not None else 0.0)

    if rain > 20.0:
        reasons.append("Heavy rainfall indicates flood risk")
    if hum > 90.0:
        reasons.append("High humidity supports storm formation")
    if wind > 10.0:
        reasons.append("Strong wind indicates thunderstorm")

    if reasons:
        return " | ".join(reasons)

    if str(risk_level).upper() == "HIGH":
        return "Severe atmospheric instability detected"
    elif str(risk_level).upper() == "MODERATE":
        return "Moderate convective indicators observed"
    else:
        return "Normal atmospheric conditions"


def generate_actionable_alert(risk_level, rainfall, humidity, wind_speed):
    alert = {
        "type": "NORMAL",
        "severity": "LOW",
        "action": "No immediate action required"
    }

    rain = float(rainfall if rainfall is not None else 0.0)
    hum = float(humidity if humidity is not None else 0.0)
    wind = float(wind_speed if wind_speed is not None else 0.0)

    if rain > 25:
        alert = {
            "type": "FLASH_FLOOD",
            "severity": "HIGH",
            "action": "Move people from low-lying areas. Activate drainage systems."
        }

    elif hum > 90 and wind > 10:
        alert = {
            "type": "THUNDERSTORM",
            "severity": "HIGH",
            "action": "Avoid outdoor activities. Secure loose structures."
        }

    elif rain > 10:
        alert = {
            "type": "MODERATE_RAIN",
            "severity": "MEDIUM",
            "action": "Monitor water levels and drainage systems."
        }

    return alert


def generate_alerts(cities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate alerts based on live weather data:
    - HIGH -> "High Risk Alert in {city}"
    - rainfall > 15 -> "Flash Flood Risk"
    - wind_speed > 8 -> "Thunderstorm Alert"
    """
    alerts = []
    for item in cities_data:
        city = item.get("city", "Unknown")
        risk_level = str(item.get("risk_level") or item.get("risk") or "LOW").upper()
        
        # Weather can be top-level or nested in weather dict
        weather = item.get("weather") or {}
        rain = float(item.get("rainfall") if item.get("rainfall") is not None else weather.get("rainfall", 0.0))
        wind = float(item.get("wind_speed") if item.get("wind_speed") is not None else weather.get("wind_speed", 0.0))

        now_iso = datetime.now().isoformat()
        if risk_level == "HIGH":
            alerts.append({
                "city": city,
                "type": "High Risk",
                "severity": "HIGH",
                "risk_level": "HIGH RISK",
                "action": "Immediate evacuation of vulnerable lowlands, activate civil defense response teams, and suspend non-essential travel.",
                "timestamp": now_iso,
                "message": f"High Risk Alert in {city}"
            })
        if rain > 15.0:
            sev = "HIGH" if rain > 25.0 else "MODERATE"
            alerts.append({
                "city": city,
                "type": "Flash Flood",
                "severity": sev,
                "risk_level": "HIGH RISK" if sev == "HIGH" else "MODERATE RISK",
                "action": "Move to higher ground immediately. Secure flood defenses and strictly avoid inundated roads and riverbanks.",
                "timestamp": now_iso,
                "message": f"Flash Flood Risk in {city} (Rainfall: {rain:.1f} mm)"
            })
        if wind > 8.0:
            sev = "HIGH" if wind > 12.0 else "MODERATE"
            alerts.append({
                "city": city,
                "type": "Thunderstorm",
                "severity": sev,
                "risk_level": "HIGH RISK" if sev == "HIGH" else "MODERATE RISK",
                "action": "Seek structural indoor shelter immediately. Keep clear of tall trees, power lines, and unplug high-draw appliances.",
                "timestamp": now_iso,
                "message": f"Thunderstorm Alert in {city} (Wind Speed: {wind:.1f} m/s)"
            })
            
    return alerts


@app.post("/predict")
def predict_risk(request: PredictionRequest):
    """
    Real-Time Prediction Pipeline with dynamic rule fallback and hybrid ML logic.
    """
    raw_city = request.location or request.city
    if not raw_city or not raw_city.strip():
        raise HTTPException(status_code=400, detail="Location name cannot be empty.")
    city = raw_city.strip()

    # 1. Location metadata lookup
    matched = find_location_by_name(city)
    state = matched.get("state") if matched else "Unknown"

    # Resolve coordinates
    lat = request.lat
    lon = request.lon
    if lat is None or lon is None:
        if matched:
            lat, lon = matched.get("lat"), matched.get("lon")
        if lat is None or lon is None:
            lat, lon = get_coordinates(city)

    if lat is None or lon is None:
        lat, lon = 22.0, 79.0

    # 2. Live Weather API call
    weather_data = fetch_weather(lat, lon)
    temp = float(weather_data.get("temperature", 30.0))
    hum = float(weather_data.get("humidity", 70.0))
    rainfall = float(weather_data.get("rainfall", 0.0))
    wind = float(weather_data.get("wind_speed", 2.0))
    pressure = float(weather_data.get("pressure", 1010.0))

    # 3. ML Inference with Rule-Based Fallback (No hardcoded fake LOW)
    now = datetime.now()
    try:
        ml_pred = predict_v2(
            state=state,
            district=city,
            month=now.month,
            day=now.day,
        )
    except Exception as e:
        rule_risk, rule_lbl = calculate_rule_risk(rainfall, hum, wind)
        ml_pred = {
            "risk_label": rule_lbl,
            "risk_level": rule_risk,
            "confidence": 0.85 if rule_risk == "HIGH" else (0.75 if rule_risk == "MODERATE" else 0.65),
            "probabilities": {
                "LOW": 0.15 if rule_risk == "HIGH" else (0.25 if rule_risk == "MODERATE" else 0.70),
                "MODERATE": 0.25 if rule_risk == "HIGH" else (0.55 if rule_risk == "MODERATE" else 0.20),
                "HIGH": 0.60 if rule_risk == "HIGH" else (0.20 if rule_risk == "MODERATE" else 0.10)
            },
        }

    city_label = matched["city"] if matched else city

    # 4. Hybrid Risk Logic
    hybrid_pred = compute_hybrid_risk(
        rainfall=rainfall,
        ml_prediction=ml_pred,
        wind_speed=wind,
        temperature=temp,
        humidity=hum,
        state=state,
        city=city_label,
    )

    # Re-evaluate with explicit rules
    rule_level, rule_label = calculate_rule_risk(rainfall, hum, wind)
    final_risk = hybrid_pred.get("risk_level", "LOW")
    final_label = hybrid_pred.get("risk_label", 0)
    if rule_label > final_label:
        final_risk = rule_level
        final_label = rule_label
        hybrid_pred["risk_level"] = final_risk
        hybrid_pred["risk_label"] = final_label
        hybrid_pred["risk_text"] = final_risk

    p_thunder = float(hybrid_pred.get("thunderstorm", hybrid_pred.get("probabilities", {}).get("MODERATE", 0.1)))
    p_cloud = float(hybrid_pred.get("cloudburst", hybrid_pred.get("probabilities", {}).get("HIGH", 0.05)))
    p_flood = float(hybrid_pred.get("flood", hybrid_pred.get("probabilities", {}).get("HIGH", 0.05)))

    alerts = get_alert(hybrid_pred)
    reason = generate_explainable_reason(rainfall, hum, wind, final_risk)
    actionable_alert = generate_actionable_alert(
        final_risk,
        rainfall,
        hum,
        wind
    )

    return {
        "city": city_label,
        "state": state,
        "lat": lat,
        "lon": lon,
        "risk_level": final_risk,
        "risk": final_risk,
        "temperature": temp,
        "humidity": hum,
        "rainfall": rainfall,
        "wind_speed": wind,
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "alert": actionable_alert,
        "explanation": hybrid_pred.get("explanation"),
        "weather": {
            "temperature": temp,
            "humidity": hum,
            "rainfall": rainfall,
            "wind_speed": wind,
            "wind": wind,
            "pressure": pressure,
        },
        "probabilities": {
            "thunderstorm": round(p_thunder, 2),
            "cloudburst": round(p_cloud, 2),
            "flash_flood": round(p_flood, 2),
        },
        "prediction": {
            "prob_thunderstorm": round(p_thunder, 2),
            "prob_cloudburst": round(p_cloud, 2),
            "prob_flood": round(p_flood, 2),
            "thunderstorm": round(p_thunder, 2),
            "cloudburst": round(p_cloud, 2),
            "flood": round(p_flood, 2),
            **hybrid_pred,
            "risk_level": final_risk,
            "risk_label": final_label,
            "reason": reason,
        },
        "alerts": alerts,
    }


@app.get("/batch_predict")
async def batch_predict(limit: int = 100, state: Optional[str] = None):
    """
    Real-Time Batch Monitoring Pipeline with Realistic Weather & Smart In-Memory Caching:
    - Expiry: 300 seconds (5 minutes)
    - Consistency across all requests (no random.uniform)
    - Real-time weather with safe fallback mock
    """
    safe_limit = min(max(1, limit), 2000)
    cache_key = f"{safe_limit}_{state or 'all'}"
    now_ts = time.time()

    if cache_key in _CACHE:
        cached, ts = _CACHE[cache_key]
        if now_ts - ts < CACHE_TTL:
            return cached

    locations = get_sampled_locations(limit=safe_limit, state=state)
    semaphore = asyncio.Semaphore(15)

    async def fetch_one(client: httpx.AsyncClient, loc: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            return await async_fetch_weather(city=loc["city"], lat=loc["lat"], lon=loc["lon"], client=client)

    async with httpx.AsyncClient(timeout=3.5) as client:
        weather_list = await asyncio.gather(*[fetch_one(client, loc) for loc in locations])

    now = datetime.now()
    current_time_iso = now.isoformat()
    try:
        ml_predictions = batch_predict_v2(locations, month=now.month, day=now.day)
    except Exception:
        ml_predictions = []

    results = []

    for i, loc in enumerate(locations):
        w = weather_list[i] if i < len(weather_list) else {}
        city_name = loc["city"]
        state_name = loc.get("state", "India")

        # Use ONLY cached or fetched data from async_fetch_weather (no random.uniform)
        rainfall = float(w.get("rainfall", 0.0))
        wind = float(w.get("wind_speed", w.get("wind", 2.0)))
        temp = float(w.get("temperature", 30.0))
        hum = float(w.get("humidity", 70.0))
        pressure = float(w.get("pressure", 1010.0))

        # Strict Rule Calculation directly on fetched/cached weather
        risk_level, risk_label = calculate_rule_risk(rainfall, hum, wind)

        # ML Prediction with rule-based fallback
        if i < len(ml_predictions):
            ml_pred = ml_predictions[i]
        else:
            ml_pred = {
                "risk_label": risk_label,
                "risk_level": risk_level,
                "confidence": 0.85 if risk_level == "HIGH" else (0.75 if risk_level == "MODERATE" else 0.65),
                "probabilities": {
                    "LOW": 0.15 if risk_level == "HIGH" else (0.25 if risk_level == "MODERATE" else 0.70),
                    "MODERATE": 0.25 if risk_level == "HIGH" else (0.55 if risk_level == "MODERATE" else 0.20),
                    "HIGH": 0.60 if risk_level == "HIGH" else (0.20 if risk_level == "MODERATE" else 0.10)
                }
            }

        hybrid_pred = compute_hybrid_risk(
            rainfall=rainfall,
            ml_prediction=ml_pred,
            wind_speed=wind,
            temperature=temp,
            humidity=hum,
            state=state_name,
            city=city_name,
        )

        # Ensure rule priority consistency
        if risk_label > hybrid_pred.get("risk_label", 0):
            hybrid_pred["risk_level"] = risk_level
            hybrid_pred["risk_label"] = risk_label
            hybrid_pred["risk_text"] = risk_level

        final_risk = hybrid_pred.get("risk_level", risk_level)
        final_label = hybrid_pred.get("risk_label", risk_label)

        p_thunder = float(hybrid_pred.get("thunderstorm", 0.75 if final_risk == "HIGH" else (0.45 if final_risk == "MODERATE" else 0.12)))
        p_cloud = float(hybrid_pred.get("cloudburst", 0.70 if final_risk == "HIGH" else (0.35 if final_risk == "MODERATE" else 0.08)))
        p_flood = float(hybrid_pred.get("flood", 0.80 if final_risk == "HIGH" else (0.40 if final_risk == "MODERATE" else 0.05)))

        if final_risk == "HIGH":
            p_thunder = max(p_thunder, 0.72)
            p_cloud = max(p_cloud, 0.68)
            p_flood = max(p_flood, 0.75)
        elif final_risk == "MODERATE":
            p_thunder = max(p_thunder, 0.42)
            p_cloud = max(p_cloud, 0.38)
            p_flood = max(p_flood, 0.35)

        alert = get_alert(hybrid_pred)
        reason = generate_explainable_reason(rainfall, hum, wind, final_risk)
        actionable_alert = generate_actionable_alert(
            final_risk,
            rainfall,
            hum,
            wind
        )

        results.append({
            "city": loc["city"],
            "state": state_name,
            "lat": loc["lat"],
            "lon": loc["lon"],
            "risk_level": final_risk,
            "risk": final_risk,
            "temperature": round(temp, 1),
            "humidity": round(hum, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind, 1),
            "timestamp": current_time_iso,
            "reason": reason,
            "alert": actionable_alert,
            "probabilities": {
                "thunderstorm": round(p_thunder, 2),
                "cloudburst": round(p_cloud, 2),
                "flash_flood": round(p_flood, 2),
            },
            "explanation": hybrid_pred.get("explanation"),
            "weather": {
                "temperature": round(temp, 1),
                "humidity": round(hum, 1),
                "rainfall": round(rainfall, 1),
                "wind_speed": round(wind, 1),
                "wind": round(wind, 1),
                "pressure": round(pressure, 1),
            },
            "prediction": {
                "prob_thunderstorm": round(p_thunder, 2),
                "prob_cloudburst": round(p_cloud, 2),
                "prob_flood": round(p_flood, 2),
                "thunderstorm": round(p_thunder, 2),
                "cloudburst": round(p_cloud, 2),
                "flood": round(p_flood, 2),
                **hybrid_pred,
                "risk_level": final_risk,
                "risk_label": final_label,
                "reason": reason,
            },
            "alerts": alert,
        })

    # Sort results with HIGH risk first
    results.sort(
        key=lambda x: (x["prediction"]["risk_label"], x["probabilities"]["flash_flood"]),
        reverse=True,
    )

    _CACHE[cache_key] = (results, now_ts)
    return results


@app.get("/alerts")
async def get_alerts():
    """
    Dynamic Alerts Feed API:
    Generates real-time national warnings compiled from current batch telemetry.
    """
    # Use cached or fresh batch prediction data for India
    batch_data = await batch_predict(limit=100)
    alerts = generate_alerts(batch_data)
    return {
        "alerts": alerts,
        "total": len(alerts),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# REAL-TIME NOWCASTING PIPELINE (ANY CITY)
# ============================================================

def engineer_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Feature Engineering for Real-Time Nowcasting:
    - moisture_index = humidity * rainfall
    - instability_index = temperature * humidity
    - rain_intensity = rainfall * wind_speed
    """
    humidity = float(data.get("humidity", 0.0) or 0.0)
    rainfall = float(data.get("rainfall", 0.0) or 0.0)
    temperature = float(data.get("temperature", 0.0) or 0.0)
    wind_speed = float(data.get("wind_speed", 0.0) or 0.0)

    moisture_index = round(humidity * rainfall, 2)
    instability_index = round(temperature * humidity, 2)
    rain_intensity = round(rainfall * wind_speed, 2)

    features = dict(data)
    features.update({
        "moisture_index": moisture_index,
        "instability_index": instability_index,
        "rain_intensity": rain_intensity,
    })
    return features


def predict_nowcast(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pluggable Nowcast Prediction Pipeline:
    - rainfall > 25 -> HIGH
    - rainfall > 10 -> MODERATE
    - else          -> LOW
    """
    rainfall = float(features.get("rainfall", 0.0) or 0.0)

    if rainfall > 25:
        risk = "HIGH"
    elif rainfall > 10:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return {
        "risk_level": risk,
        "probability": 0.85,
    }


@app.get("/nowcast")
def get_nowcast(city: str):
    """
    Real-Time Nowcasting API for ANY city.
    Pipeline:
      1. Geocode city via OpenWeather Geo API (with locations registry backup)
      2. Fetch live atmospheric observations
      3. Standardize weather object
      4. Compute engineered features
      5. Generate nowcast risk prediction
      6. Produce actionable alerts
      7. Return unified response
    """
    if not city or not city.strip():
        return {"error": "Location not found"}

    cleaned_city = city.strip()

    try:
        # STEP 2: Fetch coordinates
        lat, lon = get_coordinates(cleaned_city)

        if lat is None or lon is None:
            # Fallback to local locations registry
            loc = find_location_by_name(cleaned_city)
            if loc:
                lat, lon = loc["lat"], loc["lon"]
            else:
                return {"error": "Location not found"}

        # Fetch real weather data by coordinates
        weather = get_weather_by_coords(lat, lon, city_name=cleaned_city)
        source = "realtime_api"

        if not weather:
            # Fallback if API fails, rate limited, or key missing
            fb = get_fallback_mock(cleaned_city, lat, lon)
            temp = fb["temperature"]
            humidity = fb["humidity"]
            rainfall = fb["rainfall"]
            wind = fb["wind_speed"]
            source = "fallback_mock"
        else:
            temp = float(weather.get("temperature", 30.0))
            humidity = float(weather.get("humidity", 70.0))
            rainfall = float(weather.get("rainfall", 0.0))
            wind = float(weather.get("wind_speed", 2.0))

        # STEP 3: Standard weather object
        current_time = datetime.now().isoformat()
        weather_obj = {
            "city": cleaned_city,
            "lat": lat,
            "lon": lon,
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind, 1),
            "timestamp": current_time,
        }

        # STEP 4: Feature engineering
        features = engineer_features(weather_obj)

        # STEP 5: Prediction
        prediction = predict_nowcast(features)
        risk = prediction["risk_level"]

        # STEP 6: Actionable alert (reusing generate_actionable_alert)
        alert = generate_actionable_alert(risk, rainfall, humidity, wind)

        # STEP 7: Final response format
        return {
            "city": cleaned_city,
            "lat": lat,
            "lon": lon,
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind, 1),
            "risk_level": risk,
            "prediction": prediction,
            "alert": alert,
            "source": source,
        }

    except Exception as e:
        print(f"[NOWCAST ERROR] Exception during nowcast for '{cleaned_city}': {e}")
        # STEP 8: Safe fallback if unexpected exception occurs
        fb = get_fallback_mock(cleaned_city, 22.0, 79.0)
        temp = fb["temperature"]
        humidity = fb["humidity"]
        rainfall = fb["rainfall"]
        wind = fb["wind_speed"]

        risk = "HIGH" if rainfall > 25 else ("MODERATE" if rainfall > 10 else "LOW")
        prediction = {"risk_level": risk, "probability": 0.85}
        alert = generate_actionable_alert(risk, rainfall, humidity, wind)

        return {
            "city": cleaned_city,
            "lat": 22.0,
            "lon": 79.0,
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind, 1),
            "risk_level": risk,
            "prediction": prediction,
            "alert": alert,
            "source": "fallback_mock",
        }

