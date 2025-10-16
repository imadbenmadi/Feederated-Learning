@echo off
title IoT Pipeline - Stopping All Services

echo.
echo ========================================
echo  STOPPING ALL SERVICES
echo ========================================
echo.

REM Kill Python processes
echo [1/3] Stopping Python services...
taskkill /FI "WindowTitle eq Global Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Kafka Producer*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Flink Job*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Spark Jobs*" /F >nul 2>&1
echo [OK] Python services stopped

REM Stop Docker containers
echo.
echo [2/3] Stopping Docker containers...
cd /d "%~dp0source\kafka"
docker-compose down
cd ..\..
echo [OK] Kafka containers stopped

echo.
echo [3/3] Stopping MongoDB...
docker stop mongodb >nul 2>&1
echo [OK] MongoDB stopped

echo.
echo ========================================
echo  ALL SERVICES STOPPED
echo ========================================
echo.
pause
