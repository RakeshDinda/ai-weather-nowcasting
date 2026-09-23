import sys
import os
import pandas as pd

# Add the project root to sys.path so python can find the modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.data_loader import load_data, preprocess_data, engineer_features
from models.train_model import train_model, save_model, load_model
from models.model import predict_weather
from utils.api_fetcher import get_weather_data
from utils.alert_system import generate_alerts

def ensure_model_is_trained():
    """Helper function to make sure we have a trained model saved."""
    model = load_model()
    if model is None:
        print("No saved ML model found. Training on historical data first...")
        data_path = os.path.join(project_root, "data", "raw", "weather_data.csv")
        df = load_data(data_path)
        df_clean = preprocess_data(df)
        df_eng = engineer_features(df_clean)
        
        model = train_model(df_eng)
        save_model(model)
        print("Model trained and ready!\n")
    return model

def run():
    print("--- Starting Live Weather Prediction Pipeline ---\n")
    
    # 1. Ensure model is trained
    model = ensure_model_is_trained()
    
    # 2. Get User Input
    city = input("Enter a city name (e.g., 'Delhi', 'Mumbai'): ")
    if not city.strip():
        print("City name cannot be empty. Exiting.")
        return
        
    # 3. Fetch API Data
    print(f"\nFetching live weather data for {city}...")
    live_data = get_weather_data(city)
    
    if live_data is None:
        print("Error: Could not retrieve live weather data.")
        return
        
    # 4. Data Preparation
    data_path = os.path.join(project_root, "data", "raw", "weather_data.csv")
    historical_df = load_data(data_path)
    
    live_df = pd.DataFrame([live_data])
    combined_df = pd.concat([historical_df, live_df], ignore_index=True)
    
    combined_clean = preprocess_data(combined_df)
    combined_engineered = engineer_features(combined_clean)
    
    processed_live_row = combined_engineered.iloc[-1]
    
    # 5. Get ML Prediction
    prediction = predict_weather(processed_live_row, trained_model=model)
    
    if prediction is None or "error" in prediction:
        print("Error: Could not generate prediction. Ensure model is trained correctly.")
        return
        
    # 6. Generate Alerts
    alerts = generate_alerts(prediction)
    
    # 7. Final Clean Output Formatting
    print("\n--------------------------------------\n")
    print("--- FINAL RESULT ---\n")
    print(f"City: {city}\n")
    
    print("Live Weather Data:")
    print(f"Temperature: {live_data['temperature']} °C")
    print(f"Humidity: {live_data['humidity']} %")
    print(f"Wind Speed: {live_data['wind_speed']} m/s")
    print(f"Rainfall: {live_data['rainfall']} mm\n")
    
    print("Prediction Probabilities:")
    print(f"Flood: {prediction.get('flood', 0.0)}")
    print(f"Thunderstorm: {prediction.get('thunderstorm', 0.0)}")
    print(f"Cloudburst: {prediction.get('cloudburst', 0.0)}\n")
    
    print("Risk Alerts:")
    print(f"Flood: {alerts.get('flood', 'UNKNOWN')}")
    print(f"Thunderstorm: {alerts.get('thunderstorm', 'UNKNOWN')}")
    print(f"Cloudburst: {alerts.get('cloudburst', 'UNKNOWN')}")
    print("\n--------------------------------------")

if __name__ == "__main__":
    run()
