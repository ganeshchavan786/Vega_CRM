# 🐳 Docker Commands - Quick Reference

## Build Locally

```powershell
# Build image
docker build -t vega-crm:latest .

# Run container
docker run -d -p 8000:8000 --name vega-crm vega-crm:latest

# Check status
docker ps

# View logs
docker logs vega-crm
```

## Push to GHCR (Manual)

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

## Or Use Scripts

```powershell
# Build only
.\scripts\build_docker.ps1

# Build and push to GHCR
.\scripts\push_docker_ghcr.ps1
```

---

**Ready to build!** 🚀

