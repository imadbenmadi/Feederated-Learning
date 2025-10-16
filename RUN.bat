@echo off
title IoT Pipeline Startup

echo.
echo ========================================
echo  IoT STREAMING ML PIPELINE
echo ========================================
echo.

cd /d "%~dp0source"

echo [1/7] Checking Docker...
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Desktop is not running!
    pause
    exit /b 1
)
echo [OK] Docker is running

echo.
echo [2/8] Installing Python packages...
echo Installing core packages (this may take 2-3 minutes)...
pip install --quiet --upgrade pip
pip install numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule
echo [OK] Core packages installed
echo.
echo Note: Skipping pyspark and apache-flink (optional, very large packages)
echo Install manually if needed: pip install pyspark apache-flink

echo.
echo [3/8] Setting up MongoDB...
REM Stop and remove existing MongoDB container if it exists
docker stop mongodb >nul 2>&1
docker rm mongodb >nul 2>&1

REM Create network if it doesn't exist
docker network create iot-network >nul 2>&1

REM Start fresh MongoDB container
echo Starting MongoDB...
docker run -d -p 27017:27017 --name mongodb --network iot-network mongo:latest
echo Waiting 10 seconds for MongoDB to initialize...
timeout /t 10 /nobreak >nul
echo [OK] MongoDB ready

echo.
echo [4/8] Processing data...
if exist "data\processed\processed_iot_data.csv" (
    echo [OK] Data already processed
) else (
    cd data
    python download_dataset.py
    python preprocess_dataset.py
    cd ..
    echo [OK] Data processed
)

echo.
echo [5/8] Starting Kafka...
cd kafka
docker-compose up -d
echo Waiting 20 seconds for Kafka to initialize...
timeout /t 20 /nobreak >nul
cd ..
echo [OK] Kafka ready

echo.
echo [6/8] Initializing MongoDB...
python storage\mongodb_init.py
echo [OK] MongoDB initialized

echo.
echo [7/8] Starting Superset Visualization...
cd visualization
docker-compose up -d
echo Waiting 30 seconds for Superset to initialize...
timeout /t 30 /nobreak >nul
cd ..
echo [OK] Superset ready

echo.
echo [8/8] Starting services...
del /s /q *.pyc >nul 2>&1
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

start /min "Global Server" cmd /c "cd /d %CD%\orchestration && python start_global_server.py"
timeout /t 3 /nobreak >nul

start /min "Kafka Producer" cmd /c "cd /d %CD%\orchestration && python start_streaming.py"
timeout /t 2 /nobreak >nul

start /min "Flink Job" cmd /c "cd /d %CD%\orchestration && python start_flink.py"
timeout /t 2 /nobreak >nul

start /min "Spark Jobs" cmd /c "cd /d %CD%\orchestration && python start_spark_jobs.py"
timeout /t 2 /nobreak >nul

echo.
echo Waiting for all services to stabilize...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo  ALL SERVICES STARTED!
echo ========================================
echo.
echo  Kafka UI:         http://localhost:8080
echo  API Docs:         http://localhost:8000/docs
echo  Superset:         http://localhost:8088
echo.
echo  Superset Login:
echo  - Username: admin
echo  - Password: admin
echo.
echo  Services Running:
echo  - MongoDB (port 27017)
echo  - Kafka + Zookeeper
echo  - Superset Dashboard
echo  - Global Model Server
echo  - Kafka Producer (Data Streaming)
echo  - Flink Job
echo  - Spark Jobs (Batch + Streaming Analysis)
echo.
echo Opening browsers...
timeout /t 3 /nobreak >nul
start http://localhost:8080
start http://localhost:8000/docs
start http://localhost:8088
echo.
pause
