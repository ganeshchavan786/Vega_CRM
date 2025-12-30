// Admin Page JavaScript

// Load permissions.js if not already loaded
function loadPermissionsScript() {
    return new Promise((resolve) => {
        if (typeof window.loadPermissionsList === 'function') {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'js/pages/permissions.js?t=' + new Date().getTime();
        script.onload = () => {
            console.log('permissions.js loaded for admin page');
            resolve();
        };
        script.onerror = () => {
            console.error('Failed to load permissions.js');
            resolve();
        };
        document.head.appendChild(script);
    });
}

// Initialize admin page
window.initAdmin = async function() {
    // Load permissions.js first
    await loadPermissionsScript();
    // Check if user is admin
    if (!currentUser || (currentUser.role !== 'super_admin' && currentUser.role !== 'admin')) {
        const container = document.querySelector('.admin-page-container');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <h2>Access Denied</h2>
                    <p>You don't have permission to access this page. Admin access required.</p>
                    <button class="btn btn-primary" onclick="if(typeof loadPage === 'function') loadPage('dashboard'); else window.location.reload();">Go to Dashboard</button>
                </div>
            `;
        }
        return;
    }

    // Setup sidebar menu
    setupAdminSidebarMenu();
    
    // Load default section (permissions)
    const activeSection = document.querySelector('.admin-menu-item.active')?.dataset.adminSection || 'permissions';
    loadAdminSection(activeSection);
};

// Setup admin sidebar menu
function setupAdminSidebarMenu() {
    const menuItems = document.querySelectorAll('.admin-menu-item');
    
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.adminSection;
            
            // Update active states
            menuItems.forEach(mi => mi.classList.remove('active'));
            item.classList.add('active');
            
            // Load section
            loadAdminSection(section);
        });
    });
}

// Load admin section
function loadAdminSection(section) {
    // Hide all sections
    const sections = document.querySelectorAll('.admin-section');
    sections.forEach(sec => sec.classList.remove('active'));
    
    // Show selected section
    const targetSection = document.getElementById(`admin${section.charAt(0).toUpperCase() + section.slice(1)}Section`);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Initialize section-specific code
        if (section === 'permissions') {
            initPermissionsSection();
        } else if (section === 'users') {
            loadUsers();
        } else if (section === 'companies') {
            loadCompanies();
        } else if (section === 'settings') {
            setupSettingsTabs();
            loadEmailSettings();
        }
    }
}

// Initialize permissions section (reuse permissions.js functions)
function initPermissionsSection() {
    // Setup tabs (same as permissions.js)
    setupTabs();
    
    // Load data based on active tab
    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'list';
    if (activeTab === 'list') {
        if (typeof loadPermissionsList === 'function') {
            loadPermissionsList();
        }
    } else if (activeTab === 'roles') {
        if (typeof loadRolePermissions === 'function') {
            loadRolePermissions();
        }
    } else if (activeTab === 'company') {
        if (typeof loadCompaniesForSelector === 'function') {
            loadCompaniesForSelector();
        }
    }
}

// Setup tabs (same as permissions.js)
function setupTabs() {
    const tabButtons = document.querySelectorAll('#adminPermissionsSection .tab-btn');
    const tabContents = document.querySelectorAll('#adminPermissionsSection .tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // Update active states
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Show appropriate tab content
            if (tab === 'list') {
                document.getElementById('permissionsListTab').classList.add('active');
                if (typeof loadPermissionsList === 'function') {
                    loadPermissionsList();
                }
            } else if (tab === 'roles') {
                document.getElementById('permissionsRolesTab').classList.add('active');
                if (typeof loadRolePermissions === 'function') {
                    loadRolePermissions();
                }
            } else if (tab === 'company') {
                document.getElementById('permissionsCompanyTab').classList.add('active');
                if (typeof loadCompaniesForSelector === 'function') {
                    loadCompaniesForSelector();
                }
            }
        });
    });
}

// ==================== USER MANAGEMENT ====================
let adminAllUsers = [];
let usersDataTable = null;

window.loadUsers = async function() {
    // Create container for DataTable if not exists
    const tableContainer = document.getElementById('usersTableContainer');
    const oldTable = document.getElementById('usersTable');
    
    if (oldTable && !tableContainer) {
        // Replace old table with DataTable container
        const container = document.createElement('div');
        container.id = 'usersTableContainer';
        oldTable.parentNode.replaceChild(container, oldTable);
    }
    
    const containerId = 'usersTableContainer';
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Show loading
    container.innerHTML = '<div class="datatable-loading"><div class="datatable-loading-spinner"><div class="spinner"></div><span>Loading users...</span></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/users`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) { handle401Error(); return; }
        
        const data = await response.json();
        if (response.ok && data.data) {
            adminAllUsers = data.data;
            renderUsersDataTable(adminAllUsers);
        } else {
            container.innerHTML = '<div class="datatable-error">Error loading users</div>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        container.innerHTML = '<div class="datatable-error">Connection error</div>';
    }
};

function renderUsersDataTable(users) {
    const containerId = 'usersTableContainer';
    
    // Destroy existing DataTable
    if (usersDataTable) {
        usersDataTable.destroy();
    }
    
    // Create new DataTable
    usersDataTable = new DataTable(containerId, {
        data: users,
        columns: [
            { 
                key: 'name', 
                label: 'Name',
                render: (val, row) => `<strong>${row.first_name || ''} ${row.last_name || ''}</strong>`
            },
            { key: 'email', label: 'Email' },
            { 
                key: 'role', 
                label: 'Role',
                render: (val) => `<span class="status-badge status-${val}">${val}</span>`
            },
            { 
                key: 'is_active', 
                label: 'Status',
                render: (val) => `<span class="status-badge status-${val ? 'active' : 'inactive'}">${val ? 'Active' : 'Inactive'}</span>`
            },
            { key: 'created_at', label: 'Created', type: 'date' },
            { 
                key: 'actions', 
                label: 'Actions',
                sortable: false,
                render: (val, row) => `
                    <div class="datatable-row-actions">
                        <button class="btn-icon btn-edit" onclick="editUser(${row.id})" title="Edit">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn-icon btn-delete" onclick="deleteUser(${row.id})" title="Delete">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                `
            }
        ],
        pagination: true,
        pageSize: 10,
        sorting: true,
        showSearch: true,
        showExport: true,
        showColumnToggle: true,
        striped: true,
        hover: true,
        emptyMessage: 'No users found'
    });
    
    window.usersDataTable = usersDataTable;
}

function getRoleBadgeClass(role) {
    const classes = { super_admin: 'danger', admin: 'primary', manager: 'info', sales_rep: 'success', user: 'secondary' };
    return classes[role] || 'secondary';
}

window.filterUsers = function() {
    // DataTable has built-in search, this is for backward compatibility
    if (usersDataTable) {
        usersDataTable.refresh();
    }
};

window.showCreateUserModal = function() {
    document.getElementById('userModalTitle').textContent = 'Add New User';
    document.getElementById('userForm').reset();
    document.getElementById('editUserId').value = '';
    document.getElementById('userPassword').required = true;
    document.getElementById('createUserModal').style.display = 'flex';
};

window.closeUserModal = function() {
    document.getElementById('createUserModal').style.display = 'none';
};

window.editUser = function(userId) {
    const user = adminAllUsers.find(u => u.id === userId);
    if (!user) return;
    
    document.getElementById('userModalTitle').textContent = 'Edit User';
    document.getElementById('editUserId').value = userId;
    document.getElementById('userFirstName').value = user.first_name || '';
    document.getElementById('userLastName').value = user.last_name || '';
    document.getElementById('userEmail').value = user.email;
    document.getElementById('userRole').value = user.role;
    document.getElementById('userPhone').value = user.phone || '';
    document.getElementById('userPassword').required = false;
    document.getElementById('userPassword').value = '';
    document.getElementById('createUserModal').style.display = 'flex';
};

window.saveUser = async function(e) {
    e.preventDefault();
    
    const userId = document.getElementById('editUserId').value;
    const userData = {
        first_name: document.getElementById('userFirstName').value,
        last_name: document.getElementById('userLastName').value,
        email: document.getElementById('userEmail').value,
        role: document.getElementById('userRole').value,
        phone: document.getElementById('userPhone').value
    };
    
    const password = document.getElementById('userPassword').value;
    if (password) userData.password = password;
    
    try {
        const url = userId 
            ? `${API_BASE}/companies/${companyId}/users/${userId}`
            : `${API_BASE}/companies/${companyId}/users`;
        
        const response = await fetch(url, {
            method: userId ? 'PUT' : 'POST',
            headers: getHeaders(),
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            closeUserModal();
            loadUsers();
            alert(userId ? 'User updated successfully!' : 'User created successfully!');
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail || 'Failed to save user'}`);
        }
    } catch (error) {
        console.error('Error saving user:', error);
        alert('Connection error. Please try again.');
    }
};

window.deleteUser = async function(userId) {
    showDeleteConfirmModal(
        'Delete User',
        'Are you sure you want to delete this user? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/users/${userId}`, {
                    method: 'DELETE',
                    headers: getHeaders()
                });
                
                if (response.ok) {
                    loadUsers();
                    showToast('User deleted successfully!', 'success');
                } else {
                    const data = await response.json();
                    showToast(data.detail || 'Failed to delete user', 'error');
                }
            } catch (error) {
                console.error('Error deleting user:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// ==================== COMPANY MANAGEMENT ====================
let adminAllCompanies = [];
let companiesDataTable = null;

window.loadCompanies = async function() {
    // Create container for DataTable if not exists
    const tableContainer = document.getElementById('companiesTableContainer');
    const oldTable = document.getElementById('companiesTable');
    
    if (oldTable && !tableContainer) {
        const container = document.createElement('div');
        container.id = 'companiesTableContainer';
        oldTable.parentNode.replaceChild(container, oldTable);
    }
    
    const containerId = 'companiesTableContainer';
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div class="datatable-loading"><div class="datatable-loading-spinner"><div class="spinner"></div><span>Loading companies...</span></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/companies`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) { handle401Error(); return; }
        
        const data = await response.json();
        if (response.ok && data.data) {
            adminAllCompanies = data.data;
            renderCompaniesDataTable(adminAllCompanies);
        } else {
            container.innerHTML = '<div class="datatable-error">Error loading companies</div>';
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        container.innerHTML = '<div class="datatable-error">Connection error</div>';
    }
};

function renderCompaniesDataTable(companies) {
    const containerId = 'companiesTableContainer';
    
    if (companiesDataTable) {
        companiesDataTable.destroy();
    }
    
    companiesDataTable = new DataTable(containerId, {
        data: companies,
        columns: [
            { 
                key: 'name', 
                label: 'Company Name',
                render: (val) => `<strong>${val}</strong>`
            },
            { key: 'email', label: 'Email', render: (val) => val || '-' },
            { key: 'phone', label: 'Phone', render: (val) => val || '-' },
            { key: 'user_count', label: 'Users', render: (val) => val || 0 },
            { key: 'created_at', label: 'Created', type: 'date' },
            { 
                key: 'actions', 
                label: 'Actions',
                sortable: false,
                render: (val, row) => `
                    <div class="datatable-row-actions">
                        <button class="btn-icon btn-edit" onclick="editCompany(${row.id})" title="Edit">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn-icon btn-delete" onclick="deleteCompany(${row.id})" title="Delete">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                `
            }
        ],
        pagination: true,
        pageSize: 10,
        sorting: true,
        showSearch: true,
        showExport: true,
        showColumnToggle: true,
        striped: true,
        hover: true,
        emptyMessage: 'No companies found'
    });
    
    window.companiesDataTable = companiesDataTable;
}

