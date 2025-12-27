# 🧪 DataTable Framework - Testing Plan

## 🎯 Testing Scope

**Target:** Verify DataTable framework works correctly on all 7 pages

---

## 📋 Test Checklist

### Pre-Testing Setup:
- [ ] Backend server running
- [ ] Frontend server running (or static files served)
- [ ] User logged in
- [ ] Company selected
- [ ] At least 10-20 records per entity (for pagination testing)

---

## 🧪 Page-by-Page Testing

### 1. **Leads Page** ✅

#### Basic Functionality:
- [ ] Page loads without errors
- [ ] Table displays data correctly
- [ ] All columns visible (Name, Company, Email, Phone, Source, Status, Priority, Score, Value, Actions)
- [ ] Data is formatted correctly (currency, badges, etc.)

#### Sorting:
- [ ] Click "Name" column header → sorts ascending
- [ ] Click "Name" column header again → sorts descending
- [ ] Click "Company" column → sorts correctly
- [ ] Click "Status" column → sorts correctly
- [ ] Click "Value" column → sorts numerically correctly
- [ ] Sort indicator (↑ ↓) appears correctly

#### Search/Filter:
- [ ] Type in search box → filters results in real-time
- [ ] Search by name → finds matching leads
- [ ] Search by email → finds matching leads
- [ ] Search by company → finds matching leads
- [ ] Clear search → shows all results

#### Pagination:
- [ ] Page size selector shows (10, 25, 50, 100)
- [ ] Default page size is 25
- [ ] Change page size to 10 → shows 10 rows
- [ ] Change page size to 50 → shows 50 rows
- [ ] Click "Next" button → goes to next page
- [ ] Click "Previous" button → goes to previous page
- [ ] Click "First" button («) → goes to first page
- [ ] Click "Last" button (») → goes to last page
- [ ] Page info displays correctly ("Showing X-Y of Z")

#### Column Toggle:
- [ ] Click "Columns" button → menu appears
- [ ] Uncheck a column → column hides
- [ ] Check column again → column shows
- [ ] Multiple columns can be hidden/shown

#### Export:
- [ ] Click "Export" button → menu appears
- [ ] Click "Export CSV" → CSV file downloads
- [ ] Click "Export Excel" → Excel file downloads (if library loaded)
- [ ] Click "Print" → print dialog opens
- [ ] CSV file contains correct data

#### Actions:
- [ ] Click "Edit" button → edit modal opens
- [ ] Click "Delete" button → delete confirmation → deletes lead
- [ ] After create → table refreshes automatically
- [ ] After update → table refreshes automatically
- [ ] After delete → table refreshes automatically

#### Responsive:
- [ ] Resize browser window → table adapts
- [ ] On mobile → table scrolls horizontally
- [ ] On mobile → toolbar stacks vertically

---

### 2. **Customers Page** ✅

#### Test Same Features:
- [ ] Page loads correctly
- [ ] Table displays data
- [ ] All columns visible
- [ ] Sorting works
- [ ] Search works
- [ ] Pagination works
- [ ] Column toggle works
- [ ] Export works
- [ ] Actions (Edit/Delete) work
- [ ] Refresh after CRUD works
- [ ] Responsive design works

---

### 3. **Contacts Page** ✅

#### Additional Tests:
- [ ] Account column shows account name correctly
- [ ] Primary contact badge displays correctly
- [ ] Role badges display correctly
- [ ] All features work as expected

---

### 4. **Deals Page** ✅

#### Additional Tests:
- [ ] Customer column shows customer name correctly
- [ ] Value column formats currency correctly (₹, $)
- [ ] Stage badges display correctly
- [ ] Probability shows as percentage
- [ ] Close date formats correctly
- [ ] All features work as expected

---

### 5. **Tasks Page** ✅

#### Additional Tests:
- [ ] Complete button shows only for incomplete tasks
- [ ] Complete button → marks task as completed
- [ ] Type badges display correctly
- [ ] Priority badges display correctly
- [ ] Status badges display correctly
- [ ] Assigned To shows user name correctly
- [ ] Due date formats correctly
- [ ] All features work as expected

---

### 6. **Activities Page** ✅

#### Additional Tests:
- [ ] Description truncates if too long (>50 chars)
- [ ] Duration displays correctly
- [ ] Outcome badges display correctly
- [ ] Activity date formats correctly
- [ ] Type badges display correctly
- [ ] All features work as expected

---

## 🔍 Common Issues to Check

### JavaScript Errors:
- [ ] Open browser console (F12)
- [ ] Check for any JavaScript errors
- [ ] Check for DataTable initialization errors
- [ ] Check for undefined variable errors

### Performance:
- [ ] Table loads quickly (< 2 seconds)
- [ ] Sorting is instant
- [ ] Filtering is instant (for < 1000 rows)
- [ ] Pagination is smooth

### Data Integrity:
- [ ] All data displays correctly
- [ ] No data loss after refresh
- [ ] Filters don't break data
- [ ] Sorting doesn't break data

### UI/UX:
- [ ] Table looks good visually
- [ ] Badges display correctly
- [ ] Icons display correctly
- [ ] Buttons are clickable
- [ ] Tooltips work (on hover)
- [ ] Empty state shows when no data

---

## 📝 Test Results Template

```
Page: [Page Name]
Date: [Date]
Tester: [Name]

Basic Functionality: ✅ / ❌
Sorting: ✅ / ❌
Search: ✅ / ❌
Pagination: ✅ / ❌
Column Toggle: ✅ / ❌
Export: ✅ / ❌
Actions: ✅ / ❌
Responsive: ✅ / ❌

Issues Found:
1. [Issue description]
2. [Issue description]

Notes:
[Any additional notes]
```

---

## 🐛 Known Issues / Edge Cases to Test

1. **Empty Data:**
   - Create a new company with no records
   - Verify "No data available" message shows

2. **Large Datasets:**
   - Test with 100+ records
   - Verify pagination works correctly
   - Verify performance is acceptable

3. **Special Characters:**
   - Test with names/emails containing special characters
   - Verify HTML escaping works (no XSS issues)

4. **Unicode Characters:**
   - Test with names containing Unicode characters
   - Verify display is correct

5. **Long Text:**
   - Test with very long descriptions/names
   - Verify truncation/display works

---

## ✅ Success Criteria

**All pages pass:**
- ✅ Basic functionality (load, display data)
- ✅ Sorting (at least 3 columns tested)
- ✅ Search (at least 2 searches tested)
- ✅ Pagination (at least 2 page size changes)
- ✅ Export CSV (works)
- ✅ Actions (Edit/Delete work)
- ✅ Refresh after CRUD (works)
- ✅ No JavaScript errors in console
- ✅ Responsive (test on mobile or resize)

---

## 🚀 Quick Test Script

Run this in browser console on each page:

```javascript
// Test DataTable exists
console.log('DataTable class:', typeof DataTable !== 'undefined' ? '✅' : '❌');

// Test table instance exists (replace 'leads' with page name)
console.log('Table instance:', window.leadsTable ? '✅' : '❌');

// Test data loaded
if (window.leadsTable) {
    console.log('Data count:', window.leadsTable.currentData.length);
    console.log('Display data:', window.leadsTable.displayData.length);
}

// Test sorting
if (window.leadsTable) {
    window.leadsTable.sort(0); // Sort first column
    console.log('Sort test:', '✅');
}

// Test search
if (window.leadsTable) {
    window.leadsTable.handleGlobalSearch('test');
    console.log('Search test:', '✅');
}
```

---

**Ready for testing!** 🧪

