@echo off
title VEGA CRM - Build EXE
color 0E

echo ============================================
echo    VEGA CRM - Building Windows EXE
echo ============================================
echo.
echo This will create a standalone VegaCRM.exe file
echo that can run without Python installation.
echo.
echo Requirements:
echo   - Python 3.11+ installed
echo   - Internet connection (to download PyInstaller)
echo.
echo Build time: 5-10 minutes
echo.
pause

cd /d "%~dp0.."

echo.
echo [1/4] Installing PyInstaller...
pip install pyinstaller -q

echo [2/4] Creating build configuration...
python windows\build_exe.py

echo.
echo ============================================
echo    Build Process Complete!
echo ============================================
echo.
echo Check the 'dist' folder for:
echo   - VegaCRM.exe
echo   - Start VegaCRM.bat
echo.
pause
