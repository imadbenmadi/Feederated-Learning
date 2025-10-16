# 🔧 IMMEDIATE FIX GUIDE

## Your Current Issues:

1. ❌ **Data preprocessing failed** - All rows removed as missing values
2. ❌ **Docker not running** - Cannot start Kafka
3. ❌ **Python packages missing** - pymongo not installed
4. ❌ **Localhost links not working** - Services not actually running

---

## QUICK FIX (5 Steps)

### Step 1: Run the Fix Script ⚡

```powershell
cd C:\Users\imadb\OneDrive\Bureau\ostds\source
.\SETUP_FIX.bat
```

**Or follow manual steps below:**

---

### Step 2: Install Missing Packages ⚡

```powershell
pip install numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule pyyaml python-dotenv
```

---

### Step 3: Start Docker Desktop ⚡

1. **Open Docker Desktop** from Windows Start Menu
2. **Wait** until bottom-left shows green "Docker Desktop is running"
3. **Verify** in PowerShell:
    ```powershell
    docker ps
    ```
    Should show: `CONTAINER ID   IMAGE   ...` (even if empty)

---

### Step 4: Install MongoDB ⚡

**EASIEST: Use Docker**

```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**OR: Download MongoDB**

-   Go to: https://www.mongodb.com/try/download/community
-   Download MongoDB 7.0 for Windows
-   Install with default settings
-   It will auto-start

**Verify MongoDB:**

```powershell
# Try this first
mongo --version

# Or this
mongosh --version

# Test connection
mongosh
# Type: exit
```

---

### Step 5: Reprocess Data ⚡

```powershell
# Delete old files
Remove-Item data\raw\intel_lab_data.csv -Force
Remove-Item data\processed\processed_iot_data.csv -Force

# Redownload and process
python data\download_dataset.py
python data\preprocess_dataset.py
```

**Expected Success Output:**

```
✓ Loaded 152542 records
✓ Removed X rows with missing values
✓ Final dataset: ~150000 valid records  ← Should be > 0
✓ Processed data saved
```

---

## ✅ VERIFICATION

After the fixes above, verify everything:

### 1. Check Docker

```powershell
docker ps
# Should show running containers (or at least no error)
```

### 2. Check MongoDB

```powershell
mongosh
# Should connect without error
# Type: exit
```

### 3. Check Data

```powershell
python -c "import pandas as pd; df = pd.read_csv('data/processed/processed_iot_data.csv'); print(f'✓ Records: {len(df)}')"
# Should show: ✓ Records: 150000 (approximately)
```

### 4. Check Packages

```powershell
python -c "import pymongo, kafka, pandas, numpy, fastapi; print('✓ All packages installed')"
```

---

## 🎯 NOW START THE PIPELINE

### Terminal 1: Start Kafka

```powershell
cd kafka
docker-compose up -d
cd ..
# Wait 15 seconds
```

**Verify:** Open http://localhost:8080 in browser

### Terminal 2: Initialize MongoDB

```powershell
python storage\mongodb_init.py
```

**Expected:**

```
✓ Connected to MongoDB database: iot_analytics
✓ Collection created
```

### Terminal 3: Start Global Server

```powershell
python orchestration\start_global_server.py
```

**Verify:** Open http://localhost:8000/docs in browser

### Terminal 4: Start Streaming

```powershell
python orchestration\start_streaming.py
```

**Expected:**

```
Starting data stream...
Sent 100 records...
```

### Terminal 5: Test Consumer

```powershell
python kafka\kafka_consumer_test.py
```

**Expected:**

```
Message #10
  Device: device_001
  Temperature: 22.5°C
```

---

## 🌐 URLs That Should Work

After all services are running:

| Service       | URL                        | What You Should See  |
| ------------- | -------------------------- | -------------------- |
| Kafka UI      | http://localhost:8080      | Kafka dashboard      |
| Global Server | http://localhost:8000      | JSON response        |
| API Docs      | http://localhost:8000/docs | Interactive API docs |

---

## 🐛 Still Not Working?

### Error: "Docker daemon not running"

**Fix:**

1. Restart Docker Desktop
2. Wait 1 minute
3. Try: `docker ps`

### Error: "Cannot connect to MongoDB"

**Fix:**

```powershell
# Using Docker MongoDB
docker start mongodb

# Using installed MongoDB
net start MongoDB
```

### Error: "Port already in use"

**Fix:**

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill it (replace XXXX with PID number)
taskkill /F /PID XXXX
```

### Error: "Still no data after preprocessing"

**Fix:**
Check the raw data file manually:

```powershell
# Show first 5 lines
Get-Content data\raw\intel_lab_data.txt | Select-Object -First 5
```

The data should look like:

```
2004-02-28 00:59:16.02785 1 1 19.9884 37.0933 45.08 2.69964
```

---

## 📞 Get Help

If you're still stuck, share:

1. Output of: `docker ps`
2. Output of: `pip list | findstr -i "kafka mongo pandas"`
3. Output of: `python data\preprocess_dataset.py`
4. Screenshot of any error messages

---

## ⚡ TL;DR - Fastest Fix

```powershell
# Run this one script
.\SETUP_FIX.bat
```

Then manually start MongoDB if needed, and open 3 terminals:

```powershell
# Terminal 1
python orchestration\start_global_server.py

# Terminal 2
python orchestration\start_streaming.py

# Terminal 3
python kafka\kafka_consumer_test.py
```

---

**The main issues were:**

1. ✅ **Fixed:** Data preprocessing script (now handles Intel Lab format)
2. ⚠️ **Action needed:** Start Docker Desktop
3. ⚠️ **Action needed:** Install missing Python packages
4. ⚠️ **Action needed:** Install/start MongoDB

After these fixes, the localhost links will work! 🎉
