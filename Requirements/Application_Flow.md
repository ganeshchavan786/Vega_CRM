# CRM SAAS Application - Flow & Architecture Document

## Date: December 22, 2025

---

## 1. Application Flow

### Step 1: Company Selection (Primary Entry Point)

**First Screen After Login:**
- User logs into the system
- **Company Selection Screen** is displayed
- User selects the company they want to work with
- After company selection → Access to all modules

```
Login → Company Selection → Main Dashboard → Modules Access
```

---

## 2. Company Selection Module

### Features:
- **Company Dropdown/List**
  - Display all companies user has access to
  - Search functionality for companies
  - Recently accessed companies (quick access)
  
- **Company Information Display**
  - Company name
  - Company logo
  - Basic company details
  
- **Multi-Company Support**
  - User can switch between companies
  - Each company has separate data
  - Company-specific permissions

### User Actions:
1. View list of accessible companies
2. Select a company (click/tap)
3. Switch to another company anytime
4. View company details

---

## 3. After Company Selection - Available Modules

Once company is selected, user gets access to:

### 3.1 User Management Module
- **User Roles and Permissions**
  - Create/Edit/Delete users
  - Assign roles (Admin, Manager, Sales Rep, User)
  - Set permissions per role
  
- **Authentication**
  - Login/Logout
  - Password management
  - Session management
  
- **User Profiles**
  - Personal information
  - Contact details
  - Profile photo
  - Activity history

---

### 3.2 Customer Management Module
- **Customer Database**
  - Add new customers
  - Edit customer information
  - Delete/Archive customers
  - Customer categorization
  
- **Contact Information**
  - Name, Email, Phone
  - Address details
  - Multiple contacts per customer
  - Primary contact designation
  
- **Customer History**
  - Interaction timeline
  - Purchase history
  - Communication logs
  - Documents/Files attached
  - Notes and comments

---

### 3.3 Sales Pipeline Module
- **Lead Management**
  - Lead capture
  - Lead qualification
  - Lead assignment to sales reps
  - Lead source tracking
  
- **Deal Tracking**
  - Deal creation
  - Deal value/amount
  - Expected close date
  - Deal owner
  - Deal status updates
  
- **Sales Stages**
  - Prospect
  - Qualified
  - Proposal
  - Negotiation
  - Closed Won
  - Closed Lost
  - Stage-wise pipeline view

---

### 3.4 Task & Activity Management Module
- **Task Management**
  - Create tasks
  - Assign to users
  - Set due dates
  - Task priority (High, Medium, Low)
  - Task status (Pending, In Progress, Completed)
  
- **Activity Logging**
  - Call logs
  - Meeting notes
  - Email tracking
  - Activity timeline
  - Automatic activity capture
  
- **Reminders & Notifications**
  - Task due date reminders
  - Follow-up reminders
  - System notifications
  - Email notifications
  - In-app notifications

---

### 3.5 Reporting & Analytics Module
- **Sales Reports**
  - Sales by period
  - Sales by user
  - Sales by product/service
  - Win/Loss ratio
  
- **Performance Dashboards**
  - Key metrics display
  - Visual charts and graphs
  - Real-time data
  - Customizable widgets
  
- **Custom Reports**
  - Report builder
  - Filter and sort options
  - Export to PDF/Excel
  - Scheduled reports

---

## 4. Technical Specifications

### 4.1 Database: SQLite
**Why SQLite:**
- Lightweight and fast
- Zero configuration
- File-based database
- Perfect for SAAS applications
- Cross-platform compatibility

**Database Structure:**
- One SQLite database per company (Data isolation)
- OR Single SQLite database with company_id in all tables

**Key Tables (to be created):**
1. `companies` - Company master data
2. `users` - User accounts
3. `user_roles` - Role definitions
4. `customers` - Customer information
5. `leads` - Sales leads
6. `deals` - Sales deals
7. `tasks` - Task management
8. `activities` - Activity logs
9. `reports` - Saved reports
10. `permissions` - Role-based permissions

---

