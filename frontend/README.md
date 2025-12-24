# CRM SAAS - Frontend Application

## HTML, CSS, JavaScript Frontend

---

## 📁 Files:

- `index.html` - Main HTML structure
- `styles.css` - Complete styling
- `app.js` - JavaScript API integration

---

## 🚀 How to Use:

### **Option 1: Simple HTTP Server**

**Python:**
```bash
cd frontend
python -m http.server 8080
```

**Node.js:**
```bash
cd frontend
npx http-server -p 8080
```

**Then open:** `http://localhost:8080`

---

### **Option 2: VS Code Live Server**

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

---

### **Option 3: Direct File**

Simply open `index.html` in browser (some features may not work due to CORS)

---

## 🔐 Login Credentials:

**Default:**
- Email: `admin@crm.com`
- Password: `Admin@123`

---

## ✨ Features:

### **1. Dashboard**
- Statistics cards (Customers, Leads, Deals, Tasks)
- Recent activities timeline
- Pipeline visualization

### **2. Customers**
- List all customers
- Search functionality
- Filter by status
- View customer details

### **3. Leads**
- Lead management
- Status tracking
- Priority levels
- Value estimation

### **4. Deals (Sales Pipeline)**
- Deal tracking
- Stage management
- Win probability
- Pipeline visualization

### **5. Tasks**
- Task management
- Priority & status
- Due date tracking
- Complete tasks

### **6. Activities**
- Activity logging
- Timeline view
- Filter by type
- Outcome tracking

---

## 🎨 Design Features:

- ✅ Modern gradient design
- ✅ Responsive layout
- ✅ Smooth animations
- ✅ Color-coded badges
- ✅ Interactive tables
- ✅ Modal dialogs
- ✅ Search & filters

---

## 🔧 Configuration:

**API Base URL:**
Edit `app.js` line 2:
```javascript
const API_BASE = 'http://localhost:8000/api';
```

Change if your API is on different port/domain.

---

## 📱 Responsive:

Works on:
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

---

## 🎯 Next Steps:

1. **Start Backend Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   python -m http.server 8080
   ```

3. **Open Browser:**
   ```
   http://localhost:8080
   ```

4. **Login & Use!**

---

## 🐛 Troubleshooting:

### **CORS Error:**
Make sure backend CORS is configured in `app/main.py`

### **API Not Found:**
- Check if backend is running on port 8000
- Verify API_BASE URL in `app.js`

### **Login Fails:**
- Check backend is running
- Verify credentials
- Check browser console for errors

---

## 📝 Notes:

- All data is fetched from FastAPI backend
- Authentication uses JWT tokens
- Company selection required after login
- Data refreshes on section change

---

**Enjoy your CRM!** 🎉

