# CRM SAAS - API Endpoints Documentation

## Date: December 22, 2025
## Framework: FastAPI
## Base URL: `http://localhost:8000/api`

---

## Overview

Complete REST API documentation for Phase 1 of CRM SAAS application.

**API Features:**
- RESTful architecture
- JWT authentication
- JSON request/response
- Auto-generated Swagger documentation
- Rate limiting support
- CORS enabled

---

## Authentication

All endpoints (except auth endpoints) require JWT token in header:

```
Authorization: Bearer <jwt_token>
```

---

## Response Format

### Success Response:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-12-22T10:30:00Z"
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... },
  "timestamp": "2025-12-22T10:30:00Z"
}
```

### Paginated Response:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  },
  "message": "Data fetched successfully"
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal error |

---

# API Endpoints by Module

---

## 1. Authentication Module

### 1.1 Register New User

**Endpoint:** `POST /api/auth/register`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-555-0100"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-0100",
    "role": "user",
    "is_active": true,
    "created_at": "2025-12-22T10:30:00Z"
  },
  "message": "User registered successfully"
}
```

**Validation Rules:**
- Email: Valid email format, unique
- Password: Min 8 characters, 1 uppercase, 1 lowercase, 1 number
- First name: Required, 2-100 characters
- Last name: Required, 2-100 characters

**Errors:**
- 409: Email already exists
- 422: Validation error

---

### 1.2 Login

**Endpoint:** `POST /api/auth/login`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "user",
      "avatar": null
    }
  },
  "message": "Login successful"
}
```

**Errors:**
- 401: Invalid credentials
- 403: Account inactive

---

### 1.3 Get Current User

**Endpoint:** `GET /api/auth/me`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-0100",
    "avatar": null,
    "role": "admin",
    "is_active": true,
    "companies": [
      {
        "id": 1,
        "name": "Acme Corp",
        "role": "admin",
        "is_primary": true
      }
    ],
    "last_login": "2025-12-22T10:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "message": "User data fetched successfully"
}
```

---

### 1.4 Logout

**Endpoint:** `POST /api/auth/logout`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 1.5 Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Authentication:** Required (with valid token)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Token refreshed successfully"
}
```

---

### 1.6 Change Password

**Endpoint:** `PUT /api/auth/change-password`

**Authentication:** Required

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Errors:**
- 401: Current password incorrect
- 422: New password validation failed

---

## 2. Company Management Module

### 2.1 Get All Companies (for current user)

**Endpoint:** `GET /api/companies`

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)
- `search` (optional): Search in company name/email
- `status` (optional): Filter by status (active/inactive)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "logo": "https://example.com/logo.png",
      "email": "info@acme.com",
      "phone": "+1-555-0100",
      "status": "active",
      "user_role": "admin",
      "is_primary": true,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Tech Solutions Ltd",
      "logo": null,
      "email": "contact@techsol.com",
      "phone": "+1-555-0200",
      "status": "active",
      "user_role": "manager",
      "is_primary": false,
      "created_at": "2025-02-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 2,
    "pages": 1
  },
  "message": "Companies fetched successfully"
}
```

---

### 2.2 Create New Company

**Endpoint:** `POST /api/companies`

**Authentication:** Required (super_admin or admin)

**Request Body:**
```json
{
  "name": "New Company Ltd",
  "email": "info@newcompany.com",
  "phone": "+1-555-0300",
  "address": "123 Business St",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "zip_code": "10001",
  "website": "https://newcompany.com",
  "industry": "Technology"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 3,
    "name": "New Company Ltd",
    "email": "info@newcompany.com",
    "phone": "+1-555-0300",
    "address": "123 Business St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "zip_code": "10001",
    "website": "https://newcompany.com",
    "industry": "Technology",
    "status": "active",
    "created_at": "2025-12-22T10:30:00Z"
  },
  "message": "Company created successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 409: Email already exists
- 422: Validation error

---

### 2.3 Get Company Details

**Endpoint:** `GET /api/companies/{company_id}`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Acme Corporation",
    "logo": "https://example.com/logo.png",
    "email": "info@acme.com",
    "phone": "+1-555-0100",
    "address": "456 Corporate Blvd",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "zip_code": "94105",
    "website": "https://acme.com",
    "industry": "Manufacturing",
    "company_size": "Medium",
    "status": "active",
    "subscription_plan": "Premium",
    "subscription_start": "2025-01-01",
    "subscription_end": "2026-01-01",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-12-20T15:00:00Z",
    "stats": {
      "total_users": 15,
      "total_customers": 250,
      "total_leads": 50,
      "total_deals": 30
    }
  },
  "message": "Company details fetched successfully"
}
```

**Errors:**
- 403: No access to this company
- 404: Company not found

---

### 2.4 Update Company

**Endpoint:** `PUT /api/companies/{company_id}`

