@echo off
title IoT Pipeline - Stopping All Services

echo.
echo ========================================
echo  STOPPING ALL SERVICES
echo ========================================
echo.

REM Kill Python processes
echo [1/4] Stopping Python services...
taskkill /FI "WindowTitle eq Global Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Kafka Producer*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Flink Job*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Spark Jobs*" /F >nul 2>&1
echo [OK] Python services stopped

REM Stop Docker containers
echo.
echo [2/4] Stopping Kafka containers...
cd /d "%~dp0source\kafka"
docker-compose down
cd ..\..
echo [OK] Kafka containers stopped

echo.
echo [3/4] Stopping Superset...
cd /d "%~dp0source\visualization"
docker-compose down
cd ..\..
echo [OK] Superset stopped

echo.
echo [4/4] Stopping and removing MongoDB...
docker stop mongodb >nul 2>&1
docker rm mongodb >nul 2>&1
echo [OK] MongoDB stopped and removed

echo.
echo ========================================
echo  ALL SERVICES STOPPED
echo ========================================
echo.
pause
