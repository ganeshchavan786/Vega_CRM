@echo off
title VEGA CRM - Uninstaller
color 0C

echo ============================================
echo       VEGA CRM - Uninstaller
echo ============================================
echo.

:: Check for Admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    pause
    exit /b 1
)

set INSTALL_DIR=C:\VegaCRM
set SERVICE_NAME=VegaCRM

echo WARNING: This will remove VEGA CRM completely!
echo.
set /p CONFIRM=Are you sure? (Y/N): 
if /i not "%CONFIRM%"=="Y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/4] Stopping service...
net stop %SERVICE_NAME% 2>nul
"%INSTALL_DIR%\nssm.exe" remove %SERVICE_NAME% confirm 2>nul

echo [2/4] Stopping any running processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq VEGA CRM*" 2>nul

echo [3/4] Removing desktop shortcut...
del "%USERPROFILE%\Desktop\VEGA CRM.lnk" 2>nul

echo [4/4] Removing installation directory...
rd /s /q "%INSTALL_DIR%" 2>nul

echo.
echo ============================================
echo    VEGA CRM Uninstalled Successfully!
echo ============================================
echo.
pause
