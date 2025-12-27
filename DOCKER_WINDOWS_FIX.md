# 🐳 Docker Windows Fix - Quick Guide

## Problem:
Docker is in **Windows containers mode** but needs **Linux containers mode**.

## Quick Fix:

### Step 1: Switch to Linux Containers
1. **Right-click** Docker Desktop icon (system tray, bottom right)
2. Click **"Switch to Linux containers"**
3. Wait ~30 seconds for Docker to restart

### Step 2: Build Again
```powershell
docker build -t vega-crm:latest .
```

---

## Verify Docker Mode:
```powershell
docker version
```

Look for: **OSType: linux** (should be linux, not windows)

---

**That's it! Switch to Linux containers and build again.** ✅

