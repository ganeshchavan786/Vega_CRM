# Forms Test Instructions

**Date:** December 22, 2025

---

## 🧪 **How to Run Tests**

### **Method 1: Browser Console (Recommended)**

1. **Open the application** in browser:
   ```
   http://localhost:8080
   ```

2. **Login** and **select a company**

3. **Open Browser Console:**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Or `Cmd+Option+I` (Mac)
   - Go to **Console** tab

4. **Load the test script:**
   
   Option A: Copy-paste entire script
   - Open `frontend/test_forms_console.js`
   - Copy ALL content
   - Paste in browser console
   - Press Enter

   Option B: Load as script tag
   - Open `frontend/index.html`
   - Uncomment the test script line:
     ```html
     <script src="test_forms_console.js"></script>
     ```
   - Save and refresh page

5. **Run tests:**
   
   **Test all forms:**
   ```javascript
   quickTestForms()
   ```
   
   **Test specific form:**
   ```javascript
   testSingleForm("customer")  // or "lead", "deal", "task", "activity"
   ```

---

## 📋 **What Tests Are Performed**

### **1. Prerequisites Check**
- ✅ Authentication (auth token)
- ✅ Company selection (company ID)
- ✅ Required functions exist

### **2. Modal Elements**
- ✅ Form modal exists
- ✅ Form content container exists

### **3. Customer Form**
- ✅ Modal opens
- ✅ Required fields exist (Name, Type, Status)
- ✅ Modal closes

### **4. Lead Form**
- ✅ Modal opens
- ✅ Enterprise fields exist (Source, Campaign, Medium, Score)
- ✅ Modal closes

### **5. Deal Form**
- ✅ Modal opens
- ✅ Required fields exist (Name, Customer, Value, Stage)
- ✅ Modal closes

### **6. Task Form**
- ✅ Modal opens
- ✅ Required fields exist (Title, Type, Priority, Status)
- ✅ Modal closes

### **7. Activity Form**
- ✅ Modal opens
- ✅ Required fields exist (Type, Title, Date)
- ✅ Modal closes

### **8. API Endpoints**
- ✅ Customers API responds
- ✅ Leads API responds
- ✅ Deals API responds
- ✅ Tasks API responds
- ✅ Activities API responds

---

## 📊 **Test Output**

The test script will show:

1. **Individual Test Results:**
   - ✅ PASS - Test passed
   - ❌ FAIL - Test failed
   - ⚠️ WARN - Warning

2. **Summary:**
   - Total tests passed
   - Total tests failed
   - Pass rate percentage
   - Duration
   - Error list (if any)

---

## 🎯 **Expected Results**

### **All Tests Should Pass If:**
- ✅ Backend server is running
- ✅ User is logged in
- ✅ Company is selected
- ✅ All JavaScript files are loaded
- ✅ No console errors

### **Common Issues:**

1. **"Function not found" errors:**
   - Make sure you're on a page that loads the form scripts
   - Navigate to the specific page (e.g., `/customers`) before testing

2. **"401 Unauthorized" errors:**
   - Login again
   - Refresh token
   - Check if token is expired

3. **"Modal did not open" errors:**
   - Check if `formModal` element exists in DOM
   - Make sure `index.html` has the modal structure

4. **"Field not found" errors:**
   - Form might not have loaded completely
   - Check if form script loaded correctly
   - Check browser console for JavaScript errors

---

## 🔧 **Manual Testing Checklist**

### **Customer Form:**
1. Click "Add Customer" → Form opens
2. Fill required fields → Validation works
3. Submit → Customer created
4. Click "Edit" on customer → Form opens with data
5. Update and submit → Customer updated
6. Click "Delete" → Customer deleted

### **Lead Form:**
1. Click "Add Lead" → Form opens
2. Fill enterprise fields → All fields save
3. Check UTM fields → Source, Campaign, Medium, Term
4. Test qualification fields → Budget, Authority, Timeline
5. Test lead scoring → Score field works

### **Deal Form:**
1. Click "Add Deal" → Form opens
2. Select customer → Dropdown works
3. Fill deal value → Validation works
4. Set pipeline stage → Stage updates
5. Set probability → Probability saves

### **Task Form:**
1. Click "Add Task" → Form opens
2. Fill task details → All fields work
3. Set due date → Date picker works
4. Link to related entity → Dropdowns work
5. Complete task → Status changes

### **Activity Form:**
1. Click "Log Activity" → Form opens
2. Select activity type → Types work
3. Set date/time → DateTime picker works
4. Link to entity → Dropdowns work
5. Set outcome → Outcome saves

---

## 📝 **Test Report Format**

```
🧪 FORMS COMPREHENSIVE TEST SUITE
============================================================
📋 Checking Prerequisites...
✅ Authentication Check: PASS
✅ Company Selection Check: PASS
...

🔍 Testing Modal Elements...
✅ Modal Element: PASS
✅ Form Content Element: PASS

👥 Testing Customer Form...
✅ Customer Form: Open Modal: PASS
✅ Customer Form: Field customerName: PASS
...

============================================================
📊 TEST SUMMARY
============================================================
✅ Passed: 45
❌ Failed: 0
⏱️  Duration: 12.34s
📈 Pass Rate: 100.0%
```

---

## 🚀 **Quick Commands**

```javascript
// Run all tests
quickTestForms()

// Test specific form
testSingleForm("customer")
testSingleForm("lead")
testSingleForm("deal")
testSingleForm("task")
testSingleForm("activity")

// Check prerequisites only
checkPrerequisites()

// Test API endpoints only
testAPIEndpoints()
```

---

## 💡 **Tips**

1. **Run tests on each page separately** for more accurate results
2. **Check browser console** for JavaScript errors first
3. **Verify backend is running** before testing API endpoints
4. **Test one form at a time** if you encounter issues
5. **Check network tab** to see API calls and responses

---

**Status:** ✅ Test Script Ready - Run in Browser Console!

