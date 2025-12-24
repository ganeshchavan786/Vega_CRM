# CRM SAAS - Project Structure (FastAPI + MVC)

## Date: December 22, 2025

---

## Technology Stack - Phase 1

### Backend:
- **Framework:** FastAPI (Python)
- **Architecture:** MVC (Model-View-Controller)
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Validation:** Pydantic

### Why FastAPI?
- High performance (async support)
- Automatic API documentation (Swagger/OpenAPI)
- Type hints and validation
- Easy to learn and implement
- Modern Python framework
- Built-in security features

---

## Project Folder Structure

```
CRM-SAAS/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                          # Application entry point
│   ├── config.py                        # Configuration settings
│   ├── database.py                      # Database connection setup
│   │
│   ├── models/                          # Models (M in MVC)
│   │   ├── __init__.py
│   │   ├── company.py                   # Company model
│   │   ├── user.py                      # User model
│   │   ├── customer.py                  # Customer model
│   │   ├── lead.py                      # Lead model
│   │   ├── deal.py                      # Deal model
│   │   ├── task.py                      # Task model
│   │   └── activity.py                  # Activity model
│   │
│   ├── schemas/                         # Pydantic schemas (Data validation)
│   │   ├── __init__.py
│   │   ├── company.py                   # Company schemas
│   │   ├── user.py                      # User schemas
│   │   ├── customer.py                  # Customer schemas
│   │   ├── auth.py                      # Authentication schemas
│   │   └── response.py                  # Common response schemas
│   │
│   ├── controllers/                     # Controllers (C in MVC)
│   │   ├── __init__.py
│   │   ├── auth_controller.py           # Authentication logic
│   │   ├── company_controller.py        # Company business logic
│   │   ├── user_controller.py           # User management logic
│   │   ├── customer_controller.py       # Customer management logic
│   │   ├── lead_controller.py           # Lead management logic
│   │   ├── deal_controller.py           # Deal management logic
│   │   └── task_controller.py           # Task management logic
│   │
│   ├── routes/                          # API Routes (V in MVC - API Views)
│   │   ├── __init__.py
│   │   ├── auth.py                      # Auth endpoints
│   │   ├── company.py                   # Company endpoints
│   │   ├── user.py                      # User endpoints
│   │   ├── customer.py                  # Customer endpoints
│   │   ├── lead.py                      # Lead endpoints
│   │   ├── deal.py                      # Deal endpoints
│   │   └── task.py                      # Task endpoints
│   │
│   ├── services/                        # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py              # Authentication service
│   │   ├── company_service.py           # Company operations
│   │   ├── user_service.py              # User operations
│   │   └── email_service.py             # Email notifications
│   │
│   ├── middleware/                      # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py           # JWT verification
│   │   └── company_middleware.py        # Company context
│   │
│   ├── utils/                           # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py                  # Password hashing, JWT
│   │   ├── dependencies.py              # Common dependencies
│   │   └── helpers.py                   # Helper functions
│   │
│   └── core/                            # Core configurations
│       ├── __init__.py
│       ├── security.py                  # Security settings
│       └── constants.py                 # App constants
│
├── data/                                # SQLite database files
│   └── crm.db                          # Main database file
│
├── tests/                               # Test files
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_company.py
│   ├── test_users.py
│   └── test_customers.py
│
├── alembic/                             # Database migrations
│   ├── versions/
│   └── env.py
│
├── docs/                                # Additional documentation
│   ├── api_documentation.md
│   └── deployment_guide.md
│
├── .env                                 # Environment variables
├── .env.example                         # Example env file
├── .gitignore                          # Git ignore file
├── requirements.txt                     # Python dependencies
├── README.md                           # Project README
└── alembic.ini                         # Alembic configuration

```

---

## MVC Architecture Explanation

### Model (Models)
**Location:** `app/models/`

**Purpose:** 
- Define database tables using SQLAlchemy ORM
- Represent data structure
- Handle database relationships

**Example Models:**
- `company.py` - Company table
- `user.py` - User table
- `customer.py` - Customer table

**Responsibilities:**
- Define table schema
- Define relationships (Foreign Keys)
- No business logic

---

### View (Routes/API Endpoints)
**Location:** `app/routes/`

**Purpose:**
- Define API endpoints
- Handle HTTP requests/responses
- Route requests to controllers
- Return JSON responses