**Authentication:** Required (admin role in company)

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Company Name",
  "phone": "+1-555-9999",
  "website": "https://updated.com"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Updated Company Name",
    "phone": "+1-555-9999",
    "website": "https://updated.com",
    "updated_at": "2025-12-22T10:35:00Z"
  },
  "message": "Company updated successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 404: Company not found
- 422: Validation error

---

### 2.5 Delete Company

**Endpoint:** `DELETE /api/companies/{company_id}`

**Authentication:** Required (super_admin only)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Company deleted successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 404: Company not found

---

### 2.6 Select Company (Set Active Company)

**Endpoint:** `POST /api/companies/select/{company_id}`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "company_id": 1,
    "company_name": "Acme Corporation",
    "user_role": "admin",
    "new_token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": "Company selected successfully"
}
```

**Note:** Returns new JWT token with company_id embedded

**Errors:**
- 403: No access to this company
- 404: Company not found

---

## 3. User Management Module

### 3.1 Get All Users (in company)

**Endpoint:** `GET /api/companies/{company_id}/users`

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number
- `per_page` (optional): Items per page
- `search` (optional): Search in name/email
- `role` (optional): Filter by role
- `is_active` (optional): Filter by status (true/false)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "email": "admin@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1-555-0100",
      "avatar": "https://example.com/avatar.jpg",
      "role": "admin",
      "is_active": true,
      "last_login": "2025-12-22T09:00:00Z",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "email": "sales@acme.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "phone": "+1-555-0101",
      "avatar": null,
      "role": "sales_rep",
      "is_active": true,
      "last_login": "2025-12-22T08:30:00Z",
      "created_at": "2025-01-15T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 2,
    "pages": 1
  },
  "message": "Users fetched successfully"
}
```

---

### 3.2 Create New User

**Endpoint:** `POST /api/companies/{company_id}/users`

**Authentication:** Required (admin/manager role)

**Request Body:**
```json
{
  "email": "newuser@acme.com",
  "password": "SecurePass123!",
  "first_name": "Mike",
  "last_name": "Johnson",
  "phone": "+1-555-0102",
  "role": "sales_rep"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 3,
    "email": "newuser@acme.com",
    "first_name": "Mike",
    "last_name": "Johnson",
    "phone": "+1-555-0102",
    "role": "sales_rep",
    "is_active": true,
    "created_at": "2025-12-22T10:40:00Z"
  },
  "message": "User created successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 409: Email already exists
- 422: Validation error

---

### 3.3 Get User Details

**Endpoint:** `GET /api/companies/{company_id}/users/{user_id}`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "sales@acme.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1-555-0101",
    "avatar": null,
    "role": "sales_rep",
    "is_active": true,
    "is_verified": true,
    "last_login": "2025-12-22T08:30:00Z",
    "created_at": "2025-01-15T00:00:00Z",
    "updated_at": "2025-12-20T12:00:00Z",
    "stats": {
      "total_customers": 45,
      "total_leads": 12,
      "total_deals": 8,
      "total_tasks": 23
    }
  },
  "message": "User details fetched successfully"
}
```

**Errors:**
- 403: No access to this user
- 404: User not found

---

### 3.4 Update User

**Endpoint:** `PUT /api/companies/{company_id}/users/{user_id}`

**Authentication:** Required (admin or self)

**Request Body:** (all fields optional)
```json
{
  "first_name": "Jane Updated",
  "phone": "+1-555-9999",
  "avatar": "https://example.com/new-avatar.jpg"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "first_name": "Jane Updated",
    "phone": "+1-555-9999",
    "avatar": "https://example.com/new-avatar.jpg",
    "updated_at": "2025-12-22T10:45:00Z"
  },
  "message": "User updated successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 404: User not found
- 422: Validation error

---

### 3.5 Update User Role

**Endpoint:** `PUT /api/companies/{company_id}/users/{user_id}/role`

**Authentication:** Required (admin only)

**Request Body:**
```json
{
  "role": "manager"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "sales@acme.com",
    "role": "manager",
    "updated_at": "2025-12-22T10:50:00Z"
  },
  "message": "User role updated successfully"
}
```

**Valid Roles:**
- admin
- manager
- sales_rep
- user

**Errors:**
- 403: Insufficient permissions
- 404: User not found
- 422: Invalid role

---

### 3.6 Deactivate User

**Endpoint:** `PUT /api/companies/{company_id}/users/{user_id}/deactivate`

**Authentication:** Required (admin only)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "is_active": false,
    "updated_at": "2025-12-22T10:55:00Z"
  },
  "message": "User deactivated successfully"
}
```

---

### 3.7 Activate User

**Endpoint:** `PUT /api/companies/{company_id}/users/{user_id}/activate`

