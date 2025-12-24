# 🧪 UI Testing Checklist - CRM SAAS

**Testing Date:** _______________  
**Tester Name:** _______________

---

## 📋 Testing Overview

### **Pages to Test (In Order):**
1. ✅ **Dashboard**
2. ✅ **Customers** (Accounts)
3. ✅ **Contacts**
4. ✅ **Leads**
5. ✅ **Deals** (Opportunities)
6. ✅ **Tasks**
7. ✅ **Activities**

---

## 🔐 Phase 1: Authentication & Navigation

### **1.1 Login**
- [ ] Open application in browser (http://localhost:8080)
- [ ] Login modal appears automatically
- [ ] Enter credentials (admin@crm.com / Admin@123)
- [ ] Click "Login" button
- [ ] **Expected:** Login successful, modal closes

### **1.2 Company Selection**
- [ ] Company selection modal appears after login
- [ ] Company list displays correctly
- [ ] Select a company
- [ ] **Expected:** Company selected, modal closes, home page loads

### **1.3 Navigation Bar**
- [ ] Navbar displays at top
- [ ] All menu items visible:
  - [ ] Dashboard
  - [ ] Customers
  - [ ] Contacts
  - [ ] Leads
  - [ ] Deals
  - [ ] Tasks
  - [ ] Activities
- [ ] Top icons visible (right side):
  - [ ] Notifications icon
  - [ ] Apps icon
  - [ ] Dark Mode icon
  - [ ] Profile icon
- [ ] **Expected:** All navigation elements visible and accessible

### **1.4 Dark Mode Toggle**
- [ ] Click dark mode icon (moon/sun)
- [ ] **Expected:** Theme switches between light/dark
- [ ] Page content adapts to dark mode
- [ ] Toggle works on all pages

### **1.5 Profile Menu**
- [ ] Click profile icon
- [ ] **Expected:** Dropdown opens with "Sign Out" option
- [ ] Click "Sign Out"
- [ ] **Expected:** Logged out, redirected to home/login

---

## 📊 Phase 2: Dashboard Page

### **2.1 Page Load**
- [ ] Navigate to Dashboard (click "Dashboard" in navbar)
- [ ] **Expected:** Dashboard page loads correctly
- [ ] No console errors

### **2.2 Dashboard Content**
- [ ] Statistics cards display (if implemented)
- [ ] Charts/graphs render (if implemented)
- [ ] Recent activities section (if implemented)
- [ ] **Expected:** All dashboard widgets load

### **2.3 Dashboard Navigation**
- [ ] Dashboard link shows as "active" in navbar
- [ ] Can navigate to other pages from dashboard
- [ ] **Expected:** Navigation works smoothly

---

## 👥 Phase 3: Customers Page (Accounts)

### **3.1 Page Load**
- [ ] Navigate to "Customers" page
- [ ] **Expected:** Customers page loads
- [ ] Page title visible: "Customers" or "Accounts"
- [ ] "Add Customer" / "Add Account" button visible

### **3.2 Customer List**
- [ ] Customer table/list displays
- [ ] Columns visible (Name, Email, Phone, Company, etc.)
- [ ] Empty state shows if no customers
- [ ] **Expected:** List renders correctly

### **3.3 Add Customer Form**
- [ ] Click "Add Customer" / "Add Account" button
- [ ] **Expected:** Form modal opens
- [ ] All required fields visible:
  - [ ] Name
  - [ ] Email
  - [ ] Phone
  - [ ] Company Name
  - [ ] Other fields
- [ ] Form validation works (try submitting empty)
- [ ] Cancel button closes modal

### **3.4 Create Customer**
- [ ] Fill all required fields with valid data
- [ ] Click "Save" / "Create"
- [ ] **Expected:** 
  - [ ] Customer created successfully
  - [ ] Success message appears
  - [ ] Modal closes
  - [ ] New customer appears in list
  - [ ] No errors in console

### **3.5 Edit Customer**
- [ ] Click "Edit" button on existing customer
- [ ] **Expected:** Form modal opens with pre-filled data
- [ ] Modify fields
- [ ] Click "Save"
- [ ] **Expected:** Customer updated, changes reflect in list

### **3.6 Delete Customer**
- [ ] Click "Delete" button on customer
- [ ] Confirm deletion (if confirmation dialog)
- [ ] **Expected:** Customer removed from list

### **3.7 Search & Filters**
- [ ] Search box works (if implemented)
- [ ] Filters apply correctly (if implemented)
- [ ] **Expected:** Search/filter functionality works

### **3.8 Dark Mode on Customers Page**
- [ ] Toggle dark mode
- [ ] **Expected:** Customers page adapts to dark mode
- [ ] Form modal works in dark mode
- [ ] Table/list readable in dark mode

---

## 📇 Phase 4: Contacts Page

### **4.1 Page Load**
- [ ] Navigate to "Contacts" page
- [ ] **Expected:** Contacts page loads
- [ ] "Add Contact" button visible

### **4.2 Contact List**
- [ ] Contact table/list displays
- [ ] Columns visible
- [ ] Empty state shows if no contacts

### **4.3 Add Contact Form**
- [ ] Click "Add Contact" button
- [ ] **Expected:** Form modal opens
- [ ] Required fields visible:
  - [ ] First Name
  - [ ] Last Name
  - [ ] Email
  - [ ] Phone
  - [ ] Company/Account (if linking to accounts)
- [ ] Form validation works

### **4.4 Create Contact**
- [ ] Fill form with valid data
- [ ] Select Account/Customer (if required)
- [ ] Click "Save"
- [ ] **Expected:** Contact created, appears in list

### **4.5 Edit Contact**
- [ ] Click "Edit" on existing contact
- [ ] **Expected:** Form opens with data
- [ ] Update fields
- [ ] Save changes
- [ ] **Expected:** Contact updated

### **4.6 Delete Contact**
- [ ] Delete contact
- [ ] **Expected:** Contact removed

### **4.7 Contact-Account Linking**
- [ ] Create contact linked to account (if feature exists)
- [ ] **Expected:** Contact shows correct account association

---

## ⭐ Phase 5: Leads Page

### **5.1 Page Load**
- [ ] Navigate to "Leads" page
- [ ] **Expected:** Leads page loads
- [ ] "Add Lead" button visible

### **5.2 Lead List**
- [ ] Lead table/list displays
- [ ] Lead Score column visible (if implemented)
- [ ] Status badges visible
- [ ] Empty state shows if no leads

### **5.3 Add Lead Form**
- [ ] Click "Add Lead" button
- [ ] **Expected:** Form modal opens
- [ ] Required fields visible:
  - [ ] First Name
  - [ ] Last Name
  - [ ] Email
  - [ ] Phone
  - [ ] Company Name
  - [ ] Source
  - [ ] Status
- [ ] BANT/MEDDICC fields visible (if implemented)

### **5.4 Create Lead**
- [ ] Fill form with valid data
- [ ] Click "Save"
- [ ] **Expected:** 
  - [ ] Lead created successfully
  - [ ] Lead Score auto-calculated (check if displayed)
  - [ ] Duplicate detection runs (check console/logs)
  - [ ] Lead appears in list

### **5.5 Edit Lead**
- [ ] Edit existing lead
- [ ] Update qualification fields (BANT/MEDDICC)
- [ ] **Expected:** Lead score updates if qualification fields changed

### **5.6 Lead Status**
- [ ] Change lead status (New → Contacted → Qualified)
- [ ] **Expected:** Status updates correctly

### **5.7 Lead Conversion** (if implemented)
- [ ] Find qualified lead (Score > 70)
- [ ] Click "Convert" button (if available)
- [ ] **Expected:** 
  - [ ] Account created
  - [ ] Contact created
  - [ ] Opportunity created
  - [ ] Lead marked as "Converted"

### **5.8 Lead Filters**
- [ ] Filter by status
- [ ] Filter by source
- [ ] Search leads
- [ ] **Expected:** Filters work correctly

---

## 💼 Phase 6: Deals Page (Opportunities)

### **6.1 Page Load**
- [ ] Navigate to "Deals" page
- [ ] **Expected:** Deals page loads
- [ ] "Add Deal" / "Add Opportunity" button visible

### **6.2 Deal List**
- [ ] Deal table/list displays
- [ ] Pipeline view (if implemented)
- [ ] Stage/Status columns visible
- [ ] Amount column visible

### **6.3 Add Deal Form**
- [ ] Click "Add Deal" button
- [ ] **Expected:** Form modal opens
- [ ] Required fields visible:
  - [ ] Deal Name
  - [ ] Account/Customer
  - [ ] Amount
  - [ ] Stage
  - [ ] Close Date
  - [ ] Probability

### **6.4 Create Deal**
- [ ] Fill form with valid data
- [ ] Link to Account/Customer
- [ ] Click "Save"
- [ ] **Expected:** Deal created, appears in list/pipeline

### **6.5 Edit Deal**
- [ ] Edit existing deal
- [ ] Update stage (e.g., Prospecting → Qualification → Proposal)
- [ ] Update amount
- [ ] **Expected:** Deal updated

### **6.6 Deal Pipeline**
- [ ] View deals by stage (if pipeline view exists)
- [ ] Drag-and-drop between stages (if implemented)
- [ ] **Expected:** Pipeline visualization works

### **6.7 Delete Deal**
- [ ] Delete deal
- [ ] **Expected:** Deal removed

---

## ✅ Phase 7: Tasks Page

### **7.1 Page Load**
- [ ] Navigate to "Tasks" page
- [ ] **Expected:** Tasks page loads
- [ ] "Add Task" button visible

### **7.2 Task List**
- [ ] Task list/table displays
- [ ] Priority indicators visible
- [ ] Status indicators visible
- [ ] Due date visible

### **7.3 Add Task Form**
- [ ] Click "Add Task" button
- [ ] **Expected:** Form modal opens
- [ ] Required fields visible:
  - [ ] Task Title
  - [ ] Description
  - [ ] Priority
  - [ ] Status
  - [ ] Due Date
  - [ ] Related To (Lead/Account/Contact/Deal)

### **7.4 Create Task**
- [ ] Fill form with valid data
- [ ] Link to Lead/Account/Deal (if applicable)
- [ ] Click "Save"
- [ ] **Expected:** Task created, appears in list

### **7.5 Edit Task**
- [ ] Edit existing task
- [ ] Update status (e.g., Pending → In Progress → Completed)
- [ ] **Expected:** Task updated

### **7.6 Complete Task**
- [ ] Mark task as "Completed"
- [ ] **Expected:** Task status changes, visual indicator updates

### **7.7 Task Filters**
- [ ] Filter by priority
- [ ] Filter by status
- [ ] Filter by due date
- [ ] **Expected:** Filters work

---

## 📝 Phase 8: Activities Page

### **8.1 Page Load**
- [ ] Navigate to "Activities" page
- [ ] **Expected:** Activities page loads
- [ ] "Add Activity" / "Log Activity" button visible

### **8.2 Activity List**
- [ ] Activity timeline/list displays
- [ ] Activity types visible (Call, Email, Meeting, Note)
- [ ] Date/time stamps visible
- [ ] Related entity links visible

### **8.3 Add Activity Form**
- [ ] Click "Add Activity" / "Log Activity" button
- [ ] **Expected:** Form modal opens
- [ ] Required fields visible:
  - [ ] Activity Type (Call, Email, Meeting, Note)
  - [ ] Subject
  - [ ] Description
  - [ ] Date/Time
  - [ ] Related To (Lead/Account/Contact/Deal)
  - [ ] Outcome/Result

### **8.4 Create Activity**
- [ ] Fill form with valid data
- [ ] Select activity type
- [ ] Link to Lead/Account/Deal
- [ ] Click "Save"
- [ ] **Expected:** Activity created, appears in timeline

### **8.5 Activity Types**
- [ ] Log a "Call" activity
- [ ] Log an "Email" activity
- [ ] Log a "Meeting" activity
- [ ] Log a "Note" activity
- [ ] **Expected:** Each type creates correct activity

### **8.6 Activity Timeline**
- [ ] View activities in chronological order
- [ ] Activities grouped by date (if implemented)
- [ ] **Expected:** Timeline displays correctly

### **8.7 Activity Filters**
- [ ] Filter by type
- [ ] Filter by outcome
- [ ] Filter by related entity
- [ ] **Expected:** Filters work

---

## 📱 Phase 9: Responsive Design (Mobile)

### **9.1 Mobile Menu**
- [ ] Resize browser to mobile width (< 768px)
- [ ] **Expected:** Hamburger menu appears
- [ ] Click hamburger menu
- [ ] **Expected:** Sidebar menu opens from right
- [ ] All menu items accessible
- [ ] Close sidebar by clicking overlay or close button

### **9.2 Mobile Navigation**
- [ ] Navigate between pages on mobile
- [ ] **Expected:** Pages load correctly on mobile
- [ ] Forms are usable on mobile
- [ ] Tables scroll horizontally (if needed)

### **9.3 Mobile Forms**
- [ ] Open forms on mobile
- [ ] **Expected:** Forms are readable and usable
- [ ] Input fields are large enough to tap
- [ ] Submit buttons accessible

### **9.4 Mobile Dark Mode**
- [ ] Toggle dark mode on mobile
- [ ] **Expected:** Dark mode works on mobile
- [ ] All elements visible in dark mode

---

## 🎨 Phase 10: UI/UX Consistency

### **10.1 Button Styles**
- [ ] All "Add" buttons have consistent design
- [ ] Primary buttons (Save, Submit) consistent
- [ ] Secondary buttons (Cancel, Delete) consistent
- [ ] **Expected:** Button styles match across all pages

### **10.2 Form Modals**
- [ ] All form modals have same structure
- [ ] Close button (X) works on all modals
- [ ] Click outside modal closes it (if implemented)
- [ ] **Expected:** Consistent modal behavior

### **10.3 Table/List Styling**
- [ ] All tables have consistent styling
- [ ] Column headers styled consistently
- [ ] Row hover effects consistent
- [ ] **Expected:** Uniform table appearance

### **10.4 Dark Mode Consistency**
- [ ] Dark mode works on all pages
- [ ] Forms readable in dark mode
- [ ] Tables readable in dark mode
- [ ] Buttons visible in dark mode
- [ ] **Expected:** Consistent dark mode experience

### **10.5 Error Messages**
- [ ] Validation errors display correctly
- [ ] API error messages show (if any)
- [ ] Error messages are user-friendly
- [ ] **Expected:** Clear error feedback

### **10.6 Success Messages**
- [ ] Success messages appear after create/update
- [ ] Success messages auto-dismiss (if implemented)
- [ ] **Expected:** Clear success feedback

---

## 🔗 Phase 11: Data Relationships

### **11.1 Lead → Account → Contact → Deal Flow**
- [ ] Create a Lead
- [ ] Convert Lead to Account + Contact + Deal (if conversion feature exists)
- [ ] **Expected:** All relationships created correctly
- [ ] Check Account shows Contact
- [ ] Check Account shows Deal
- [ ] Check Contact shows Account link

### **11.2 Activity Linking**
- [ ] Create Activity linked to Lead
- [ ] Create Activity linked to Account
- [ ] Create Activity linked to Deal
- [ ] **Expected:** Activities appear in related entity's activity timeline

### **11.3 Task Linking**
- [ ] Create Task linked to Lead
- [ ] Create Task linked to Account
- [ ] Create Task linked to Deal
- [ ] **Expected:** Tasks show correct relationships

---

## 🐛 Phase 12: Error Handling & Edge Cases

### **12.1 Empty States**
- [ ] Navigate to pages with no data
- [ ] **Expected:** Empty state messages show
- [ ] Empty states are user-friendly

### **12.2 Network Errors**
- [ ] Disconnect internet (or stop backend)
- [ ] Try to create/update record
- [ ] **Expected:** Error message shows, app doesn't crash

### **12.3 Invalid Data**
- [ ] Try to submit forms with invalid data
- [ ] Try invalid email format
- [ ] Try invalid phone number
- [ ] **Expected:** Validation errors show

### **12.4 Large Data Sets**
- [ ] Create many records (if possible)
- [ ] Check pagination (if implemented)
- [ ] Check performance with large lists
- [ ] **Expected:** App handles large data gracefully

---

## ✅ Final Checklist

### **Before Signing Off:**
- [ ] All critical features tested
- [ ] No console errors on any page
- [ ] All forms work correctly
- [ ] Navigation smooth on all pages
- [ ] Dark mode works everywhere
- [ ] Mobile responsive tested
- [ ] Data relationships work correctly
- [ ] Error handling tested

### **Issues Found:**
**List any bugs or issues discovered during testing:**

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________
4. _________________________________________________________________
5. _________________________________________________________________

### **Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 📝 Testing Sign-off

**Tester Name:** _______________  
**Date:** _______________  
**Status:** ⬜ Pass ⬜ Fail ⬜ Partial Pass  
**Comments:** _________________________________________________

---

**🎯 Start testing from Phase 1 and work through systematically!**

