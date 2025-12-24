# 🚀 UI Testing - Quick Start Guide

## 📋 **Page Names (Consistent across UI):**

1. **Dashboard** - Main dashboard with statistics
2. **Customers** - Account management (Accounts/Customers)
3. **Contacts** - Contact management
4. **Leads** - Lead management
5. **Deals** - Opportunity/Deal management
6. **Tasks** - Task management
7. **Activities** - Activity logging

---

## ✅ **Start Testing (Step by Step):**

### **Step 1: Start Servers**

**Backend:**
```powershell
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Frontend (New Terminal):**
```powershell
cd frontend
python -m http.server 8080
```

**Access:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### **Step 2: Login & Setup**

1. Open http://localhost:8080
2. Login with:
   - Email: `admin@crm.com`
   - Password: `Admin@123`
3. Select company from dropdown
4. ✅ You should see Dashboard

---

### **Step 3: Test Each Page (In Order)**

#### **1. Dashboard** ⬜
- [ ] Page loads
- [ ] Statistics display (if any)
- [ ] Navigation works

#### **2. Customers** ⬜
- [ ] Page loads
- [ ] Click "Add Customer" → Form opens
- [ ] Create customer → Save → Appears in list
- [ ] Edit customer → Update → Changes saved
- [ ] Delete customer → Removed from list

#### **3. Contacts** ⬜
- [ ] Page loads
- [ ] Click "Add Contact" → Form opens
- [ ] Create contact → Save → Appears in list
- [ ] Link contact to Account (if field exists)
- [ ] Edit/Delete contact

#### **4. Leads** ⬜
- [ ] Page loads
- [ ] Click "Add Lead" → Form opens
- [ ] Create lead → Save → Appears in list
- [ ] Check Lead Score (if displayed)
- [ ] Update qualification fields (BANT/MEDDICC)
- [ ] Convert lead (if button available)

#### **5. Deals** ⬜
- [ ] Page loads
- [ ] Click "Add Deal" → Form opens
- [ ] Create deal → Link to Account
- [ ] Update deal stage
- [ ] View pipeline (if available)

#### **6. Tasks** ⬜
- [ ] Page loads
- [ ] Click "Add Task" → Form opens
- [ ] Create task → Link to Lead/Account/Deal
- [ ] Mark task as completed
- [ ] Filter by priority/status

#### **7. Activities** ⬜
- [ ] Page loads
- [ ] Click "Add Activity" / "Log Activity" → Form opens
- [ ] Log Call activity
- [ ] Log Email activity
- [ ] Log Meeting activity
- [ ] Link activity to Lead/Account/Deal

---

### **Step 4: Test Common Features**

#### **Dark Mode** ⬜
- [ ] Click dark mode icon (top right)
- [ ] All pages switch theme
- [ ] Forms readable in dark mode
- [ ] Buttons visible in dark mode

#### **Navigation** ⬜
- [ ] All navbar links work
- [ ] Active page highlighted
- [ ] Mobile menu works (resize browser)

#### **Forms** ⬜
- [ ] All forms open in modal
- [ ] Close button (X) works
- [ ] Cancel button closes form
- [ ] Validation works (try empty submit)
- [ ] Success messages appear

#### **Profile & Sign Out** ⬜
- [ ] Click profile icon → Dropdown opens
- [ ] Click "Sign Out" → Logged out
- [ ] Redirected to home/login

---

### **Step 5: Test Data Flow**

#### **Complete Workflow:**
1. ⬜ Create **Lead**
2. ⬜ Add **Activity** (Call) to Lead
3. ⬜ Update Lead qualification (BANT fields)
4. ⬜ Convert Lead (if feature exists) → Creates Account + Contact + Deal
5. ⬜ Create **Task** linked to Account
6. ⬜ Log **Activity** to Deal
7. ⬜ Update Deal stage
8. ⬜ Check all relationships correct

---

## 🐛 **Common Issues to Check:**

- [ ] Console errors (F12 → Console tab)
- [ ] Forms not closing after save
- [ ] Buttons not working
- [ ] Data not loading
- [ ] API errors (check Network tab)
- [ ] Dark mode issues
- [ ] Mobile responsive issues

---

## 📝 **Testing Notes:**

**Date:** _______________  
**Issues Found:**
1. _________________________________
2. _________________________________
3. _________________________________

---

## 🎯 **Quick Test Checklist:**

**Critical Path (Must Test):**
- [ ] Login → Company Selection → Dashboard
- [ ] Create Customer → Edit → Delete
- [ ] Create Lead → Update → Convert (if available)
- [ ] Create Deal → Update Stage
- [ ] Log Activity
- [ ] Dark Mode Toggle
- [ ] Sign Out

**Nice to Test:**
- [ ] All pages load
- [ ] All forms work
- [ ] Mobile menu
- [ ] Search/filter (if implemented)
- [ ] Data relationships

---

**🚀 Start with Login and work through each page systematically!**

**Full detailed checklist:** See `UI_TESTING_CHECKLIST.md`

