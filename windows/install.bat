@echo off
title VEGA CRM - Windows Installer
color 0A

echo ============================================
echo    VEGA CRM - Windows Installation
echo    Production Ready Setup
echo ============================================
echo.

:: Check for Admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Set installation directory
set INSTALL_DIR=C:\VegaCRM
set PYTHON_VERSION=3.11.0

echo [1/6] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

:: Check if Python is installed
echo [2/6] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found. Installing Python %PYTHON_VERSION%...
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found!
python --version

:: Copy application files
echo [3/6] Copying application files...
xcopy /E /I /Y "%~dp0..\app" "%INSTALL_DIR%\app"
xcopy /E /I /Y "%~dp0..\frontend" "%INSTALL_DIR%\frontend"
xcopy /E /I /Y "%~dp0..\guides" "%INSTALL_DIR%\guides"
copy /Y "%~dp0..\requirements.txt" "%INSTALL_DIR%\"
copy /Y "%~dp0..\run_production.py" "%INSTALL_DIR%\"

:: Create data directory
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"

:: Create virtual environment
echo [4/6] Creating Python virtual environment...
cd /d "%INSTALL_DIR%"
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [5/6] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip
pip install -r requirements.txt

:: Create startup scripts
echo [6/6] Creating startup scripts...

:: Create start.bat
echo @echo off > "%INSTALL_DIR%\start.bat"
echo title VEGA CRM Server >> "%INSTALL_DIR%\start.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\start.bat"
echo call venv\Scripts\activate.bat >> "%INSTALL_DIR%\start.bat"
echo echo Starting VEGA CRM... >> "%INSTALL_DIR%\start.bat"
echo echo Access at: http://localhost:8000 >> "%INSTALL_DIR%\start.bat"
echo start http://localhost:8000 >> "%INSTALL_DIR%\start.bat"
echo python run_production.py >> "%INSTALL_DIR%\start.bat"
echo pause >> "%INSTALL_DIR%\start.bat"

:: Create stop.bat
echo @echo off > "%INSTALL_DIR%\stop.bat"
echo taskkill /F /IM python.exe /FI "WINDOWTITLE eq VEGA CRM*" >> "%INSTALL_DIR%\stop.bat"
echo echo VEGA CRM stopped. >> "%INSTALL_DIR%\stop.bat"

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\VEGA CRM.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll,21'; $Shortcut.Save()"

echo.
echo ============================================
echo    Installation Complete!
echo ============================================
echo.
echo Installation Directory: %INSTALL_DIR%
echo.
echo To start VEGA CRM:
echo   1. Double-click "VEGA CRM" shortcut on Desktop
echo   OR
echo   2. Run: %INSTALL_DIR%\start.bat
echo.
echo Access URL: http://localhost:8000
echo.
pause
