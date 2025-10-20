## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    SIMPLIFIED IoT PIPELINE                       │
│                     (Development Version)                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Dataset         │  
│                  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 1: DATA INGESTION                                     │
│ Team: SU YOUNG, ROBERT                                          │
│ File: 1_data_ingestion.py                                       │
│ Test: 1_TEST_DATA.bat                                           │
├─────────────────────────────────────────────────────────────────┤
│ • Downloads dataset from web                                    │
│ • Converts to CSV format                                        │
│ • Saves to data/raw/                                            │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 2: PREPROCESSING                                      │
│ Team: SU YOUNG, ROBERT                                          │
│ File: 1_preprocessing.py                                        │
│ Test: 2_TEST_PREPROCESSING.bat                                  │
├─────────────────────────────────────────────────────────────────┤
│ • Removes outliers                                              │
│ • Adds derived features (hour, day_of_week)                     │
│ • Normalizes data                                               │
│ • Saves to data/processed/                                      │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 3: LOCAL TRAINING                                     │
│ Team: IMED, AMIR                                                │
│ File: 2_local_training.py                                       │
│ Test: 3_TEST_TRAINING.bat                                       │
├─────────────────────────────────────────────────────────────────┤
│ • Splits data by device (54 devices)                            │
│ • Trains MLPRegressor per device                                │
│ • Evaluates on test set (R² score)                              │
│ • Saves models as .pkl files                                    │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 4: FEDERATED AGGREGATION                              │
│ Team: IMED, AMIR                                                │
│ File: 3_aggregation.py                                          │
│ Test: 4_TEST_AGGREGATION.bat                                    │
├─────────────────────────────────────────────────────────────────┤
│ • Loads all local models                                        │
│ • Implements FedAvg algorithm                                   │
│ • Weighted averaging by sample count                            │
│ • Creates global model                                          │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 5: ANALYTICS                                          │
│ Team: SU YOUNG, ROBERT                                          │
│ File: 4_analytics.py                                            │
│ Test: 5_TEST_ANALYTICS.bat                                      │
├─────────────────────────────────────────────────────────────────┤
│ • Stores data in MongoDB                                        │
│ • Computes device statistics                                    │
│ • Detects anomalies (threshold-based)                           │
│ • Generates JSON report                                         │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPONENT 6: VISUALIZATION                                      │
│ Team: YUSIF, AMIR                                               │
│ File: 5_visualization.py                                        │
│ Test: 6_TEST_VISUALIZATION.bat                                  │
├─────────────────────────────────────────────────────────────────┤
│ • Loads data and models                                         │
│ • Creates 9-panel dashboard                                     │
│ • Sensor distributions, model performance                       │
│ • Saves as PNG image                                            │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
    ┌────────┐
    │ OUTPUTS│
    └────────┘
```

---

## File System Layout

```
/
│
├──  SETUP.bat                    ← Run this first!
├──  RUN_ALL.bat                  ← Run complete pipeline
├──  STOP_ALL.bat                 ← Stop services
├──  README.md                    ← Full documentation
├──  GETTING_STARTED.md           ← Quick start guide
├──  requirements.txt             ← Python dependencies
│
├── 📁 config/
│   └──  settings.json            ← Configuration
│
├── 📁 scripts/                     ← YOUR CODE HERE
│   ├──  1_data_ingestion.py      ← SU YOUNG, ROBERT
│   ├──  1_preprocessing.py       ← SU YOUNG, ROBERT
│   ├──  2_local_training.py      ← IMED, AMIR
│   ├──  3_aggregation.py         ← IMED, AMIR
│   ├──  4_analytics.py           ← SU YOUNG, ROBERT
│   └──  5_visualization.py       ← YUSIF, AMIR
│
├── 📁 tests/                       ← RUN TESTS HERE
│   ├──  1_TEST_DATA.bat
│   ├──  2_TEST_PREPROCESSING.bat
│   ├──  3_TEST_TRAINING.bat
│   ├──  4_TEST_AGGREGATION.bat
│   ├──  5_TEST_ANALYTICS.bat
│   └──  6_TEST_VISUALIZATION.bat
│
├── 📁 data/
│   ├── 📁 raw/                     ← Downloaded data
│   │   └── intel_lab_data.csv      (152,533 records)
│   └── 📁 processed/               ← Cleaned data
│       └── processed_iot_data.csv  (ready for ML)
│
├── 📁 models/
│   ├── 📁 local/                   ← Per-device models
│   │   ├── device_1.pkl
│   │   ├── device_2.pkl
│   │   └── ... (54 files)
│   └── 📁 global/                  ← Federated model
│       └── global_model.pkl
│
└── 📁 outputs/
    ├── 📁 analytics/               ← Analytics reports
    │   └── analytics_report.json
    └── 📁 visualizations/          ← Charts & dashboards
        └── dashboard.png
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         DATA FLOW                            │
└─────────────────────────────────────────────────────────────┘

Raw Dataset
    ↓
[Download] → data/raw/intel_lab_data.csv
    ↓
[Clean] → data/processed/processed_iot_data.csv
    ↓
[Split by Device] → 54 device-specific datasets
    ↓
    ├─→ Device 1 → Train → models/local/device_1.pkl
    ├─→ Device 2 → Train → models/local/device_2.pkl
    ├─→ Device 3 → Train → models/local/device_3.pkl
    └─→ ... (54 devices total)
    ↓
[FedAvg Aggregation] → models/global/global_model.pkl
    ↓
    ├─→ [MongoDB Storage] → Collections in database
    └─→ [Visualization] → outputs/visualizations/dashboard.png
```


## Commands Reference

```bash
# Setup (first time)
cd
SETUP.bat

# Start MongoDB
docker run -d --name mongodb_simple -p 27017:27017 mongo:latest

# Run complete pipeline
RUN_ALL.bat

# Test individual component
cd tests
1_TEST_DATA.bat               # Data ingestion
2_TEST_PREPROCESSING.bat      # Preprocessing
3_TEST_TRAINING.bat           # Local training
4_TEST_AGGREGATION.bat        # FedAvg aggregation
5_TEST_ANALYTICS.bat          # Analytics
6_TEST_VISUALIZATION.bat      # Visualization

# Stop everything
cd ..
STOP_ALL.bat

# Check MongoDB status
docker ps | findstr mongodb_simple

# View MongoDB logs
docker logs mongodb_simple
```
