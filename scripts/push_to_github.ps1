# PowerShell script to push code to GitHub and activate workflow

Write-Host "Pushing code to GitHub..." -ForegroundColor Green
Write-Host ""

# Step 1: Check git status
Write-Host "Checking git status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "Staging all changes..." -ForegroundColor Yellow
git add .

# Step 2: Show what will be committed
Write-Host ""
Write-Host "Files staged for commit:" -ForegroundColor Yellow
git status --short

# Step 3: Commit
Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Yellow
$commitMessage = @"
feat: DataTable integration, navigation updates, and bug fixes

- Integrate DataTable framework on all 7 pages (Leads, Accounts, Contacts, Opportunities, Tasks, Activities)
- Rename navigation: Customers to Accounts, Deals to Opportunities
- Fix API pagination limits (per_page: 1000 to 100)
- Fix DataTable method existence checks
- Fix escapeHtml missing in contacts.js
- Fix backend contact route success_response meta parameter
- Organize files: Move docs to docs/, scripts to scripts/
- Add DataTable CSS/JS framework files
- Update all page files with DataTable integration
- Update navigation labels across all pages
- Add comprehensive documentation
- Organize scripts and test files
"@
git commit -m $commitMessage

# Step 4: Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub (main branch)..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "Code pushed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub Actions workflow will now trigger automatically..." -ForegroundColor Cyan
Write-Host "Check workflow status at: https://github.com/ganeshchavan786/Vega_CRM/actions" -ForegroundColor Cyan
Write-Host "Docker image will be available at: ghcr.io/ganeshchavan786/vega_crm:latest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Workflow typically takes 2-5 minutes to complete" -ForegroundColor Yellow

