@echo off
title VEGA CRM - Stop Server
color 0C

echo ============================================
echo       VEGA CRM - Stopping Server
echo ============================================
echo.

:: Kill Python processes running VEGA CRM
taskkill /F /IM python.exe /FI "WINDOWTITLE eq VEGA CRM*" 2>nul
taskkill /F /IM uvicorn.exe 2>nul

echo.
echo VEGA CRM Server stopped successfully.
echo.
pause
