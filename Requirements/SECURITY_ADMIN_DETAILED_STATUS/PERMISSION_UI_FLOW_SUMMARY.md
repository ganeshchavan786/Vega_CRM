# Permission UI Flow Summary (Text Format)

**Date:** December 27, 2025

---

## 📋 Simple Flow Description

### Main Flow:

```
1. User Login
   ↓
2. Go to Dashboard
   ↓
3. Click "Settings" → "Permissions"
   ↓
4. See Permissions Page with 3 Tabs:
   ├─ Tab 1: All Permissions (List)
   ├─ Tab 2: Role Permissions (Matrix)
   └─ Tab 3: Company Permissions (Matrix with Company Selector)
   ↓
5. User can:
   - View all permissions
   - Toggle checkboxes in matrix
   - Click "Save" to update
   - Select company to see company-specific permissions
```

---

## 🎯 Page Layout (Simple Text)

### Page Header:
- Title: "Permissions Management"
- Buttons: [Back] [Help] [Save] (when changes made)

### Tab Navigation:
```
[All Permissions] [Role Permissions] [Company Permissions]
```

### Tab 1: All Permissions
```
Search Box: [Search permissions...]

Table:
- Column 1: Resource (customer, lead, deal, etc.)
- Column 2: Action (create, read, update, delete, convert)
- Column 3: Description
- Column 4: Actions ([View] button)

Rows: Each permission listed
Pagination: [< Prev] [Next >]
```

### Tab 2: Role Permissions (Main Feature)
```
Matrix Table:
- Rows: Each permission (customer:create, customer:read, etc.)
- Columns: Roles (Admin, Manager, Sales Rep, User)
- Cells: Checkboxes (☑ or ☐)

Actions:
- [Save Changes] button (appears when changes made)
- [Reset to Defaults] button
- [Export CSV] button
- [Export JSON] button
```

### Tab 3: Company Permissions
```
Company Selector:
- Dropdown: [Select Company ▼]

Matrix Table: (Same as Tab 2, but for selected company)
- Rows: Permissions
- Columns: Roles
- Cells: Checkboxes

Actions:
- [Save Company Permissions]
- [Copy from Global] (copy global permissions to company)
- [Reset] (reset company permissions to global)
```

---

## 🔄 User Actions (Step by Step)

### Action 1: View Role Permissions

```
1. User clicks "Role Permissions" tab
   ↓
2. Page loads matrix
   ↓
3. Shows:
   - All permissions in rows
   - All roles in columns
   - Checkboxes showing current state
   ↓
4. User can see which roles have which permissions
```

### Action 2: Change Permission

```
1. User finds "deal:delete" permission row
   ↓
2. User sees "Manager" column has ☑ (checked)
   ↓
3. User clicks checkbox to uncheck it (☐)
   ↓
4. Checkbox changes to ☐
   ↓
5. [Save Changes] button appears/highlights
   ↓
6. User clicks [Save Changes]
   ↓
7. Loading indicator shows
   ↓
8. Success message: "Permissions updated successfully"
   ↓
9. Matrix refreshes with saved data
```

### Action 3: View Company Permissions

```
1. User clicks "Company Permissions" tab
   ↓
2. Page shows company dropdown
   ↓
3. User selects company: "Acme Corp"
   ↓
4. Matrix loads with Acme Corp's permissions
   ↓
5. User can see/toggle permissions for that company
   ↓
6. User clicks [Save Company Permissions]
   ↓
7. Only Acme Corp's permissions are updated
```

### Action 4: Bulk Update

```
1. User checks/unchecks multiple checkboxes
   ↓
2. All changes tracked in memory
   ↓
3. User clicks [Save Changes]
   ↓
4. All changes sent to API in one request
   ↓
5. All permissions updated at once
```

---

## 📊 Data Flow (Simple)

### When Page Loads:

```
1. JavaScript: Fetch all permissions
   API: GET /api/permissions
   Response: List of permissions

2. JavaScript: Fetch role-permissions
   API: GET /api/permissions/roles
   Response: Matrix data (which roles have which permissions)

3. JavaScript: Render matrix with data
   Display: Checkboxes filled based on data
```

