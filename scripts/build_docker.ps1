# PowerShell script to build Docker image locally

Write-Host "Building Docker image..." -ForegroundColor Green
Write-Host ""

# Build image with explicit platform for Linux
docker build --platform linux/amd64 -t vega-crm:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image name: vega-crm:latest" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the container:" -ForegroundColor Yellow
    Write-Host "  docker run -d -p 8000:8000 --name vega-crm vega-crm:latest" -ForegroundColor White
    Write-Host ""
    Write-Host "To check container status:" -ForegroundColor Yellow
    Write-Host "  docker ps" -ForegroundColor White
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker logs vega-crm" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Build failed! Check errors above." -ForegroundColor Red
}