window.showCreateCompanyModal = function() {
    document.getElementById('companyModalTitle').textContent = 'Add New Company';
    document.getElementById('companyForm').reset();
    document.getElementById('editCompanyId').value = '';
    document.getElementById('createCompanyModal').style.display = 'flex';
};

window.closeCompanyModal = function() {
    document.getElementById('createCompanyModal').style.display = 'none';
};

window.editCompany = function(companyId) {
    const company = adminAllCompanies.find(c => c.id === companyId);
    if (!company) return;
    
    document.getElementById('companyModalTitle').textContent = 'Edit Company';
    document.getElementById('editCompanyId').value = companyId;
    document.getElementById('companyName').value = company.name;
    document.getElementById('companyEmail').value = company.email || '';
    document.getElementById('companyPhone').value = company.phone || '';
    document.getElementById('companyAddress').value = company.address || '';
    document.getElementById('createCompanyModal').style.display = 'flex';
};

window.saveCompany = async function(e) {
    e.preventDefault();
    
    const companyId = document.getElementById('editCompanyId').value;
    const companyData = {
        name: document.getElementById('companyName').value,
        email: document.getElementById('companyEmail').value,
        phone: document.getElementById('companyPhone').value,
        address: document.getElementById('companyAddress').value
    };
    
    try {
        const url = companyId 
            ? `${API_BASE}/companies/${companyId}`
            : `${API_BASE}/companies`;
        
        const response = await fetch(url, {
            method: companyId ? 'PUT' : 'POST',
            headers: getHeaders(),
            body: JSON.stringify(companyData)
        });
        
        if (response.ok) {
            closeCompanyModal();
            loadCompanies();
            alert(companyId ? 'Company updated successfully!' : 'Company created successfully!');
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail || 'Failed to save company'}`);
        }
    } catch (error) {
        console.error('Error saving company:', error);
        alert('Connection error. Please try again.');
    }
};

window.deleteCompany = async function(companyId) {
    showDeleteConfirmModal(
        'Delete Company',
        'Are you sure you want to delete this company? This will delete all associated data and cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}`, {
                    method: 'DELETE',
                    headers: getHeaders()
                });
                
                if (response.ok) {
                    loadCompanies();
                    showToast('Company deleted successfully!', 'success');
                } else {
                    const data = await response.json();
                    showToast(data.detail || 'Failed to delete company', 'error');
                }
            } catch (error) {
                console.error('Error deleting company:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// ==================== SETTINGS SECTION ====================

// Setup settings tabs
window.setupSettingsTabs = function() {
    const tabButtons = document.querySelectorAll('#adminSettingsSection .tab-btn');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.settingsTab;
            
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('#adminSettingsSection .tab-content').forEach(c => c.classList.remove('active'));
            
            const tabContent = document.getElementById(`${tab}SettingsTab`);
            if (tabContent) {
                tabContent.classList.add('active');
                
                // Load tab-specific data
                if (tab === 'email') loadEmailSettings();
                else if (tab === 'system') loadSystemStats();
                else if (tab === 'audit') loadAuditTrails();
                else if (tab === 'logs') loadSystemLogs();
            }
        });
    });
};

