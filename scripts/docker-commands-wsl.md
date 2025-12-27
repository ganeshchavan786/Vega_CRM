# Docker Commands for CRM SAAS (WSL/PowerShell)

## 🚀 Quick Start Commands

### Using PowerShell with WSL

#### 1. Build and Start (First Time)
```powershell
# Navigate to project directory
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"

# Build and start containers
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d --build"
```

#### 2. Start Containers (Already Built)
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d"
```

#### 3. Stop Containers
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose stop"
```

#### 4. Restart Containers
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose restart"
```

#### 5. View Logs
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose logs -f"
```

#### 6. Stop and Remove Containers
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose down"
```

#### 7. View Container Status
```powershell
wsl docker ps -a --filter "name=crm-saas"
```

#### 8. Rebuild (Force Rebuild)
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d --build --force-recreate"
```

---

## 📝 Using the PowerShell Script

### Easy Method - Run the Script:
```powershell
# Navigate to scripts folder
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS\scripts"

# Run the script
.\docker-run-wsl.ps1
```

The script will show a menu with all options.

---

## 🔧 Direct WSL Commands (Alternative)

If you prefer to use WSL directly:

```bash
# Open WSL terminal
wsl

# Navigate to project (in WSL)
cd /mnt/d/Project/Katara\ Dental/TDL/Pramit/CRM\ SAAS

# Then use standard docker-compose commands
docker-compose up -d --build
docker-compose logs -f
docker-compose down
```

---

## 🌐 Access URLs

- **Application**: http://localhost:8016
- **API Documentation**: http://localhost:8016/docs
- **ReDoc**: http://localhost:8016/redoc
- **Health Check**: http://localhost:8016/health

---

## 🐛 Troubleshooting

### Check if Docker is running:
```powershell
wsl docker info
```

### Check container logs:
```powershell
wsl docker logs crm-saas
```

### Remove and rebuild:
```powershell
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose down && docker-compose up -d --build"
```

### Check port usage:
```powershell
netstat -ano | findstr :8016
```

---

## 📋 Environment Variables

You can set environment variables in PowerShell before running:

```powershell
$env:SECRET_KEY = "your-secret-key-here"
$env:DEBUG = "true"
wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d"
```

---

## ✅ Quick Reference

| Action | Command |
|--------|---------|
| Build & Start | `wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d --build"` |
| Start | `wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose up -d"` |
| Stop | `wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose stop"` |
| Logs | `wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose logs -f"` |
| Down | `wsl bash -c "cd '/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS' && docker-compose down"` |

---

**Note**: Port 8016 is mapped to container port 8000. The application runs on port 8000 inside the container, but is accessible on port 8016 from your host machine.

