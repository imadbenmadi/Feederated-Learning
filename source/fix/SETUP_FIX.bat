@echo off
REM Quick Fix Script for IoT Pipeline Setup Issues

echo ==========================================
echo IoT Pipeline - Quick Fix Setup
echo ==========================================
echo.

REM Step 1: Install Missing Python Packages
echo [1/5] Installing Python packages...
echo.
pip install numpy pandas kafka-python pymongo fastapi uvicorn pydantic requests schedule pyyaml python-dotenv colorlog

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ✓ Python packages installed
echo.

REM Step 2: Check Docker
echo [2/5] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker not found or not running
    echo Please start Docker Desktop and run this script again
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker daemon not running
    echo Please start Docker Desktop and run this script again
    pause
    exit /b 1
)

echo ✓ Docker is running
echo.

REM Step 3: Clean and Reprocess Data
echo [3/5] Cleaning old data files...
if exist "data\raw\intel_lab_data.csv" del /F data\raw\intel_lab_data.csv
if exist "data\processed\processed_iot_data.csv" del /F data\processed\processed_iot_data.csv

echo [3/5] Downloading and processing data...
python data\download_dataset.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to download data
    pause
    exit /b 1
)

python data\preprocess_dataset.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to preprocess data
    pause
    exit /b 1
)

echo ✓ Data processed successfully
echo.

REM Step 4: Start Kafka
echo [4/5] Starting Kafka...
cd kafka
docker-compose down >nul 2>&1
docker-compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start Kafka
    cd ..
    pause
    exit /b 1
)

cd ..
echo Waiting for Kafka to initialize...
timeout /t 20 /nobreak >nul

echo ✓ Kafka started
echo.

REM Step 5: Check MongoDB
echo [5/5] Checking MongoDB...
mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ MongoDB is running
    echo.
    echo Initializing MongoDB collections...
    python storage\mongodb_init.py
) else (
    echo ✗ MongoDB not running
    echo.
    echo OPTION 1: Install MongoDB Community Edition
    echo   Download from: https://www.mongodb.com/try/download/community
    echo.
    echo OPTION 2: Run MongoDB in Docker
    echo   Run: docker run -d -p 27017:27017 --name mongodb mongo:latest
    echo.
    echo After starting MongoDB, run: python storage\mongodb_init.py
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo ✓ Python packages installed
echo ✓ Docker running
echo ✓ Data processed
echo ✓ Kafka started
echo.
echo Access points:
echo   - Kafka UI: http://localhost:8080
echo   - Global Server (after start): http://localhost:8000/docs
echo.
echo Next steps:
echo   1. Make sure MongoDB is running
echo   2. Open 2 PowerShell windows:
echo.
echo      Window 1: python orchestration\start_global_server.py
echo      Window 2: python orchestration\start_streaming.py
echo.
echo   3. Test with: python kafka\kafka_consumer_test.py
echo.
pause