// Email Settings
window.loadEmailSettings = async function() {
    try {
        const response = await fetch(`${API_BASE}/admin/email-settings`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('smtpHost').value = data.smtp_host || '';
            document.getElementById('smtpPort').value = data.smtp_port || 587;
            document.getElementById('smtpUsername').value = data.smtp_username || '';
            document.getElementById('smtpFromEmail').value = data.smtp_from_email || '';
            document.getElementById('smtpFromName').value = data.smtp_from_name || 'Vega CRM';
            document.getElementById('smtpUseTls').checked = data.smtp_use_tls !== false;
            
            const statusEl = document.getElementById('emailConfigStatus');
            statusEl.innerHTML = data.is_configured 
                ? '<span class="status-success">Email is configured</span>'
                : '<span class="status-warning">Email not configured</span>';
        }
    } catch (error) {
        console.error('Error loading email settings:', error);
    }
};

window.selectEmailProvider = function(provider) {
    const providers = {
        gmail: { host: 'smtp.gmail.com', port: 587 },
        outlook: { host: 'smtp.office365.com', port: 587 },
        yahoo: { host: 'smtp.mail.yahoo.com', port: 587 },
        sendgrid: { host: 'smtp.sendgrid.net', port: 587 },
        custom: { host: '', port: 587 }
    };
    
    if (providers[provider]) {
        document.getElementById('smtpHost').value = providers[provider].host;
        document.getElementById('smtpPort').value = providers[provider].port;
    }
};

