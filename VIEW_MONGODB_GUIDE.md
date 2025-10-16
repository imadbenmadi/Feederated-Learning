# How to View Data in MongoDB

## Method 1: Using the Viewer Script (Easiest)

```batch
.\VIEW_DATA.bat
```

This will show:

-   Total documents in each collection
-   Latest sensor readings
-   Local model statistics
-   Global model information
-   Anomaly predictions

---

## Method 2: MongoDB Shell (Command Line)

### Connect to MongoDB:

```batch
docker exec -it mongodb mongosh
```

### Switch to database:

```javascript
use iot_analytics
```

### View Collections:

```javascript
show collections
```

### Query Device Data:

```javascript
// Count all sensor readings
db.device_data.countDocuments();

// View latest 5 readings
db.device_data.find().sort({ timestamp: -1 }).limit(5).pretty();

// Find data for specific device
db.device_data.find({ device_id: "device_001" }).limit(10).pretty();

// Get unique devices
db.device_data.distinct("device_id");
```

### Query Local Models:

```javascript
// Count models
db.local_models.countDocuments();

// View latest model update
db.local_models.find().sort({ timestamp: -1 }).limit(1).pretty();

// Find model for specific device
db.local_models.find({ device_id: "device_001" }).pretty();
```

### Query Global Model:

```javascript
// View latest global model
db.global_model.find().sort({ aggregation_round: -1 }).limit(1).pretty();

// View all aggregation rounds
db.global_model.find().sort({ aggregation_round: 1 }).pretty();
```

### Query Predictions:

```javascript
// Count predictions
db.predictions.countDocuments();

// View anomalies only
db.predictions.find({ is_anomaly: true }).limit(10).pretty();

// View predictions for a device
db.predictions.find({ device_id: "device_001" }).limit(10).pretty();
```

### Exit MongoDB Shell:

```javascript
exit;
```

---

## Method 3: MongoDB Compass (GUI)

### Install MongoDB Compass:

Download from: https://www.mongodb.com/try/download/compass

### Connection String:

```
mongodb://localhost:27017
```

### Database Name:

```
iot_analytics
```

### Collections to Explore:

1. **device_data** - Raw sensor readings
2. **local_models** - Per-device ML models
3. **global_model** - Aggregated federated model
4. **predictions** - Model predictions and anomalies

---

## Method 4: Python Script (Custom Queries)

```python
from pymongo import MongoClient

# Connect
client = MongoClient('mongodb://localhost:27017/')
db = client['iot_analytics']

# Query examples
device_data = db.device_data.find().limit(10)
for doc in device_data:
    print(doc)

# Count by device
pipeline = [
    {"$group": {"_id": "$device_id", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
result = db.device_data.aggregate(pipeline)
for doc in result:
    print(doc)
```

---

## Quick Reference

| Action          | Command                                                    |
| --------------- | ---------------------------------------------------------- |
| View all data   | `.\VIEW_DATA.bat`                                          |
| MongoDB Shell   | `docker exec -it mongodb mongosh`                          |
| Count documents | `db.collection_name.countDocuments()`                      |
| Find latest     | `db.collection_name.find().sort({timestamp: -1}).limit(5)` |
| Find by device  | `db.collection_name.find({device_id: "device_001"})`       |
| Export to JSON  | `mongoexport -d iot_analytics -c device_data -o data.json` |

---

## Data Storage Flow

1. **Kafka Producer** → Streams data to Kafka topic
2. **Flink Job** → Consumes from Kafka → Stores in `device_data` collection
3. **Flink Job** → Trains local models → Stores in `local_models` collection
4. **Global Server** → Aggregates models → Stores in `global_model` collection
5. **Spark Jobs** → Analyzes data → Stores predictions in `predictions` collection

---

## Troubleshooting

### No data in collections?

1. Check if services are running: `.\CHECK_STATUS.bat`
2. Verify Kafka producer is streaming: Check Kafka UI at http://localhost:8080
3. Check logs: `Get-Content source\logs\*.log`

### Can't connect to MongoDB?

```batch
docker ps | findstr mongodb
docker exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### Reset all data:

```batch
docker exec -it mongodb mongosh
use iot_analytics
db.dropDatabase()
exit
```

Then re-run: `.\RUN.bat`