### 4.2 Backend Architecture (Phase 1)
**Framework:** FastAPI (Python)
**Architecture Pattern:** MVC (Model-View-Controller)
**ORM:** SQLAlchemy
**Authentication:** JWT (JSON Web Tokens)

### 4.3 Frontend Architecture
**Framework:** (To be decided - React/Next.js/Vue etc.)

**Key Screens:**
1. Login Screen
2. **Company Selection Screen** (Primary after login)
3. Main Dashboard (After company selection)
4. User Management Screen
5. Customer Management Screen
6. Sales Pipeline Screen
7. Tasks Screen
8. Reports Screen

**Navigation Flow:**
```
Login
  ↓
Company Selection (Must Select)
  ↓
Main Dashboard
  ├── User Management
  ├── Customer Management
  ├── Sales Pipeline
  ├── Task Management
  └── Reports & Analytics
```

---

### 4.4 API Structure
- RESTful APIs
- FastAPI framework
- Company context in all API calls
- Automatic API documentation (Swagger/OpenAPI)

**Key API Endpoints:**
```
POST   /api/auth/login
GET    /api/companies                 (List companies for user)
POST   /api/company/select/:id        (Select company)
GET    /api/company/:id/dashboard     (Company dashboard)

GET    /api/company/:id/users
POST   /api/company/:id/users
PUT    /api/company/:id/users/:userId
DELETE /api/company/:id/users/:userId

GET    /api/company/:id/customers
POST   /api/company/:id/customers
PUT    /api/company/:id/customers/:customerId
DELETE /api/company/:id/customers/:customerId

... (Similar for other modules)
```

---

## 5. Data Flow

### Company-Centric Architecture:
1. User authenticates
2. System fetches companies accessible to user
3. User selects company
4. Company ID is stored in session
5. All subsequent operations are scoped to selected company
6. User can switch company anytime

### Data Isolation:
- Each company's data is separate
- Users can only see data for companies they have access to
- Company-level permissions and roles

---

## 6. User Roles & Permissions

### Role Hierarchy:
1. **Super Admin**
   - Access to all companies
   - System configuration
   - Company creation/deletion

2. **Company Admin**
   - Full access within company
   - User management
   - All modules access

3. **Manager**
   - Team management
   - View all team data
   - Reports access

4. **Sales Representative**
   - Own customers/leads/deals
   - Task management
   - Basic reporting

5. **User (Basic)**
   - View-only access
   - Limited functionality

---

## 7. Security Considerations

### SQLite Security:
- Database file encryption
- Secure file permissions
- Regular backups
- Connection pooling

### Application Security:
- JWT authentication
- Role-based access control (RBAC)
- Company-level data isolation
- Input validation
- SQL injection prevention
- XSS protection

---

## 8. SAAS Features

### Multi-Tenancy:
- Company-based isolation
- Shared application, separate data
- Company-specific customization

### Subscription Management:
- Company-level subscriptions
- User limits per plan
- Feature access by plan
- Payment tracking

---

## 9. Implementation Priority

### Phase 1 (Core):
1. ✓ Company Selection Module
2. ✓ User Authentication
3. ✓ Basic User Management
4. ✓ Customer Management (CRUD)

### Phase 2:
5. Sales Pipeline (Leads & Deals)
6. Task Management
7. Activity Logging

### Phase 3:
8. Reporting & Analytics
9. Notifications
10. Integrations

---

## 10. Next Steps

1. **Database Design**
   - Create detailed SQLite schema
   - Define relationships
   - Create ER diagram

2. **UI/UX Design**
   - Company selection screen mockup
   - Dashboard design
   - Module-wise screen designs

3. **Technical Stack Selection**
   - Frontend framework
   - Backend framework
   - Additional libraries

4. **Development Planning**
   - Sprint planning
   - Task breakdown
   - Timeline estimation

---

## Notes:
- This is a **discussion document**
- No coding has been done
- Technical specifications will be refined based on discussions
- Company Selection is the **primary entry point** after login
- All modules are accessible only after company selection

