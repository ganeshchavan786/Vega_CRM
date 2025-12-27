# View Logs Script for CRM SAAS Docker (WSL)

$WSLPath = "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

Write-Host "Viewing CRM SAAS Docker logs (Press Ctrl+C to exit)..." -ForegroundColor Yellow
Write-Host ""
wsl bash -c "cd '$WSLPath' && docker-compose logs -f"

