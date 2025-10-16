# IoT Streaming ML Pipeline - Quick Start

## ONE-CLICK START

Simply double-click `RUN.bat` to start the entire pipeline!

### What it does:

1.  Checks Docker Desktop is running
2.  Installs Python dependencies
3.  Downloads and processes IoT data
4.  Starts Kafka + Zookeeper + Kafka UI
5.  Initializes MongoDB
6.  Starts FastAPI Global Server
7.  Starts Kafka streaming producer
8.  Starts Flink processing job
9.  Starts Spark analytics

### Access Points

After running `RUN.bat`, access:

-   **Kafka UI**: http://localhost:8080
-   **API Docs**: http://localhost:8000/docs
-   **API Status**: http://localhost:8000/api/status

## STOP ALL SERVICES

Double-click `STOP.bat` to stop everything cleanly.

## Manual Control

If you prefer manual control:

```powershell
# Start everything
cd source\orchestration
python start_global_server.py    # Terminal 1
python start_streaming.py         # Terminal 2
python start_flink.py             # Terminal 3
python start_spark_jobs.py        # Terminal 4
```

## Status Check

Run `CHECK_STATUS.bat` to see what's running and what needs to be fixed.

## Project Structure

```
ostds/
├── RUN.bat              ← START HERE!
├── STOP.bat             ← Stop all services
├── CHECK_STATUS.bat     ← Check system status
└── source/
    ├── data/            ← IoT sensor data
    ├── kafka/           ← Kafka configuration
    ├── models/          ← ML models (local + global)
    ├── global_server/   ← FastAPI server
    ├── flink/           ← Stream processing
    ├── spark/           ← Batch analytics
    ├── storage/         ← MongoDB integration
    └── orchestration/   ← Service startup scripts
```

## What This Pipeline Does

1. **Streams IoT Data**: Continuously sends sensor data to Kafka
2. **Processes in Real-Time**: Flink processes each message as it arrives
3. **Local Training**: Each device trains its own ML model
4. **Federated Learning**: Models are aggregated into a global model
5. **Analytics**: Spark provides batch and streaming analytics
6. **Monitoring**: Kafka UI shows real-time message flow
