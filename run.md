## **TO START THE APP:**

### **Option 1: Double-Click (Easiest)**

Simply double-click this file in Windows Explorer:

```
c:\Users\imadb\OneDrive\Bureau\ostds\RUN.bat
```

### **Option 2: From PowerShell/CMD**

```powershell
cd c:\Users\imadb\OneDrive\Bureau\ostds
.\RUN.bat
```

---

## 🛑 **TO STOP THE APP:**

### **Option 1: Double-Click (Easiest)**

Simply double-click this file in Windows Explorer:

```
c:\Users\imadb\OneDrive\Bureau\ostds\STOP.bat
```

### **Option 2: From PowerShell/CMD**

```powershell
cd c:\Users\imadb\OneDrive\Bureau\ostds
.\STOP.bat
```

---

## 📋 **WHAT EACH ONE DOES:**

### **RUN.bat starts:**

1. ✅ Checks if Docker Desktop is running
2. ✅ Installs Python dependencies
3. ✅ Starts MongoDB container
4. ✅ Downloads & processes IoT data (if not already done)
5. ✅ Starts Kafka + Zookeeper + Kafka UI
6. ✅ Initializes MongoDB collections
7. ✅ Starts Global Server (FastAPI) at http://localhost:8000
8. ✅ Starts Kafka Producer (streams IoT data)
9. ✅ Starts Flink processing job
10. ✅ Starts Spark analytics
11. ✅ Opens Kafka UI (http://localhost:8080) and API docs (http://localhost:8000/docs) in your browser

### **STOP.bat stops:**

1. 🛑 All Python services (Global Server, Kafka Producer, Flink, Spark)
2. 🛑 Kafka containers (Kafka, Zookeeper, Kafka UI)
3. 🛑 MongoDB container

---

## 🎯 **SIMPLE WORKFLOW:**

```
1. Make sure Docker Desktop is running (green icon in system tray)
2. Double-click RUN.bat
3. Wait ~30 seconds
4. Access http://localhost:8080 and http://localhost:8000/docs
5. When done, double-click STOP.bat
```
