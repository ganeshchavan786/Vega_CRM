@echo off
title VEGA CRM - Windows Service Installation
color 0A

echo ============================================
echo    VEGA CRM - Windows Service Setup
echo    (Auto-start on Windows Boot)
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

:: Install NSSM (Non-Sucking Service Manager)
echo [1/3] Downloading NSSM service manager...
if not exist "%INSTALL_DIR%\nssm.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%TEMP%\nssm.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\nssm' -Force"
    copy "%TEMP%\nssm\nssm-2.24\win64\nssm.exe" "%INSTALL_DIR%\nssm.exe"
)

:: Create service runner script
echo [2/3] Creating service runner...
echo @echo off > "%INSTALL_DIR%\service-runner.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\service-runner.bat"
echo call venv\Scripts\activate.bat >> "%INSTALL_DIR%\service-runner.bat"
echo python run_production.py >> "%INSTALL_DIR%\service-runner.bat"

:: Install Windows Service
echo [3/3] Installing Windows Service...
"%INSTALL_DIR%\nssm.exe" stop %SERVICE_NAME% 2>nul
"%INSTALL_DIR%\nssm.exe" remove %SERVICE_NAME% confirm 2>nul

"%INSTALL_DIR%\nssm.exe" install %SERVICE_NAME% "%INSTALL_DIR%\venv\Scripts\python.exe"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% AppParameters "%INSTALL_DIR%\run_production.py"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% AppDirectory "%INSTALL_DIR%"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% DisplayName "VEGA CRM Server"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% Description "VEGA CRM Application Server"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% Start SERVICE_AUTO_START
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% AppStdout "%INSTALL_DIR%\logs\service.log"
"%INSTALL_DIR%\nssm.exe" set %SERVICE_NAME% AppStderr "%INSTALL_DIR%\logs\error.log"

:: Create logs directory
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"

:: Start the service
echo Starting VEGA CRM Service...
net start %SERVICE_NAME%

echo.
echo ============================================
echo    Windows Service Installed!
echo ============================================
echo.
echo Service Name: %SERVICE_NAME%
echo Status: Running
echo Auto-Start: Enabled (starts on Windows boot)
echo.
echo Commands:
echo   Start:   net start %SERVICE_NAME%
echo   Stop:    net stop %SERVICE_NAME%
echo   Status:  sc query %SERVICE_NAME%
echo.
echo Access URL: http://localhost:8000
echo.
pause
