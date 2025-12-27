# PowerShell script to build and push Docker image to GHCR

Write-Host "Building and pushing Docker image to GHCR..." -ForegroundColor Green
Write-Host ""

# Step 1: Build image
Write-Host "Step 1: Building Docker image..." -ForegroundColor Yellow
docker build -t vega-crm:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed! Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "Build successful!" -ForegroundColor Green
Write-Host ""

# Step 2: Tag image for GHCR
Write-Host "Step 2: Tagging image for GHCR..." -ForegroundColor Yellow
docker tag vega-crm:latest ghcr.io/ganeshchavan786/vega_crm:latest

Write-Host "Image tagged successfully!" -ForegroundColor Green
Write-Host ""

# Step 3: Login to GHCR
Write-Host "Step 3: Login to GHCR..." -ForegroundColor Yellow
Write-Host "You will be prompted for username and password (use Personal Access Token)" -ForegroundColor Cyan
docker login ghcr.io -u ganeshchavan786

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed! Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "Login successful!" -ForegroundColor Green
Write-Host ""

# Step 4: Push image
Write-Host "Step 4: Pushing image to GHCR..." -ForegroundColor Yellow
docker push ghcr.io/ganeshchavan786/vega_crm:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Image pushed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image available at: ghcr.io/ganeshchavan786/vega_crm:latest" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To pull the image:" -ForegroundColor Yellow
    Write-Host "  docker pull ghcr.io/ganeshchavan786/vega_crm:latest" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Push failed! Check errors above." -ForegroundColor Red
}

