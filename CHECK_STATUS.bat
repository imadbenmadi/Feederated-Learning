@echo off
title IoT Pipeline - Service Status Check

echo ==========================================
echo  SERVICE STATUS CHECK
echo ==========================================
echo.

cd /d "%~dp0source"

echo [1/8] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Docker NOT installed
    goto :end
)

docker ps >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Docker is running
) else (
    echo [FAIL] Docker Desktop is NOT RUNNING - Start it first!
    goto :end
)

echo.
echo [2/8] Checking MongoDB...
docker ps | findstr mongodb >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] MongoDB container is running
    docker exec mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] MongoDB is responding
    ) else (
        echo [WARN] MongoDB container exists but not responding yet
    )
) else (
    echo [FAIL] MongoDB container not running
)

echo.
echo [3/8] Checking Python packages...
python -c "import pymongo" 2>nul && echo [OK] pymongo installed || echo [FAIL] pymongo NOT installed
python -c "import kafka" 2>nul && echo [OK] kafka-python installed || echo [FAIL] kafka-python NOT installed
python -c "import fastapi" 2>nul && echo [OK] fastapi installed || echo [FAIL] fastapi NOT installed
python -c "import pyspark" 2>nul && echo [OK] pyspark installed || echo [FAIL] pyspark NOT installed

echo.
echo [4/8] Checking Kafka containers...
docker ps | findstr kafka >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Kafka container is running
) else (
    echo [FAIL] Kafka container not found
)

docker ps | findstr zookeeper >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Zookeeper container is running
) else (
    echo [FAIL] Zookeeper container not found
)

docker ps | findstr kafka-ui >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Kafka UI is running
) else (
    echo [FAIL] Kafka UI not found
)

echo.
echo [5/8] Checking Superset...
docker ps | findstr superset >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Superset container is running
    curl -s http://localhost:8088/health >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Superset responding at http://localhost:8088
    ) else (
        echo [WARN] Superset container exists but not ready yet
    )
) else (
    echo [FAIL] Superset container not found
)

echo.
echo [6/8] Checking Web Services...
curl -s http://localhost:8000/docs >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Global Model Server: http://localhost:8000
) else (
    echo [FAIL] Global Model Server not responding
)

curl -s http://localhost:8080 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Kafka UI: http://localhost:8080
) else (
    echo [FAIL] Kafka UI not responding
)

echo.
echo [7/8] Checking Python Processes...
tasklist /FI "WindowTitle eq Global Server*" 2>nul | findstr cmd.exe >nul
if %ERRORLEVEL% EQU 0 ( echo [OK] Global Server ) else ( echo [WARN] Global Server process not found )

tasklist /FI "WindowTitle eq Kafka Producer*" 2>nul | findstr cmd.exe >nul
if %ERRORLEVEL% EQU 0 ( echo [OK] Kafka Producer ) else ( echo [WARN] Kafka Producer process not found )

tasklist /FI "WindowTitle eq Flink Job*" 2>nul | findstr cmd.exe >nul
if %ERRORLEVEL% EQU 0 ( echo [OK] Flink Job ) else ( echo [WARN] Flink Job process not found )

tasklist /FI "WindowTitle eq Spark Jobs*" 2>nul | findstr cmd.exe >nul
if %ERRORLEVEL% EQU 0 ( echo [OK] Spark Jobs ) else ( echo [WARN] Spark Jobs process not found )

echo.
echo [8/8] Checking Data Files...
if exist "data\processed\processed_iot_data.csv" (
    echo [OK] Processed data file exists
) else (
    echo [FAIL] Processed data NOT found - Run data preprocessing first
)

echo.
echo ==========================================
echo  DOCKER CONTAINERS STATUS
echo ==========================================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ==========================================
echo  ACCESS URLs
echo ==========================================
echo  Kafka UI:         http://localhost:8080
echo  API Docs:         http://localhost:8000/docs
echo  Superset:         http://localhost:8088 (admin/admin)
echo.

:end
pause