window.testEmailSettings = async function() {
    const email = prompt('Enter email address to send test email:');
    if (!email) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/email-settings/test`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ to_email: email })
        });
        
        const data = await response.json();
        alert(data.message || (data.success ? 'Test email sent!' : 'Failed to send test email'));
    } catch (error) {
        console.error('Error testing email:', error);
        alert('Connection error. Please try again.');
    }
};

// System Stats
window.loadSystemStats = async function() {
    try {
        const response = await fetch(`${API_BASE}/admin/system/stats`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('statTotalUsers').textContent = data.total_users || 0;
            document.getElementById('statTotalCompanies').textContent = data.total_companies || 0;
            document.getElementById('statTotalCustomers').textContent = data.total_customers || 0;
            document.getElementById('statTotalLeads').textContent = data.total_leads || 0;
            document.getElementById('statTotalDeals').textContent = data.total_deals || 0;
            document.getElementById('statTotalTasks').textContent = data.total_tasks || 0;
        }
        
        // Load health status
        refreshSystemHealth();
    } catch (error) {
        console.error('Error loading system stats:', error);
    }
};

window.refreshSystemHealth = async function() {
    try {
        const response = await fetch(`${API_BASE}/admin/system/health`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('healthDatabase').innerHTML = 
                `<span class="health-${data.database === 'healthy' ? 'good' : 'bad'}">${data.database}</span>`;
            document.getElementById('healthEmail').innerHTML = 
                `<span class="health-${data.email_service === 'configured' ? 'good' : 'warning'}">${data.email_service}</span>`;
            document.getElementById('healthApi').innerHTML = 
                `<span class="health-good">${data.status}</span>`;
        }
    } catch (error) {
        document.getElementById('healthApi').innerHTML = '<span class="health-bad">Error</span>';
    }
};

// Audit Trail
window.loadAuditTrails = async function() {
    const tableBody = document.getElementById('auditTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '<tr><td colspan="6" class="loading-state">Loading audit trails...</td></tr>';
    
    const action = document.getElementById('auditActionFilter')?.value || '';
    const resource = document.getElementById('auditResourceFilter')?.value || '';
    const search = document.getElementById('auditSearch')?.value || '';
    
    let url = `${API_BASE}/audit-trails?per_page=50`;
    if (action) url += `&action=${action}`;
    if (resource) url += `&resource_type=${resource}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    
    try {
        const response = await fetch(url, { headers: getHeaders() });
        
        if (response.ok) {
            const data = await response.json();
            renderAuditTrails(data.audit_trails || []);
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" class="error-state">Error loading audit trails</td></tr>';
        }
    } catch (error) {
        console.error('Error loading audit trails:', error);
        tableBody.innerHTML = '<tr><td colspan="6" class="error-state">Connection error</td></tr>';
    }
};

