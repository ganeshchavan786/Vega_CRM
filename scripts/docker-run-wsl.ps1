# PowerShell Script for Running CRM SAAS with Docker (WSL)
# This script works with WSL-based Docker

# Get the script directory and navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CRM SAAS - Docker Commands (WSL)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerStatus = wsl docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running or not accessible via WSL!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop or ensure WSL integration is enabled." -ForegroundColor Red
    exit 1
}
Write-Host "Docker is running ✓" -ForegroundColor Green
Write-Host ""

# Function to run docker-compose commands via WSL
function Run-DockerCompose {
    param(
        [string]$Command
    )
    Write-Host "Running: docker-compose $Command" -ForegroundColor Yellow
    wsl bash -c "cd '$($ProjectRoot -replace '\\', '/')' && docker-compose $Command"
}

# Menu
Write-Host "Select an option:" -ForegroundColor Cyan
Write-Host "1. Build and start containers" -ForegroundColor White
Write-Host "2. Start containers (if already built)" -ForegroundColor White
Write-Host "3. Stop containers" -ForegroundColor White
Write-Host "4. Restart containers" -ForegroundColor White
Write-Host "5. View logs" -ForegroundColor White
Write-Host "6. Build only (no start)" -ForegroundColor White
Write-Host "7. Stop and remove containers" -ForegroundColor White
Write-Host "8. View container status" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-8)"

switch ($choice) {
    "1" {
        Write-Host "Building and starting containers..." -ForegroundColor Yellow
        Run-DockerCompose "up -d --build"
        Write-Host ""
        Write-Host "Application will be available at: http://localhost:8016" -ForegroundColor Green
        Write-Host "API Docs: http://localhost:8016/docs" -ForegroundColor Green
        Write-Host "Health Check: http://localhost:8016/health" -ForegroundColor Green
    }
    "2" {
        Write-Host "Starting containers..." -ForegroundColor Yellow
        Run-DockerCompose "up -d"
        Write-Host ""
        Write-Host "Application will be available at: http://localhost:8016" -ForegroundColor Green
    }
    "3" {
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        Run-DockerCompose "stop"
        Write-Host "Containers stopped." -ForegroundColor Green
    }
    "4" {
        Write-Host "Restarting containers..." -ForegroundColor Yellow
        Run-DockerCompose "restart"
        Write-Host "Containers restarted." -ForegroundColor Green
    }
    "5" {
        Write-Host "Viewing logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
        Run-DockerCompose "logs -f"
    }
    "6" {
        Write-Host "Building containers..." -ForegroundColor Yellow
        Run-DockerCompose "build"
        Write-Host "Build complete." -ForegroundColor Green
    }
    "7" {
        Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
        Run-DockerCompose "down"
        Write-Host "Containers stopped and removed." -ForegroundColor Green
    }
    "8" {
        Write-Host "Container status:" -ForegroundColor Yellow
        wsl docker ps -a --filter "name=crm-saas"
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

