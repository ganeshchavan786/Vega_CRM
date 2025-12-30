# How to Assign Permissions to New User

**Date:** December 27, 2025  
**Language:** Marathi/English

---

## 📋 Overview

नवीन user ला permissions देण्यासाठी 2 पद्धती आहेत:

1. **Role-Based Permissions** (सोपी पद्धत)
   - User ला role assign करा (admin, manager, sales_rep, user)
   - Role च्या आधारे permissions automatically मिळतात

2. **Custom Permissions** (Advanced)
   - Specific permissions manually assign करा
   - Company-specific permissions set करा

---

## 🎯 Method 1: Role-Based Permissions (Recommended)

### Step 1: User Create करा

**API Endpoint:**
```
POST /api/companies/{company_id}/users
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123",
  "role": "manager",  // ← Role येथे set करा
  "phone": "+91-9876543210"
}
```

**Available Roles:**
- `super_admin` - सर्व permissions (सर्व companies)
- `admin` - Company admin (सर्व permissions company मध्ये)
- `manager` - Manager (बहुतेक permissions, काही restrictions)
- `sales_rep` - Sales Representative (create/read/update, limited delete)
- `user` - Regular User (read-only)

### Step 2: Company मध्ये Add करा

User create झाल्यावर, त्याला company मध्ये add करा:

**API Endpoint:**
```
POST /api/companies/{company_id}/users/{user_id}/assign
```

**Request Body:**
```json
{
  "role": "manager",  // ← Company मध्ये काय role द्यायचा
  "is_primary": false
}
```

**Company Roles:**
- `admin` - Company admin
- `manager` - Company manager
- `sales_rep` - Sales rep
- `user` - Regular user

---

## 🔧 Method 2: Custom Permissions (Advanced)

### Step 1: User Create करा (Role सह)

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "password": "Password123",
  "role": "user"  // Base role
}
```

### Step 2: Specific Permissions Assign करा

**API Endpoint:**
```
POST /api/companies/{company_id}/role-permissions
```

**Request Body:**
```json
{
  "permission_id": 1,  // Permission ID (e.g., customer:create)
  "role": "user",      // User चा role
  "company_id": 1,     // Company ID (company-specific permission)
  "granted": true      // true = allow, false = deny
}
```

### Step 3: Bulk Permissions Assign करा

**API Endpoint:**
```
POST /api/companies/{company_id}/role-permissions/bulk-update
```

**Request Body:**
```json
{
  "role": "user",
  "permissions": [
    {
      "permission_id": 1,  // customer:create
      "granted": true
    },
    {
      "permission_id": 2,  // customer:read
      "granted": true
    },
    {
      "permission_id": 3,  // customer:update
      "granted": false     // Deny update
    }
  ]
}
```

---

## 📊 Permission Flow

```
New User Created
    │
    ├─> Global Role Assigned (user.role)
    │   └─> Global Permissions Applied
    │
    ├─> Company Role Assigned (UserCompany.role)
    │   └─> Company-Specific Permissions Applied
    │
    └─> Custom Permissions (Optional)
        └─> Specific Permissions Override
