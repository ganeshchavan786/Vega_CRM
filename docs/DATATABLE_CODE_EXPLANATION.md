# 📊 DataTable Framework - Code Explanation (Marathi/English)

## 🎯 Overview (सारांश)

**DataTable Framework** हा एक **Vanilla JavaScript** (कोणत्याही library शिवाय) framework आहे जो advanced data tables बनवण्यासाठी वापरला जातो.

**Location:**
- Core Code: `static/js/datatable.js` (1000+ lines)
- Styles: `static/css/datatable.css`
- Example: `static/js/datatable-subscriptions-example.js`

---

## 🏗️ Architecture (आर्किटेक्चर)

### 1. **DataTable Class** (Main Framework)

```javascript
class DataTable {
    constructor(containerId, options = {}) {
        // Container ID जिथे table render होईल
        this.container = document.getElementById(containerId);
        
        // Options (configuration)
        this.options = {
            data: [],           // Array of data objects
            columns: [],        // Column definitions
            sorting: true,      // Enable sorting
            filtering: true,    // Enable filtering
            pagination: true,   // Enable pagination
            export: true,       // Enable export
            // ... more options
        };
        
        // State management
        this.currentData = [];
        this.filteredData = [];
        this.sortedData = [];
        this.currentPage = 1;
        this.sortState = {};
        this.filterState = {};
        
        // Initialize
        this.init();
    }
}
```

### 2. **Key Methods** (मुख्य Methods)

#### **Data Loading:**
```javascript
loadData(data) {
    // Data load करते आणि process करते
    this.currentData = Array.isArray(data) ? data : [];
    this.applyFilters();
    this.render();
}

async loadDataAsync() {
    // Async data loading (API calls साठी)
    const data = await this.options.data();
    this.loadData(data);
}
```

#### **Rendering:**
```javascript
render() {
    // Complete table HTML generate करते
    // - Toolbar (search, export, column toggle)
    // - Table (headers + rows)
    // - Pagination
}
```

#### **Sorting:**
```javascript
sort(columnKey, direction) {
    // Column wise sorting
    // 'asc' or 'desc'
    // Visual indicators (↑ ↓) add करते
}
```

#### **Filtering:**
```javascript
handleGlobalSearch(query) {
    // Global search across all columns
    // Real-time filtering
}
```

#### **Pagination:**
```javascript
paginate(page, pageSize) {
    // Page navigation
    // Page size selector
    // Page info display
}
```

#### **Export:**
```javascript
export(format) {
    // CSV, Excel, PDF, Print
    // Uses SheetJS for Excel
    // Uses jsPDF for PDF
}
```

---

## 📝 Column Configuration (Column Setup)

### Basic Column:
```javascript
{
    key: 'id',              // Data object मधील key
    label: 'ID',            // Column header text
    sortable: true,         // Sorting enable
    filterable: true,       // Filtering enable
    width: '80px',          // Column width
    align: 'center'         // left, center, right
}
```

### Custom Render (Custom Display):
```javascript
{
    key: 'customer.name',
    label: 'Customer',
    render: (value, row) => {
        // Custom HTML return करते
        return row.customer?.name || 'N/A';
    }
}
```

### Column Types (Predefined Formats):
```javascript
// Currency
{
    key: 'amount',
    label: 'Amount',
    type: 'currency',
    format: 'INR'  // or 'USD'
}

// Date
{
    key: 'created_at',
    label: 'Created',
    type: 'date'
}

// Badge (Status)
{
    key: 'status',
    label: 'Status',
    type: 'badge'  // Green/Yellow/Red badges
}

// Number
{
    key: 'count',
    label: 'Count',
    type: 'number'
}
```

---

## 🚀 Usage Example (वापराचे उदाहरण)

### Step 1: HTML Include
```html
<!-- CSS -->
<link rel="stylesheet" href="/static/css/datatable.css">

<!-- JavaScript -->
<script src="/static/js/datatable.js"></script>
```

### Step 2: Container Div
```html
<div id="myTable"></div>
```

### Step 3: Initialize
```javascript
// Simple Data
const table = new DataTable('myTable', {
    data: [
        { id: 1, name: 'John', email: 'john@example.com' },
        { id: 2, name: 'Jane', email: 'jane@example.com' }
    ],
    columns: [
        { key: 'id', label: 'ID', sortable: true },
        { key: 'name', label: 'Name', filterable: true },
        { key: 'email', label: 'Email' }
    ],
    pagination: true,
    sorting: true,
    filtering: true
});
```

### Step 4: API Data (Async)
```javascript
// API Data Loading
const table = new DataTable('myTable', {
    data: async () => {
        // API call
        const response = await fetch('/api/subscriptions/');
        return await response.json();
    },
    columns: [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Name' }
    ]
});
```

---

## 💡 Real Example: Subscriptions Table

### Complete Implementation:
```javascript
async function initSubscriptionsDataTable() {
    // 1. Fetch Data
    const response = await fetch('/api/subscriptions/');
    const subscriptions = await response.json();
    
    // 2. Initialize DataTable
    const table = new DataTable('subscriptionsDataTable', {
        data: subscriptions,
        columns: [
            {
                key: 'id',
                label: 'ID',
                sortable: true,
                width: '80px'
            },
            {
                key: 'customer.name',
                label: 'Customer',
                sortable: true,
                render: (value, row) => {
                    return row.customer?.name || 'N/A';
                }
            },
            {
                key: 'amount',
                label: 'Amount',
                type: 'currency',
                format: 'INR',
                sortable: true
            },
            {
                key: 'status',
                label: 'Status',
                type: 'badge',
                filterable: true
            },
            {
                key: 'actions',
                label: 'Actions',
                render: (value, row) => {
                    return `
                        <button onclick="editSubscription(${row.id})">Edit</button>
                        <button onclick="deleteSubscription(${row.id})">Delete</button>
                    `;
                }
            }
        ],
        pagination: {
            enabled: true,
            pageSize: 25,
            pageSizeOptions: [10, 25, 50, 100]
        },
        sorting: true,
        filtering: true,
        export: {
            enabled: true,
            formats: ['csv', 'excel', 'pdf']
        }
    });
    
    // 3. Store globally for refresh
    window.subscriptionsTable = table;
}

// Refresh function
function refreshSubscriptionsTable() {
    if (window.subscriptionsTable) {
        window.subscriptionsTable.refresh();
    }
}
```

