# 🚀 Quick Push Commands

## ✅ Simple Commands (Copy-Paste):

### Option 1: Use Simple Script
```powershell
.\scripts\push_to_github_simple.ps1
```

### Option 2: Manual Commands
```powershell
git add .
git commit -m "feat: DataTable integration, navigation updates, and bug fixes"
git push origin main
```

---

## ✅ What Happens:

1. **Code pushed** → GitHub पर्यंत code push होईल
2. **Workflow triggers** → GitHub Actions automatically trigger होईल
3. **Docker image builds** → ~2-5 minutes मध्ये build होईल
4. **Image pushed to GHCR** → `ghcr.io/ganeshchavan786/vega_crm:latest`

**होय, दोन्ही होईल:**
- ✅ Code push होईल
- ✅ Docker image automatically build होईल आणि GHCR वर push होईल

---

**Run command आणि push करा!** 🚀

