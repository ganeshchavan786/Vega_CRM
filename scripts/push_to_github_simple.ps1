# Simple PowerShell script to push code to GitHub

Write-Host "Pushing code to GitHub..." -ForegroundColor Green
Write-Host ""

# Stage all changes
Write-Host "Staging all changes..." -ForegroundColor Yellow
git add .

# Commit with simple message
Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "feat: DataTable integration, navigation updates, and bug fixes"

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub (main branch)..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "Code pushed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub Actions workflow will now trigger automatically..." -ForegroundColor Cyan
Write-Host "Check workflow: https://github.com/ganeshchavan786/Vega_CRM/actions" -ForegroundColor Cyan
Write-Host "Docker image: ghcr.io/ganeshchavan786/vega_crm:latest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Workflow typically takes 2-5 minutes to complete" -ForegroundColor Yellow
