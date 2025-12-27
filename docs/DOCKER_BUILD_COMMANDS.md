# 🐳 Docker Build Commands - Manual

## Local Build and Test

### Step 1: Build Docker Image Locally
```powershell
# Build image with tag
docker build -t vega-crm:latest .

# Or with specific version
docker build -t vega-crm:v1.0.0 .
```

### Step 2: Run Docker Container
```powershell
# Run container (detached mode)
docker run -d -p 8000:8000 --name vega-crm vega-crm:latest

# Run with volume mount (for data persistence)
docker run -d -p 8000:8000 -v "$(pwd)/data:/app/data" --name vega-crm vega-crm:latest
```

### Step 3: Check Container Status
```powershell
# Check if container is running
docker ps

# Check logs
docker logs vega-crm

# Follow logs (real-time)
docker logs -f vega-crm
```

### Step 4: Stop and Remove Container
```powershell
# Stop container
docker stop vega-crm

# Remove container
docker rm vega-crm

# Stop and remove in one command
docker rm -f vega-crm
```

---

## Push to GHCR (Manual)

### Step 1: Tag Image for GHCR
```powershell
# Tag image for GHCR
docker tag vega-crm:latest ghcr.io/ganeshchavan786/vega_crm:latest

# Or tag with version
docker tag vega-crm:v1.0.0 ghcr.io/ganeshchavan786/vega_crm:v1.0.0
```

### Step 2: Login to GHCR
```powershell
# Login to GitHub Container Registry
# You'll be prompted for username and password (use Personal Access Token)
docker login ghcr.io -u ganeshchavan786

# Or using token directly (replace YOUR_TOKEN with your token)
echo YOUR_TOKEN | docker login ghcr.io -u ganeshchavan786 --password-stdin
```

### Step 3: Push Image to GHCR
```powershell
# Push latest tag
docker push ghcr.io/ganeshchavan786/vega_crm:latest

# Push version tag
docker push ghcr.io/ganeshchavan786/vega_crm:v1.0.0
```

---

## Complete Build and Push Sequence

### Option 1: Build and Push Latest
```powershell
# Build
docker build -t vega-crm:latest .

# Tag
docker tag vega-crm:latest ghcr.io/ganeshchavan786/vega_crm:latest

# Login
docker login ghcr.io -u ganeshchavan786

# Push
docker push ghcr.io/ganeshchavan786/vega_crm:latest
```

### Option 2: Build and Push with Version
```powershell
# Build
docker build -t vega-crm:v1.0.0 .

# Tag
docker tag vega-crm:v1.0.0 ghcr.io/ganeshchavan786/vega_crm:v1.0.0

# Login
docker login ghcr.io -u ganeshchavan786

# Push
docker push ghcr.io/ganeshchavan786/vega_crm:v1.0.0
```

---

## Test Locally

### Run and Test
```powershell
# Build
docker build -t vega-crm:latest .

# Run
docker run -d -p 8000:8000 --name vega-crm vega-crm:latest

# Check if running
docker ps

# Check logs
docker logs vega-crm

# Test API
# Open browser: http://localhost:8000/docs
```

### Stop and Cleanup
```powershell
# Stop
docker stop vega-crm

# Remove container
docker rm vega-crm

# Remove image (optional)
docker rmi vega-crm:latest
```

---

## Pull from GHCR (After Push)

### Pull Latest
```powershell
# Login first
docker login ghcr.io -u ganeshchavan786

# Pull image
docker pull ghcr.io/ganeshchavan786/vega_crm:latest

# Run
docker run -d -p 8000:8000 ghcr.io/ganeshchavan786/vega_crm:latest
```

### Pull Specific Version
```powershell
docker pull ghcr.io/ganeshchavan786/vega_crm:v1.0.0
docker run -d -p 8000:8000 ghcr.io/ganeshchavan786/vega_crm:v1.0.0
```

---

## Useful Docker Commands

### Image Management
```powershell
# List all images
docker images

# Remove image
docker rmi vega-crm:latest

# Remove all unused images
docker image prune -a
```

### Container Management
```powershell
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop container
docker stop vega-crm

# Start stopped container
docker start vega-crm

# Restart container
docker restart vega-crm

# Remove container
docker rm vega-crm

# Remove all stopped containers
docker container prune
```

### Debugging
```powershell
# View logs
docker logs vega-crm

# Follow logs
docker logs -f vega-crm

# Execute command in running container
docker exec -it vega-crm /bin/bash

# Inspect container
docker inspect vega-crm
```

---

## Quick Reference

### Build and Run Locally
```powershell
docker build -t vega-crm:latest .
docker run -d -p 8000:8000 --name vega-crm vega-crm:latest
```

### Build and Push to GHCR
```powershell
docker build -t vega-crm:latest .
docker tag vega-crm:latest ghcr.io/ganeshchavan786/vega_crm:latest
docker login ghcr.io -u ganeshchavan786
docker push ghcr.io/ganeshchavan786/vega_crm:latest
```

### Pull and Run from GHCR
```powershell
docker login ghcr.io -u ganeshchavan786
docker pull ghcr.io/ganeshchavan786/vega_crm:latest
docker run -d -p 8000:8000 ghcr.io/ganeshchavan786/vega_crm:latest
```

---

## Notes

1. **Build Time:** ~1-3 minutes (first build takes longer)
2. **Image Size:** ~200-500 MB (estimated)
3. **Port:** Container runs on port 8000
4. **Data Persistence:** Use `-v` flag to mount data directory
5. **Authentication:** Use Personal Access Token for GHCR login

---

**Ready to build!** 🚀

