"""
Component 2: Local Training
Team: IMED, AMIR

Trains a neural network model for each IoT device
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import pickle
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def train_local_models():
    """Train one model per device"""
    config = load_config()
    
    # Load data
    data_file = Path(__file__).parent.parent / "data" / "processed" / "processed_iot_data.csv"
    model_dir = Path(__file__).parent.parent / "models" / "local"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LOCAL TRAINING - Per-Device Models")
    print("=" * 60)
    print(f"\nLoading data from: {data_file}")
    
    df = pd.read_csv(data_file)
    devices = df['device_id'].unique()
    
    print(f"Total devices: {len(devices)}")
    print(f"Total records: {len(df)}")
    
    # Training configuration
    hidden_layers = tuple(config['training']['hidden_layers'])
    epochs = config['training']['epochs']
    
    models_trained = {}
    
    print(f"\nTraining models (Hidden layers: {hidden_layers}, Epochs: {epochs})...")
    print("-" * 60)
    
    for i, device in enumerate(devices, 1):
        # Get device data
        device_data = df[df['device_id'] == device]
        
        # Features: temperature, humidity, light
        # Target: voltage (for demonstration)
        X = device_data[['temperature', 'humidity', 'light']].values
        y = device_data['voltage'].values
        
        # Skip if not enough data
        if len(X) < 10:
            print(f"[{i}/{len(devices)}] {device}: SKIPPED (insufficient data)")
            continue
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = MLPRegressor(
            hidden_layer_sizes=hidden_layers,
            max_iter=epochs,
            random_state=42,
            verbose=False
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Save model and scaler
        model_data = {
            'model': model,
            'scaler': scaler,
            'train_score': train_score,
            'test_score': test_score,
            'num_samples': len(X)
        }
        
        model_file = model_dir / f"{device}.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        models_trained[device] = {
            'samples': len(X),
            'train_score': train_score,
            'test_score': test_score
        }
        
        print(f"[{i}/{len(devices)}] {device}: Train R²={train_score:.4f}, Test R²={test_score:.4f}, Samples={len(X)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("LOCAL TRAINING COMPLETE")
    print("=" * 60)
    print(f"\nModels trained: {len(models_trained)}")
    print(f"Models saved in: {model_dir}")
    
    # Calculate average scores
    avg_train = np.mean([m['train_score'] for m in models_trained.values()])
    avg_test = np.mean([m['test_score'] for m in models_trained.values()])
    
    print(f"\nAverage Training R²: {avg_train:.4f}")
    print(f"Average Test R²: {avg_test:.4f}")
    
    return models_trained


if __name__ == "__main__":
    print()
    models = train_local_models()
    print("\nNext step: Run 3_aggregation.py")
