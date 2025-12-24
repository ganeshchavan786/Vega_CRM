# 🧪 CRM Testing Workflow Guide

## ✅ Proper Order to Create Records

### **Step 1: Create LEAD (First)**
**Why?** Lead is the entry point - it's a person with potential interest.

**How to Test:**
1. Go to **Leads** page
2. Click **"Add Lead"** button
3. Fill required fields:
   - First Name
   - Last Name
   - Email
   - Phone
   - Company Name
   - Source (e.g., "Website", "Referral")
4. Save

**What Happens:**
- ✅ Lead Score automatically calculated
- ✅ Duplicate detection runs
- ✅ Lead assigned to SDR (if rules configured)
- ✅ Lead Status = "New"

---

### **Step 2: Nurture & Qualify Lead**
**Actions:**
1. Update Lead Status to "Contacted"
2. Add Activities (calls, emails, meetings)
3. Fill BANT/MEDDICC fields (Budget, Authority, Need, Timeline)
4. Lead Score increases with activities

**When Ready:**
- Lead Score > 70
- Status = "Contacted" or "Qualified"
- BANT fields filled

---

### **Step 3: Convert Lead → Account + Contact + Opportunity**
**How to Convert:**
1. Go to Leads page
2. Find qualified lead (Score > 70)
3. Click **"Convert"** button (if available)
4. OR manually create:
   - **Account** (Company) - from Lead's Company Name
   - **Contact** (Person) - from Lead's Name/Email/Phone
   - **Opportunity** (Deal) - from Lead's Budget/Timeline

**What Gets Created:**
- ✅ **Account** = Company becomes permanent entity
- ✅ **Contact** = Person linked to Account
- ✅ **Opportunity** = Revenue tracking starts
- ✅ Lead Status changes to "Converted"

---

## 📋 Quick Testing Checklist

### ✅ Test Scenario 1: Basic Lead Creation
```
1. Create Lead
   → Check Lead Score (should be auto-calculated)
   → Check Duplicate Detection
   → Check Assignment

2. Add Activity
   → Check Lead Score increment

3. Update Qualification Fields
   → Check BANT/MEDDICC scoring
```

### ✅ Test Scenario 2: Lead Conversion
```
1. Create Qualified Lead (Score > 70)
2. Convert Lead
   → Account created
   → Contact created & linked to Account
   → Opportunity created
   → Lead marked as "Converted"
```

### ✅ Test Scenario 3: Direct Account Creation (Alternative)
```
If you already have a customer:
1. Create Account directly (Customers page)
2. Create Contact linked to Account
3. Create Opportunity for revenue tracking
```

---

## 🎯 Recommended Testing Order

### **For New Users (Start Here):**
1. **Lead** → Create first lead
2. **Activity** → Log a call/email
3. **Lead** → Check score increment
4. **Account** → Convert lead OR create directly
5. **Contact** → Create contact linked to account
6. **Deal** → Create opportunity/deal

### **For Existing Customers:**
1. **Account** (Customers) → Create company
2. **Contact** → Create person linked to account
3. **Deal** → Create opportunity

---

## ⚠️ Important Notes

- **Lead is Temporary** - Convert to Account when qualified
- **Account is Permanent** - Never deleted, only marked inactive
- **One Account → Many Contacts** - Multiple people per company
- **One Account → Many Opportunities** - Multiple deals per account

---

## 🔄 Complete Flow Diagram

```
LEAD (Person + Intent)
    ↓
[Nurture & Qualify]
    ↓
[Convert Button]
    ↓
ACCOUNT (Company) ← Permanent
    ├── CONTACT (Person) ← Linked
    └── OPPORTUNITY (Deal) ← Revenue
```

---

## 💡 Quick Start Commands

**Backend:**
```powershell
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Frontend:**
```powershell
cd frontend
python -m http.server 8080
```

**Access:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

**Start with LEAD creation first!** 🚀