### When User Saves:

```
1. User clicks [Save Changes]
   ↓
2. JavaScript: Collect all changed checkboxes
   ↓
3. JavaScript: Create update request
   API: POST /api/companies/{company_id}/permissions/bulk-update
   Body: { role: "manager", permissions: [...] }
   ↓
4. API: Updates database
   ↓
5. API: Returns success
   ↓
6. JavaScript: Shows success message
   ↓
7. JavaScript: Refreshes matrix (optional)
```

---

## 🎨 Visual Elements (Simple Description)

### Checkbox States:
- **☑ Checked (Green)**: Role has permission
- **☐ Unchecked (Gray)**: Role doesn't have permission

### Buttons:
- **Primary Button (Blue)**: [Save Changes], [Save Company Permissions]
- **Secondary Button (Gray)**: [Reset], [Back]
- **Tertiary Button (White)**: [Export], [Copy from Global]

### Colors:
- **Green**: Granted permission, Success message
- **Red**: Error message
- **Blue**: Primary actions, Links
- **Gray**: Disabled, Unchecked
- **Orange**: Warning, Company-specific override

### Layout:
- **Header**: Top of page (title, buttons)
- **Tabs**: Below header (navigation)
- **Content**: Below tabs (table/matrix)
- **Footer**: Bottom (pagination, info)

---

## 📱 Screen Sizes

### Desktop (Large Screen):
```
- Full matrix visible
- All columns side by side
- Large checkboxes
- Wide table
```

### Tablet (Medium Screen):
```
- Matrix scrolls horizontally
- Some columns may stack
- Medium checkboxes
- Responsive table
```

### Mobile (Small Screen):
```
- Each role shown separately
- Cards instead of matrix
- Swipeable sections
- Touch-friendly checkboxes
- Bottom sheet for company selection
```

---

## 🔐 Access Control

### Who Can Access:
- ✅ **Super Admin**: Can see all permissions for all companies
- ✅ **Admin**: Can see permissions for their company only
- ❌ **Others**: Cannot access (shown error page)

### Before Loading Page:
```
1. Check user role
   ↓
2. If Super Admin → Show all
   ↓
3. If Admin → Show only their company
   ↓
4. If Other → Show "Access Denied" message
```

---

## 🎯 Key Features

### Must Have:
1. ✅ View all permissions
2. ✅ View role-permission matrix
3. ✅ Toggle permissions (check/uncheck)
4. ✅ Save changes
5. ✅ Company-specific permissions

### Nice to Have:
1. ⏳ Search permissions
2. ⏳ Filter by resource
3. ⏳ Export to CSV/JSON
4. ⏳ Permission detail view
5. ⏳ Copy global to company
6. ⏳ Reset to defaults

---

## 🗂️ Files Needed

### HTML:
- `frontend/pages/permissions.html` - Main page

### JavaScript:
- `frontend/js/pages/permissions.js` - Main logic
- `frontend/js/components/permission-matrix.js` - Matrix component (optional)

### CSS:
- Already in `frontend/styles.css` (add permission-specific styles)

---

## 🚀 Implementation Steps

### Step 1: Create HTML Page
```
- Create permissions.html
- Add tabs structure
- Add table/matrix structure
- Add buttons
```

### Step 2: Create JavaScript
```
- Fetch permissions from API
- Render matrix
- Handle checkbox clicks
- Handle save button
- Handle company selection
```

### Step 3: Add to Navigation
```
- Add "Permissions" link in Settings menu
- Add route in navigation.js
```

### Step 4: Test
```
- Test loading permissions
- Test toggling checkboxes
- Test saving changes
- Test company selection
- Test access control
```

---

## 📝 Summary

**Simple Version:**
- 3 tabs: List, Matrix, Company Matrix
- Matrix shows permissions (rows) vs roles (columns)
- Checkboxes to toggle permissions
- Save button to update
- Company selector for company-specific permissions

**Complex Version:**
- Everything above +
- Search/Filter
- Export
- Detail views
- Bulk operations
- Templates
- Audit log

---

**Status:** Design Complete ✅  
**Ready for:** Implementation