```

---

## 🎯 Example: Complete Flow

### Scenario: नवीन Manager Create करायचा

**Step 1: User Create**
```bash
POST /api/companies/1/users
{
  "first_name": "Raj",
  "last_name": "Patel",
  "email": "raj.patel@company.com",
  "password": "SecurePass123",
  "role": "manager",
  "phone": "+91-9876543210"
}
```

**Step 2: Company मध्ये Add (Optional - जर user already exists)**
```bash
POST /api/companies/1/users/{user_id}/assign
{
  "role": "manager",
  "is_primary": true
}
```

**Result:**
- User ला "manager" role मिळेल
- Manager role च्या सर्व permissions automatically apply होतील:
  - ✅ customer:create, read, update, delete
  - ✅ lead:create, read, update, delete, convert
  - ✅ deal:create, read, update, delete
  - ❌ user:delete (restricted)
  - ❌ company:delete (restricted)

---

## 🔐 Role Permissions Summary

### Super Admin
- ✅ सर्व permissions (सर्व companies)
- ✅ User management
- ✅ Company management
- ✅ Permission management

### Admin
- ✅ Company मध्ये सर्व permissions
- ✅ User management (company मध्ये)
- ❌ Company delete (restricted)

### Manager
- ✅ Create, Read, Update (सर्व resources)
- ✅ Delete (except users, companies)
- ❌ User delete
- ❌ Company delete

### Sales Rep
- ✅ Create, Read, Update (सर्व resources)
- ✅ Lead convert
- ❌ Deal delete
- ❌ User delete
- ❌ Company delete

### User
- ✅ Read-only (सर्व resources)
- ❌ Create, Update, Delete (सर्व resources)

---

## 🛠️ UI मधून Permissions Assign करणे

### Step 1: Permissions Page Open करा
```
Login → Navbar → "Permissions" → "Role Permissions" Tab
```

### Step 2: Role Select करा
Matrix मध्ये role column select करा (Admin, Manager, Sales Rep, User)

### Step 3: Permissions Toggle करा
- Checkbox check करा = Permission grant
- Checkbox uncheck करा = Permission deny

### Step 4: Save करा
"Save Changes" button click करा

### Step 5: User ला Role Assign करा
```
Users Page → Edit User → Role Change करा
```

---

## 📝 Step-by-Step Guide (Marathi)

### नवीन User ला Permissions देणे:

**1. User Create करा:**
```
POST /api/companies/{company_id}/users
Body: {
  "first_name": "नाव",
  "last_name": "आडनाव",
  "email": "email@example.com",
  "password": "पासवर्ड",
  "role": "manager"  // ← Role येथे set करा
}
```

**2. Company मध्ये Add करा (जर needed):**
```
POST /api/companies/{company_id}/users/{user_id}/assign
Body: {
  "role": "manager",  // Company मध्ये काय role
  "is_primary": true
}
```

**3. Permissions Automatically Apply होतील:**
- Role च्या आधारे permissions automatically मिळतात
- Database मध्ये role-permission mappings already आहेत
- Custom permissions हवे असल्यास UI मधून set करा

---

## 🎨 UI मधून Custom Permissions

### Company-Specific Permissions:

1. Permissions Page → "Company Permissions" Tab
2. Company Select करा
3. Matrix मध्ये permissions toggle करा
4. "Save Company Permissions" click करा

**Example:**
- Company "Acme Corp" मध्ये
- User "Raj" ला "manager" role
- But "deal:delete" permission deny करायचे
- Company Permissions Tab → Acme Corp select → deal:delete uncheck → Save

---

## ⚠️ Important Notes

1. **Global Role vs Company Role:**
   - Global role: `user.role` (सर्व companies साठी)
   - Company role: `UserCompany.role` (specific company साठी)
   - Company role priority जास्त आहे

2. **Permission Priority:**
   ```
   Super Admin → Always All
   Company Admin → All in Company
   Company Role Permissions → Override Global
   Global Role Permissions → Fallback
   ```

3. **Default Permissions:**
   - Permissions already seeded आहेत database मध्ये
   - Role-permission mappings default मध्ये set आहेत
   - Custom changes UI मधून करू शकता

---

## 🔄 Quick Reference

### User Create करताना Role Set करा:
```json
{
  "role": "manager"  // admin, manager, sales_rep, user
}
```

### Company मध्ये Role Assign करा:
```json
{
  "role": "manager",
  "is_primary": true
}
```

### Custom Permissions Set करा:
```
Permissions UI → Role Permissions Tab → Toggle → Save
```

---

## 📚 Related Files

- **User Creation:** `app/routes/user.py` - `create_user()`
- **Role Assignment:** `app/routes/user.py` - `update_user_role()`
- **Permission Management:** `app/routes/permission.py`
- **Permission UI:** `frontend/pages/permissions.html`

---

**Summary:** नवीन user ला permissions देण्यासाठी, user create करताना role set करा. Role च्या आधारे permissions automatically apply होतील. Custom permissions हवे असल्यास Permissions UI मधून set करा.