**Authentication:** Required (admin only)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 2,
    "is_active": true,
    "updated_at": "2025-12-22T11:00:00Z"
  },
  "message": "User activated successfully"
}
```

---

### 3.8 Delete User

**Endpoint:** `DELETE /api/companies/{company_id}/users/{user_id}`

**Authentication:** Required (admin only)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 404: User not found

---

## 4. Customer Management Module

### 4.1 Get All Customers

**Endpoint:** `GET /api/companies/{company_id}/customers`

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `search` (optional): Search in name/email/phone
- `status` (optional): Filter by status (active/inactive/prospect/lost)
- `customer_type` (optional): Filter by type (individual/business)
- `assigned_to` (optional): Filter by assigned user ID
- `sort_by` (optional): Sort field (name/created_at)
- `order` (optional): Sort order (asc/desc)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_code": "CUST-001",
      "name": "ABC Corporation",
      "email": "contact@abc.com",
      "phone": "+1-555-1001",
      "customer_type": "business",
      "status": "active",
      "priority": "high",
      "assigned_to": {
        "id": 2,
        "name": "Jane Smith"
      },
      "created_by": {
        "id": 1,
        "name": "John Doe"
      },
      "created_at": "2025-11-01T00:00:00Z",
      "updated_at": "2025-12-20T10:00:00Z"
    },
    {
      "id": 2,
      "customer_code": "CUST-002",
      "name": "John Smith",
      "email": "john@email.com",
      "phone": "+1-555-1002",
      "customer_type": "individual",
      "status": "active",
      "priority": "medium",
      "assigned_to": {
        "id": 2,
        "name": "Jane Smith"
      },
      "created_by": {
        "id": 2,
        "name": "Jane Smith"
      },
      "created_at": "2025-11-15T00:00:00Z",
      "updated_at": "2025-11-15T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 2,
    "pages": 1
  },
  "message": "Customers fetched successfully"
}
```

---

### 4.2 Create New Customer

**Endpoint:** `POST /api/companies/{company_id}/customers`

**Authentication:** Required

**Request Body:**
```json
{
  "name": "New Customer Ltd",
  "email": "info@newcustomer.com",
  "phone": "+1-555-2001",
  "secondary_phone": "+1-555-2002",
  "address": "789 Customer Ave",
  "city": "Los Angeles",
  "state": "CA",
  "country": "USA",
  "zip_code": "90001",
  "customer_type": "business",
  "industry": "Retail",
  "company_name": "New Customer Ltd",
  "website": "https://newcustomer.com",
  "status": "active",
  "source": "Website",
  "priority": "high",
  "notes": "Important client",
  "assigned_to": 2
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 3,
    "customer_code": "CUST-003",
    "name": "New Customer Ltd",
    "email": "info@newcustomer.com",
    "phone": "+1-555-2001",
    "secondary_phone": "+1-555-2002",
    "address": "789 Customer Ave",
    "city": "Los Angeles",
    "state": "CA",
    "country": "USA",
    "zip_code": "90001",
    "customer_type": "business",
    "industry": "Retail",
    "company_name": "New Customer Ltd",
    "website": "https://newcustomer.com",
    "status": "active",
    "source": "Website",
    "priority": "high",
    "notes": "Important client",
    "assigned_to": {
      "id": 2,
      "name": "Jane Smith"
    },
    "created_by": {
      "id": 1,
      "name": "John Doe"
    },
    "created_at": "2025-12-22T11:00:00Z"
  },
  "message": "Customer created successfully"
}
```

**Validation Rules:**
- Name: Required, 2-255 characters
- Email: Valid email format (if provided)
- Phone: Valid phone format (if provided)
- Customer type: individual or business
- Status: active, inactive, prospect, or lost
- Priority: low, medium, or high

**Errors:**
- 403: Insufficient permissions
- 422: Validation error

---

### 4.3 Get Customer Details

