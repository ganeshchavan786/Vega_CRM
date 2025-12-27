# Quick Start Script for CRM SAAS Docker (WSL)
# Simple one-command script

$ProjectPath = "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"
$WSLPath = "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

Write-Host "Starting CRM SAAS Docker containers..." -ForegroundColor Cyan
Write-Host "Port: 8016" -ForegroundColor Yellow
Write-Host ""

wsl bash -c "cd '$WSLPath' && docker-compose up -d --build"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Containers started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Cyan
    Write-Host "  Application: http://localhost:8016" -ForegroundColor White
    Write-Host "  API Docs:    http://localhost:8016/docs" -ForegroundColor White
    Write-Host "  Health:      http://localhost:8016/health" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "✗ Failed to start containers!" -ForegroundColor Red
}

