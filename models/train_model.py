import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

MODEL_PATH = os.path.join(os.path.dirname(__file__), "weather_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

def create_labels(df):
    """
    Creates realistic continuous meteorological probabilities and labels based on physical triggers:
      Thunderstorm: High humidity + instability + pressure drop
      Flood: High sustained rainfall + moisture_index
      Cloudburst: Extreme rainfall spikes + rain intensity
    """
    df = df.copy()
    
    def sigmoid(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -6.0, 6.0)))
    
    # 1. Thunderstorm: High humidity + instability index + pressure drop
    z_thunder = (
        0.055 * (df['humidity'] - 65.0) +
        1.75 * (df['instability_index'] - 2.05) +
        0.12 * (df['pressure_drop'] - 2.0) +
        0.04 * (df['wind_speed'] - 5.0)
    )
    p_thunder = np.clip(sigmoid(z_thunder), 0.05, 0.92)
    df['thunderstorm'] = np.random.binomial(1, p_thunder)
    
    # 2. Flood: High sustained rainfall + moisture_index
    z_flood = (
        0.065 * (df['rainfall'] - 40.0) +
        0.00075 * (df['moisture_index'] - 2400.0)
    )
    p_flood = np.clip(sigmoid(z_flood), 0.04, 0.92)
    df['flood'] = np.random.binomial(1, p_flood)
    
    # 3. Cloudburst: Extreme rainfall spike + high rain intensity
    z_cloudburst = (
        0.075 * (df['rainfall'] - 65.0) +
        1.5 * (df['rain_intensity'] - 0.65)
    )
    p_cloudburst = np.clip(sigmoid(z_cloudburst), 0.03, 0.90)
    df['cloudburst'] = np.random.binomial(1, p_cloudburst)
    
    return df

def train_model(df):
    print("Creating realistic meteorological labels...")
    df = create_labels(df)
    
    features = ['temperature', 'humidity', 'wind_speed', 'pressure', 'rainfall',
                'moisture_index', 'instability_index', 'rain_intensity', 'pressure_drop']
    
    targets = ['flood', 'thunderstorm', 'cloudburst']
    
    X = df[features]
    y = df[targets]
    
    print("Normalizing features with StandardScaler...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 80/20 Train-Test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    print("Training Optimized RandomForest Classifier (250 estimators)...")
    # min_samples_leaf=6 and max_depth=10 guarantee smooth, non-extreme tree probability distributions
    model = RandomForestClassifier(
        n_estimators=250, 
        max_depth=10, 
        min_samples_leaf=6, 
        class_weight='balanced', 
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    print("\n--- Model Evaluation ---")
    predictions = model.predict(X_test)
    prob_predictions = model.predict_proba(X_test)
    
    for i, target in enumerate(targets):
        acc = accuracy_score(y_test.iloc[:, i], predictions[:, i])
        probs = prob_predictions[i][:, 1] if len(prob_predictions[i].shape) == 2 else np.zeros(len(y_test))
        try:
            auc = roc_auc_score(y_test.iloc[:, i], probs)
        except ValueError:
            auc = 0.0
            
        print(f"[{target.upper()}] Accuracy: {acc:.4f} | ROC-AUC: {auc:.4f}")
        
    print("------------------------\n")
        
    # Save the scaler so the API can normalize inputs correctly
    joblib.dump(scaler, SCALER_PATH)
    
    return model

def save_model(model):
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully to {MODEL_PATH}")

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def load_scaler():
    if os.path.exists(SCALER_PATH):
        return joblib.load(SCALER_PATH)
    return None

