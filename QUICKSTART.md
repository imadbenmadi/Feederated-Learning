# IoT Federated Learning Pipeline - Quick Start Guide

## Prerequisites

-   Docker Desktop running
-   Python 3.8+
-   8GB RAM minimum

## One-Click Startup

```batch
.\RUN.bat
```

**Initialization time:** 2-3 minutes

This automated script:

1. Validates Docker environment
2. Installs required Python packages
3. Configures MongoDB container
4. Processes IoT dataset (152K records, 53 devices)
5. Launches Kafka cluster (Zookeeper, Kafka, Kafka UI)
6. Initializes MongoDB collections
7. Starts Superset visualization
8. Deploys core services:
    - Global Model Server (FastAPI)
    - Kafka Producer (Data streaming)
    - Flink Job (Local model training)
    - Spark Jobs (Analytics)

## Service Access

| Component          | URL                        | Credentials | Purpose                         |
| ------------------ | -------------------------- | ----------- | ------------------------------- |
| Kafka UI           | http://localhost:8080      | None        | Monitor streaming data flow     |
| API Documentation  | http://localhost:8000/docs | None        | FastAPI endpoints, model status |
| Superset Dashboard | http://localhost:8088      | admin/admin | Data visualization, analytics   |

## System Architecture

```
IoT Data (152K records, continuous loop)
    ↓ 10 records/second
Kafka Topic (iot_stream)
    ↓ Real-time processing
Flink (Per-device training every 30s)
    ↓ Model updates
Global Server (FedAvg aggregation every 1 min)
    ↓ Persistent storage
MongoDB (4 collections: device_data, local_models, global_model, predictions)
    ↓ Analytics pipeline
Spark (Batch + Streaming)
    ↓ Visualization
Superset Dashboards
```

## Core Services

### Docker Containers (5)

-   **MongoDB** (port 27017): NoSQL database for all data persistence
-   **Zookeeper** (port 2181): Kafka cluster coordination
-   **Kafka** (port 9092): Message broker for data streaming
-   **Kafka UI** (port 8080): Web interface for Kafka monitoring
-   **Superset** (port 8088): Business intelligence and visualization

### Python Services (4)

-   **Global Model Server**: FastAPI application managing federated aggregation
-   **Kafka Producer**: Streams IoT data at 10 records/second with infinite loop
-   **Flink Job**: Per-device incremental model training
-   **Spark Jobs**: Batch and streaming analytics for model evaluation

## Data Pipeline Configuration

### Streaming Settings

```json
{
    "records_per_second": 10,
    "loop_dataset": true,
    "dataset_size": 152533
}
```

**Runtime:** Continuous (loops every ~4.2 hours)

### Federated Learning Settings

```json
{
    "local_training_interval_seconds": 30,
    "global_update_interval_minutes": 1,
    "min_devices_for_aggregation": 3,
    "aggregation_strategy": "fedavg"
}
```

## Monitoring and Verification

### Check System Status

```batch
.\CHECK_STATUS.bat
```

Validates:

-   Docker daemon status
-   Container health checks
-   Python package installation
-   Service endpoint availability
-   Process execution status

### View Stored Data

```batch
.\VIEW_DATA.bat
```

Displays:

-   Collection statistics (document counts)
-   Recent sensor readings
-   Model training metrics
-   Anomaly detection results

### MongoDB Direct Access

```bash
docker exec -it mongodb mongosh
use iot_analytics
db.device_data.countDocuments()
db.device_data.find().limit(5).pretty()
exit
```

## Operational Commands

### Shutdown All Services

```batch
.\STOP.bat
```

Cleanly terminates:

-   Python service processes
-   Kafka containers
-   Superset container
-   MongoDB container (removed for clean restart)

### Service-Level Control

```powershell
# Manual service startup (if needed)
cd source\orchestration

# Terminal 1: Global Server
python start_global_server.py

# Terminal 2: Data Streaming
python start_streaming.py

# Terminal 3: Flink Processing
python start_flink.py

# Terminal 4: Spark Analytics
python start_spark_jobs.py
```

## Troubleshooting

### Container Conflicts

```batch
.\STOP.bat
.\RUN.bat
```

### MongoDB Connection Issues

```batch
docker ps | findstr mongodb
docker exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### Service Not Responding

-   Verify initialization completed (2-3 minutes required)
-   Check Docker Desktop is running
-   Ensure ports 8000, 8080, 8088, 9092, 27017 are available

### View Logs

```batch
Get-Content source\logs\pipeline.log -Tail 50
Get-Content source\logs\global_server.log -Tail 50
```

## Project Structure

```
project/
├── RUN.bat                    # Automated startup
├── STOP.bat                   # Clean shutdown
├── CHECK_STATUS.bat           # Health check
├── VIEW_DATA.bat              # MongoDB viewer
├── STREAMING_EXPLAINED.md     # Pipeline details
├── VIEW_MONGODB_GUIDE.md      # Database queries
└── source/
    ├── data/                  # Dataset (raw + processed)
    ├── kafka/                 # Streaming configuration
    ├── flink/                 # Stream processing
    ├── spark/                 # Analytics jobs
    ├── models/                # ML models (local + global)
    ├── global_server/         # FastAPI application
    ├── storage/               # MongoDB integration
    ├── visualization/         # Superset configuration
    ├── orchestration/         # Service launchers
    ├── config/                # System configuration
    └── logs/                  # Application logs
```

## MongoDB Collections Schema

### device_data

Stores raw sensor readings from streaming pipeline

```json
{
    "device_id": "device_001",
    "timestamp": "2004-02-28T00:00:03",
    "temperature": 19.9884,
    "humidity": 37.0933,
    "light": 45.08,
    "voltage": 2.69964
}
```

### local_models

Per-device model weights and training metrics

```json
{
  "device_id": "device_001",
  "model_weights": {...},
  "accuracy": 0.95,
  "sample_count": 2400,
  "timestamp": "2025-10-16T..."
}
```

### global_model

Aggregated federated learning model

```json
{
  "aggregation_round": 5,
  "num_devices": 53,
  "global_accuracy": 0.94,
  "aggregated_weights": {...},
  "timestamp": "2025-10-16T..."
}
```

### predictions

Model inference results and anomaly flags

```json
{
    "device_id": "device_001",
    "prediction": 19.5,
    "actual_value": 19.8,
    "is_anomaly": false,
    "confidence": 0.92,
    "timestamp": "2025-10-16T..."
}
```

## Dataset Information

**Source:** Intel Berkeley Research Lab  
**URL:** http://db.csail.mit.edu/labdata/data.txt  
**Records:** 152,533 validated sensor readings  
**Devices:** 54 Mica2Dot sensor nodes  
**Duration:** ~80 minutes of data  
**Date:** February 28, 2004  
**Sensors:** Temperature, Humidity, Light, Voltage

## Next Steps

1. Start pipeline: `.\RUN.bat`
2. Verify streaming: http://localhost:8080 (Kafka UI)
3. Check API status: http://localhost:8000/docs
4. View dashboards: http://localhost:8088 (Superset)
5. Monitor data: `.\VIEW_DATA.bat`

For detailed streaming configuration, see `STREAMING_EXPLAINED.md`  
For database queries, see `VIEW_MONGODB_GUIDE.md`
