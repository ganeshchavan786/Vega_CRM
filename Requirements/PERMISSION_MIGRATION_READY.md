# Permission Migration - Ready ✅

**Date:** December 27, 2025

---

## ✅ Migration Scripts Created

### 1. Table Creation Script
📄 **`scripts/create_permission_tables.py`**

**Usage:**
```powershell
python scripts/create_permission_tables.py
```

**What it does:**
- Creates `permissions` table
- Creates `role_permissions` table
- Checks if tables exist (safe to run multiple times)

---

### 2. Seed Script
📄 **`scripts/seed_default_permissions.py`**

**Usage:**
```powershell
python scripts/seed_default_permissions.py
```

**What it does:**
- Creates 33 default permissions (8 resources × 4 actions + lead:convert)
- Creates default role permissions for manager, sales_rep, user roles
- Skips existing permissions (safe to run multiple times)

---

### 3. Complete Migration Script
📄 **`scripts/migrate_permissions.py`**

**Usage:**
```powershell
python scripts/migrate_permissions.py
```

**What it does:**
- Runs both table creation and seeding
- Complete migration in one command

---

## 📊 Default Permissions

### Resources (8):
1. **customer** - create, read, update, delete
2. **lead** - create, read, update, delete, convert
3. **deal** - create, read, update, delete
4. **task** - create, read, update, delete
5. **activity** - create, read, update, delete
6. **contact** - create, read, update, delete
7. **user** - create, read, update, delete
8. **company** - create, read, update, delete

**Total: 33 permissions**

---

## 📊 Default Role Permissions

### Manager Role:
- ✅ All permissions except user:delete and company:delete

### Sales Rep Role:
- ✅ Most permissions except user:delete, company:delete, deal:delete

### User Role:
- ✅ Read-only (read permissions only)

---

## 🚀 Quick Start

### Option 1: Complete Migration (Recommended)
```powershell
python scripts/migrate_permissions.py
```

### Option 2: Step by Step
```powershell
# Step 1: Create tables
python scripts/create_permission_tables.py

# Step 2: Seed permissions
python scripts/seed_default_permissions.py
```

---

## ✅ Ready to Run

**Status:** ✅ Migration scripts ready

**Next:** Run the migration script to create tables and seed permissions

---

**Last Updated:** December 27, 2025

