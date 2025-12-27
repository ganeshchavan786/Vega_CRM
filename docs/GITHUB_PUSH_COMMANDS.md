# 🚀 GitHub Push Commands - Step by Step

**For:** Pushing code to GitHub and activating GHCR workflow

---

## 📋 Quick Commands (Copy-Paste)

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\scripts\push_to_github.ps1
```

### Option 2: Manual Commands (Step by Step)

```powershell
# Step 1: Stage all changes
git add .

# Step 2: Check what will be committed (optional)
git status

# Step 3: Create commit
git commit -m "feat: DataTable integration, navigation updates, and bug fixes"

# Step 4: Push to GitHub
git push origin main
```

---

## 📝 Detailed Commands with Explanations

### Step 1: Navigate to Project Directory
```powershell
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"
```

### Step 2: Check Current Status
```powershell
git status
```
This shows what files are modified, deleted, or untracked.

### Step 3: Stage All Changes
```powershell
git add .
```
This stages all changes (modified, deleted, and new files).

### Step 4: Verify Staged Files (Optional)
```powershell
git status
```
This shows what will be committed.

### Step 5: Create Commit
```powershell
git commit -m "feat: DataTable integration, navigation updates, and bug fixes

- Integrate DataTable framework on all 7 pages
- Rename navigation: Customers → Accounts, Deals → Opportunities
- Fix API pagination limits
- Fix DataTable method existence checks
- Fix escapeHtml missing in contacts.js
- Fix backend contact route success_response meta parameter
- Organize files: Move docs to docs/, scripts to scripts/
- Add DataTable CSS/JS framework files
- Update all page files with DataTable integration
- Update navigation labels across all pages
- Add comprehensive documentation"
```

### Step 6: Push to GitHub
```powershell
git push origin main
```

**If you need to authenticate:**
```powershell
# Using Personal Access Token (Classic Token)
# When prompted for password, paste your token
git push origin main
```

**Or set up credential helper:**
```powershell
git config --global credential.helper wincred
git push origin main
```

---

## 🔐 Using GitHub Token (Classic Token)

### If Prompted for Credentials:

1. **Username:** Your GitHub username (`ganeshchavan786`)
2. **Password:** Paste your **Personal Access Token** (not your GitHub password)

### Token Setup (If Not Already Done):

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `write:packages` (Upload packages)
   - ✅ `read:packages` (Download packages)
4. Generate token
5. Copy token (save it securely, you won't see it again)
6. Use token as password when pushing

---

## 🚀 After Push - What Happens:

1. ✅ Code pushed to GitHub
2. ✅ GitHub Actions workflow triggers automatically
3. ✅ Docker image builds (~2-5 minutes)
4. ✅ Image pushed to GHCR
5. ✅ Image available at: `ghcr.io/ganeshchavan786/vega_crm:latest`

---

## ✅ Verify After Push:

### Check Workflow Status:
```powershell
# Open in browser
start https://github.com/ganeshchavan786/Vega_CRM/actions
```

### Check GHCR Package:
```powershell
# Open in browser
start https://github.com/users/ganeshchavan786/packages/container/package/vega_crm
```

### Pull Docker Image (After Build):
```powershell
docker pull ghcr.io/ganeshchavan786/vega_crm:latest
```

---

## 🏷️ Create Version Tag (Optional):

After successful push, you can create a version tag:

```powershell
# Create tag
git tag -a v1.0.0 -m "Version 1.0.0: Initial release with DataTable integration"

# Push tag
git push origin v1.0.0
```

This will trigger another workflow run and create a versioned image:
- `ghcr.io/ganeshchavan786/vega_crm:v1.0.0`

---

## 🔧 Troubleshooting

### Error: "Authentication failed"
**Solution:** Use Personal Access Token instead of password

### Error: "Permission denied"
**Solution:** Check token has `repo` scope

### Error: "Updates were rejected"
**Solution:** 
```powershell
git pull origin main
git push origin main
```

### Error: "Remote origin already exists"
**Solution:** Already configured, proceed with push

---

## 📊 Expected Output:

### Successful Push:
```
Enumerating objects: 150, done.
Counting objects: 100% (150/150), done.
Delta compression using up to 8 threads
Compressing objects: 100% (120/120), done.
Writing objects: 100% (150/150), 2.5 MiB | 5.2 MiB/s, done.
Total 150 (delta 45), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (45/45), completed.
To https://github.com/ganeshchavan786/Vega_CRM.git
   abc1234..def5678  main -> main
```

### Workflow Triggered:
- Go to GitHub Actions tab to see workflow running
- Wait 2-5 minutes for completion
- Docker image will be available in GHCR

---

## ✅ Complete Command Sequence:

```powershell
# Navigate to project
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"

# Stage all changes
git add .

# Commit
git commit -m "feat: DataTable integration, navigation updates, and bug fixes"

# Push to GitHub
git push origin main

# (Optional) Create version tag
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

---

**Ready to push!** 🚀

