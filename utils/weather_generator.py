import random
import hashlib
import time
from datetime import datetime

def generate_realistic_weather(city_name, lat=None, lon=None, region="North"):
    """
    Generates realistic, physically-consistent weather patterns for Indian cities
    constrained strictly within:
      Temperature: 10°C – 45°C
      Humidity: 30% – 100%
      Rainfall: Skewed (most 0–10mm, occasional 50–150mm)
      Pressure: 980 – 1030 hPa
      Wind: 0.5 – 15 m/s
    """
    # Deterministic base seed per city + current hour so weather is stable yet dynamic
    current_hour = datetime.now().strftime("%Y-%m-%d-%H")
    seed_str = f"{city_name}-{current_hour}"
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed_val)

    # 1. Base climate determination by region and latitude
    is_hill_station = any(hill in city_name.lower() for hill in [
        'shimla', 'manali', 'leh', 'srinagar', 'dharamshala', 'nainital', 
        'gangtok', 'darjeeling', 'cherrapunji', 'shillong', 'ooty', 'munnar'
    ])
    
    is_coastal = any(coast in city_name.lower() for coast in [
        'mumbai', 'chennai', 'kochi', 'kolkata', 'visakhapatnam', 'mangalore', 
        'goa', 'panaji', 'thiruvananthapuram', 'surat', 'bhavnagar', 'puri'
    ]) or (lat is not None and lat < 18 and lon is not None and (lon < 75 or lon > 80))

    is_arid = any(arid in city_name.lower() for arid in [
        'jodhpur', 'bikaner', 'jaisalmer', 'barmer', 'bhuj', 'hisar'
    ]) or (region == "West" and lat is not None and lat > 24 and lon is not None and lon < 74)

    # Temperature (°C): 10 to 45
    if is_hill_station:
        base_temp = rng.uniform(11.0, 22.0)
    elif is_arid:
        base_temp = rng.uniform(32.0, 43.5)
    elif is_coastal:
        base_temp = rng.uniform(27.0, 34.5)
    elif region == "Northeast":
        base_temp = rng.uniform(21.0, 31.0)
    elif region == "South":
        base_temp = rng.uniform(26.0, 36.0)
    else: # North, Central, East
        base_temp = rng.uniform(23.0, 38.0)
    
    temperature = round(max(10.0, min(45.0, base_temp)), 2)

    # Humidity (%): 30 to 100
    if is_coastal or region == "Northeast":
        base_hum = rng.uniform(68.0, 96.0)
    elif is_arid:
        base_hum = rng.uniform(30.0, 52.0)
    elif is_hill_station:
        base_hum = rng.uniform(55.0, 88.0)
    else:
        base_hum = rng.uniform(42.0, 82.0)
        
    humidity = round(max(30.0, min(100.0, base_hum)), 1)

    # Pressure (hPa): 980 to 1030
    # Higher altitudes have lower barometric pressure
    if is_hill_station:
        base_press = rng.uniform(982.0, 1004.0)
    else:
        base_press = rng.uniform(1002.0, 1022.0)
    
    # Storm low-pressure perturbation
    if rng.random() < 0.15:
        base_press -= rng.uniform(8.0, 18.0)
        
    pressure = round(max(980.0, min(1030.0, base_press)), 1)

    # Wind speed (m/s): 0.5 to 15.0
    if is_coastal or is_hill_station:
        wind_speed = round(rng.uniform(3.0, 13.5), 2)
    else:
        wind_speed = round(rng.uniform(1.0, 8.5), 2)
    wind_speed = max(0.5, min(15.0, wind_speed))

    # Rainfall (mm): Skewed distribution (mostly 0–10mm, few 50–150mm)
    rain_roll = rng.random()
    if is_arid:
        # Very low chance of rain in desert regions
        rainfall = 0.0 if rain_roll > 0.12 else round(rng.uniform(0.5, 8.0), 1)
    elif region == "Northeast" or (is_coastal and humidity > 80):
        # Higher monsoon propensity
        if rain_roll < 0.35:
            rainfall = round(rng.uniform(0.0, 4.0), 1)
        elif rain_roll < 0.75:
            rainfall = round(rng.uniform(5.0, 25.0), 1)
        elif rain_roll < 0.92:
            rainfall = round(rng.uniform(30.0, 75.0), 1)
        else:
            # Extreme severe event (50–150mm)
            rainfall = round(rng.uniform(75.0, 145.0), 1)
    else:
        # Standard Indian distribution: majority low/dry
        if rain_roll < 0.55:
            rainfall = 0.0
        elif rain_roll < 0.82:
            rainfall = round(rng.uniform(0.5, 9.5), 1)
        elif rain_roll < 0.95:
            rainfall = round(rng.uniform(12.0, 45.0), 1)
        else:
            # Few high rainfall spikes (50–150mm)
            rainfall = round(rng.uniform(55.0, 125.0), 1)

    rainfall = max(0.0, min(150.0, rainfall))

    return {
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "rainfall": rainfall,
        "lat": lat,
        "lon": lon,
        "city_name": city_name
    }
