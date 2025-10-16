@echo off
echo ==========================================
echo CHECKING SYSTEM STATUS
echo ==========================================
echo.

echo [1] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker NOT installed
    echo    Install from: https://www.docker.com/products/docker-desktop
    goto :mongodb_check
)

docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✗ Docker Desktop is NOT RUNNING
    echo    YOU MUST START DOCKER DESKTOP!
    echo    1. Open Docker Desktop from Start Menu
    echo    2. Wait until it says "running"
    echo    3. Run this script again
) else (
    echo ✓ Docker is running
    docker ps
)

:mongodb_check
echo.
echo [2] Checking MongoDB...
mongosh --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    mongo --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ✗ MongoDB NOT installed
        echo    Option 1: docker run -d -p 27017:27017 --name mongodb mongo:latest
        echo    Option 2: Download from https://www.mongodb.com/try/download/community
    ) else (
        echo ✓ mongo found
    )
) else (
    echo ✓ mongosh found
)

echo.
echo [3] Checking Python packages...
python -c "import pymongo; print('✓ pymongo installed')" 2>nul || echo ✗ pymongo NOT installed - Run: pip install pymongo
python -c "import kafka; print('✓ kafka-python installed')" 2>nul || echo ✗ kafka-python NOT installed - Run: pip install kafka-python
python -c "import fastapi; print('✓ fastapi installed')" 2>nul || echo ✗ fastapi NOT installed - Run: pip install fastapi uvicorn

echo.
echo [4] Checking if services are running...
netstat -ano | findstr ":8080 :8000 :9092" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Some services are running:
    netstat -ano | findstr ":8080 :8000 :9092"
) else (
    echo ✗ NO services are running on ports 8080, 8000, or 9092
)

echo.
echo [5] Checking processed data...
if exist "source\data\processed\processed_iot_data.csv" (
    echo ✓ Processed data file exists
) else (
    echo ✗ Processed data NOT found
    echo    Run: python data\download_dataset.py
    echo    Then: python data\preprocess_dataset.py
)

echo.
echo ==========================================
echo SUMMARY
echo ==========================================
echo.
echo Next Steps:
echo   1. START DOCKER DESKTOP (if not running)
echo   2. Install missing packages: pip install pymongo kafka-python fastapi uvicorn
echo   3. Start MongoDB: docker run -d -p 27017:27017 --name mongodb mongo:latest
echo   4. Then run: cd source
echo   5. Start Kafka: cd kafka ^&^& docker-compose up -d ^&^& cd ..
echo   6. Start server: python orchestration\start_global_server.py
echo   7. Start streaming: python orchestration\start_streaming.py
echo.
pause
