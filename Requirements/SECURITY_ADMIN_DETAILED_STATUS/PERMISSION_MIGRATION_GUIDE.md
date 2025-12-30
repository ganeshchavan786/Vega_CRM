# Permission Migration Guide

**Date:** December 27, 2025

---

## 📋 Migration Steps

### Step 1: Create Permission Tables

Run the migration script to create the permission tables:

```powershell
python scripts/create_permission_tables.py
```

**What it does:**
- Creates `permissions` table
- Creates `role_permissions` table
- Checks if tables already exist (safe to run multiple times)

---

### Step 2: Seed Default Permissions

Run the seed script to populate default permissions:

```powershell
python scripts/seed_default_permissions.py
```

**What it does:**
- Creates 32 default permissions (customer, lead, deal, task, activity, contact, user, company CRUD)
- Creates default role permissions for:
  - Manager role (all permissions except sensitive deletes)
  - Sales rep role (most permissions, restricted deletes)
  - User role (read-only)
- Skips existing permissions (safe to run multiple times)

---

### Step 3: Complete Migration (Both Steps)

Run the complete migration script:

```powershell
python scripts/migrate_permissions.py
```

**What it does:**
- Runs both table creation and seeding
- Complete migration in one command

---

## 📊 Default Permissions Created

### Resources & Actions:
- **Customer:** create, read, update, delete (4 permissions)
- **Lead:** create, read, update, delete, convert (5 permissions)
- **Deal:** create, read, update, delete (4 permissions)
- **Task:** create, read, update, delete (4 permissions)
- **Activity:** create, read, update, delete (4 permissions)
- **Contact:** create, read, update, delete (4 permissions)
- **User:** create, read, update, delete (4 permissions)
- **Company:** create, read, update, delete (4 permissions)

**Total: 33 permissions**

---

## 📊 Default Role Permissions

### Manager Role:
- ✅ All customer, lead, deal, task, activity, contact permissions
- ❌ Cannot delete users or companies (handled in code)

### Sales Rep Role:
- ✅ All customer, lead, task, activity, contact permissions
- ✅ Deal create, read, update (delete restricted)
- ❌ Cannot delete users, companies, or deals (handled in code)

### User Role:
- ✅ Read-only access to all resources
- ❌ No create, update, or delete permissions

---

## 🔍 Verify Migration

### Check Tables:
```python
from app.database import SessionLocal
from app.models.permission import Permission, RolePermission

db = SessionLocal()

# Count permissions
permission_count = db.query(Permission).count()
print(f"Total permissions: {permission_count}")

# Count role permissions
role_perm_count = db.query(RolePermission).count()
print(f"Total role permissions: {role_perm_count}")

db.close()
```

---

## ⚠️ Notes

1. **Safe to Run Multiple Times:**
   - Scripts check for existing data before creating
   - Won't create duplicates

2. **Database Tables:**
   - Tables are created automatically on app startup (via `Base.metadata.create_all()`)
   - Migration script is for explicit control

3. **Default Permissions:**
   - Super admin and admin roles get all permissions automatically (handled in `has_permission()`)
   - Role permissions are for manager, sales_rep, and user roles

4. **Company-Specific Permissions:**
   - Can be added later via API
   - Set `company_id` when creating role permissions

---

## 🎯 Next Steps After Migration

1. ✅ Verify tables created
2. ✅ Verify permissions seeded
3. ⏳ Update `has_permission()` to check database
4. ⏳ Test permission system

---

**Status:** ✅ Migration scripts ready

**Last Updated:** December 27, 2025

