@echo off
title VEGA CRM Server
color 0B

echo ============================================
echo       VEGA CRM - Starting Server
echo ============================================
echo.

cd /d "C:\VegaCRM"

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Starting VEGA CRM Server...
echo.
echo Access URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

:: Open browser after 3 seconds
start /min cmd /c "timeout /t 3 >nul && start http://localhost:8000"

:: Start the server
python run_production.py

pause
