# 🧪 DataTable Testing - Quick Start Guide

## 🚀 How to Start Testing

### Step 1: Start Servers
```bash
# Terminal 1: Start Backend
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend (if using static server)
# Or just open index.html in browser
```

### Step 2: Login
1. Open browser: `http://localhost:8000` (or your frontend URL)
2. Login with credentials
3. Select a company

### Step 3: Navigate to Each Page

#### Test Page Order:
1. **Leads** - `/leads` or click "Leads" in navbar
2. **Customers** - `/customers` or click "Customers" in navbar
3. **Contacts** - `/contacts` or click "Contacts" in navbar
4. **Deals** - `/deals` or click "Deals" in navbar
5. **Tasks** - `/tasks` or click "Tasks" in navbar
6. **Activities** - `/activities` or click "Activities" in navbar

---

## 🎯 Quick Manual Tests

### For Each Page, Test:

#### 1. **Visual Check** (5 seconds)
- [ ] Table loads and displays data
- [ ] No error messages visible
- [ ] All columns are visible
- [ ] Data looks correct

#### 2. **Sorting** (30 seconds)
- [ ] Click any column header → sorts
- [ ] Click again → reverses sort
- [ ] Sort indicator (↑ ↓) appears
- [ ] Data is actually sorted correctly

#### 3. **Search** (30 seconds)
- [ ] Type in search box (top left)
- [ ] Results filter in real-time
- [ ] Clear search → shows all results

#### 4. **Pagination** (30 seconds)
- [ ] Change page size (10, 25, 50, 100)
- [ ] Click Next/Previous buttons
- [ ] Click First/Last buttons (« »)
- [ ] Page info shows correctly

#### 5. **Export** (20 seconds)
- [ ] Click "Export" button
- [ ] Click "Export CSV" → file downloads
- [ ] Open CSV → verify data is correct

#### 6. **Actions** (30 seconds)
- [ ] Click "Edit" button → modal opens
- [ ] Close modal
- [ ] Click "Delete" button → confirmation → deletes
- [ ] Table refreshes after delete

#### 7. **Responsive** (20 seconds)
- [ ] Resize browser window
- [ ] Table adapts (horizontal scroll if needed)
- [ ] On mobile: toolbar stacks vertically

---

## 🔍 Browser Console Testing

### Open Console:
- Press `F12` or `Ctrl+Shift+I`
- Go to "Console" tab

### Run Quick Test:
1. Navigate to any page (e.g., Leads)
2. Paste this in console:

```javascript
// Load test script (if available)
// Or run directly:

// Test DataTable exists
console.log('DataTable:', typeof DataTable !== 'undefined' ? '✅' : '❌');

// Test table instance
console.log('Leads Table:', window.leadsTable ? '✅' : '❌');

// Test data
if (window.leadsTable) {
    console.log('Data count:', window.leadsTable.currentData.length);
    console.log('Columns:', window.leadsTable.options.columns.length);
}
```

### Check for Errors:
- Look for red error messages
- Check for warnings (yellow)
- Common errors:
  - `DataTable is not defined` → JS file not loaded
  - `Container not found` → HTML element missing
  - `Cannot read property` → Data not loaded

---

## 📋 Use Testing Checklist

### Option 1: HTML Checklist
1. Open `scripts/test_datatable.html` in browser
2. Check boxes as you test
3. Click "Generate Report" when done
4. Copy report from console

### Option 2: Markdown Checklist
1. Open `docs/DATATABLE_TESTING_PLAN.md`
2. Follow the checklist
3. Mark items as ✅ or ❌
4. Note any issues

---

## ⚡ Quick Test Script

### Copy this script and run in console:

```javascript
function quickTest(page) {
    const table = window[`${page}Table`];
    console.log(`\n🧪 Testing ${page.toUpperCase()}`);
    console.log('Table exists:', table ? '✅' : '❌');
    if (table) {
        console.log('Data loaded:', table.currentData.length, 'records');
        console.log('Columns:', table.options.columns.length);
        console.log('Pagination:', table.options.pagination ? '✅' : '❌');
        console.log('Sorting:', table.options.sorting ? '✅' : '❌');
        console.log('Filtering:', table.options.filtering ? '✅' : '❌');
    }
}

// Test all pages
['leads', 'customers', 'contacts', 'deals', 'tasks', 'activities'].forEach(quickTest);
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "DataTable is not defined"
**Fix:** Check if `datatable.js` is loaded
- Open Network tab in DevTools
- Look for `datatable.js` → should be 200 OK
- Check `index.html` has correct script tag

### Issue 2: Table not showing
**Fix:** Check container element
- Verify HTML has `<div id="pageNameTable">`
- Check JavaScript console for errors
- Verify page JS file is loaded

### Issue 3: No data showing
**Fix:** Check API response
- Open Network tab → look for API calls
- Check if API returns data
- Verify auth token is valid

### Issue 4: Sorting/Search not working
**Fix:** Check DataTable options
- Verify `sorting: true` and `filtering: true` in options
- Check browser console for errors
- Verify data is loaded correctly

---

## ✅ Success Criteria

**Page passes if:**
- ✅ Table loads and displays data
- ✅ Sorting works (test 2-3 columns)
- ✅ Search works (test 1-2 searches)
- ✅ Pagination works (change page size once)
- ✅ Export CSV works
- ✅ Edit/Delete buttons work
- ✅ No JavaScript errors in console
- ✅ Table refreshes after CRUD

---

## 📝 Test Results Template

```
Test Date: [Date]
Tester: [Your Name]

PAGE: [Page Name]
Status: ✅ PASS / ❌ FAIL

Tests:
- Visual Check: ✅ / ❌
- Sorting: ✅ / ❌
- Search: ✅ / ❌
- Pagination: ✅ / ❌
- Export: ✅ / ❌
- Actions: ✅ / ❌
- Responsive: ✅ / ❌

Issues Found:
1. [Description]

Notes:
[Any additional notes]
```

---

## 🚀 Start Testing Now!

1. **Open your CRM application**
2. **Navigate to Leads page**
3. **Follow Quick Manual Tests above**
4. **Repeat for each page**
5. **Report any issues**

**Good luck!** 🧪✨

