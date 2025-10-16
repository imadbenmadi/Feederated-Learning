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
echo [2/7] Installing Python packages...
pip install --quiet numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule
echo [OK] Packages installed

echo.
echo [3/7] Checking MongoDB...
docker ps | findstr mongodb >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting MongoDB...
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    timeout /t 5 /nobreak >nul
)
echo [OK] MongoDB ready

echo.
echo [4/7] Processing data...
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
echo [5/7] Starting Kafka...
cd kafka
docker-compose up -d
echo Waiting 20 seconds for Kafka to initialize...
timeout /t 20 /nobreak >nul
cd ..
echo [OK] Kafka ready

echo.
echo [6/7] Initializing MongoDB...
python storage\mongodb_init.py
echo [OK] MongoDB initialized

echo.
echo [7/7] Starting services...
del /s /q *.pyc >nul 2>&1
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

start /min "Global Server" cmd /c "cd /d %CD%\orchestration && python start_global_server.py"
timeout /t 3 /nobreak >nul

start /min "Kafka Producer" cmd /c "cd /d %CD%\orchestration && python start_streaming.py"
timeout /t 2 /nobreak >nul

start /min "Flink Job" cmd /c "cd /d %CD%\orchestration && python start_flink.py"
timeout /t 2 /nobreak >nul

start /min "Spark Jobs" cmd /c "cd /d %CD%\orchestration && python start_spark_jobs.py"

echo.
echo ========================================
echo  ALL SERVICES STARTED!
echo ========================================
echo.
echo  Kafka UI:    http://localhost:8080
echo  API Docs:    http://localhost:8000/docs
echo.
echo Opening browsers...
timeout /t 3 /nobreak >nul
start http://localhost:8080
start http://localhost:8000/docs
echo.
pause
