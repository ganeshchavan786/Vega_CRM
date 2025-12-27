# Restart Script for CRM SAAS Docker (WSL)

$WSLPath = "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

Write-Host "Restarting CRM SAAS Docker containers..." -ForegroundColor Yellow
wsl bash -c "cd '$WSLPath' && docker-compose restart"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Containers restarted successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application available at: http://localhost:8016" -ForegroundColor Cyan
} else {
    Write-Host "✗ Failed to restart containers!" -ForegroundColor Red
}

