# CRM SAAS - Database Schema Documentation

## Date: December 22, 2025
## Database: SQLite with SQLAlchemy ORM

---

## Overview

This document provides detailed database schema for Phase 1 of the CRM SAAS application.

**Key Features:**
- Multi-tenant architecture (Company-based)
- Data isolation per company
- Relational database design
- Audit fields (created_at, updated_at)

---

## Database Design Principles

1. **Company-Centric:** All data is scoped to a company
2. **Soft Deletes:** Use status/is_active instead of hard deletes
3. **Audit Trail:** Track created_at, updated_at, created_by
4. **Normalization:** Follow 3NF (Third Normal Form)
5. **Foreign Keys:** Enforce referential integrity

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│   companies     │
└────────┬────────┘
         │
         │ 1:N
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│     users       │    │   customers     │
└────────┬────────┘    └────────┬────────┘
         │                      │
         │ N:M                  │
         ▼                      │
┌─────────────────┐             │
│ user_companies  │             │
└─────────────────┘             │
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌──────────┐  ┌─────────┐  ┌──────────┐
            │  leads   │  │  deals  │  │  tasks   │
            └──────────┘  └─────────┘  └──────────┘
                    │           │
                    └─────┬─────┘
                          ▼
                  ┌──────────────┐
                  │ activities   │
                  └──────────────┘
