"""
Component 1: Data Preprocessing
Team: SU YOUNG, ROBERT

Cleans and prepares the dataset for training
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def preprocess_data():
    """Preprocess the raw dataset"""
    config = load_config()
    
    # File paths
    raw_file = Path(__file__).parent.parent / "data" / "raw" / "intel_lab_data.txt"
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_file = processed_dir / "processed_iot_data.csv"
    
    print("=" * 60)
    print("DATA PREPROCESSING")
    print("=" * 60)
    print(f"\nLoading: {raw_file}")
    
    # Read data
    data = []
    with open(raw_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                data.append(parts[:6])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['epoch', 'device_id', 'temperature', 'humidity', 'light', 'voltage'])
    
    print(f"Loaded {len(df)} records")
    
    # Convert types
    df['epoch'] = pd.to_numeric(df['epoch'], errors='coerce')
    df['device_id'] = pd.to_numeric(df['device_id'], errors='coerce').astype(int)
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
    df['light'] = pd.to_numeric(df['light'], errors='coerce')
    df['voltage'] = pd.to_numeric(df['voltage'], errors='coerce')
    
    # Remove missing values
    initial_count = len(df)
    df = df.dropna()
    print(f"Removed {initial_count - len(df)} rows with missing values")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_count - len(df)} duplicate rows")
    
    # Remove outliers
    initial_count = len(df)
    df = df[
        (df['temperature'] >= -50) & (df['temperature'] <= 150) &
        (df['humidity'] >= 0) & (df['humidity'] <= 100) &
        (df['light'] >= 0) & (df['light'] <= 10000) &
        (df['voltage'] >= 0) & (df['voltage'] <= 10)
    ]
    print(f"Removed {initial_count - len(df)} outliers")
    
    # Add datetime
    base_date = pd.Timestamp('2004-02-28')
    df['datetime'] = base_date + pd.to_timedelta(df['epoch'], unit='s')
    df['device_id'] = 'device_' + df['device_id'].astype(str).str.zfill(3)
    
    # Sort
    df = df.sort_values(['device_id', 'epoch'])
    
    # Save
    df.to_csv(processed_file, index=False)
    
    print(f"\n[SUCCESS] Saved {len(df)} records")
    print(f"Number of devices: {df['device_id'].nunique()}")
    print(f"Output: {processed_file}")
    
    # Summary statistics
    print("\nSensor Statistics:")
    print(df[['temperature', 'humidity', 'light', 'voltage']].describe())
    
    return processed_file


if __name__ == "__main__":
    print()
    result = preprocess_data()
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    print("\nData ready for training!")
    print("Next step: Run 2_local_training.py")
