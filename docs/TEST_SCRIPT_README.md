# 🧪 Comprehensive Test Script - Usage Guide

## 📋 Overview

`test_all_forms_debug.py` हा comprehensive test script आहे जो सर्व CRM forms/entities test करतो with detailed error debugging.

## ✅ Test Coverage

**Total Records:** 25
- **8 Leads** (सर्व fields सह)
- **5 Customers/Accounts** (सर्व fields सह)
- **4 Contacts** (Customers ला link केलेले)
- **4 Deals/Opportunities** (Customers ला link केलेले)
- **2 Tasks** (Customers/Deals ला link केलेले)
- **2 Activities** (Customers/Deals ला link केलेले)

**Plus:**
- Edit operations on Leads, Customers, and Deals
- Field-level error tracking
- Detailed debug information

## 🚀 How to Run

### **Prerequisites:**
1. Backend server running: `python -m uvicorn app.main:app --reload`
2. Database initialized
3. Admin user exists: `admin@crm.com` / `Admin@123`

### **Run Script:**

```powershell
# Navigate to project directory
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"

# Activate virtual environment (if using)
venv\Scripts\activate

# Run test script
python test_all_forms_debug.py
```

## 📊 Output

### **Console Output:**
- ✅ **Green**: Passed tests
- ❌ **Red**: Failed tests
- ⚠️ **Yellow**: Warnings
- 📋 **Blue**: Section headers

### **Test Results:**
1. **Console Summary:**
   - Total tests run
   - Passed/Failed count
   - Success rate
   - Created records count

2. **JSON File:** `test_results_debug.json`
   - Complete test statistics
   - All errors with details
   - Created record IDs
   - Field-level error information

## 🔍 Error Debugging

### **Error Information Includes:**
1. **HTTP Status Code**
2. **Error Type** (duplicate, validation, etc.)
3. **Field-Level Errors** (Pydantic validation errors)
4. **Error Messages** (user-friendly descriptions)
5. **Request Data** (what was sent)

### **Example Error Output:**
```
✗ Create Lead 1: FAIL
   Status 409: Create Lead 1
   Error Type: Duplicate lead detected
   Duplicate Leads: ['John Doe', 'Jane Smith']
   Match Reason: Email match
   Confidence: 95%
```

### **Field-Level Validation Errors:**
```
✗ Create Customer 2: FAIL
   Status 422: Create Customer 2
   Field 'email': Invalid email format (value_error.email)
   Field 'phone': String length must be between 10 and 20 (string_too_short)
```

## 📝 What Gets Tested

### **1. Lead Form Fields:**
- ✅ Basic: lead_name, first_name, last_name, email, phone, company_name
- ✅ Source Attribution: source, campaign, medium, term
- ✅ Management: status, stage, priority, lead_score
- ✅ Qualification: budget_range, authority_level, timeline, interest_product
- ✅ Additional: country, industry, estimated_value, notes

### **2. Customer Form Fields:**
- ✅ Basic: name, email, phone, secondary_phone, address, city, state, country, zip_code
- ✅ Type: customer_type, company_name, website, industry
- ✅ Management: status, source, priority, notes
- ✅ Enterprise: account_type, company_size, annual_revenue, gstin, health_score, lifecycle_stage, is_active

### **3. Contact Form Fields:**
- ✅ Basic: name, job_title, email, phone
- ✅ Role: role, preferred_channel, influence_score, is_primary_contact
- ✅ Link: account_id (Customer)

### **4. Deal Form Fields:**
- ✅ Basic: deal_name, deal_value, currency
- ✅ Management: stage, probability, expected_close_date, status, notes
- ✅ Link: customer_id, lead_id

### **5. Task Form Fields:**
- ✅ Basic: title, description, task_type, priority, status
- ✅ Dates: due_date, completed_at
- ✅ Links: customer_id, lead_id, deal_id, assigned_to

### **6. Activity Form Fields:**
- ✅ Basic: activity_type, title, description, duration, outcome
- ✅ Date: activity_date
- ✅ Links: customer_id, lead_id, deal_id, task_id

## 🎯 Test Flow

```
1. Authentication (Login)
   ↓
2. Get Company ID
   ↓
3. Create 8 Leads (with all fields)
   ↓
4. Update 2 Leads
   ↓
5. Create 5 Customers (with all fields)
   ↓
6. Update 2 Customers
   ↓
7. Create 4 Contacts (linked to Customers)
   ↓
8. Create 4 Deals (linked to Customers)
   ↓
9. Update 2 Deals
   ↓
10. Create 2 Tasks (linked to Customers/Deals)
   ↓
11. Create 2 Activities (linked to Customers/Deals)
   ↓
12. Generate Summary Report
```

## 📈 Expected Results

### **Success Criteria:**
- ✅ All 25 records created successfully
- ✅ All edit operations successful
- ✅ No field validation errors
- ✅ All relationships (links) working

### **Common Issues to Check:**
1. **409 Conflict**: Duplicate detection working
2. **422 Validation**: Check field formats (email, phone, dates)
3. **404 Not Found**: Check if linked entities exist (customer_id, etc.)
4. **500 Server Error**: Check backend logs

## 🔧 Troubleshooting

### **If script fails at login:**
- Check backend is running on port 8000
- Verify credentials: `admin@crm.com` / `Admin@123`
- Check database connection

### **If records fail to create:**
- Check `test_results_debug.json` for detailed errors
- Verify required fields are provided
- Check field format (email, phone, dates)
- Check duplicate detection (409 errors)

### **If relationships fail:**
- Ensure parent records exist (Customer before Contact/Deal)
- Check foreign key constraints
- Verify IDs are correct

## 📄 Output Files

1. **Console Output**: Real-time test progress
2. **test_results_debug.json**: Complete test results with errors

## 💡 Tips

- Run script multiple times to test duplicate detection
- Check JSON file for detailed field-level errors
- Use error messages to identify problematic fields
- Test different field combinations

---

**🎯 Run this script to test all forms and identify any field-level issues!**

