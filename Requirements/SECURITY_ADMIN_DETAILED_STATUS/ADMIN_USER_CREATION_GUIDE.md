# Admin User Creation Guide

## Problem
`admin@crm.com` user does NOT exist in database.

## Current Database Users
From database check:
- `test_admin@example.com` - Role: admin ✅
- `superadmin@test.com` - Role: super_admin ✅
- `test_manager@example.com` - Role: manager
- `test_sales_rep@example.com` - Role: sales_rep
- `test_user@example.com` - Role: user

## Solution Options

### Option 1: Create admin@crm.com user (Recommended)

Run this script:
```powershell
python scripts\create_admin_user.py
```

This will create:
- Email: `admin@crm.com`
- Password: `Admin@123`
- Role: `admin`

### Option 2: Use existing admin user

Login with:
- Email: `test_admin@example.com`
- Password: (check database or reset)

Or:
- Email: `superadmin@test.com`
- Password: (check database or reset)

### Option 3: Update existing user email

Update `test_admin@example.com` email to `admin@crm.com`:
```python
# Run in Python console
python scripts\update_user_role.py test_admin@example.com admin
# Then update email manually in database
```

## Quick Fix

**Run this command to create admin@crm.com:**
```powershell
python scripts\create_admin_user.py
```

Then login with:
- Email: `admin@crm.com`
- Password: `Admin@123`

Admin menu link will show in profile dropdown! ✅

