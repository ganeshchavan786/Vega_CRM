# Permission UI Design & Flow

**Date:** December 27, 2025  
**Purpose:** Permission Management Frontend UI Design

---

## 📋 Overview

Permission Management UI will allow admins to:
1. View all permissions (resource:action combinations)
2. View role-permission mappings
3. Grant/revoke permissions for roles
4. Manage company-specific permissions
5. Bulk update permissions

---

## 🎯 User Flow

### Flow 1: View Permissions

```
Login → Dashboard → Settings → Permissions
    │
    ├─> Permissions List Page
    │   ├─> All Permissions Table
    │   │   - Resource (e.g., "customer")
    │   │   - Action (e.g., "create")
    │   │   - Description
    │   │   - Actions (View, Edit)
    │   │
    │   └─> Search/Filter
    │       - Filter by Resource
    │       - Filter by Action
```

### Flow 2: Manage Role Permissions

```
Permissions Page → Role Permissions Tab
    │
    ├─> Role Permissions Matrix
    │   ├─> Roles (columns): super_admin, admin, manager, sales_rep, user
    │   ├─> Permissions (rows): customer:create, customer:read, etc.
    │   ├─> Checkboxes for each role-permission combination
    │   │
    │   └─> Actions:
    │       - Save Changes (bulk update)
    │       - Reset to Defaults
    │       - Export (CSV/JSON)
```

### Flow 3: Company-Specific Permissions

```
Permissions Page → Company Permissions Tab
    │
    ├─> Select Company Dropdown
    │
    ├─> Company Role Permissions Matrix
    │   ├─> Same as Role Permissions Matrix
    │   ├─> But scoped to selected company
    │   │
    │   └─> Actions:
    │       - Save Company Permissions
    │       - Copy from Global
    │       - Reset Company Permissions
```

---

## 🎨 UI Design

### Page 1: Permissions List

```
┌─────────────────────────────────────────────────────────────┐
│  Permissions Management                        [Back] [Help] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [All Permissions] [Role Permissions] [Company Permissions]  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🔍 Search...                    Filter: [All] [▼]    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Resource  │ Action    │ Description         │ Actions│   │
│  ├───────────┼───────────┼─────────────────────┼────────┤   │
│  │ customer  │ create    │ Create customers    │ [View] │   │
│  │ customer  │ read      │ View customers      │ [View] │   │
│  │ customer  │ update    │ Update customers    │ [View] │   │
│  │ customer  │ delete    │ Delete customers    │ [View] │   │
│  │ lead      │ create    │ Create leads        │ [View] │   │
│  │ lead      │ read      │ View leads          │ [View] │   │
│  │ lead      │ update    │ Update leads        │ [View] │   │
│  │ lead      │ delete    │ Delete leads        │ [View] │   │
│  │ lead      │ convert   │ Convert leads       │ [View] │   │
│  │ ...       │ ...       │ ...                 │ [View] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Showing 1-10 of 35 permissions        [< Prev] [Next >]     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Page 2: Role Permissions Matrix

```
┌─────────────────────────────────────────────────────────────┐
│  Role Permissions                            [Save] [Reset]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Permission          │ Admin │ Manager│ Sales │ User │   │
│  ├─────────────────────┼───────┼────────┼───────┼──────┤   │
│  │ customer:create     │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ customer:read       │  ☑    │   ☑    │   ☑   │  ☑   │   │
│  │ customer:update     │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ customer:delete     │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ lead:create         │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ lead:read           │  ☑    │   ☑    │   ☑   │  ☑   │   │
│  │ lead:update         │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ lead:delete         │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ lead:convert        │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ deal:create         │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ deal:read           │  ☑    │   ☑    │   ☑   │  ☑   │   │
│  │ deal:update         │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ deal:delete         │  ☑    │   ☐    │   ☐   │  ☐   │   │
│  │ user:delete         │  ☑    │   ☐    │   ☐   │  ☐   │   │
│  │ company:delete      │  ☑    │   ☐    │   ☐   │  ☐   │   │
│  │ ...                 │  ...  │  ...   │  ...  │  ... │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  [Save Changes] [Reset to Defaults] [Export CSV] [Export JSON]│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Page 3: Company Permissions

```
┌─────────────────────────────────────────────────────────────┐
│  Company Permissions                  [Save] [Copy Global]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Select Company: [Acme Corp ▼]                              │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Permission          │ Admin │ Manager│ Sales │ User │   │
│  ├─────────────────────┼───────┼────────┼───────┼──────┤   │
│  │ customer:create     │  ☑    │   ☑    │   ☑   │  ☐   │   │
│  │ customer:read       │  ☑    │   ☑    │   ☑   │  ☑   │   │
│  │ ...                 │  ...  │  ...   │  ...  │  ... │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ℹ️ Company-specific permissions override global permissions  │
│                                                               │
│  [Save Company Permissions] [Copy from Global] [Reset]       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Page 4: Permission Detail View

```
┌─────────────────────────────────────────────────────────────┐
│  Permission: customer:create                    [Edit] [Back]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Resource: customer                                           │
│  Action: create                                               │
│  Description: Create new customers                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Roles with this permission:                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ ☑ Admin (Global)                                     │   │
│  │ ☑ Manager (Global)                                   │   │
│  │ ☑ Sales Rep (Global)                                 │   │
│  │ ☐ User (Global)                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Company-specific permissions:                        │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Acme Corp:                                           │   │
│  │   ☑ Admin  ☑ Manager  ☑ Sales Rep  ☐ User          │   │
│  │                                                       │   │
│  │ Tech Solutions:                                      │   │
│  │   ☑ Admin  ☑ Manager  ☐ Sales Rep  ☐ User          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Created: 2025-12-27 10:00:00                                │
│  Updated: 2025-12-27 15:30:00                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 User Interactions