function renderAuditTrails(trails) {
    const tableBody = document.getElementById('auditTableBody');
    if (!tableBody) return;
    
    if (trails.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6" class="empty-state">No audit trails found</td></tr>';
        return;
    }
    
    tableBody.innerHTML = trails.map((trail, index) => `
        <tr>
            <td>${formatDateTimeIST(trail.timestamp)}</td>
            <td>${trail.user_email || '-'}</td>
            <td><span class="badge badge-${getActionBadgeClass(trail.action)}">${trail.action}</span></td>
            <td>${trail.resource_type}${trail.resource_id ? ' #' + trail.resource_id : ''}</td>
            <td><span class="status-badge ${trail.status.toLowerCase()}">${trail.status}</span></td>
            <td>
                <button class="btn btn-sm btn-link" onclick="showAuditDetails(${index})">View Details</button>
            </td>
        </tr>
    `).join('');
    
    // Store trails for detail view
    window.currentAuditTrails = trails;
}

function getActionBadgeClass(action) {
    const classes = { CREATE: 'success', UPDATE: 'info', DELETE: 'danger', LOGIN: 'primary', LOGOUT: 'secondary' };
    return classes[action] || 'secondary';
}

// System Logs
window.loadSystemLogs = async function() {
    const tableBody = document.getElementById('logsTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '<tr><td colspan="6" class="loading-state">Loading logs...</td></tr>';
    
    const level = document.getElementById('logLevelFilter')?.value || '';
    const category = document.getElementById('logCategoryFilter')?.value || '';
    
    let url = `${API_BASE}/logs?per_page=50`;
    if (level) url += `&level=${level}`;
    if (category) url += `&category=${category}`;
    
    try {
        const response = await fetch(url, { headers: getHeaders() });
        
        if (response.ok) {
            const data = await response.json();
            renderSystemLogs(data.logs || []);
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" class="error-state">Error loading logs</td></tr>';
        }
        
        // Load stats
        loadLogStats();
    } catch (error) {
        console.error('Error loading logs:', error);
        tableBody.innerHTML = '<tr><td colspan="6" class="error-state">Connection error</td></tr>';
    }
};

function renderSystemLogs(logs) {
    const tableBody = document.getElementById('logsTableBody');
    if (!tableBody) return;
    
    if (logs.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6" class="empty-state">No logs found</td></tr>';
        return;
    }
    
    tableBody.innerHTML = logs.map(log => `
        <tr class="log-row log-${log.level.toLowerCase()}">
            <td>${formatDateTimeIST(log.timestamp)}</td>
            <td><span class="log-level ${log.level.toLowerCase()}">${log.level}</span></td>
            <td>${log.category}</td>
            <td>${log.action}</td>
            <td>${log.message}</td>
            <td>${log.user_email || '-'}</td>
        </tr>
    `).join('');
}

window.loadLogStats = async function() {
    try {
        const response = await fetch(`${API_BASE}/logs/statistics`, { headers: getHeaders() });
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('logStatTotal').textContent = data.total_logs || 0;
            document.getElementById('logStatErrors').textContent = data.error_count || 0;
            document.getElementById('logStatWarnings').textContent = data.warning_count || 0;
            document.getElementById('logStatInfo').textContent = data.info_count || 0;
        }
    } catch (error) {
        console.error('Error loading log stats:', error);
    }
};

