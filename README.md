# IoT Streaming ML Pipeline with Federated Learning

## FLEAD: Federated Deep Learning for IoT-Based Anomaly Detection in Real-Time Monitoring

A comprehensive end-to-end IoT data processing and analytics pipeline that simulates live streaming from IoT devices, performs per-device local model training using federated learning, aggregates these into a global model, and evaluates data with batch and streaming analytics.

![Architecture Diagram](architecture_diagram.png)

## Table of Contents

-   [Overview](#overview)
-   [Architecture](#architecture)
-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [Quick Start](#quick-start)
-   [Components](#components)
-   [Usage](#usage)
-   [Configuration](#configuration)
-   [Monitoring](#monitoring)
-   [Troubleshooting](#troubleshooting)
-   [Contributing](#contributing)
-   [License](#license)

## Overview

This project implements a complete IoT analytics pipeline with the following capabilities:

-   **Real-time Data Streaming**: Simulates live IoT sensor data using Apache Kafka
-   **Federated Learning**: Per-device local neural networks with global model aggregation
-   **Distributed Processing**: Apache Flink for stream processing, Apache Spark for analytics
-   **Data Storage**: MongoDB for flexible document storage
-   **Visualization**: Apache Superset for interactive dashboards

## Architecture

### System Components

1. **Data Ingestion Layer**

    - Intel Lab IoT Dataset (temperature, humidity, light, voltage sensors)
    - Kafka Producer for continuous streaming

2. **Stream Processing Layer**

    - Apache Kafka for message brokering
    - Apache Flink for per-device model training
    - Local neural networks (one per device)

3. **Federated Learning Layer**

    - Global Model Server (FastAPI)
    - FedAvg aggregation algorithm
    - Periodic model synchronization

4. **Analytics Layer**

    - Apache Spark for batch and streaming analysis
    - Global model evaluation
    - Anomaly detection

5. **Storage Layer**

    - MongoDB for all data, models, and predictions

6. **Visualization Layer**
    - Apache Superset for dashboards
    - Per-device and global metrics

### Data Flow

```
IoT Data (152K records, loops forever)
    ↓ 10 records/sec
Kafka (iot_stream topic)
    ↓ Real-time processing
Flink (Per-device training every 30 sec)
    ↓ Model updates
Global Server (Aggregation every 1 minute)
    ↓ Storage
MongoDB (4 collections growing continuously)
    ↓ Analytics
Spark (Batch + Streaming)
    ↓ Visualization
Superset Dashboard
```

## Features

-   **Continuous Streaming**: Automatically loops dataset to simulate real-time IoT data
-   **Dynamic Device Handling**: Automatically creates models for new devices
-   **Incremental Learning**: Models train continuously on streaming data
-   **Federated Aggregation**: Privacy-preserving model updates using FedAvg
-   **Dual Analytics**: Both batch and streaming evaluation pipelines
-   **Anomaly Detection**: Automatic flagging of unusual sensor readings
-   **Scalable Architecture**: Modular design for easy expansion
-   **Comprehensive Monitoring**: Logs, metrics, and visualizations

## Installation

### 1. Clone the Repository

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Docker

Follow instructions at: https://docs.docker.com/get-docker/

### 5. Install MongoDB

Follow instructions at: https://docs.mongodb.com/manual/installation/

### 6. Install Apache Flink (Optional)

```bash
wget https://archive.apache.org/dist/flink/flink-1.17.0/flink-1.17.0-bin-scala_2.12.tgz
tar -xzf flink-1.17.0-bin-scala_2.12.tgz
export FLINK_HOME=/path/to/flink-1.17.0
```

### 7. Install Apache Spark (Optional)

```bash
wget https://archive.apache.org/dist/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz
tar -xzf spark-3.4.0-bin-hadoop3.tgz
export SPARK_HOME=/path/to/spark-3.4.0
```

## Quick Start

### Step 1: Download and Preprocess Data

```bash
# Download Intel Lab dataset
python data/download_dataset.py

# Preprocess the data
python data/preprocess_dataset.py
```

### Step 2: Start Kafka

```bash
cd kafka
docker-compose up -d
cd ..
```

Verify Kafka is running:

-   Kafka UI: http://localhost:8080

### Step 3: Initialize MongoDB

```bash
# Start MongoDB service
mongod

# Initialize collections
python storage/mongodb_init.py
```

### Step 4: Start Global Model Server

```bash
python orchestration/start_global_server.py
```

Access API documentation: http://localhost:8000/docs

### Step 5: Start Data Streaming

```bash
python orchestration/start_streaming.py
```

### Step 6: Run Analytics (Optional)

```bash
# Batch analysis
python spark/spark_batch_analysis.py

# Streaming analysis
python spark/spark_streaming_analysis.py
```

### Step 7: Start Visualization (Optional)

```bash
cd visualization
./superset_setup.sh
```

Access Superset: http://localhost:8088

## Components

### Data Processing

-   **download_dataset.py**: Downloads Intel Lab IoT dataset
-   **preprocess_dataset.py**: Cleans and prepares data for streaming

### Kafka Streaming

-   **kafka_producer.py**: Streams IoT data to Kafka
-   **kafka_consumer_test.py**: Tests Kafka consumer
-   **docker-compose.yml**: Kafka and Zookeeper setup

### Local Models

-   **model_template.py**: Feedforward neural network implementation
-   **model_utils.py**: Model utilities and federated averaging

### Flink Processing

-   **flink_job.py**: Main Flink streaming job
-   **flink_local_model_manager.py**: Per-device model management

### Global Server

-   **app.py**: FastAPI server for model aggregation
-   **global_model.py**: Global model management
-   **aggregator.py**: FedAvg implementation

### Spark Analytics

-   **spark_batch_analysis.py**: Batch evaluation
-   **spark_streaming_analysis.py**: Real-time evaluation

### Storage

-   **mongodb_connection.py**: Database connection manager
-   **mongodb_init.py**: Collection initialization
-   **schemas/**: JSON schemas for validation

### Visualization

-   **superset_setup.sh**: Superset installation
-   **dashboards/**: Dashboard configurations

## Configuration

### Project Configuration

Edit `config/project_config.yaml` to modify:

-   Kafka settings
-   Model hyperparameters
-   MongoDB connection
-   Aggregation intervals

### Environment Variables

Copy and edit `config/environment.env`:

```bash
cp config/environment.env .env
# Edit .env with your settings
```

### Kafka Configuration

Edit `kafka/config/kafka_config.json` for:

-   Bootstrap servers
-   Topic settings
-   Producer/consumer parameters

## Monitoring

### Kafka UI

View Kafka topics, messages, and consumer groups:

```
http://localhost:8080
```

### Global Server API

Monitor model aggregation:

```
http://localhost:8000/api/status
http://localhost:8000/api/history
```

### Logs

View logs in the `logs/` directory:

```bash
tail -f logs/pipeline.log
```

### MongoDB

Query collections directly:

```bash
mongo
use iot_analytics
db.predictions.find().limit(10)
```

## Troubleshooting

### Kafka Connection Issues

```bash
# Check if Kafka is running
docker ps

# Restart Kafka
cd kafka
docker-compose restart
```

### MongoDB Connection Issues

```bash
# Check MongoDB status
systemctl status mongod

# Restart MongoDB
systemctl restart mongod
```

### Model Training Issues

```bash
# Check global server logs
# Verify models are being saved
ls -la models/local/
ls -la models/global_model/
```

### Memory Issues

-   Reduce Spark batch size in config
-   Decrease Flink parallelism
-   Limit Kafka retention





## 📖 References

-   [Federated Learning: Collaborative Machine Learning without Centralized Training Data](https://ai.googleblog.com/2017/04/federated-learning-collaborative.html)
-   [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
-   [Apache Flink Documentation](https://flink.apache.org/documentation.html)
-   [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
-   [MongoDB Documentation](https://docs.mongodb.com/)

---

**Built with ❤️ for IoT and Machine Learning**
