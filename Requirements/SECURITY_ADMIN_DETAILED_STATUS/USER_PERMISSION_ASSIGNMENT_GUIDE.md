# User Permission Assignment Guide (Marathi/English)

**Date:** December 27, 2025

---

## 🎯 नवीन User ला Permissions कसे द्यायचे

### सोपी पद्धत (Recommended):

**1. User Create करताना Role Set करा:**

```bash
POST /api/companies/{company_id}/users

Request Body:
{
  "first_name": "Raj",
  "last_name": "Patel",
  "email": "raj@example.com",
  "password": "Password123",
  "role": "manager",  // ← येथे role set करा
  "phone": "+91-9876543210"
}
```

**Available Roles:**
- `super_admin` - सर्व permissions
- `admin` - Company admin (सर्व permissions)
- `manager` - Manager (बहुतेक permissions)
- `sales_rep` - Sales rep (limited permissions)
- `user` - Read-only

**2. Permissions Automatically Apply होतील:**
- Role च्या आधारे permissions database मधून automatically मिळतात
- काहीही manual setup करण्याची गरज नाही

---

## 🔧 Advanced: Custom Permissions

### जर specific permissions हवे असतील:

**Method 1: Permissions UI मधून**

1. Login करा (admin/super_admin)
2. Permissions Page → "Role Permissions" Tab
3. Matrix मध्ये permissions toggle करा
4. "Save Changes" click करा

**Method 2: API मधून**

```bash
POST /api/companies/{company_id}/role-permissions/bulk-update

Request Body:
{
  "role": "user",
  "permissions": [
    {"permission_id": 1, "granted": true},   // customer:create
    {"permission_id": 2, "granted": true},   // customer:read
    {"permission_id": 3, "granted": false}   // customer:update (deny)
  ]
}
```

---

## 📊 Complete Example

### Scenario: नवीन Manager Create करायचा

**Step 1: User Create**
```bash
POST http://localhost:8000/api/companies/1/users

Headers:
  Authorization: Bearer {token}
  Content-Type: application/json

Body:
{
  "first_name": "Raj",
  "last_name": "Patel",
  "email": "raj.patel@company.com",
  "password": "SecurePass123",
  "role": "manager",
  "phone": "+91-9876543210"
}
```

**Step 2: Result**
- User create होईल
- Role "manager" assign होईल
- Manager role च्या सर्व permissions automatically मिळतील:
  - ✅ Customer: create, read, update, delete
  - ✅ Lead: create, read, update, delete, convert
  - ✅ Deal: create, read, update, delete
  - ✅ Task: create, read, update, delete
  - ❌ User: delete (restricted)
  - ❌ Company: delete (restricted)

---

## 🎨 UI मधून Permissions Set करणे

### Role Permissions Change करणे:

1. **Permissions Page Open करा:**
   ```
   Login → Navbar → "Permissions" → "Role Permissions" Tab
   ```

2. **Matrix मध्ये Change करा:**
   - Checkbox check = Permission grant
   - Checkbox uncheck = Permission deny

3. **Save करा:**
   - "Save Changes" button click करा
   - सर्व users ज्यांचा तो role आहे, त्यांना automatically apply होईल

### Company-Specific Permissions:

1. **Company Permissions Tab:**
   ```
   Permissions → "Company Permissions" Tab
   ```

2. **Company Select करा:**
   - Dropdown मधून company select करा

3. **Permissions Toggle करा:**
   - Matrix मध्ये permissions change करा

4. **Save करा:**
   - "Save Company Permissions" click करा

---

## 🔐 Role Permissions Chart

| Role | Create | Read | Update | Delete | Special |
|------|--------|------|--------|--------|---------|
| **Super Admin** | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |
| **Admin** | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All (Company) |
| **Manager** | ✅ All | ✅ All | ✅ All | ⚠️ Limited | ❌ No User/Company Delete |
| **Sales Rep** | ✅ All | ✅ All | ✅ All | ⚠️ Limited | ❌ No Deal/User/Company Delete |
| **User** | ❌ None | ✅ All | ❌ None | ❌ None | Read-only |

---

## 📝 Step-by-Step (Marathi)

### नवीन User ला Permissions देणे:

**पद्धत 1: User Create करताना (सोपी)**

1. User Create API call करा:
   ```json
   {
     "first_name": "नाव",
     "last_name": "आडनाव",
     "email": "email@example.com",
     "password": "पासवर्ड",
     "role": "manager"  // ← Role येथे set करा
   }
   ```

2. Permissions automatically apply होतील!

**पद्धत 2: UI मधून (Visual)**

1. Permissions Page open करा
2. Role Permissions Tab → Matrix मध्ये permissions toggle करा
3. Save Changes click करा
4. User ला तो role assign करा

**पद्धत 3: Company-Specific**

1. Permissions → Company Permissions Tab
2. Company select करा
3. Permissions toggle करा
4. Save Company Permissions click करा

---

## ⚠️ Important Points

1. **Role Priority:**
   - Company role > Global role
   - Super admin = Always all permissions

2. **Default Permissions:**
   - Database मध्ये already seeded आहेत
   - Role-permission mappings default मध्ये set आहेत

3. **Bulk Changes:**
   - Role permissions change केल्यास, सर्व users ज्यांचा तो role आहे, त्यांना apply होईल

---

## 🔗 API Endpoints

### User Create:
```
POST /api/companies/{company_id}/users
```

### Role Update:
```
PUT /api/companies/{company_id}/users/{user_id}/role
```

### Permissions Bulk Update:
```
POST /api/companies/{company_id}/role-permissions/bulk-update
```

### Company Role Permissions:
```
GET /api/companies/{company_id}/role-permissions?role={role}
```

---

## 📚 Summary

**सोपी पद्धत:**
1. User create करा role सह
2. Permissions automatically apply होतील

**Advanced पद्धत:**
1. Permissions UI → Role Permissions Tab
2. Permissions toggle करा
3. Save करा

**Company-Specific:**
1. Permissions UI → Company Permissions Tab
2. Company select करा
3. Permissions set करा
4. Save करा

---

**Ready to use!** 🚀