### Interaction 1: Toggle Role Permission

```
1. User clicks checkbox in Role Permissions Matrix
   │
   ├─> Checkbox state changes (☐ → ☑ or ☑ → ☐)
   │
   ├─> Change tracked in local state
   │
   └─> [Save Changes] button becomes active (highlighted)
```

### Interaction 2: Save Role Permissions

```
1. User clicks [Save Changes]
   │
   ├─> Loading indicator shown
   │
   ├─> API Call: POST /api/companies/{company_id}/permissions/bulk-update
   │   │
   │   └─> Request Body:
   │       {
   │         "role": "manager",
   │         "permissions": [
   │           {"permission_id": 1, "granted": true},
   │           {"permission_id": 2, "granted": false},
   │           ...
   │         ]
   │       }
   │
   ├─> Success: Green toast notification "Permissions updated successfully"
   │
   └─> Error: Red toast notification with error message
```

### Interaction 3: Filter Permissions

```
1. User selects filter (e.g., "customer" resource)
   │
   ├─> Table filters to show only customer permissions
   │
   └─> URL updates: /permissions?resource=customer
```

### Interaction 4: Select Company for Company Permissions

```
1. User selects company from dropdown
   │
   ├─> API Call: GET /api/companies/{company_id}/permissions/roles/{role}
   │
   ├─> Matrix updates with company-specific permissions
   │
   └─> [Save Company Permissions] button becomes active
```

---

## 📱 Responsive Design

### Desktop (> 1024px)
- Full matrix view with all columns visible
- Side-by-side layout
- Large checkboxes for easy clicking

### Tablet (768px - 1024px)
- Horizontal scroll for matrix
- Collapsible sections
- Touch-friendly checkboxes

### Mobile (< 768px)
- Stacked layout
- Accordion-style sections per role
- Swipeable cards
- Bottom sheet for company selection

---

## 🎨 Color Coding

### Permission States:
- ✅ **Granted (☑)**: Green checkmark
- ❌ **Denied (☐)**: Gray unchecked
- ⚠️ **Overridden**: Orange indicator (company-specific overrides global)

### Role Colors:
- **Super Admin**: Purple/Pink gradient
- **Admin**: Blue
- **Manager**: Green
- **Sales Rep**: Orange
- **User**: Gray

### Status Indicators:
- **Success**: Green background + white text
- **Warning**: Yellow background + black text
- **Error**: Red background + white text
- **Info**: Blue background + white text

---

## 🔐 Access Control

### Who Can Access:
- ✅ Super Admin: Full access (all companies)
- ✅ Admin: Company-specific permissions only
- ❌ Manager, Sales Rep, User: No access (403 error)

### Permission Check:
```javascript
// Before showing page
if (currentUser.role !== 'super_admin' && currentUser.role !== 'admin') {
    showError('Access Denied');
    redirectToDashboard();
}
```

---

## 📊 Data Flow

### 1. Load Permissions
```
Page Load
    │
    ├─> API: GET /api/permissions
    │   └─> Response: List of all permissions
    │
    ├─> API: GET /api/permissions/roles
    │   └─> Response: All role-permission mappings
    │
    └─> Render Matrix with data
```

### 2. Update Permission
```
User clicks checkbox
    │
    ├─> Update local state
    │
    ├─> User clicks [Save]
    │
    ├─> API: POST /api/companies/{company_id}/permissions/bulk-update
    │   └─> Request: { role, permissions: [...] }
    │
    └─> Refresh matrix with updated data
```

### 3. Company Permissions
```
User selects company
    │
    ├─> API: GET /api/companies/{company_id}/permissions/roles
    │   └─> Response: Company-specific role-permissions
    │
    └─> Render matrix with company data
```

---

## 🗂️ File Structure

```
frontend/
├── pages/
│   └── permissions.html          # Permissions page
│
└── js/
    ├── pages/
    │   └── permissions.js        # Permissions logic
    │
    └── components/
        └── permission-matrix.js  # Reusable matrix component
```

---

## 🔗 API Endpoints Used

1. **GET** `/api/permissions` - List all permissions
2. **GET** `/api/permissions/{permission_id}` - Get permission details
3. **GET** `/api/permissions/roles` - Get all role-permissions
4. **GET** `/api/companies/{company_id}/permissions/roles` - Get company role-permissions
5. **POST** `/api/companies/{company_id}/permissions/bulk-update` - Bulk update permissions
6. **POST** `/api/permissions` - Create new permission (admin only)
7. **PUT** `/api/permissions/{permission_id}` - Update permission (admin only)
8. **DELETE** `/api/permissions/{permission_id}` - Delete permission (admin only)

---

## 🎯 Features Summary

### Must Have (MVP):
- ✅ View all permissions
- ✅ View role-permission matrix
- ✅ Toggle role permissions
- ✅ Save changes (bulk update)
- ✅ Company-specific permissions view

### Nice to Have:
- ⏳ Search/Filter permissions
- ⏳ Export permissions (CSV/JSON)
- ⏳ Permission detail view
- ⏳ Copy permissions from global to company
- ⏳ Permission history/audit log
- ⏳ Permission templates/presets

---

## 🚀 Implementation Plan

### Phase 1: Basic UI (MVP)
1. Create `permissions.html` page
2. Create `permissions.js` logic
3. List all permissions
4. Basic role-permission matrix
5. Save functionality

### Phase 2: Enhanced Features
1. Search/Filter
2. Company-specific permissions
3. Permission detail view
4. Export functionality

### Phase 3: Advanced Features
1. Permission templates
2. Audit log
3. Bulk operations
4. Advanced filtering

---

**Status:** Design Complete ✅  
**Next:** Implementation

