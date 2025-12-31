@echo off
title VEGA CRM - Create Customer Package
color 0E

echo ============================================
echo    VEGA CRM - Create Customer Package
echo    Creates ZIP file for distribution
echo ============================================
echo.

set PACKAGE_DIR=%~dp0..\dist\VegaCRM-Windows
set ZIP_NAME=VegaCRM-Windows-Setup.zip

echo [1/5] Cleaning previous package...
if exist "%~dp0..\dist" rd /s /q "%~dp0..\dist"
mkdir "%PACKAGE_DIR%"

echo [2/5] Copying application files...
xcopy /E /I /Y "%~dp0..\app" "%PACKAGE_DIR%\app"
xcopy /E /I /Y "%~dp0..\frontend" "%PACKAGE_DIR%\frontend"
xcopy /E /I /Y "%~dp0..\guides" "%PACKAGE_DIR%\guides"
copy /Y "%~dp0..\requirements.txt" "%PACKAGE_DIR%\"
copy /Y "%~dp0..\run_production.py" "%PACKAGE_DIR%\"
copy /Y "%~dp0..\LICENSE" "%PACKAGE_DIR%\"

echo [3/5] Copying Windows scripts...
mkdir "%PACKAGE_DIR%\windows"
copy /Y "%~dp0install.bat" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0start.bat" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0stop.bat" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0install-service.bat" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0uninstall.bat" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0README.txt" "%PACKAGE_DIR%\windows\"
copy /Y "%~dp0run_server.py" "%PACKAGE_DIR%\"

echo [4/5] Creating main installer shortcut...
copy /Y "%~dp0install.bat" "%PACKAGE_DIR%\INSTALL.bat"

echo [5/5] Creating ZIP package...
powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%~dp0..\dist\%ZIP_NAME%' -Force"

echo.
echo ============================================
echo    Package Created Successfully!
echo ============================================
echo.
echo Package Location: %~dp0..\dist\%ZIP_NAME%
echo.
echo This ZIP file contains everything needed to
echo install VEGA CRM on customer's Windows PC.
echo.
echo Instructions for customer:
echo   1. Extract ZIP file
echo   2. Run INSTALL.bat as Administrator
echo   3. Follow on-screen instructions
echo.
pause
