# Stop Script for CRM SAAS Docker (WSL)

$WSLPath = "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

Write-Host "Stopping CRM SAAS Docker containers..." -ForegroundColor Yellow
wsl bash -c "cd '$WSLPath' && docker-compose stop"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Containers stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to stop containers!" -ForegroundColor Red
}

