## **DO THIS RIGHT NOW:**

### **Option 1: Automatic Fix (Recommended)**

Run this one command in PowerShell:

```powershell
cd C:\Users\imadb\OneDrive\Bureau\ostds\source
.\SETUP_FIX.bat
```

This will automatically:

-   Install all missing Python packages
-   Check Docker
-   Clean and reprocess data correctly
-   Start Kafka

### **Option 2: Manual Steps**

**Step 1:** Install packages

```powershell
pip install numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule
```

**Step 2:** Start Docker Desktop

-   Open Docker Desktop from Start Menu
-   Wait until it says "running"

**Step 3:** Install MongoDB

```powershell
# Easiest: Run MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Step 4:** Reprocess data

```powershell
python data\download_dataset.py
python data\preprocess_dataset.py
```

---

## ✅ **Then Start Services:**

Open 3 separate PowerShell windows:

**Window 1:**

```powershell
cd C:\Users\imadb\OneDrive\Bureau\ostds\source
python orchestration\start_global_server.py
```

**Window 2:**

```powershell
cd C:\Users\imadb\OneDrive\Bureau\ostds\source
python orchestration\start_streaming.py
```

**Window 3:**

```powershell
cd C:\Users\imadb\OneDrive\Bureau\ostds\source
python kafka\kafka_consumer_test.py
```

---

## **Then Your URLs Will Work:**

-   http://localhost:8080 (Kafka UI)
-   http://localhost:8000/docs (API Docs)

**The localhost links weren't working because the services weren't actually running due to the errors!**

Read the **FIX_NOW.md** file I created for detailed step-by-step instructions!

Made changes.