window.cleanupOldLogs = async function() {
    const days = prompt('Delete logs older than how many days? (minimum 30)', '90');
    if (!days || isNaN(days) || parseInt(days) < 30) {
        alert('Please enter a valid number (minimum 30 days)');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete logs older than ${days} days?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/logs/cleanup?days=${days}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(data.message || `Deleted ${data.deleted_count} old logs`);
            loadSystemLogs();
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail || 'Failed to cleanup logs'}`);
        }
    } catch (error) {
        console.error('Error cleaning up logs:', error);
        alert('Connection error. Please try again.');
    }
};

// Show Audit Details Modal
window.showAuditDetails = function(index) {
    const trail = window.currentAuditTrails[index];
    if (!trail) return;
    
    // Remove existing modal
    const existingModal = document.getElementById('auditDetailModal');
    if (existingModal) existingModal.remove();
    
    // Format old and new values
    const oldValues = trail.old_values || {};
    const newValues = trail.new_values || {};
    
    // Get all changed fields
    const allFields = new Set([...Object.keys(oldValues), ...Object.keys(newValues)]);
    
    let changesHtml = '';
    if (allFields.size > 0) {
        changesHtml = `
            <table class="audit-changes-table">
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Old Value</th>
                        <th>New Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${Array.from(allFields).map(field => {
                        const oldVal = oldValues[field] !== undefined ? oldValues[field] : '-';
                        const newVal = newValues[field] !== undefined ? newValues[field] : '-';
                        const changed = JSON.stringify(oldVal) !== JSON.stringify(newVal);
                        return `
                            <tr class="${changed ? 'changed' : ''}">
                                <td><strong>${field}</strong></td>
                                <td class="old-value">${formatValue(oldVal)}</td>
                                <td class="new-value">${formatValue(newVal)}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    } else {
        changesHtml = '<p class="no-changes">No detailed changes recorded</p>';
    }
    
    const modalHtml = `
        <div id="auditDetailModal" class="modal" style="display: flex;">
            <div class="modal-content" style="max-width: 800px;">
                <div class="form-modal-header">
                    <h2>Audit Trail Details</h2>
                    <button class="btn-close-modal" onclick="closeAuditDetailModal()">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="audit-detail-content">
                    <div class="audit-detail-header">
                        <div class="audit-detail-item">
                            <label>Timestamp</label>
                            <span>${formatDateTimeIST(trail.timestamp)}</span>
                        </div>
                        <div class="audit-detail-item">
                            <label>User</label>
                            <span>${trail.user_email || '-'}</span>
                        </div>
                        <div class="audit-detail-item">
                            <label>Action</label>
                            <span class="badge badge-${getActionBadgeClass(trail.action)}">${trail.action}</span>
                        </div>
                        <div class="audit-detail-item">
                            <label>Resource</label>
                            <span>${trail.resource_type} #${trail.resource_id || '-'}</span>
                        </div>
                        <div class="audit-detail-item">
                            <label>Status</label>
                            <span class="status-badge ${trail.status.toLowerCase()}">${trail.status}</span>
                        </div>
                    </div>
                    <div class="audit-detail-message">
                        <label>Message</label>
                        <p>${trail.message || 'No message'}</p>
                    </div>
                    <div class="audit-detail-changes">
                        <label>Changes (Old → New)</label>
                        ${changesHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Close on backdrop click
    document.getElementById('auditDetailModal').addEventListener('click', (e) => {
        if (e.target.id === 'auditDetailModal') {
            closeAuditDetailModal();
        }
    });
};

window.closeAuditDetailModal = function() {
    const modal = document.getElementById('auditDetailModal');
    if (modal) modal.remove();
};

function formatValue(val) {
    if (val === null || val === undefined) return '<em>null</em>';
    if (val === '') return '<em>empty</em>';
    if (typeof val === 'object') return JSON.stringify(val);
    return String(val);
}

// Helper functions
function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN');
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('en-IN');
}

// Format datetime in IST (Indian Standard Time)
function formatDateTimeIST(dateStr) {
    if (!dateStr) return '-';
    // Backend stores UTC time without 'Z' suffix, so we need to add it
    let utcDateStr = dateStr;
    if (!dateStr.endsWith('Z') && !dateStr.includes('+')) {
        utcDateStr = dateStr + 'Z';
    }
    const date = new Date(utcDateStr);
    return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