**Example Routes:**
```
POST   /api/auth/login
GET    /api/companies
POST   /api/company/select/{id}
GET    /api/users
POST   /api/users
```

**Responsibilities:**
- URL routing
- Request validation (using schemas)
- Call controller methods
- Return formatted responses

---

### Controller (Controllers)
**Location:** `app/controllers/`

**Purpose:**
- Business logic implementation
- Process data
- Interact with models
- Call services when needed

**Example Controllers:**
- `company_controller.py` - Company operations
- `user_controller.py` - User CRUD operations
- `customer_controller.py` - Customer management

**Responsibilities:**
- Implement business rules
- Data processing
- Database operations (via models)
- Error handling

---

## Phase 1 - Core Modules Implementation

### 1. Authentication Module
**Files:**
- `models/user.py` - User model
- `schemas/auth.py` - Login/Register schemas
- `controllers/auth_controller.py` - Auth logic
- `routes/auth.py` - Auth endpoints
- `services/auth_service.py` - JWT handling
- `utils/security.py` - Password hashing

**Endpoints:**
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
POST /api/auth/refresh
```

---

### 2. Company Selection Module
**Files:**
- `models/company.py` - Company model
- `schemas/company.py` - Company schemas
- `controllers/company_controller.py` - Company logic
- `routes/company.py` - Company endpoints
- `services/company_service.py` - Company operations

**Endpoints:**
```
GET    /api/companies                    # List all companies for user
POST   /api/companies                    # Create new company
GET    /api/companies/{id}               # Get company details
POST   /api/companies/select/{id}        # Select company
PUT    /api/companies/{id}               # Update company
DELETE /api/companies/{id}               # Delete company
```

**Model Structure:**
```
Company:
  - id
  - name
  - logo
  - email
  - phone
  - address
  - status (active/inactive)
  - created_at
  - updated_at
```

---

### 3. User Management Module
**Files:**
- `models/user.py` - User model (already created for auth)
- `schemas/user.py` - User schemas
- `controllers/user_controller.py` - User logic
- `routes/user.py` - User endpoints
- `services/user_service.py` - User operations

**Endpoints:**
```
GET    /api/company/{company_id}/users          # List all users
POST   /api/company/{company_id}/users          # Create new user
GET    /api/company/{company_id}/users/{id}     # Get user details
PUT    /api/company/{company_id}/users/{id}     # Update user
DELETE /api/company/{company_id}/users/{id}     # Delete user
PUT    /api/company/{company_id}/users/{id}/role # Update user role
```

**Model Structure:**
```
User:
  - id
  - company_id (Foreign Key)
  - email
  - password_hash
  - first_name
  - last_name
  - phone
  - role (admin/manager/sales_rep/user)
  - is_active
  - created_at
  - updated_at
```

---

### 4. Customer Management Module (CRUD)
**Files:**
- `models/customer.py` - Customer model
- `schemas/customer.py` - Customer schemas
- `controllers/customer_controller.py` - Customer logic
- `routes/customer.py` - Customer endpoints
- `services/customer_service.py` - Customer operations

**Endpoints:**
```
GET    /api/company/{company_id}/customers           # List all customers
POST   /api/company/{company_id}/customers           # Create customer
GET    /api/company/{company_id}/customers/{id}      # Get customer
PUT    /api/company/{company_id}/customers/{id}      # Update customer
DELETE /api/company/{company_id}/customers/{id}      # Delete customer
GET    /api/company/{company_id}/customers/search    # Search customers
```

**Model Structure:**
```
Customer:
  - id
  - company_id (Foreign Key)
  - name
  - email
  - phone
  - address
  - city
  - state
  - country
  - zip_code
  - customer_type (individual/business)
  - status (active/inactive)
  - notes
  - created_by (User ID)
  - created_at
  - updated_at
