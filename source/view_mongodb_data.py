"""
MongoDB Data Viewer
View data stored in MongoDB collections
"""

import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from storage.mongodb_connection import get_mongodb_connection


def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")


def view_collection_stats(db, collection_name):
    """View statistics for a collection"""
    collection = db[collection_name]
    count = collection.count_documents({})
    
    print(f"\n📊 Collection: {collection_name}")
    print(f"   Total Documents: {count}")
    
    if count > 0:
        # Get sample document
        sample = collection.find_one()
        print(f"   Sample Document Keys: {list(sample.keys())}")
        
        # Get date range if timestamp exists
        if 'timestamp' in sample:
            oldest = collection.find_one(sort=[('timestamp', 1)])
            newest = collection.find_one(sort=[('timestamp', -1)])
            print(f"   Date Range: {oldest.get('timestamp')} to {newest.get('timestamp')}")
    
    return count


def view_device_data(db, limit=10):
    """View device sensor data"""
    print_separator("DEVICE DATA")
    
    collection = db['device_data']
    count = collection.count_documents({})
    
    print(f"Total sensor readings: {count}")
    
    if count > 0:
        # Get unique devices
        devices = collection.distinct('device_id')
        print(f"Number of devices: {len(devices)}")
        print(f"Devices: {devices[:10]}...")
        
        print(f"\nLast {limit} readings:")
        for doc in collection.find().sort('timestamp', -1).limit(limit):
            print(f"  Device: {doc.get('device_id')}, "
                  f"Temp: {doc.get('temperature', 'N/A')}°C, "
                  f"Humidity: {doc.get('humidity', 'N/A')}%, "
                  f"Time: {doc.get('timestamp', 'N/A')}")
    else:
        print("⚠️  No device data found in MongoDB")


def view_local_models(db, limit=5):
    """View local model information"""
    print_separator("LOCAL MODELS")
    
    collection = db['local_models']
    count = collection.count_documents({})
    
    print(f"Total local models: {count}")
    
    if count > 0:
        devices = collection.distinct('device_id')
        print(f"Devices with models: {devices}")
        
        print(f"\nLast {limit} model updates:")
        for doc in collection.find().sort('timestamp', -1).limit(limit):
            print(f"  Device: {doc.get('device_id')}, "
                  f"Version: {doc.get('model_version', 'N/A')}, "
                  f"Accuracy: {doc.get('accuracy', 'N/A')}, "
                  f"Time: {doc.get('timestamp', 'N/A')}")
    else:
        print("⚠️  No local models found in MongoDB")


def view_global_model(db):
    """View global model information"""
    print_separator("GLOBAL MODEL")
    
    collection = db['global_model']
    count = collection.count_documents({})
    
    print(f"Total aggregation rounds: {count}")
    
    if count > 0:
        latest = collection.find_one(sort=[('aggregation_round', -1)])
        print(f"\nLatest Global Model:")
        print(f"  Round: {latest.get('aggregation_round', 'N/A')}")
        print(f"  Timestamp: {latest.get('timestamp', 'N/A')}")
        print(f"  Participating Devices: {latest.get('num_devices', 'N/A')}")
        print(f"  Global Accuracy: {latest.get('global_accuracy', 'N/A')}")
    else:
        print("⚠️  No global model found in MongoDB")


def view_predictions(db, limit=10):
    """View prediction results"""
    print_separator("PREDICTIONS")
    
    collection = db['predictions']
    count = collection.count_documents({})
    
    print(f"Total predictions: {count}")
    
    if count > 0:
        anomalies = collection.count_documents({'is_anomaly': True})
        print(f"Anomalies detected: {anomalies}")
        
        print(f"\nLast {limit} predictions:")
        for doc in collection.find().sort('timestamp', -1).limit(limit):
            anomaly_flag = "🚨 ANOMALY" if doc.get('is_anomaly') else "✓ Normal"
            print(f"  {anomaly_flag} | Device: {doc.get('device_id')}, "
                  f"Prediction: {doc.get('prediction', 'N/A'):.2f}, "
                  f"Actual: {doc.get('actual_value', 'N/A'):.2f}, "
                  f"Time: {doc.get('timestamp', 'N/A')}")
    else:
        print("⚠️  No predictions found in MongoDB")


def main():
    """Main function"""
    print_separator("IoT PIPELINE - MongoDB Data Viewer")
    
    try:
        # Connect to MongoDB
        print("\nConnecting to MongoDB...")
        mongo = get_mongodb_connection()
        db = mongo.db
        print(f"✓ Connected to database: {db.name}")
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"✓ Available collections: {collections}")
        
        # View statistics for each collection
        print_separator("COLLECTION STATISTICS")
        total_docs = 0
        for coll_name in collections:
            count = view_collection_stats(db, coll_name)
            total_docs += count
        
        print(f"\n📈 Total documents across all collections: {total_docs}")
        
        # View detailed data for each collection
        view_device_data(db, limit=10)
        view_local_models(db, limit=5)
        view_global_model(db)
        view_predictions(db, limit=10)
        
        print_separator("END OF REPORT")
        
        # Interactive query option
        print("\n💡 Tip: You can also use MongoDB Compass for GUI access:")
        print("   Connection String: mongodb://localhost:27017")
        print("   Database: iot_analytics")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure MongoDB is running: docker ps | findstr mongodb")
        print("  2. Check connection: docker exec mongodb mongosh --eval 'db.adminCommand(\"ping\")'")
        print("  3. Verify services are running: .\\CHECK_STATUS.bat")


if __name__ == "__main__":
    main()
