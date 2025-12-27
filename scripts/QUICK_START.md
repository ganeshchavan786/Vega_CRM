# Quick Start Guide - CRM SAAS Docker

## 🔍 Check Docker Installation

First, check what you have installed:

```bash
# Check Docker
docker --version

# Check docker compose (v2 - modern, recommended)
docker compose version

# Check docker-compose (v1 - legacy)
docker-compose --version
```

---

## ✅ Option 1: Use `docker compose` (v2) - Recommended

If you have Docker Desktop or modern Docker, use **`docker compose`** (without hyphen):

```bash
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

# Build and start
docker compose up -d --build

# Start (already built)
docker compose up -d

# Stop
docker compose stop

# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop and remove
docker compose down
```

**All scripts have been updated to use `docker compose` (v2)**

---

## 📦 Option 2: Install docker-compose (v1)

If you need the old `docker-compose` command:

```bash
# Install docker-compose
sudo apt update
sudo apt install -y docker-compose

# Or use the install script
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS/scripts"
chmod +x install-docker-compose.sh
./install-docker-compose.sh
```

---

## 🚀 Quick Start Commands

### Using Scripts (Updated to use docker compose v2):

```bash
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS/scripts"

# Start containers
./start-docker.sh

# Stop containers
./stop-docker.sh

# Restart containers
./restart-docker.sh

# View logs
./view-logs.sh

# Interactive menu
./docker-run.sh
```

### Direct Commands:

```bash
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

# Build and start
docker compose up -d --build

# View logs
docker compose logs -f
```

---

## 🐳 Docker Desktop Setup (Windows)

If you're using WSL with Docker Desktop:

1. **Install Docker Desktop** from: https://www.docker.com/products/docker-desktop
2. **Enable WSL Integration**:
   - Open Docker Desktop
   - Go to Settings → Resources → WSL Integration
   - Enable integration with your WSL distro
3. **Restart WSL**:
   ```bash
   # In PowerShell
   wsl --shutdown
   # Then reopen WSL
   ```

After this, `docker compose` should work in WSL.

---

## 🔧 Troubleshooting

### Check if Docker is running:
```bash
docker info
```

### If Docker is not accessible:
```bash
# Check Docker service
sudo service docker status

# Start Docker service (if needed)
sudo service docker start
```

### Test Docker:
```bash
docker run hello-world
```

---

## 📝 Summary

- **Modern way**: `docker compose` (v2) - no hyphen
- **Legacy way**: `docker-compose` (v1) - with hyphen
- **All scripts updated**: Now use `docker compose` (v2)
- **Port**: 8016
- **URL**: http://localhost:8016

---

## ✅ Next Steps

1. Check if `docker compose` works: `docker compose version`
2. If yes, use the scripts or direct commands
3. If no, install docker-compose (v1) or set up Docker Desktop

