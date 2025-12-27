# PowerShell script to build Docker image (Linux containers)

Write-Host "Building Docker image for Linux..." -ForegroundColor Green
Write-Host ""

# Check Docker mode
Write-Host "Checking Docker configuration..." -ForegroundColor Yellow
$dockerInfo = docker version 2>&1
if ($dockerInfo -match "OSType:\s*windows") {
    Write-Host ""
    Write-Host "WARNING: Docker is in Windows containers mode!" -ForegroundColor Red
    Write-Host "Please switch to Linux containers:" -ForegroundColor Yellow
    Write-Host "  1. Right-click Docker Desktop icon (system tray)" -ForegroundColor Cyan
    Write-Host "  2. Click 'Switch to Linux containers'" -ForegroundColor Cyan
    Write-Host "  3. Wait for Docker to restart" -ForegroundColor Cyan
    Write-Host "  4. Run this script again" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Build image with explicit platform
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build --platform linux/amd64 -t vega-crm:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image name: vega-crm:latest" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the container:" -ForegroundColor Yellow
    Write-Host "  docker run -d -p 8000:8000 --name vega-crm vega-crm:latest" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Build failed! Check errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "If you see 'no matching manifest' error:" -ForegroundColor Yellow
    Write-Host "  1. Switch Docker Desktop to Linux containers" -ForegroundColor Cyan
    Write-Host "  2. Or use: docker build --platform linux/amd64 -t vega-crm:latest ." -ForegroundColor Cyan
}

