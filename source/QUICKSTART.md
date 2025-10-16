# Quick Start Guide

## Get Up and Running in 10 Minutes

This guide will help you get the IoT Streaming ML Pipeline running quickly.

### Prerequisites Checklist

-   [ ] Python 3.8+ installed
-   [ ] Docker installed and running
-   [ ] MongoDB installed
-   [ ] At least 8GB RAM available

### Step-by-Step Instructions

#### 1. Install Dependencies (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

#### 2. Download and Prepare Data (3 minutes)

```bash
# Download Intel Lab dataset
python data/download_dataset.py

# Preprocess the data
python data/preprocess_dataset.py
```

Expected output:

```
✓ Dataset downloaded successfully
✓ Loaded 2,313,153 records
✓ Processed data saved
```

#### 3. Start Kafka (2 minutes)

```bash
cd kafka
docker-compose up -d
cd ..
```

Wait about 15 seconds for Kafka to fully start.

Verify at: http://localhost:8080 (Kafka UI)

#### 4. Initialize MongoDB (1 minute)

Make sure MongoDB is running:

```bash
# Check if MongoDB is running
mongod --version
```

Initialize collections:

```bash
python storage/mongodb_init.py
```

Expected output:

```
✓ Connected to MongoDB database: iot_analytics
✓ All collections initialized
```

#### 5. Start the Pipeline (2 minutes)

Open **3 separate terminals** and run:

**Terminal 1 - Global Model Server:**

```bash
python orchestration/start_global_server.py
```

**Terminal 2 - Data Streaming:**

```bash
python orchestration/start_streaming.py
```

**Terminal 3 - Monitor (Optional):**

```bash
python kafka/kafka_consumer_test.py
```

### 🎉 You're Running!

The pipeline is now:

-   ✅ Streaming IoT data through Kafka
-   ✅ Accepting local model updates
-   ✅ Ready for analytics

### What's Happening?

1. **Kafka Producer** is reading the dataset and sending sensor readings to the `iot_stream` topic
2. **Global Server** is waiting to receive model updates from devices
3. Data is continuously looping to simulate real-time IoT sensors

### Next Steps

#### Run Batch Analysis

```bash
python spark/spark_batch_analysis.py
```

This will:

-   Load the global model
-   Evaluate predictions on the full dataset
-   Save results to MongoDB

#### View Results in MongoDB

```bash
mongo
use iot_analytics
db.predictions.find().limit(5).pretty()
```

#### Access API Documentation

Open browser: http://localhost:8000/docs

Available endpoints:

-   `POST /api/local-update` - Receive model updates
-   `GET /api/global-model` - Get current global model
-   `GET /api/status` - View system status
-   `POST /api/aggregate` - Trigger manual aggregation

### Stopping the Pipeline

```bash
# Stop Kafka
cd kafka
docker-compose down

# Stop Python processes
# Press Ctrl+C in each terminal
```

Or use the stop script:

```bash
./orchestration/stop_all.sh
```

### Troubleshooting

#### Kafka won't start

```bash
# Check Docker
docker ps

# Restart Docker Desktop
```

#### MongoDB connection error

```bash
# Start MongoDB
mongod

# Or on Linux:
sudo systemctl start mongod
```

#### Port already in use

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Kill the process
```

### Configuration Quick Tips

Edit these files to customize:

-   `config/project_config.yaml` - Main settings
-   `kafka/config/kafka_config.json` - Streaming parameters
-   `config/environment.env` - Environment variables

### Viewing Logs

```bash
# View all logs
tail -f logs/pipeline.log

# Or check individual component logs
```

### Testing Everything Works

Run this test command:

```bash
# Test Kafka consumer
python kafka/kafka_consumer_test.py
```

You should see messages like:

```
Message #10
  Device: device_001
  Temperature: 22.5°C
  Humidity: 45.0%
```

### Getting Help

-   Check the full README.md for detailed documentation
-   View API docs at http://localhost:8000/docs
-   Check logs in the `logs/` directory

---

**Congratulations! Your IoT ML Pipeline is running! 🎊**