```

---

## Phase 1 Tables (Detailed)

---

### 1. companies

**Purpose:** Store company/organization information

**Table Name:** `companies`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique company ID |
| name | VARCHAR(255) | NOT NULL | Company name |
| logo | VARCHAR(500) | NULL | Logo image URL/path |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Company email |
| phone | VARCHAR(20) | NULL | Contact phone |
| address | TEXT | NULL | Full address |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State/Province |
| country | VARCHAR(100) | NULL | Country |
| zip_code | VARCHAR(20) | NULL | Postal code |
| website | VARCHAR(255) | NULL | Company website |
| industry | VARCHAR(100) | NULL | Industry type |
| company_size | VARCHAR(50) | NULL | Small/Medium/Large |
| status | VARCHAR(20) | DEFAULT 'active' | active/inactive/suspended |
| subscription_plan | VARCHAR(50) | NULL | Plan name |
| subscription_start | DATE | NULL | Subscription start date |
| subscription_end | DATE | NULL | Subscription end date |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `status`

**Sample Data:**
```sql
INSERT INTO companies (name, email, phone, status) VALUES
('Acme Corporation', 'info@acme.com', '+1-555-0100', 'active'),
('Tech Solutions Ltd', 'contact@techsol.com', '+1-555-0200', 'active');
```

---

### 2. users

**Purpose:** Store user accounts and authentication details

**Table Name:** `users`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email (login) |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NOT NULL | Last name |
| phone | VARCHAR(20) | NULL | Contact phone |
| avatar | VARCHAR(500) | NULL | Profile picture URL |
| role | VARCHAR(50) | DEFAULT 'user' | super_admin/admin/manager/sales_rep/user |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| last_login | DATETIME | NULL | Last login timestamp |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `role`
- INDEX on `is_active`

**Constraints:**
- `role` CHECK IN ('super_admin', 'admin', 'manager', 'sales_rep', 'user')

**Sample Data:**
```sql
INSERT INTO users (email, password_hash, first_name, last_name, role) VALUES
('admin@acme.com', '$2b$12$...', 'John', 'Doe', 'admin'),
('sales@acme.com', '$2b$12$...', 'Jane', 'Smith', 'sales_rep');
```

---

### 3. user_companies

**Purpose:** Many-to-many relationship between users and companies

**Table Name:** `user_companies`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique relationship ID |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to users.id |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| role | VARCHAR(50) | NOT NULL | User role in this company |
| is_primary | BOOLEAN | DEFAULT FALSE | Primary company for user |
| permissions | JSON | NULL | Custom permissions |
| joined_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When user joined company |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `(user_id, company_id)`
- INDEX on `user_id`
- INDEX on `company_id`

**Constraints:**
- UNIQUE (`user_id`, `company_id`) - One user, one role per company

**Sample Data:**
```sql
INSERT INTO user_companies (user_id, company_id, role, is_primary) VALUES
(1, 1, 'admin', TRUE),
(2, 1, 'sales_rep', TRUE),
(1, 2, 'manager', FALSE);
```

---

### 4. customers

**Purpose:** Store customer/client information

**Table Name:** `customers`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique customer ID |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| customer_code | VARCHAR(50) | NULL | Custom customer code |
| name | VARCHAR(255) | NOT NULL | Customer name |
| email | VARCHAR(255) | NULL | Customer email |
| phone | VARCHAR(20) | NULL | Primary phone |
| secondary_phone | VARCHAR(20) | NULL | Secondary phone |
| address | TEXT | NULL | Full address |
| city | VARCHAR(100) | NULL | City |
| state | VARCHAR(100) | NULL | State/Province |
| country | VARCHAR(100) | NULL | Country |
| zip_code | VARCHAR(20) | NULL | Postal code |
| customer_type | VARCHAR(50) | DEFAULT 'individual' | individual/business |
| industry | VARCHAR(100) | NULL | Customer industry |
| company_name | VARCHAR(255) | NULL | If business customer |
| website | VARCHAR(255) | NULL | Customer website |
| status | VARCHAR(20) | DEFAULT 'active' | active/inactive/prospect/lost |
| source | VARCHAR(100) | NULL | Lead source |
| priority | VARCHAR(20) | DEFAULT 'medium' | low/medium/high |
| credit_limit | DECIMAL(15,2) | DEFAULT 0 | Credit limit |
| notes | TEXT | NULL | Additional notes |
| tags | JSON | NULL | Customer tags |
| created_by | INTEGER | FOREIGN KEY | Reference to users.id |
| assigned_to | INTEGER | NULL, FOREIGN KEY | Assigned sales rep |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Foreign Keys:**
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE
- `created_by` REFERENCES `users(id)` ON DELETE SET NULL
- `assigned_to` REFERENCES `users(id)` ON DELETE SET NULL

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `company_id`
- INDEX on `email`
- INDEX on `status`
- INDEX on `customer_type`
- INDEX on `created_by`
- INDEX on `assigned_to`
- INDEX on `customer_code`

**Sample Data:**
```sql
INSERT INTO customers (company_id, name, email, phone, customer_type, status, created_by) VALUES
(1, 'ABC Corp', 'contact@abc.com', '+1-555-1001', 'business', 'active', 1),
(1, 'John Smith', 'john@email.com', '+1-555-1002', 'individual', 'active', 2);
```

---

## Phase 2 Tables (Preview)

### 5. leads

**Purpose:** Sales lead tracking

**Table Name:** `leads`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique lead ID |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| customer_id | INTEGER | NULL, FOREIGN KEY | Reference to customers.id |
| lead_name | VARCHAR(255) | NOT NULL | Lead name |
| email | VARCHAR(255) | NULL | Lead email |
| phone | VARCHAR(20) | NULL | Lead phone |
| source | VARCHAR(100) | NULL | Lead source |
| status | VARCHAR(50) | DEFAULT 'new' | new/contacted/qualified/lost |
| priority | VARCHAR(20) | DEFAULT 'medium' | low/medium/high |
| estimated_value | DECIMAL(15,2) | NULL | Potential deal value |
| notes | TEXT | NULL | Lead notes |
| assigned_to | INTEGER | NULL, FOREIGN KEY | Assigned sales rep |
| created_by | INTEGER | FOREIGN KEY | Reference to users.id |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Foreign Keys:**
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE
- `customer_id` REFERENCES `customers(id)` ON DELETE SET NULL
- `assigned_to` REFERENCES `users(id)` ON DELETE SET NULL
- `created_by` REFERENCES `users(id)` ON DELETE SET NULL

---

### 6. deals

**Purpose:** Sales pipeline deal tracking

**Table Name:** `deals`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique deal ID |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| customer_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to customers.id |
| lead_id | INTEGER | NULL, FOREIGN KEY | Reference to leads.id |
| deal_name | VARCHAR(255) | NOT NULL | Deal name |
| deal_value | DECIMAL(15,2) | NOT NULL | Deal amount |
| currency | VARCHAR(10) | DEFAULT 'USD' | Currency code |
| stage | VARCHAR(50) | DEFAULT 'prospect' | Sales stage |
| probability | INTEGER | DEFAULT 0 | Win probability % |
| expected_close_date | DATE | NULL | Expected close date |
| actual_close_date | DATE | NULL | Actual close date |
| status | VARCHAR(50) | DEFAULT 'open' | open/won/lost |
| loss_reason | TEXT | NULL | Reason if lost |
| notes | TEXT | NULL | Deal notes |
| assigned_to | INTEGER | NULL, FOREIGN KEY | Deal owner |
| created_by | INTEGER | FOREIGN KEY | Reference to users.id |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Foreign Keys:**
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE
- `customer_id` REFERENCES `customers(id)` ON DELETE CASCADE
- `lead_id` REFERENCES `leads(id)` ON DELETE SET NULL
- `assigned_to` REFERENCES `users(id)` ON DELETE SET NULL
- `created_by` REFERENCES `users(id)` ON DELETE SET NULL

**Stages:**
- prospect
- qualified
- proposal
- negotiation
- closed_won
- closed_lost

---

### 7. tasks

**Purpose:** Task management and tracking

**Table Name:** `tasks`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique task ID |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULL | Task description |
| task_type | VARCHAR(50) | DEFAULT 'general' | call/email/meeting/general |
| priority | VARCHAR(20) | DEFAULT 'medium' | low/medium/high/urgent |
| status | VARCHAR(50) | DEFAULT 'pending' | pending/in_progress/completed/cancelled |
| due_date | DATETIME | NULL | Task due date |
| completed_at | DATETIME | NULL | Completion timestamp |
| customer_id | INTEGER | NULL, FOREIGN KEY | Related customer |
| lead_id | INTEGER | NULL, FOREIGN KEY | Related lead |
| deal_id | INTEGER | NULL, FOREIGN KEY | Related deal |
| assigned_to | INTEGER | NOT NULL, FOREIGN KEY | Assigned user |
| created_by | INTEGER | FOREIGN KEY | Task creator |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Foreign Keys:**
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE
- `customer_id` REFERENCES `customers(id)` ON DELETE CASCADE
- `lead_id` REFERENCES `leads(id)` ON DELETE CASCADE
- `deal_id` REFERENCES `deals(id)` ON DELETE CASCADE
- `assigned_to` REFERENCES `users(id)` ON DELETE CASCADE
- `created_by` REFERENCES `users(id)` ON DELETE SET NULL

---

### 8. activities

**Purpose:** Activity logging and history

**Table Name:** `activities`

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique activity ID |
| company_id | INTEGER | NOT NULL, FOREIGN KEY | Reference to companies.id |
| activity_type | VARCHAR(50) | NOT NULL | call/email/meeting/note/status_change |
| title | VARCHAR(255) | NOT NULL | Activity title |
| description | TEXT | NULL | Activity details |
| duration | INTEGER | NULL | Duration in minutes |
| outcome | VARCHAR(100) | NULL | Activity outcome |
| customer_id | INTEGER | NULL, FOREIGN KEY | Related customer |
| lead_id | INTEGER | NULL, FOREIGN KEY | Related lead |
| deal_id | INTEGER | NULL, FOREIGN KEY | Related deal |
| task_id | INTEGER | NULL, FOREIGN KEY | Related task |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | User who performed |
| activity_date | DATETIME | NOT NULL | When activity occurred |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Foreign Keys:**
- `company_id` REFERENCES `companies(id)` ON DELETE CASCADE
- `customer_id` REFERENCES `customers(id)` ON DELETE CASCADE
- `lead_id` REFERENCES `leads(id)` ON DELETE CASCADE
- `deal_id` REFERENCES `deals(id)` ON DELETE CASCADE
- `task_id` REFERENCES `tasks(id)` ON DELETE CASCADE
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

---

## Database Migrations Strategy

### Using Alembic

**Initial Migration:**
```bash
alembic revision --autogenerate -m "Initial schema - Phase 1"
alembic upgrade head
```

**Migration Files:**
```
alembic/versions/
├── 001_initial_schema_companies.py
├── 002_initial_schema_users.py
├── 003_initial_schema_customers.py
└── 004_user_companies_mapping.py
```

---

## Data Integrity Rules

### 1. Cascade Deletes
- When company deleted → All related data deleted
- When user deleted → Set created_by/assigned_to to NULL
- When customer deleted → All related leads/deals/tasks deleted

### 2. Referential Integrity
- All foreign keys enforced
- Cannot delete parent if children exist (except with CASCADE)

### 3. Business Rules
- User must belong to at least one company
- Customer must belong to exactly one company
- Email must be unique across users
- Company email must be unique

---

## Indexes Strategy

### High Priority Indexes:
1. Foreign key columns (automatic)
2. Email fields (frequent lookups)
3. Status fields (filtering)
4. Date fields (range queries)
5. company_id (every query uses this)

### Composite Indexes:
```sql
CREATE INDEX idx_customer_company_status ON customers(company_id, status);
CREATE INDEX idx_tasks_assigned_status ON tasks(assigned_to, status);
CREATE INDEX idx_deals_company_stage ON deals(company_id, stage);
```

---

## Query Optimization Tips

### 1. Always Include company_id
```sql
SELECT * FROM customers 
WHERE company_id = ? AND status = 'active';
```

### 2. Use Indexes Effectively
```sql
SELECT * FROM tasks 
WHERE assigned_to = ? AND status = 'pending'
ORDER BY due_date;
```

### 3. Limit Results
```sql
SELECT * FROM activities 
WHERE company_id = ? 
ORDER BY created_at DESC 
LIMIT 50;
```

---

## Backup Strategy

### Daily Backups:
- SQLite database file backup
- Store in separate location
- Keep last 30 days

### Backup Command:
```bash
cp data/crm.db backups/crm_backup_$(date +%Y%m%d).db
```

---

## Security Considerations

### 1. Password Storage
- **Never** store plain text passwords
- Use bcrypt with salt rounds = 12
- Hash before storing in database

### 2. Sensitive Data
- Consider encrypting:
  - Customer emails
  - Phone numbers
  - Addresses (if required by compliance)

### 3. SQL Injection Prevention
- Use SQLAlchemy ORM (parameterized queries)
- Never concatenate user input in queries
- Validate all inputs

---

## Sample Queries

### Get User's Companies:
```sql
SELECT c.* FROM companies c
INNER JOIN user_companies uc ON c.id = uc.company_id
WHERE uc.user_id = ?;
```

### Get Company's Active Customers:
```sql
SELECT * FROM customers
WHERE company_id = ? AND status = 'active'
ORDER BY created_at DESC;
```

### Get User's Tasks:
```sql
SELECT t.*, c.name as customer_name
FROM tasks t
LEFT JOIN customers c ON t.customer_id = c.id
WHERE t.assigned_to = ? AND t.status != 'completed'
ORDER BY t.due_date ASC;
```

### Customer Activity Timeline:
```sql
SELECT * FROM activities
WHERE customer_id = ? AND company_id = ?
ORDER BY activity_date DESC
LIMIT 50;
```

---

## Database Size Estimation

### Phase 1 (1 year):
- Companies: ~100 records = ~50 KB
- Users: ~1,000 records = ~500 KB
- Customers: ~10,000 records = ~5 MB
- User_Companies: ~1,500 records = ~100 KB

**Total Estimated: ~6 MB**

### With Phase 2-3 (1 year):
- Leads: ~20,000 records = ~10 MB
- Deals: ~5,000 records = ~3 MB
- Tasks: ~50,000 records = ~25 MB
- Activities: ~100,000 records = ~50 MB

**Total Estimated: ~94 MB**

---

## Next Steps

1. ✅ Create SQLAlchemy models
2. ✅ Setup Alembic migrations
3. ✅ Create initial migration
4. ✅ Add seed data
5. ✅ Test database operations

---

## Notes

- This is Phase 1 schema
- Phase 2-3 tables are preview only
- Schema may evolve based on requirements
- Always use migrations for schema changes
- Test thoroughly before production

