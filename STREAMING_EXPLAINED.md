# Streaming Pipeline Configuration

## Overview

This system implements a **real-time continuous streaming pipeline** for federated learning with IoT sensor data.

---

## Data Flow Architecture

```
IoT Data (152K records)
    ↓ [Loops infinitely]
Kafka Producer (10 records/sec)
    ↓ [iot_stream topic]
Apache Flink (Real-time processing)
    ↓ [Per-device training]
Local Models (53 devices)
    ↓ [Every 30 seconds]
Global Server (Aggregation every 1 minute)
    ↓ [FedAvg algorithm]
Global Model Update
    ↓ [Continuous storage]
MongoDB (4 collections)
    ↓ [Analytics]
Spark Streaming & Batch
    ↓ [Visualization]
Superset Dashboard
```

---

## Streaming Configuration

### **Kafka Producer** (`kafka_config.json`)

-   **Rate:** 10 records per second
-   **Loop:** Enabled (restarts from beginning when dataset ends)
-   **Dataset:** 152,533 records (53 devices)
-   **Runtime:** Infinite (continuous streaming)

```json
{
    "streaming": {
        "loop_dataset": true,
        "records_per_second": 10,
        "batch_size": 10
    }
}
```

**Calculation:**

-   152,533 records ÷ 10 records/sec = ~4.2 hours per loop
-   System runs 24/7, continuously looping

---

### **Local Model Training** (Flink)

-   **Trigger:** Every 30 seconds per device
-   **Method:** Incremental learning on streaming data
-   **Devices:** 53 independent local models
-   **Algorithm:** Feedforward Neural Network

---

### **Global Aggregation** (`scheduler_config.json`)

-   **Interval:** Every 1 minute (for testing)
-   **Strategy:** FedAvg (Federated Averaging)
-   **Min Devices:** 3 devices required for aggregation
-   **Auto-trigger:** Enabled

```json
{
    "global_update_interval_minutes": 1,
    "local_training_interval_seconds": 30,
    "min_devices_for_aggregation": 3
}
```

---

## MongoDB Collections (Real-time Updates)

### 1. **device_data**

-   Stores every streamed sensor reading
-   **Update frequency:** 10 inserts/second
-   **Total capacity:** Unlimited (loops don't duplicate)

### 2. **local_models**

-   Stores per-device model weights
-   **Update frequency:** Every 30 seconds × 53 devices
-   **Growth:** ~106 updates/minute

### 3. **global_model**

-   Stores aggregated federated model
-   **Update frequency:** Every 1 minute
-   **Growth:** 1 document/minute

### 4. **predictions**

-   Stores anomaly detection results
-   **Update frequency:** Real-time (Spark Streaming)
-   **Growth:** Continuous

---

## How to Verify Streaming

### **1. Check Kafka UI** (http://localhost:8080)

-   View `iot_stream` topic
-   See messages flowing in real-time
-   ~10 messages/second

### **2. Check MongoDB Growth**

```bash
# Run this multiple times to see count increasing
docker exec -it mongodb mongosh
use iot_analytics
db.device_data.countDocuments()
# Wait 10 seconds, run again - should increase by ~100
```

### **3. Check Global Server Logs**

```bash
# View aggregation happening every 1 minute
Get-Content source\logs\global_server.log -Tail 20 -Wait
```

### **4. View Live Data**

```bash
.\VIEW_DATA.bat
# Run multiple times to see data growing
```

---

## Expected Behavior

### **First 1 Minute:**

-   Kafka Producer: 600 records streamed (10/sec × 60 sec)
-   MongoDB device_data: 600 documents
-   Flink: 53 local models training (2 cycles @ 30 sec each)
-   Global Server: 1 aggregation (at 1 minute mark)

### **First 10 Minutes:**

-   Kafka: 6,000 records streamed
-   MongoDB device_data: 6,000 documents
-   Local models: ~1,060 updates (20 cycles × 53 devices)
-   Global aggregations: 10 rounds

### **Complete Loop (4.2 hours):**

-   All 152,533 records streamed once
-   System automatically restarts from beginning
-   Continuous operation 24/7

---

## Production vs Testing Settings

### **Current (Testing):**

```json
{
    "records_per_second": 10,
    "global_update_interval_minutes": 1,
    "local_training_interval_seconds": 30
}
```

### **Production (Recommended):**

```json
{
    "records_per_second": 100,
    "global_update_interval_minutes": 30,
    "local_training_interval_seconds": 300
}
```

---

## Monitoring Streaming Status

### **CHECK_STATUS.bat**

Shows if all streaming components are running

### **Kafka UI** (http://localhost:8080)

-   Consumer lag: Should be near 0
-   Messages/sec: Should show ~10/sec
-   Topic partitions: Should show data flowing

### **API Docs** (http://localhost:8000/docs)

-   `/api/status` - Shows pending updates
-   `/api/history` - Shows aggregation history
-   `/api/models/latest` - Current global model

### **MongoDB Compass**

-   Connect: `mongodb://localhost:27017`
-   Watch collections growing in real-time

---

## Troubleshooting

### "No data streaming"

1. Check Kafka producer is running: `CHECK_STATUS.bat`
2. View Kafka UI: http://localhost:8080
3. Check logs: `source\logs\kafka_producer.log`

### "Global aggregation not happening"

1. Check scheduler config: 1 minute interval
2. Ensure min 3 devices have sent updates
3. View server logs: `source\logs\global_server.log`

### "Data not in MongoDB"

1. Verify Flink job is running
2. Check MongoDB connection
3. Run: `.\VIEW_DATA.bat`

---

## Summary

**Yes, this IS a streaming system:**

-   ✅ 10 records/second continuous stream
-   ✅ Infinite loop (restarts when dataset ends)
-   ✅ Real-time processing with Flink
-   ✅ Global aggregation every 1 minute
-   ✅ Persistent storage in MongoDB
-   ✅ Live visualization in Superset

**To start streaming:**

```batch
.\RUN.bat
```

**To verify streaming:**

```batch
.\CHECK_STATUS.bat
.\VIEW_DATA.bat
```

**Watch in real-time:**

-   Kafka UI: http://localhost:8080
-   API Status: http://localhost:8000/docs
-   Superset: http://localhost:8088