**Endpoint:** `GET /api/companies/{company_id}/customers/{customer_id}`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "customer_code": "CUST-001",
    "name": "ABC Corporation",
    "email": "contact@abc.com",
    "phone": "+1-555-1001",
    "secondary_phone": "+1-555-1003",
    "address": "123 Business Park",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "zip_code": "10001",
    "customer_type": "business",
    "industry": "Technology",
    "company_name": "ABC Corporation",
    "website": "https://abc.com",
    "status": "active",
    "source": "Referral",
    "priority": "high",
    "credit_limit": 50000.00,
    "notes": "Key account - handle with care",
    "tags": ["vip", "tech-partner"],
    "assigned_to": {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@acme.com"
    },
    "created_by": {
      "id": 1,
      "name": "John Doe",
      "email": "john@acme.com"
    },
    "created_at": "2025-11-01T00:00:00Z",
    "updated_at": "2025-12-20T10:00:00Z",
    "stats": {
      "total_deals": 5,
      "total_value": 125000.00,
      "active_deals": 2,
      "total_tasks": 12,
      "pending_tasks": 3
    }
  },
  "message": "Customer details fetched successfully"
}
```

**Errors:**
- 403: No access to this customer
- 404: Customer not found

---

### 4.4 Update Customer

**Endpoint:** `PUT /api/companies/{company_id}/customers/{customer_id}`

**Authentication:** Required

**Request Body:** (all fields optional)
```json
{
  "name": "ABC Corporation Updated",
  "phone": "+1-555-9999",
  "status": "active",
  "priority": "high",
  "notes": "Updated notes"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "ABC Corporation Updated",
    "phone": "+1-555-9999",
    "status": "active",
    "priority": "high",
    "notes": "Updated notes",
    "updated_at": "2025-12-22T11:10:00Z"
  },
  "message": "Customer updated successfully"
}
```

**Errors:**
- 403: Insufficient permissions
- 404: Customer not found
- 422: Validation error

---

### 4.5 Delete Customer

**Endpoint:** `DELETE /api/companies/{company_id}/customers/{customer_id}`

**Authentication:** Required (admin/manager only)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Customer deleted successfully"
}
```

**Note:** This will also delete all related leads, deals, tasks, and activities

**Errors:**
- 403: Insufficient permissions
- 404: Customer not found

---

### 4.6 Search Customers

**Endpoint:** `GET /api/companies/{company_id}/customers/search`

**Authentication:** Required

**Query Parameters:**
- `q`: Search query (required)
- `fields`: Fields to search (name,email,phone)
- `limit`: Max results (default: 10)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "ABC Corporation",
      "email": "contact@abc.com",
      "phone": "+1-555-1001",
      "customer_type": "business",
      "status": "active"
    }
  ],
  "message": "Search results"
}
```

---

### 4.7 Get Customer Statistics

**Endpoint:** `GET /api/companies/{company_id}/customers/stats`

**Authentication:** Required (admin/manager)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "total_customers": 250,
    "active_customers": 200,
    "inactive_customers": 30,
    "prospect_customers": 20,
    "by_type": {
      "individual": 150,
      "business": 100
    },
    "by_priority": {
      "high": 50,
      "medium": 150,
      "low": 50
    },
    "by_source": {
      "Website": 100,
      "Referral": 80,
      "Direct": 70
    },
    "this_month": 25,
    "this_week": 7
  },
  "message": "Customer statistics fetched successfully"
}
```

---

## Rate Limiting

**Default Limits:**
- Authentication endpoints: 5 requests per minute
- Read endpoints (GET): 100 requests per minute
- Write endpoints (POST/PUT): 30 requests per minute
- Delete endpoints: 10 requests per minute

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640188800
```

---

## Pagination

**Default:** Page 1, 10 items per page  
**Max per page:** 100

**Query Parameters:**
- `page`: Page number (starts from 1)
- `per_page`: Items per page

**Response Headers:**
```
X-Page: 1
X-Per-Page: 10
X-Total: 250
X-Total-Pages: 25
```

---

## Error Codes

| Code | Error | Description |
|------|-------|-------------|
| AUTH_001 | Invalid credentials | Email/password incorrect |
| AUTH_002 | Account inactive | User account disabled |
| AUTH_003 | Token expired | JWT token expired |
| AUTH_004 | Invalid token | JWT token invalid |
| COMP_001 | Company not found | Company doesn't exist |
| COMP_002 | No access | User has no access to company |
| USER_001 | User not found | User doesn't exist |
| USER_002 | Email exists | Email already registered |
| CUST_001 | Customer not found | Customer doesn't exist |
| PERM_001 | Insufficient permissions | User lacks required role |
| VAL_001 | Validation error | Input validation failed |

---

## Swagger/OpenAPI Documentation

Access auto-generated interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Testing Examples (using curl)

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.com","password":"SecurePass123!"}'
```

### Get Companies:
```bash
curl -X GET http://localhost:8000/api/companies \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Customer:
```bash
curl -X POST http://localhost:8000/api/companies/1/customers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Customer","email":"test@example.com"}'
```

---

## Postman Collection

A Postman collection will be provided with:
- All endpoints pre-configured
- Environment variables
- Example requests
- Test scripts

---

## Next Steps

1. ✅ Implement all endpoints in FastAPI
2. ✅ Add request/response validation (Pydantic)
3. ✅ Implement authentication middleware
4. ✅ Add rate limiting
5. ✅ Create automated API tests
6. ✅ Generate Swagger documentation
7. ✅ Create Postman collection

---

## Notes

- All dates in ISO 8601 format (UTC)
- All monetary values in 2 decimal places
- Phone numbers in international format
- Email validation follows RFC 5322
- Passwords hashed with bcrypt (cost: 12)
- JWT tokens expire in 30 minutes
- Refresh tokens valid for 7 days