---

## 🎨 Features (Features)

### ✅ Core Features:
1. **Sorting** - Column header click करून sort
2. **Global Search** - सर्व columns मध्ये search
3. **Pagination** - Page navigation (10, 25, 50, 100 per page)
4. **Column Toggle** - Show/Hide columns
5. **Export** - CSV, Excel, PDF, Print
6. **Responsive** - Mobile-friendly design

### ✅ Advanced Features:
1. **Custom Renderers** - Custom HTML for cells
2. **Nested Data** - `customer.name` जसे nested keys
3. **Type Formatting** - Currency, Date, Badge auto-formatting
4. **Row Selection** - Checkbox selection (bulk actions)
5. **Row Click** - Click events for rows

---

## 🔧 Methods (Available Methods)

### Public Methods:
```javascript
// Refresh data
table.refresh();

// Update data
table.updateData(newDataArray);

// Get selected rows
const selected = table.getSelectedRows();

// Sort programmatically
table.sort('columnKey', 'asc');

// Filter programmatically
table.filter('columnKey', 'value');
```

---

## 📦 Dependencies (आवश्यक Libraries)

### Required:
- **None!** (Pure Vanilla JavaScript)

### Optional (for Export):
```html
<!-- Excel Export -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js"></script>

<!-- PDF Export -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

---

## 🎯 How to Use in Your CRM Project

### For Leads Table:
```javascript
// frontend/js/pages/leads.js मध्ये

async function initLeadsDataTable() {
    const response = await fetch(`${API_BASE}/leads/`);
    const leads = await response.json();
    
    const table = new DataTable('leadsTable', {
        data: leads,
        columns: [
            { key: 'id', label: 'ID', sortable: true },
            { key: 'first_name', label: 'First Name', filterable: true },
            { key: 'last_name', label: 'Last Name', filterable: true },
            { key: 'email', label: 'Email', filterable: true },
            { key: 'phone', label: 'Phone' },
            { key: 'company_name', label: 'Company', filterable: true },
            { key: 'status', label: 'Status', type: 'badge' },
            { key: 'score', label: 'Score', type: 'number', sortable: true },
            {
                key: 'actions',
                label: 'Actions',
                render: (value, row) => {
                    return `
                        <button onclick="editLead(${row.id})">Edit</button>
                        <button onclick="deleteLead(${row.id})">Delete</button>
                    `;
                }
            }
        ],
        pagination: true,
        sorting: true,
        filtering: true,
        export: true
    });
    
    window.leadsTable = table;
}
```

### For Accounts Table:
```javascript
// Similar structure for accounts
async function initAccountsDataTable() {
    // ... same pattern
}
```

---

## 🛠️ Development Tips (Development साठी Tips)

### 1. **Copy Framework Files:**
```bash
# SubscriptionSaas project मधून copy करा:
- static/js/datatable.js → आपल्या CRM project मध्ये
- static/css/datatable.css → आपल्या CRM project मध्ये
```

### 2. **Include in HTML:**
```html
<!-- Each page मध्ये -->
<link rel="stylesheet" href="/static/css/datatable.css">
<script src="/static/js/datatable.js"></script>
```

### 3. **Initialize on Page Load:**
```javascript
// Page load वर
document.addEventListener('DOMContentLoaded', () => {
    initLeadsDataTable();
});
```

### 4. **Refresh After CRUD:**
```javascript
// Create/Update/Delete नंतर
function handleLeadSubmit() {
    // ... API call
    refreshLeadsTable(); // Refresh table
}

function refreshLeadsTable() {
    if (window.leadsTable) {
        window.leadsTable.refresh();
    } else {
        initLeadsDataTable();
    }
}
```

---

## 📊 File Structure (File Structure)

```
CRM Project/
├── frontend/
│   ├── static/
│   │   ├── js/
│   │   │   ├── datatable.js          # Core framework
│   │   │   └── pages/
│   │   │       ├── leads.js          # Leads table init
│   │   │       ├── accounts.js        # Accounts table init
│   │   │       └── contacts.js       # Contacts table init
│   │   └── css/
│   │       └── datatable.css         # Table styles
│   └── pages/
│       ├── leads.html                 # Include datatable.js
│       ├── accounts.html              # Include datatable.js
│       └── contacts.html              # Include datatable.js
```

---

## ✅ Benefits (फायदे)

1. **No External Dependencies** - Pure JavaScript
2. **Lightweight** - Fast performance
3. **Customizable** - Full control over styling
4. **Reusable** - Same framework for all tables
5. **Modern Features** - Sorting, filtering, export, pagination
6. **Responsive** - Mobile-friendly

---

## 🎓 Summary (सारांश)

**DataTable Framework** हा एक **self-contained JavaScript class** आहे जो:
- ✅ Advanced table features provide करते
- ✅ Easy to use (simple configuration)
- ✅ Reusable across all pages
- ✅ No external libraries needed
- ✅ Fully customizable

**Usage Pattern:**
1. Include CSS & JS files
2. Create container div
3. Initialize with data & columns
4. Store instance globally
5. Refresh after CRUD operations

---

**Ready to implement in your CRM project!** 🚀

