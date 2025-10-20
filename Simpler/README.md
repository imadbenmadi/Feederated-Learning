# Simplified IoT Federated Learning Pipeline

**Development Version for Team Collaboration**

---

## Overview

This is a **simplified, modular version** of the IoT Federated Learning pipeline designed for development and team collaboration. Each component can be developed and tested independently.

### Key Differences from Main Pipeline

-   **Simplified Architecture**: Uses only sklearn (no TensorFlow/PyTorch)
-   **Minimal Docker**: Only MongoDB required (no Kafka, Spark, Flink)
-   **Individual Testing**: Each component has its own test script
-   **No Streaming**: Batch processing for easier debugging
-   **Team-Oriented**: Clear separation for team assignments

---

## Team Assignments

### **SU YOUNG & ROBERT**

-   **Components**: Data Ingestion + Preprocessing + Analytics
-   **Scripts**:
    -   `scripts/1_data_ingestion.py`
    -   `scripts/1_preprocessing.py`
    -   `scripts/4_analytics.py`
-   **Tests**:
    -   `tests/1_TEST_DATA.bat`
    -   `tests/2_TEST_PREPROCESSING.bat`
    -   `tests/5_TEST_ANALYTICS.bat`

### **IMED & AMIR**

-   **Components**: Local Training + Federated Aggregation
-   **Scripts**:
    -   `scripts/2_local_training.py`
    -   `scripts/3_aggregation.py`
-   **Tests**:
    -   `tests/3_TEST_TRAINING.bat`
    -   `tests/4_TEST_AGGREGATION.bat`

### **YUSIF & AMIR**

-   **Components**: Visualization + Dashboard
-   **Scripts**:
    -   `scripts/5_visualization.py`
-   **Tests**:
    -   `tests/6_TEST_VISUALIZATION.bat`

---

## Quick Start

### Prerequisites

-   **Python 3.8+**
-   **Docker Desktop** (for MongoDB)
-   **pip** installed

### Installation

1. **Install Python Dependencies**

    ```bash
    cd
    pip install -r requirements.txt
    ```

2. **Start MongoDB** (required for analytics only)

    ```bash
    docker run -d --name mongodb_simple -p 27017:27017 mongo:latest
    ```

3. **Run Complete Pipeline**
    ```bash
    RUN_ALL.bat
    ```

### Individual Component Testing

Test each component separately during development:

```bash
# Data ingestion
cd tests
1_TEST_DATA.bat

# Preprocessing
2_TEST_PREPROCESSING.bat

# Local training
3_TEST_TRAINING.bat

# Federated aggregation
4_TEST_AGGREGATION.bat

# Analytics (requires MongoDB)
5_TEST_ANALYTICS.bat

# Visualization
6_TEST_VISUALIZATION.bat
```

---

## Project Structure

```
/
├── RUN_ALL.bat              # Run complete pipeline
├── STOP_ALL.bat             # Stop services & cleanup
├── README.md                # This file
├── requirements.txt         # Python dependencies
│
├── config/
│   └── settings.json        # Configuration (paths, training params)
│
├── scripts/
│   ├── 1_data_ingestion.py      # Download Intel Lab dataset
│   ├── 1_preprocessing.py       # Clean data, remove outliers
│   ├── 2_local_training.py      # Train per-device models
│   ├── 3_aggregation.py         # FedAvg aggregation
│   ├── 4_analytics.py           # MongoDB storage & analytics
│   └── 5_visualization.py       # Dashboard & charts
│
├── tests/
│   ├── 1_TEST_DATA.bat
│   ├── 2_TEST_PREPROCESSING.bat
│   ├── 3_TEST_TRAINING.bat
│   ├── 4_TEST_AGGREGATION.bat
│   ├── 5_TEST_ANALYTICS.bat
│   └── 6_TEST_VISUALIZATION.bat
│
├── data/
│   ├── raw/                 # Downloaded datasets
│   └── processed/           # Cleaned data
│
├── models/
│   ├── local/               # Per-device models (.pkl)
│   └── global/              # Aggregated global model
│
└── outputs/
    ├── analytics/           # Analytics reports (JSON)
    └── visualizations/      # Charts & dashboards (PNG)
```

---

## Configuration

Edit `config/settings.json`:

```json
{
    "data": {
        "raw_dir": "data/raw",
        "processed_dir": "data/processed"
    },
    "training": {
        "hidden_layers": [64, 32],
        "epochs": 100,
        "learning_rate": 0.001,
        "test_split": 0.2
    },
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "database": "iot_federated"
    }
}
```

---

## Component Details

### Component 1: Data Ingestion (`1_data_ingestion.py`)

-   Downloads the dataset
-   Converts to CSV format
-   **Output**: `data/raw/intel_lab_data.csv`
-   **Team**: SU YOUNG, ROBERT

### Component 2: Preprocessing (`1_preprocessing.py`)

-   Removes outliers 
-   Adds derived features (hour, day_of_week)
-   **Output**: `data/processed/processed_iot_data.csv`
-   **Team**: SU YOUNG, ROBERT

### Component 3: Local Training (`2_local_training.py`)

-   Trains sklearn MLPRegressor per device
-   Predicts temperature from other sensors
-   **Output**: `models/local/{device_id}.pkl` files
-   **Team**: IMED, AMIR

### Component 4: Federated Aggregation (`3_aggregation.py`)

-   Implements FedAvg algorithm
-   Weighted averaging by sample count
-   **Output**: `models/global/global_model.pkl`
-   **Team**: IMED, AMIR

### Component 5: Analytics (`4_analytics.py`)

-   Stores data in MongoDB
-   Device statistics
-   Anomaly detection
-   **Output**: `outputs/analytics/analytics_report.json`
-   **Team**: SU YOUNG, ROBERT

### Component 6: Visualization (`5_visualization.py`)

-   9-panel dashboard
-   Sensor distributions, model performance, summary stats
-   **Output**: `outputs/visualizations/dashboard.png`
-   **Team**: YUSIF, AMIR

---

## Pipeline Execution Order

```
1. Data Ingestion
   └─> downloads dataset to data/raw/

2. Preprocessing
   └─> cleans data to data/processed/

3. Local Training
   └─> trains models to models/local/

4. Federated Aggregation
   └─> creates global model in models/global/

5. Analytics (requires MongoDB)
   └─> stores in MongoDB + generates report

6. Visualization
   └─> creates dashboard PNG
```

---

## Run the project

1. Ensure MongoDB is running:

    ```bash
    docker ps | findstr mongodb_simple
    ```

2. Run complete pipeline:

    ```bash
    RUN_ALL.bat
    ```


---

## Stopping & Cleanup

### Stop Everything

```bash
STOP_ALL.bat
```

### Stop MongoDb Manualy

```bash
docker stop mongodb_simple
docker rm mongodb_simple
```

### Clean Generated Files

```bash
# Delete all outputs (optional)
rmdir /s /q data\raw
rmdir /s /q data\processed
rmdir /s /q models\local
rmdir /s /q models\global
rmdir /s /q outputs
```
