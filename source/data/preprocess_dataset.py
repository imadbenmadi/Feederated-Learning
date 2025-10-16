"""
Dataset Preprocessing Script
Cleans and prepares the Intel Lab Data for streaming and analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def load_raw_data(raw_file_path):
    """
    Load the raw dataset
    """
    print(f"Loading raw data from {raw_file_path}...")
    
    try:
        # Read CSV with appropriate column names
        df = pd.read_csv(raw_file_path, names=['date', 'time', 'epoch', 'device_id', 'temperature', 'humidity', 'light', 'voltage'], skiprows=1)
        print(f"✓ Loaded {len(df)} records")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return None


def clean_data(df):
    """
    Clean and validate the dataset
    """
    print("\nCleaning data...")
    initial_count = len(df)
    
    # Convert sensor readings to float first
    numeric_columns = ['temperature', 'humidity', 'light', 'voltage']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert epoch to numeric
    df['epoch'] = pd.to_numeric(df['epoch'], errors='coerce')
    df['device_id'] = pd.to_numeric(df['device_id'], errors='coerce')
    
    # Remove rows with missing values
    df = df.dropna()
    print(f"✓ Removed {initial_count - len(df)} rows with missing values")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    print(f"✓ Removed {initial_count - len(df)} duplicate rows")
    
    # Convert to appropriate types
    df['epoch'] = df['epoch'].astype(int)
    df['device_id'] = df['device_id'].astype(int)
    
    # Remove outliers (values beyond reasonable sensor ranges)
    initial_count = len(df)
    df = df[
        (df['temperature'] >= -50) & (df['temperature'] <= 150) &  # Celsius
        (df['humidity'] >= 0) & (df['humidity'] <= 100) &  # Percentage
        (df['light'] >= 0) & (df['light'] <= 10000) &  # Lux
        (df['voltage'] >= 0) & (df['voltage'] <= 10)  # Volts
    ]
    print(f"✓ Removed {initial_count - len(df)} outliers")
    print(f"✓ Final dataset: {len(df)} valid records")
    
    return df


def add_derived_features(df):
    """
    Add useful derived features
    """
    print("\nAdding derived features...")
    
    # Convert epoch timestamp to datetime
    # Intel Lab data: epoch is in seconds since 2004-02-28
    base_date = pd.Timestamp('2004-02-28')
    df['datetime'] = base_date + pd.to_timedelta(df['epoch'], unit='s')
    
    # Convert device_id to string format
    df['device_id'] = 'device_' + df['device_id'].astype(str).str.zfill(3)
    
    # Create date and time strings for compatibility
    df['date'] = df['datetime'].dt.strftime('%Y-%m-%d')
    df['time'] = df['datetime'].dt.strftime('%H:%M:%S')
    
    # Sort by timestamp
    df = df.sort_values(['device_id', 'epoch'])
    
    # Add time-based features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    
    # Add rolling averages per device (for anomaly detection)
    df['temp_rolling_mean'] = df.groupby('device_id')['temperature'].transform(
        lambda x: x.rolling(window=10, min_periods=1).mean()
    )
    
    df['temp_rolling_std'] = df.groupby('device_id')['temperature'].transform(
        lambda x: x.rolling(window=10, min_periods=1).std()
    )
    
    print(f"✓ Added derived features")
    
    return df


def save_processed_data(df, output_path):
    """
    Save the processed dataset
    """
    print(f"\nSaving processed data to {output_path}...")
    
    try:
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"✓ Processed data saved successfully")
        
        # Display summary statistics
        print("\n" + "=" * 60)
        print("Dataset Summary:")
        print("=" * 60)
        print(f"Total records: {len(df)}")
        print(f"Number of devices: {df['device_id'].nunique()}")
        print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"\nDevices: {sorted(df['device_id'].unique())}")
        
        print("\nSensor Statistics:")
        print(df[['temperature', 'humidity', 'light', 'voltage']].describe())
        
        return True
        
    except Exception as e:
        print(f"✗ Error saving data: {e}")
        return False


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Intel Lab Data Preprocessing Script")
    print("=" * 60)
    
    # Define paths
    data_dir = Path(__file__).parent
    raw_file = data_dir / "raw" / "intel_lab_data.csv"
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_file = processed_dir / "processed_iot_data.csv"
    
    # Check if raw file exists
    if not raw_file.exists():
        print(f"✗ Raw data file not found: {raw_file}")
        print("Please run download_dataset.py first")
        return
    
    # Load raw data
    df = load_raw_data(raw_file)
    
    if df is not None:
        # Clean data
        df = clean_data(df)
        
        # Add derived features
        df = add_derived_features(df)
        
        # Save processed data
        save_processed_data(df, processed_file)
        
        print("\n" + "=" * 60)
        print("✓ Preprocessing complete!")
        print("=" * 60)
        print(f"Processed data location: {processed_file}")
        print("\nNext step: Start the Kafka producer to stream the data")


if __name__ == "__main__":
    main()
