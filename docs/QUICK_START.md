# CRM SAAS - Quick Start Guide

## 🚀 Get Started in 5 Minutes

---

## Step 1: Setup Environment

### Create & Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- SQLAlchemy
- JWT authentication
- Bcrypt password hashing
- And all other dependencies

---

## Step 3: Setup Environment Variables

Create `.env` file in project root:

```env
APP_NAME=CRM SAAS
DEBUG=True
DATABASE_URL=sqlite:///./data/crm.db
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

⚠️ **Important:** Change the `SECRET_KEY` to a strong random string in production!

---

## Step 4: Create Data Folder

```bash
mkdir data
```

This folder will store the SQLite database.

---

## Step 5: Run the Application

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 6: Access API Documentation

Open your browser and go to:

**Swagger UI (Interactive):**
```
http://localhost:8000/docs
```

**ReDoc (Beautiful Docs):**
```
http://localhost:8000/redoc
```

---

## Step 7: Test the API

### Method 1: Using Swagger UI

1. Go to http://localhost:8000/docs
2. Try the "POST /api/auth/register" endpoint
3. Click "Try it out"
4. Fill in the details:
```json
{
  "email": "admin@test.com",
  "password": "Admin123!",
  "first_name": "Admin",
  "last_name": "User",
  "phone": "+1234567890"
}
```
5. Click "Execute"

### Method 2: Using cURL

**Register User:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"Admin123!\",\"first_name\":\"Admin\",\"last_name\":\"User\"}"
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"Admin123!\"}"
```

Copy the `access_token` from response.

**Get Current User:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📋 API Flow Example

### 1. Register a User
```
POST /api/auth/register
```

### 2. Login
```
POST /api/auth/login
→ Receive JWT token
```

### 3. Create a Company
```
POST /api/companies
Headers: Authorization: Bearer {token}
```

### 4. Select Company
```
POST /api/companies/select/{company_id}
→ Receive new token with company context
```

### 5. Create a Customer
```
POST /api/companies/{company_id}/customers
Headers: Authorization: Bearer {token}
```

---

## 🎯 Common Endpoints

### Authentication
- Register: `POST /api/auth/register`
- Login: `POST /api/auth/login`
- Get User: `GET /api/auth/me`

### Companies
- List: `GET /api/companies`
- Create: `POST /api/companies`
- Get: `GET /api/companies/{id}`
- Update: `PUT /api/companies/{id}`
- Select: `POST /api/companies/select/{id}`

### Users
- List: `GET /api/companies/{company_id}/users`
- Create: `POST /api/companies/{company_id}/users`
- Get: `GET /api/companies/{company_id}/users/{id}`
- Update: `PUT /api/companies/{company_id}/users/{id}`

### Customers
- List: `GET /api/companies/{company_id}/customers`
- Create: `POST /api/companies/{company_id}/customers`
- Get: `GET /api/companies/{company_id}/customers/{id}`
- Update: `PUT /api/companies/{company_id}/customers/{id}`
- Stats: `GET /api/companies/{company_id}/customers/stats`

---

## 🔐 Authentication

All endpoints (except register/login) require JWT token:

```
Authorization: Bearer {your_jwt_token}
```

---

## 🗂️ Database

The SQLite database is created automatically at:
```
data/crm.db
```

To view/edit database, use:
- DB Browser for SQLite
- SQLite Studio
- VS Code SQLite extension

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "No such file or directory: 'data'"
```bash
mkdir data
```

### Error: "SECRET_KEY not set"
Create `.env` file with SECRET_KEY

### Port 8000 already in use
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 📚 Documentation

Detailed docs available in `Requirements/` folder:
- Application_Flow.md
- Database_Schema.md
- API_Endpoints.md
- Project_Structure.md

---

## 💡 Tips

1. **Use Swagger UI** for easy testing (http://localhost:8000/docs)
2. **Check logs** in terminal for errors
3. **Auto-reload** is enabled in dev mode
4. **Database** is created automatically
5. **All routes** are in `app/routes/` folder

---

## ✅ Quick Test Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file created
- [ ] data/ folder exists
- [ ] Server running (http://localhost:8000)
- [ ] Swagger UI accessible (http://localhost:8000/docs)
- [ ] Register user successful
- [ ] Login successful
- [ ] Create company successful
- [ ] Create customer successful

---

## 🎉 You're Ready!

The CRM SAAS application is now running and ready to use!

For detailed API documentation, visit: http://localhost:8000/docs

---

**Need Help?**
- Check README.md for more details
- Review Requirements/ folder for documentation
- Check terminal logs for errors

