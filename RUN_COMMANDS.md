# CRM SAAS - Run Commands Guide

**Date:** December 23, 2025

---

## 🚀 **QUICK START**

### **1. Activate Virtual Environment**

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

---

### **2. Install Dependencies (if not installed)**

```bash
pip install -r requirements.txt
```

---

### **3. Run Backend Server**

#### **Development Mode (Auto-reload):**
```bash
python -m uvicorn app.main:app --reload
```

**OR**

```bash
uvicorn app.main:app --reload
```

#### **Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **Custom Port:**
```bash
uvicorn app.main:app --reload --port 8001
```

---

### **4. Access Application**

- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📋 **COMPLETE SETUP COMMANDS**

### **First Time Setup:**

```bash
# 1. Navigate to project directory
cd "D:\Project\Katara Dental\TDL\Pramit\CRM SAAS"

# 2. Create virtual environment (if not exists)
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file (if not exists)
# Copy .env.example to .env and update SECRET_KEY

# 6. Run application
python -m uvicorn app.main:app --reload
```

---

## 🔧 **RUNNING WITH PYTHON DIRECTLY**

### **Using Python:**
```bash
python app/main.py
```

**OR**

```bash
python -m app.main
```

---

## 🌐 **FRONTEND ACCESS**

### **Open Frontend:**
1. Backend server running on `http://localhost:8000`
2. Open `frontend/index.html` in browser
3. Or use a local server:

```bash
# Using Python HTTP Server
cd frontend
python -m http.server 8080
```

Then access: `http://localhost:8080`

---

## 🧪 **TESTING COMMANDS**

### **Run API Tests:**
```bash
python test_forms_api.py
```

### **Run All Page Tests:**
```bash
python test_all_pages.py
```

---

## 📊 **BACKGROUND PROCESS**

### **Run in Background (Windows PowerShell):**
```powershell
Start-Process python -ArgumentList "-m uvicorn app.main:app --reload" -WindowStyle Hidden
```

### **Run in Background (Linux/Mac):**
```bash
nohup uvicorn app.main:app --reload > server.log 2>&1 &
```

---

## 🔍 **VERIFY SERVER IS RUNNING**

### **Check Health:**
```bash
curl http://localhost:8000/health
```

**OR**

Open browser: `http://localhost:8000/health`

---

## 🛑 **STOP SERVER**

Press `Ctrl + C` in terminal where server is running

---

## 📝 **ENVIRONMENT VARIABLES**

### **Create .env file:**
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///./data/crm.db
ALLOWED_ORIGINS=["http://localhost:8080", "http://localhost:3000"]
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **Daily Development:**

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Start backend server
python -m uvicorn app.main:app --reload

# 3. Open frontend in browser
# Navigate to: frontend/index.html
```

---

## ⚙️ **ADVANCED OPTIONS**

### **Run with Custom Settings:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --log-level debug
```

### **Run with Workers (Production):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🐛 **TROUBLESHOOTING**

### **Port Already in Use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### **Module Not Found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### **Database Issues:**
```bash
# Database will be created automatically on first run
# If issues, delete data/crm.db and restart
```

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Backend server running (port 8000)
- [ ] API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Frontend accessible

---

## 📞 **QUICK REFERENCE**

| Command | Purpose |
|---------|---------|
| `uvicorn app.main:app --reload` | Start development server |
| `uvicorn app.main:app --host 0.0.0.0 --port 8000` | Start production server |
| `python -m uvicorn app.main:app --reload` | Alternative command |
| `pip install -r requirements.txt` | Install dependencies |
| `venv\Scripts\activate` | Activate virtual environment (Windows) |

---

**Status:** ✅ Ready to Run!