```

---

## Database Schema - Phase 1

### Tables to Create:

#### 1. companies
```sql
- id (Primary Key)
- name
- logo
- email
- phone
- address
- status
- created_at
- updated_at
```

#### 2. users
```sql
- id (Primary Key)
- company_id (Foreign Key -> companies.id)
- email (Unique)
- password_hash
- first_name
- last_name
- phone
- role
- is_active
- created_at
- updated_at
```

#### 3. customers
```sql
- id (Primary Key)
- company_id (Foreign Key -> companies.id)
- name
- email
- phone
- address
- city
- state
- country
- zip_code
- customer_type
- status
- notes
- created_by (Foreign Key -> users.id)
- created_at
- updated_at
```

#### 4. user_companies (Many-to-Many relationship)
```sql
- id (Primary Key)
- user_id (Foreign Key -> users.id)
- company_id (Foreign Key -> companies.id)
- role
- created_at
```

---

## Request/Response Flow

### Example: Get All Customers

```
1. Client Request:
   GET /api/company/1/customers
   Headers: Authorization: Bearer <JWT_TOKEN>

2. Route (routes/customer.py):
   - Receives request
   - Validates JWT token
   - Calls controller method

3. Controller (controllers/customer_controller.py):
   - Validates company_id
   - Checks user permissions
   - Calls model to fetch data

4. Model (models/customer.py):
   - Queries database
   - Returns data

5. Controller:
   - Processes data
   - Returns to route

6. Route:
   - Formats response using schema
   - Returns JSON response

7. Client receives:
   {
     "success": true,
     "data": [...customers...],
     "message": "Customers fetched successfully"
   }
```

---

## Key Features Implementation

### 1. JWT Authentication
**Flow:**
```
Login → Generate JWT Token → Store in client
Every request → Send token in header → Verify token → Allow/Deny
```

**Token Contains:**
- User ID
- Company ID (after selection)
- Role
- Expiry time

---

### 2. Company Context
**Middleware:**
- Every API call (except auth) requires company context
- Company ID from JWT or request
- Validate user has access to company
- All database queries scoped to company

---

### 3. Role-Based Access Control (RBAC)
**Roles:**
- `super_admin` - Full access
- `company_admin` - Full company access
- `manager` - Team management
- `sales_rep` - Own data + team view
- `user` - Limited access

**Decorator:**
```python
@require_role(['admin', 'manager'])
def get_all_users():
    ...
```

---

## API Response Format

### Success Response:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

---

## Dependencies (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
alembic==1.13.0
```

---

## Environment Variables (.env)

```
# Application
APP_NAME=CRM SAAS
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=sqlite:///./data/crm.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Development Setup Steps

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
alembic upgrade head
```

### 4. Run Application
```bash
uvicorn app.main:app --reload
```

### 5. Access API Documentation
```
http://localhost:8000/docs  (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

---

## Phase 1 Development Order

### Week 1: Setup & Authentication
1. Project structure setup
2. Database configuration
3. User model & authentication
4. Login/Register endpoints
5. JWT implementation

### Week 2: Company Module
1. Company model
2. Company CRUD endpoints
3. Company selection logic
4. User-Company relationship
5. Company middleware

### Week 3: User Management
1. User management endpoints
2. Role-based access
3. User permissions
4. User profile management

### Week 4: Customer Management
1. Customer model
2. Customer CRUD endpoints
3. Customer search/filter
4. Customer validation
5. Testing & bug fixes

---

## API Documentation (Auto-generated)

FastAPI automatically generates:
- **Swagger UI**: Interactive API testing
- **ReDoc**: Beautiful API documentation
- **OpenAPI Schema**: JSON schema for APIs

Access at: `http://localhost:8000/docs`

---

## Security Considerations

### 1. Password Security
- Bcrypt hashing
- Salt rounds: 12
- Never store plain passwords

### 2. JWT Security
- Short expiry time (30 mins)
- Refresh token mechanism
- Secure secret key
- HTTPS only in production

### 3. SQL Injection Prevention
- SQLAlchemy ORM (parameterized queries)
- Input validation (Pydantic)

### 4. CORS Configuration
- Allowed origins only
- Credentials support
- Specific methods

---

## Testing Strategy

### Unit Tests:
- Model tests
- Controller tests
- Service tests

### Integration Tests:
- API endpoint tests
- Authentication flow tests
- Database operation tests

### Tools:
- pytest
- pytest-asyncio
- httpx (for API testing)

---

## Next Steps After Phase 1

1. ✅ Complete Phase 1 modules
2. Frontend integration
3. Phase 2: Sales Pipeline
4. Phase 3: Reports & Analytics
5. Deployment setup

---

## Notes:
- This is **documentation only** - no code yet
- MVC structure for clean separation
- FastAPI for modern, fast API development
- SQLite for lightweight database
- JWT for secure authentication
- Company-centric architecture

