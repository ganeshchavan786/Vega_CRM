@echo off
title VEGA CRM - Build Professional Installer
color 0E

echo ============================================
echo    VEGA CRM - Build Professional Installer
echo    Using Inno Setup
echo ============================================
echo.

:: Check if Inno Setup is installed
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_PATH% (
    echo [ERROR] Inno Setup not found!
    echo.
    echo Please download and install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    start https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

:: Check if EXE exists
if not exist "%~dp0..\dist\VegaCRM.exe" (
    echo [ERROR] VegaCRM.exe not found!
    echo.
    echo Please run build-exe.bat first to create the EXE.
    pause
    exit /b 1
)

:: Create installer output directory
if not exist "%~dp0..\installer" mkdir "%~dp0..\installer"

:: Create placeholder icon if not exists
if not exist "%~dp0vega_icon.ico" (
    echo [INFO] Creating placeholder icon...
    echo Please replace vega_icon.ico with your actual icon file.
)

echo.
echo [1/2] Building installer...
%INNO_PATH% "%~dp0VegaCRM_Setup.iss"

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Installer Build Complete!
echo ============================================
echo.
echo Installer Location:
echo   %~dp0..\installer\VegaCRM-Setup-1.0.0.exe
echo.
echo This installer includes:
echo   - Professional setup wizard
echo   - Desktop shortcut option
echo   - Start menu shortcuts
echo   - Auto-start option
echo   - Firewall rule configuration
echo   - Clean uninstaller
echo.
pause
