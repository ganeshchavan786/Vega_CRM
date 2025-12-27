# CRM SAAS Docker Scripts

## 📋 Available Scripts

### For WSL/Bash Users (Use .sh files):

1. **docker-run.sh** - Interactive menu with all options
2. **start-docker.sh** - Quick start containers
3. **stop-docker.sh** - Stop containers
4. **restart-docker.sh** - Restart containers
5. **view-logs.sh** - View container logs

### For PowerShell Users (Use .ps1 files):

1. **docker-run-wsl.ps1** - Interactive menu with all options
2. **start-docker.ps1** - Quick start containers
3. **stop-docker.ps1** - Stop containers
4. **restart-docker.ps1** - Restart containers
5. **view-logs.ps1** - View container logs

---

## 🚀 Quick Start (WSL/Bash)

### First Time Setup:

```bash
# Navigate to scripts folder (in WSL)
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS/scripts"

# Make scripts executable (one time only)
chmod +x *.sh

# Run the interactive menu
./docker-run.sh
```

### Quick Commands:

```bash
# Start containers
./start-docker.sh

# Stop containers
./stop-docker.sh

# Restart containers
./restart-docker.sh

# View logs
./view-logs.sh
```

---

## 🔧 Direct Docker Commands (WSL)

If you prefer to use docker-compose directly:

```bash
# Navigate to project root (in WSL)
cd "/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS"

# Build and start
docker-compose up -d --build

# Start (already built)
docker-compose up -d

# Stop
docker-compose stop

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Stop and remove
docker-compose down

# View status
docker ps -a --filter "name=crm-saas"
```

---

## 💻 PowerShell Commands (Windows)

If you're using PowerShell (not WSL bash):

```powershell
# Navigate to scripts folder
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS\scripts"

# Run PowerShell scripts
.\start-docker.ps1
.\stop-docker.ps1
.\restart-docker.ps1
.\view-logs.ps1
.\docker-run-wsl.ps1
```

---

## 🌐 Access URLs

- **Application**: http://localhost:8016
- **API Docs**: http://localhost:8016/docs
- **ReDoc**: http://localhost:8016/redoc
- **Health Check**: http://localhost:8016/health

---

## ⚠️ Important Notes

1. **WSL Users**: Use `.sh` files (bash scripts)
2. **PowerShell Users**: Use `.ps1` files (PowerShell scripts)
3. **Path Format**: 
   - In WSL: `/mnt/d/Project/Katara Dental/TDL/Pramit/CRM SAAS`
   - In Windows: `D:\Project\Katara Dental\TDL\Pramit\CRM SAAS`

---

## 🐛 Troubleshooting

### Scripts not executable:
```bash
chmod +x /mnt/d/Project/Katara\ Dental/TDL/Pramit/CRM\ SAAS/scripts/*.sh
```

### Check Docker status:
```bash
docker info
```

### Check container logs:
```bash
docker logs crm-saas
```

### Check port usage:
```bash
netstat -tuln | grep 8016
```

---

## 📝 Quick Reference

| Action | WSL Command | PowerShell Command |
|--------|-------------|-------------------|
| Start | `./start-docker.sh` | `.\start-docker.ps1` |
| Stop | `./stop-docker.sh` | `.\stop-docker.ps1` |
| Restart | `./restart-docker.sh` | `.\restart-docker.ps1` |
| Logs | `./view-logs.sh` | `.\view-logs.ps1` |
| Menu | `./docker-run.sh` | `.\docker-run-wsl.ps1` |

