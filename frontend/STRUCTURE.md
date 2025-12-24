# Frontend File Structure

## 📁 Complete File Organization

```
frontend/
│
├── index.html                  # Main entry point
├── styles.css                  # All styles
├── README.md                   # Documentation
├── STRUCTURE.md                # This file
│
├── components/                 # Reusable components
│   └── navbar.html            # Navigation bar component
│
├── pages/                      # Page HTML files
│   ├── dashboard.html         # Dashboard page
│   ├── customers.html         # Customers page
│   ├── leads.html             # Leads page
│   ├── deals.html             # Deals page
│   ├── tasks.html             # Tasks page
│   └── activities.html        # Activities page
│
└── js/                         # JavaScript files
    ├── config.js              # API configuration & globals
    ├── auth.js                # Authentication functions
    ├── navigation.js          # Navigation & routing
    ├── main.js                # Main entry point
    │
    └── pages/                  # Page-specific JavaScript
        ├── dashboard.js       # Dashboard logic
        ├── customers.js       # Customers logic
        ├── leads.js           # Leads logic
        ├── deals.js           # Deals logic
        ├── tasks.js           # Tasks logic
        └── activities.js      # Activities logic

```

---

## 📄 File Descriptions

### **Root Files:**

#### `index.html`
- Main HTML entry point
- Loads navigation component
- Contains modals (login, company selection, forms)
- Loads all JavaScript files in order

#### `styles.css`
- Complete CSS styling
- Responsive design
- Component styles
- Utility classes

---

### **Components:**

#### `components/navbar.html`
- Navigation bar HTML
- Menu items
- User info
- Logout button

---

### **Pages:**

#### `pages/dashboard.html`
- Dashboard layout
- Statistics cards
- Recent activities
- Pipeline chart

#### `pages/customers.html`
- Customer list layout
- Search & filters
- Table container

#### `pages/leads.html`
- Lead management layout
- Search & status filters
- Table container

#### `pages/deals.html`
- Sales pipeline layout
- Stage & status filters
- Table container

#### `pages/tasks.html`
- Task management layout
- Priority & status filters
- Table container

#### `pages/activities.html`
- Activity timeline layout
- Type & outcome filters
- Activity list container

---

### **JavaScript Files:**

#### `js/config.js`
- API base URL
- Global variables (authToken, companyId, currentUser)
- Helper functions (getHeaders)

#### `js/auth.js`
- Authentication functions
- Login handler
- Company selection
- Logout function
- Modal management

#### `js/navigation.js`
- Navigation bar loading
- Page routing
- Section switching
- Dynamic page loading

#### `js/main.js`
- Application entry point
- Initialization
- Event listener setup

#### `js/pages/dashboard.js`
- Dashboard data loading
- Statistics updates
- Charts rendering
- Recent activities

#### `js/pages/customers.js`
- Customer list loading
- Search & filter
- Table rendering
- CRUD operations

#### `js/pages/leads.js`
- Lead list loading
- Status & priority filters
- Table rendering
- Lead management

#### `js/pages/deals.js`
- Deal list loading
- Stage & status filters
- Pipeline visualization
- Deal management

#### `js/pages/tasks.js`
- Task list loading
- Priority & status filters
- Complete task function
- Task management

#### `js/pages/activities.js`
- Activity timeline loading
- Type & outcome filters
- Activity rendering
- Timeline view

---

## 🔄 How It Works:

### **1. Page Load:**
```
index.html → Loads config.js → auth.js → navigation.js → main.js
```

### **2. Navigation:**
```
User clicks nav link → navigation.js loads page HTML → Loads page JS → Initialize
```

### **3. Data Loading:**
```
Page JS → API calls (using config.js) → Render data → Display
```

---

## 📝 Benefits of This Structure:

✅ **Modular** - Each page is separate  
✅ **Maintainable** - Easy to find and edit files  
✅ **Scalable** - Add new pages easily  
✅ **Clean** - Separation of concerns  
✅ **Reusable** - Components can be reused  

---

## 🎯 Adding New Pages:

### **1. Create HTML:**
```
frontend/pages/newpage.html
```

### **2. Create JS:**
```
frontend/js/pages/newpage.js
```

### **3. Add Navigation:**
Edit `components/navbar.html` and add:
```html
<a href="#" class="nav-link" data-section="newpage">New Page</a>
```

### **4. Done!**
The routing system will automatically handle it.

---

## 🔧 Customization:

### **Change API URL:**
Edit `js/config.js`:
```javascript
const API_BASE = 'http://your-api-url/api';
```

### **Add New Component:**
1. Create `components/component.html`
2. Load it in any page using fetch

### **Modify Styles:**
Edit `styles.css` - All styles in one place

---

**This structure makes the frontend clean, organized, and easy to maintain!** ✨

