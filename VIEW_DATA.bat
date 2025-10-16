@echo off
title View MongoDB Data

echo.
echo ========================================
echo  MongoDB Data Viewer
echo ========================================
echo.

cd /d "%~dp0source"

echo Checking MongoDB connection...
docker exec mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MongoDB is not running!
    echo.
    echo Please start MongoDB first:
    echo   docker run -d -p 27017:27017 --name mongodb mongo:latest
    echo.
    pause
    exit /b 1
)
echo [OK] MongoDB is running

echo.
echo Fetching data from MongoDB...
echo.
python view_mongodb_data.py

echo.
pause
