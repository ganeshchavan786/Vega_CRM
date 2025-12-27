@echo off
REM Push Docker image to GHCR using GitHub PAT token
REM Usage: scripts\push_to_ghcr_with_token.bat [tag]

setlocal enabledelayedexpansion

REM Configuration
set GITHUB_USERNAME=ganeshchavan786
set IMAGE_NAME=crm-saas
set REGISTRY=ghcr.io
set TAG=%1
if "%TAG%"=="" set TAG=latest

REM Full image name
set FULL_IMAGE_NAME=%REGISTRY%/%GITHUB_USERNAME%/%IMAGE_NAME%:%TAG%

echo ==========================================
echo Push Docker Image to GHCR (with Token)
echo ==========================================
echo Image: %FULL_IMAGE_NAME%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    pause
    exit /b 1
)

REM Step 1: Login to GHCR
echo [STEP 1] Login to GHCR
echo.
echo Please enter your GitHub Personal Access Token (PAT)
echo Token should have 'write:packages' permission
echo.
set /p PAT_TOKEN="Enter your GitHub PAT: "

if "%PAT_TOKEN%"=="" (
    echo [ERROR] Token is required
    pause
    exit /b 1
)

echo %PAT_TOKEN% | docker login %REGISTRY% -u %GITHUB_USERNAME% --password-stdin
if errorlevel 1 (
    echo [ERROR] Login failed. Check your token.
    pause
    exit /b 1
)

echo [SUCCESS] Logged in to GHCR
echo.

REM Step 2: Build image (with Linux platform for Windows compatibility)
echo [STEP 2] Building Docker image (Linux platform)...
docker buildx build --platform linux/amd64 -t %FULL_IMAGE_NAME% --load .
if errorlevel 1 (
    echo [INFO] buildx failed, trying regular build...
    docker build -t %FULL_IMAGE_NAME% .
)

if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo [SUCCESS] Image built successfully
echo.

REM Step 4: Push image
echo [STEP 4] Pushing image to GHCR...
docker push %FULL_IMAGE_NAME%

if errorlevel 1 (
    echo [ERROR] Push failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [SUCCESS] Image pushed successfully!
echo ==========================================
echo.
echo Image: %FULL_IMAGE_NAME%
echo.
echo To pull this image:
echo   docker pull %FULL_IMAGE_NAME%
echo.
echo View on GitHub:
echo   https://github.com/%GITHUB_USERNAME%?tab=packages
echo.
pause

