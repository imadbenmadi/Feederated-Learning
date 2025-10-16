# TROUBLESHOOTING GUIDE

## Current Issues and Fixes

### Issue 1: Missing Python Packages ❌

**Error:** `ModuleNotFoundError: No module named 'pymongo'`

**Solution:**

```bash
# Install all required packages
pip install pymongo kafka-python numpy pandas fastapi uvicorn pydantic requests schedule
```

### Issue 2: Docker Desktop Not Running ❌

**Error:** `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**Solution:**

1. Open Docker Desktop application
2. Wait for it to fully start (you'll see "Docker Desktop is running" in system tray)
3. Verify with: `docker ps`
4. Then restart the pipeline

### Issue 3: Data Preprocessing Fixed ✅

The preprocessing script has been fixed to handle the Intel Lab data format correctly.

---

## Step-by-Step Setup (Windows)

### Step 1: Install Python Packages

```powershell
# Navigate to project directory
cd C:\Users\imadb\OneDrive\Bureau\ostds\source

# Install all dependencies
pip install numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule pyyaml python-dotenv
```

### Step 2: Start Docker Desktop

1. **Open Docker Desktop** from Start Menu
2. **Wait** until you see "Docker Desktop is running"
3. **Verify** by running:
    ```powershell
    docker --version
    docker ps
    ```

### Step 3: Install and Start MongoDB

**Option A: Install MongoDB Community Edition**

1. Download from: https://www.mongodb.com/try/download/community
2. Install with default settings
3. Start MongoDB:
    ```powershell
    # MongoDB should start automatically, or run:
    net start MongoDB
    ```

**Option B: Use MongoDB in Docker**

```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Verify MongoDB:**

```powershell
# Test connection
mongosh
# Or
mongo
```

### Step 4: Re-process Data

```powershell
# Clean up old data
Remove-Item data\raw\intel_lab_data.csv
Remove-Item data\processed\processed_iot_data.csv

# Download and process again
python data\download_dataset.py
python data\preprocess_dataset.py
```

Expected output:

```
✓ Loaded 152542 records
✓ Removed X rows with missing values
✓ Final dataset: ~150000 valid records
```

### Step 5: Start Kafka

```powershell
cd kafka
docker-compose up -d
timeout /t 15
cd ..
```

Verify at: http://localhost:8080

### Step 6: Initialize MongoDB

```powershell
python storage\mongodb_init.py
```

### Step 7: Start Services

**Terminal 1 - Global Server:**

```powershell
python orchestration\start_global_server.py
```

Verify at: http://localhost:8000/docs

**Terminal 2 - Kafka Producer:**

```powershell
python orchestration\start_streaming.py
```

**Terminal 3 - Test Consumer:**

```powershell
python kafka\kafka_consumer_test.py
```

---

## Verification Checklist ✅

-   [ ] Python packages installed: `pip list | findstr pymongo`
-   [ ] Docker Desktop running: `docker ps`
-   [ ] MongoDB running: `mongosh` or `mongo`
-   [ ] Data processed: Check `data\processed\processed_iot_data.csv` exists
-   [ ] Kafka running: http://localhost:8080
-   [ ] Global Server running: http://localhost:8000/docs
-   [ ] Data streaming: See messages in consumer test

---

## Quick Fix Commands

### If Kafka won't start:

```powershell
cd kafka
docker-compose down
docker-compose up -d
```

### If ports are in use:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>
```

### If MongoDB connection fails:

```powershell
# Check if MongoDB is running
net start | findstr MongoDB

# Start MongoDB service
net start MongoDB
```

### If data processing fails:

```powershell
# Delete old files and retry
Remove-Item data\raw\intel_lab_data.csv -Force
Remove-Item data\processed\processed_iot_data.csv -Force
python data\download_dataset.py
python data\preprocess_dataset.py
```

---

## Testing Everything Works

### Test 1: Check Data

```powershell
python -c "import pandas as pd; df = pd.read_csv('data/processed/processed_iot_data.csv'); print(f'Records: {len(df)}'); print(df.head())"
```

### Test 2: Check Kafka

```powershell
# Should show Kafka containers running
docker ps
```

### Test 3: Check MongoDB

```powershell
mongosh --eval "db.adminCommand('ping')"
```

### Test 4: Check Global Server

```powershell
# In browser or:
curl http://localhost:8000/api/status
```

---

## Common Errors and Solutions

| Error                       | Solution                         |
| --------------------------- | -------------------------------- |
| `ModuleNotFoundError`       | Run: `pip install <module-name>` |
| Docker pipe error           | Start Docker Desktop             |
| MongoDB connection error    | Start MongoDB service            |
| Port already in use         | Kill process or change port      |
| No data after preprocessing | Run fixed preprocessing script   |
| Kafka timeout               | Wait 30 seconds after starting   |

---

## Need More Help?

1. Check logs in `logs/` directory
2. Review error messages carefully
3. Verify all prerequisites are installed
4. Try running components individually
5. Check firewall/antivirus settings
