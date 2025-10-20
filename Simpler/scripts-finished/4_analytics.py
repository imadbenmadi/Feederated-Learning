"""
Component 4: Batch Analytics & Storage
Team: SU YOUNG, ROBERT

Stores data in MongoDB and performs batch analytics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from pymongo import MongoClient
from datetime import datetime


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def store_in_mongodb():
    """Store processed data in MongoDB"""
    config = load_config()
    
    print("=" * 60)
    print("BATCH ANALYTICS & STORAGE")
    print("=" * 60)
    
    # Connect to MongoDB
    client = MongoClient(f"mongodb://{config['mongodb']['host']}:{config['mongodb']['port']}/")
    db = client[config['mongodb']['database']]
    
    print(f"\nConnected to MongoDB: {config['mongodb']['database']}")
    
    # Load data
    data_file = Path(__file__).parent.parent / "data" / "processed" / "processed_iot_data.csv"
    df = pd.read_csv(data_file)
    
    print(f"Loaded {len(df)} records")
    
    # Store in MongoDB
    collection = db['sensor_data']
    
    # Clear existing data
    collection.delete_many({})
    print("Cleared existing data")
    
    # Convert to records
    records = df.to_dict('records')
    
    # Insert
    print("Inserting records...")
    result = collection.insert_many(records)
    
    print(f"[SUCCESS] Inserted {len(result.inserted_ids)} documents")
    
    # Perform analytics
    print("\n" + "-" * 60)
    print("BATCH ANALYTICS")
    print("-" * 60)
    
    # 1. Device statistics
    pipeline = [
        {
            "$group": {
                "_id": "$device_id",
                "count": {"$sum": 1},
                "avg_temp": {"$avg": "$temperature"},
                "avg_humidity": {"$avg": "$humidity"},
                "avg_light": {"$avg": "$light"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    device_stats = list(collection.aggregate(pipeline))
    
    print(f"\nDevice Statistics (Top 10):")
    print(f"{'Device':<15} {'Count':<10} {'Avg Temp':<12} {'Avg Humidity':<15} {'Avg Light':<12}")
    print("-" * 70)
    
    for stat in device_stats[:10]:
        print(f"{stat['_id']:<15} {stat['count']:<10} "
              f"{stat['avg_temp']:<12.2f} {stat['avg_humidity']:<15.2f} {stat['avg_light']:<12.2f}")
    
    # 2. Temperature analysis
    temp_stats = collection.aggregate([
        {
            "$group": {
                "_id": None,
                "min_temp": {"$min": "$temperature"},
                "max_temp": {"$max": "$temperature"},
                "avg_temp": {"$avg": "$temperature"}
            }
        }
    ])
    
    temp_result = list(temp_stats)[0]
    print(f"\nTemperature Analysis:")
    print(f"  Min: {temp_result['min_temp']:.2f}°C")
    print(f"  Max: {temp_result['max_temp']:.2f}°C")
    print(f"  Avg: {temp_result['avg_temp']:.2f}°C")
    
    # 3. Anomaly detection (simple threshold-based)
    temp_mean = temp_result['avg_temp']
    temp_std = df['temperature'].std()
    
    anomalies = collection.count_documents({
        "$or": [
            {"temperature": {"$gt": temp_mean + 2 * temp_std}},
            {"temperature": {"$lt": temp_mean - 2 * temp_std}}
        ]
    })
    
    print(f"\nAnomaly Detection:")
    print(f"  Threshold: Mean ± 2*STD")
    print(f"  Anomalies found: {anomalies} ({anomalies/len(df)*100:.2f}%)")
    
    # Save analytics report
    output_dir = Path(__file__).parent.parent / "outputs" / "analytics"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_records": len(df),
        "num_devices": len(device_stats),
        "temperature": {
            "min": float(temp_result['min_temp']),
            "max": float(temp_result['max_temp']),
            "avg": float(temp_result['avg_temp'])
        },
        "anomalies": anomalies,
        "top_devices": [
            {
                "device": stat['_id'],
                "count": stat['count'],
                "avg_temp": float(stat['avg_temp'])
            }
            for stat in device_stats[:10]
        ]
    }
    
    report_file = output_dir / "analytics_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[SUCCESS] Analytics report saved: {report_file}")
    
    print("\n" + "=" * 60)
    print("ANALYTICS COMPLETE")
    print("=" * 60)
    
    client.close()
    
    return report


if __name__ == "__main__":
    print()
    result = store_in_mongodb()
    print("\nData stored in MongoDB!")
    print("Next step: Run 5_visualization.py")
