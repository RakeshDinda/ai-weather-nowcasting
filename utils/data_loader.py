import pandas as pd
import numpy as np
import os

def generate_realistic_dataset(filepath, n_samples=20000):
    np.random.seed(42)
    
    # 1. Temperature: 10°C – 45°C
    # Truncated normal centered around 28°C
    raw_temp = np.random.normal(28, 7.5, n_samples)
    temperature = np.clip(raw_temp, 10.0, 45.0)
    
    # 2. Humidity: 30% – 100%
    raw_humidity = np.random.normal(68, 18, n_samples)
    humidity = np.clip(raw_humidity, 30.0, 100.0)
    
    # 3. Pressure: 980 – 1030 hPa
    raw_pressure = np.random.normal(1008, 8, n_samples)
    pressure = np.clip(raw_pressure, 980.0, 1030.0)
    
    # 4. Wind: 0.5 – 15 m/s
    raw_wind = np.random.gamma(2.2, 1.8, n_samples)
    wind_speed = np.clip(raw_wind, 0.5, 15.0)
    
    # 5. Rainfall: Skewed distribution
    # Most values low (0–10mm), few high (50–150mm)
    # Zero-inflated exponential + extreme right tail
    rain_presence = np.random.binomial(1, 0.45, n_samples)
    low_rain = np.random.exponential(scale=3.5, size=n_samples) * (rain_presence == 1)
    
    # High rainfall events (50–150mm) for about 6% of samples
    extreme_mask = (np.random.random(n_samples) < 0.06) & (humidity > 70)
    extreme_rain = np.random.uniform(50.0, 150.0, size=n_samples)
    
    rainfall = np.where(extreme_mask, extreme_rain, low_rain)
    rainfall = np.clip(rainfall, 0.0, 150.0)
    
    df = pd.DataFrame({
        'temperature': np.round(temperature, 2),
        'humidity': np.round(humidity, 1),
        'wind_speed': np.round(wind_speed, 2),
        'pressure': np.round(pressure, 1),
        'rainfall': np.round(rainfall, 2)
    })
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Generated realistic dataset with {n_samples} samples at {filepath}")
    return df

def load_data(filepath):
    if not os.path.exists(filepath):
        print("Generating realistic synthetic dataset...")
        return generate_realistic_dataset(filepath)
    
    df = pd.read_csv(filepath)
    if len(df) < 5000:
        print("Regenerating dataset with 20,000 realistic samples...")
        return generate_realistic_dataset(filepath)
        
    return df

def preprocess_data(df):
    df = df.copy()
    # Fill missing values with numeric column means
    df.fillna(df.mean(numeric_only=True), inplace=True)
    return df

def engineer_features(df):
    df = df.copy()
    
    # Meaningful derived meteorological features (Strictly matching specifications)
    # moisture_index = humidity * rainfall
    df['moisture_index'] = df['humidity'] * df['rainfall']
    
    # instability_index = (temperature * humidity) / pressure
    df['instability_index'] = (df['temperature'] * df['humidity']) / df['pressure']
    
    # rain_intensity = rainfall / (humidity + 1)
    df['rain_intensity'] = df['rainfall'] / (df['humidity'] + 1)
    
    # pressure_drop = 1013 - pressure
    df['pressure_drop'] = 1013.0 - df['pressure']
    
    return df
