# 🐳 Docker Windows Container Mode Fix

## ❌ Error:
```
no matching manifest for windows(10.0.19045)/amd64 in the manifest list entries
```

## 🔍 Problem:
Docker Desktop is running in **Windows containers mode** but trying to build a **Linux image**.

---

## ✅ Solution 1: Switch to Linux Containers (Recommended)

### Method 1: Using Docker Desktop GUI
1. **Right-click** Docker Desktop icon in system tray
2. Click **"Switch to Linux containers"**
3. Wait for Docker to restart
4. Try build again

### Method 2: Using Command Line
```powershell
# Check current context
docker version

# Switch to Linux containers (if using Docker Desktop)
# This requires Docker Desktop to be running
```

**Note:** If you see "OSType: linux" in `docker version`, you're already in Linux mode. The issue might be different.

---

## ✅ Solution 2: Use WSL2 Backend (Best for Windows)

### Enable WSL2 in Docker Desktop:
1. Open **Docker Desktop**
2. Go to **Settings** (gear icon)
3. Go to **General**
4. Check **"Use the WSL 2 based engine"**
5. Go to **Resources > WSL Integration**
6. Enable integration with your WSL distro
7. Click **Apply & Restart**

### Build from WSL2:
```bash
# In WSL2 terminal
cd /mnt/d/Project/Katara\ Dental/TDL/Pramit/CRM\ SAAS
docker build -t vega-crm:latest .
```

---

## ✅ Solution 3: Use Docker Buildx (Platform-specific Build)

```powershell
# Build for Linux platform explicitly
docker buildx build --platform linux/amd64 -t vega-crm:latest .

# Or if buildx not available, try:
docker build --platform linux/amd64 -t vega-crm:latest .
```

---

## 🔍 Check Docker Configuration

### Check Docker Context:
```powershell
# List contexts
docker context ls

# Check current context
docker context show

# Check Docker info
docker info
```

### Check Docker Version:
```powershell
docker version
```

Look for:
- **OSType:** Should be `linux` (not `windows`)
- **Architecture:** Should be `amd64`

---

## 🚀 Recommended Steps:

### Step 1: Switch Docker to Linux Containers
1. Right-click Docker Desktop icon in system tray
2. Click "Switch to Linux containers"
3. Wait for restart (~30 seconds)

### Step 2: Verify
```powershell
docker version
```

Should show:
```
OSType: linux
```

### Step 3: Build Again
```powershell
docker build -t vega-crm:latest .
```

---

## 📝 Alternative: Build in WSL2

If Docker Desktop doesn't work well:

1. **Install WSL2** (if not installed):
   ```powershell
   wsl --install
   ```

2. **Install Docker in WSL2**:
   ```bash
   # In WSL2
   sudo apt update
   sudo apt install docker.io
   sudo service docker start
   ```

3. **Build from WSL2**:
   ```bash
   cd /mnt/d/Project/Katara\ Dental/TDL/Pramit/CRM\ SAAS
   docker build -t vega-crm:latest .
   ```

---

## ✅ Quick Fix Summary:

**Easiest Solution:**
1. Right-click Docker Desktop tray icon
2. Click "Switch to Linux containers"
3. Wait for restart
4. Run build command again

---

**After switching to Linux containers, try building again!** 🚀

