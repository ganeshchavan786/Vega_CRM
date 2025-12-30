// Permissions Page JavaScript

// State management
if (typeof window.permissionsState === 'undefined') {
    window.permissionsState = {
        permissions: [],
        rolePermissions: {},
        companyRolePermissions: {},
        selectedCompanyId: null,
        changes: new Map(), // Track changes: key = "role:permission_id", value = granted (boolean)
        companyChanges: new Map() // Track company-specific changes
    };
}

// Initialize permissions page
window.initPermissions = function() {
    // Check if user is admin
    if (!currentUser || (currentUser.role !== 'super_admin' && currentUser.role !== 'admin')) {
        const container = document.querySelector('.page-container');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <h2>Access Denied</h2>
                    <p>You don't have permission to access this page.</p>
                    <button class="btn btn-primary" onclick="loadPage('dashboard')">Go to Dashboard</button>
                </div>
            `;
        }
        return;
    }

    // Setup tab switching
    setupTabs();
    
    // Load data based on active tab
    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'list';
    if (activeTab === 'list') {
        loadPermissionsList();
    } else if (activeTab === 'roles') {
        loadRolePermissions();
    } else if (activeTab === 'company') {
        loadCompaniesForSelector();
    }
};

// Setup tab switching (make global for reuse)
window.setupTabs = function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

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
                loadPermissionsList();
            } else if (tab === 'roles') {
                document.getElementById('permissionsRolesTab').classList.add('active');
                loadRolePermissions();
            } else if (tab === 'company') {
                document.getElementById('permissionsCompanyTab').classList.add('active');
                loadCompaniesForSelector();
            }
        });
    });
}

// Load all permissions list
window.loadPermissionsList = async function() {
    const tableBody = document.getElementById('permissionsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '<tr><td colspan="4" class="loading-state"><div class="spinner"></div>Loading permissions...</td></tr>';

    try {
        console.log('Loading permissions from:', `${API_BASE}/permissions`);
        console.log('Headers:', getHeaders());
        
        const response = await fetch(`${API_BASE}/permissions`, {
            headers: getHeaders()
        });

        console.log('Permissions API response status:', response.status);

        if (response.status === 401) {
            console.error('401 Unauthorized - redirecting to login');
            handle401Error();
            return;
        }
        
        if (response.status === 403) {
            tableBody.innerHTML = '<tr><td colspan="4" class="error-state">Access denied. Admin role required.</td></tr>';
            return;
        }

        const data = await response.json();
        console.log('Permissions API response data:', data);

        if (response.ok && data.permissions) {
            window.permissionsState.permissions = data.permissions;
            renderPermissionsList(data.permissions);
            setupPermissionFilters();
        } else {
            tableBody.innerHTML = `<tr><td colspan="4" class="error-state">Error: ${data.detail || 'Failed to load permissions'}</td></tr>`;
        }
    } catch (error) {
        console.error('Error loading permissions:', error);
        tableBody.innerHTML = '<tr><td colspan="4" class="error-state">Connection error. Please try again.</td></tr>';
    }
}

// Render permissions list
window.renderPermissionsList = function(permissions) {
    const tableBody = document.getElementById('permissionsTableBody');
    if (!tableBody) return;

    if (permissions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="empty-state">No permissions found</td></tr>';
        return;
    }

    tableBody.innerHTML = permissions.map(perm => `
        <tr>
            <td><strong>${perm.resource}</strong></td>
            <td><span class="badge badge-primary">${perm.action}</span></td>
            <td>${perm.description || '-'}</td>
            <td>
                <button class="btn btn-sm btn-link" onclick="viewPermissionDetail(${perm.id})" title="View Details">
                    View
                </button>
            </td>
        </tr>
    `).join('');
}

// Setup permission filters
function setupPermissionFilters() {
    const searchInput = document.getElementById('permissionSearch');
    const resourceFilter = document.getElementById('permissionResourceFilter');
    const actionFilter = document.getElementById('permissionActionFilter');

    if (searchInput) {
        searchInput.addEventListener('input', filterPermissions);
    }
    if (resourceFilter) {
        resourceFilter.addEventListener('change', filterPermissions);
    }
    if (actionFilter) {
        actionFilter.addEventListener('change', filterPermissions);
    }
}

// Filter permissions
window.filterPermissions = function() {
    const search = document.getElementById('permissionSearch')?.value.toLowerCase() || '';
    const resource = document.getElementById('permissionResourceFilter')?.value || '';
    const action = document.getElementById('permissionActionFilter')?.value || '';

    const filtered = window.permissionsState.permissions.filter(perm => {
        const matchSearch = !search || 
            perm.resource.toLowerCase().includes(search) ||
            perm.action.toLowerCase().includes(search) ||
            (perm.description && perm.description.toLowerCase().includes(search));
        
        const matchResource = !resource || perm.resource === resource;
        const matchAction = !action || perm.action === action;

        return matchSearch && matchResource && matchAction;
    });

    renderPermissionsList(filtered);
}

// View permission detail (simple alert for now)
window.viewPermissionDetail = function(permissionId) {
    const perm = window.permissionsState.permissions.find(p => p.id === permissionId);
    if (perm) {
        alert(`Permission: ${perm.resource}:${perm.action}\n\nDescription: ${perm.description || 'N/A'}`);
    }
};

// Load role permissions matrix
async function loadRolePermissions() {
    const matrixBody = document.getElementById('rolesMatrixBody');
    if (!matrixBody) return;

    matrixBody.innerHTML = '<tr><td colspan="5" class="loading-state"><div class="spinner"></div>Loading role permissions...</td></tr>';

    try {
        // Load permissions first
        const permsResponse = await fetch(`${API_BASE}/permissions`, {
            headers: getHeaders()
        });

        if (permsResponse.status === 401) {
            handle401Error();
            return;
        }

        const permsData = await permsResponse.json();
        if (!permsResponse.ok || !permsData.permissions) {
            matrixBody.innerHTML = `<tr><td colspan="5" class="error-state">Error loading permissions</td></tr>`;
            return;
        }

        const permissions = permsData.permissions;
        window.permissionsState.permissions = permissions;

        // Load role-permissions for each role
        const roles = ['admin', 'manager', 'sales_rep', 'user'];
        const rolePermsMap = {};

        for (const role of roles) {
            try {
                // Use correct backend endpoint: /api/role-permissions with query params
                const rolePermsResponse = await fetch(`${API_BASE}/role-permissions?role=${role}${companyId ? '&company_id=' + companyId : ''}`, {
                    headers: getHeaders()
                });

                if (rolePermsResponse.ok) {
                    const rolePermsData = await rolePermsResponse.json();
                    if (rolePermsData.role_permissions) {
                        rolePermsMap[role] = rolePermsData.role_permissions.reduce((acc, rp) => {
                            // Include company-specific permissions
                            if (rp.granted && rp.company_id === companyId) {
                                acc[rp.permission_id] = true;
                            }
                            return acc;
                        }, {});
                    }
                }
            } catch (error) {
                console.error(`Error loading permissions for role ${role}:`, error);
            }
        }

        window.permissionsState.rolePermissions = rolePermsMap;
        renderRolePermissionsMatrix(permissions, rolePermsMap);
        setupRolePermissionsHandlers();
    } catch (error) {
        console.error('Error loading role permissions:', error);
        matrixBody.innerHTML = '<tr><td colspan="5" class="error-state">Connection error. Please try again.</td></tr>';
    }
}

// Render role permissions matrix
function renderRolePermissionsMatrix(permissions, rolePermsMap) {
    const matrixBody = document.getElementById('rolesMatrixBody');
    if (!matrixBody) return;

    const roles = ['admin', 'manager', 'sales_rep', 'user'];

    matrixBody.innerHTML = permissions.map(perm => {
        const row = roles.map(role => {
            const isGranted = rolePermsMap[role] && rolePermsMap[role][perm.id];
            const checkboxId = `role_${role}_perm_${perm.id}`;
            return `
                <td class="matrix-checkbox-cell">
                    <label class="checkbox-label">
                        <input 
                            type="checkbox" 
                            id="${checkboxId}"
                            data-role="${role}"
                            data-permission-id="${perm.id}"
                            ${isGranted ? 'checked' : ''}
                            class="permission-checkbox"
                        />
                        <span class="checkmark"></span>
                    </label>
                </td>
            `;
        }).join('');

        return `
            <tr>
                <td class="matrix-permission-cell">
                    <strong>${perm.resource}:${perm.action}</strong>
                    ${perm.description ? `<br><small class="text-muted">${perm.description}</small>` : ''}
                </td>
                ${row}
            </tr>
        `;
    }).join('');
}

// Setup role permissions checkbox handlers
window.setupRolePermissionsHandlers = function() {
    const checkboxes = document.querySelectorAll('#rolesMatrix .permission-checkbox');
    const saveBtn = document.getElementById('permissionsSaveBtn');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            markRolePermissionsChanged();
        });
    });

    // Save button handler
    if (saveBtn) {
        saveBtn.addEventListener('click', saveRolePermissions);
    }

    // Reset button handler
    const resetBtn = document.getElementById('permissionsResetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Reset all role permissions to defaults? This will discard all changes.')) {
                window.permissionsState.changes.clear();
                loadRolePermissions();
            }
        });
    }
}

// Mark role permissions as changed
function markRolePermissionsChanged() {
    const saveBtn = document.getElementById('permissionsSaveBtn');
    if (saveBtn) {
        saveBtn.style.display = 'inline-flex';
    }
}

// Save role permissions
window.saveRolePermissions = async function() {
    if (!companyId) {
        alert('Please select a company first');
        return;
    }

    const checkboxes = document.querySelectorAll('#rolesMatrix .permission-checkbox');
    const roles = ['admin', 'manager', 'sales_rep', 'user'];
    const saveBtn = document.getElementById('permissionsSaveBtn');

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="icon">⏳</i> Saving...';
    }

    try {
        // Group changes by role
        const roleUpdates = {};

        checkboxes.forEach(checkbox => {
            const role = checkbox.dataset.role;
            const permissionId = parseInt(checkbox.dataset.permissionId);
            const granted = checkbox.checked;

            if (!roleUpdates[role]) {
                roleUpdates[role] = [];
            }

            roleUpdates[role].push({
                permission_id: permissionId,
                granted: granted
            });
        });

        // Save each role's permissions using correct backend endpoint
        const promises = Object.entries(roleUpdates).map(([role, permissions]) => {
            return fetch(`${API_BASE}/role-permissions/bulk-update`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    role: role,
                    company_id: companyId ? parseInt(companyId) : null,
                    permissions: permissions
                })
            });
        });

        const responses = await Promise.all(promises);
        const allOk = responses.every(r => r.ok);

        if (allOk) {
            alert('Permissions updated successfully!');
            window.permissionsState.changes.clear();
            if (saveBtn) {
                saveBtn.style.display = 'none';
            }
            // Reload to get fresh data
            loadRolePermissions();
        } else {
            const errorData = await responses.find(r => !r.ok).json();
            alert(`Error: ${errorData.detail || 'Failed to update permissions'}`);
        }
    } catch (error) {
        console.error('Error saving role permissions:', error);
        alert('Connection error. Please try again.');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="icon">💾</i> Save Changes';
        }
    }
}

// Load companies for company selector
async function loadCompaniesForSelector() {
    const select = document.getElementById('companyPermissionsSelect');
    if (!select) return;

    try {
        const response = await fetch(`${API_BASE}/companies`, {
            headers: getHeaders()
        });

        if (response.status === 401) {
            handle401Error();
            return;
        }

        const data = await response.json();

        if (response.ok && data.data) {
            const companies = data.data;
            select.innerHTML = '<option value="">-- Select Company --</option>' +
                companies.map(comp => `<option value="${comp.id}">${comp.name}</option>`).join('');

            // If current company is set, select it
            if (companyId) {
                select.value = companyId;
                loadCompanyPermissions(companyId);
            }

            // Setup change handler
            select.addEventListener('change', (e) => {
                const selectedCompanyId = parseInt(e.target.value);
                if (selectedCompanyId) {
                    window.permissionsState.selectedCompanyId = selectedCompanyId;
                    loadCompanyPermissions(selectedCompanyId);
                } else {
                    document.getElementById('companyPermissionsMatrixContainer').style.display = 'none';
                    document.getElementById('companyPermissionsEmpty').style.display = 'block';
                }
            });
        }
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

// Load company-specific permissions
async function loadCompanyPermissions(companyId) {
    const matrixBody = document.getElementById('companyMatrixBody');
    const container = document.getElementById('companyPermissionsMatrixContainer');
    const emptyState = document.getElementById('companyPermissionsEmpty');
    const copyBtn = document.getElementById('copyFromGlobalBtn');
    const resetBtn = document.getElementById('resetCompanyPermsBtn');

    if (!matrixBody) return;

    container.style.display = 'block';
    emptyState.style.display = 'none';
    if (copyBtn) copyBtn.style.display = 'inline-flex';
    if (resetBtn) resetBtn.style.display = 'inline-flex';

    matrixBody.innerHTML = '<tr><td colspan="5" class="loading-state"><div class="spinner"></div>Loading company permissions...</td></tr>';

    try {
        // Load permissions
        const permsResponse = await fetch(`${API_BASE}/permissions`, {
            headers: getHeaders()
        });

        if (!permsResponse.ok) {
            matrixBody.innerHTML = '<tr><td colspan="5" class="error-state">Error loading permissions</td></tr>';
            return;
        }

        const permsData = await permsResponse.json();
        const permissions = permsData.permissions || [];
        window.permissionsState.permissions = permissions;

        // Load company role-permissions
        const roles = ['admin', 'manager', 'sales_rep', 'user'];
        const rolePermsMap = {};

        for (const role of roles) {
            try {
                // Use correct backend endpoint: /api/role-permissions with company_id filter
                const rolePermsResponse = await fetch(`${API_BASE}/role-permissions?role=${role}&company_id=${companyId}`, {
                    headers: getHeaders()
                });

                if (rolePermsResponse.ok) {
                    const rolePermsData = await rolePermsResponse.json();
                    if (rolePermsData.role_permissions) {
                        rolePermsMap[role] = rolePermsData.role_permissions.reduce((acc, rp) => {
                            // Include company-specific permissions
                            if (rp.granted && rp.company_id === companyId) {
                                acc[rp.permission_id] = true;
                            }
                            return acc;
                        }, {});
                    }
                }
            } catch (error) {
                console.error(`Error loading company permissions for role ${role}:`, error);
            }
        }

        window.permissionsState.companyRolePermissions = rolePermsMap;
        renderCompanyPermissionsMatrix(permissions, rolePermsMap);
        setupCompanyPermissionsHandlers(companyId);
    } catch (error) {
        console.error('Error loading company permissions:', error);
        matrixBody.innerHTML = '<tr><td colspan="5" class="error-state">Connection error. Please try again.</td></tr>';
    }
}

// Render company permissions matrix
window.renderCompanyPermissionsMatrix = function(permissions, rolePermsMap) {
    const matrixBody = document.getElementById('companyMatrixBody');
    if (!matrixBody) return;

    const roles = ['admin', 'manager', 'sales_rep', 'user'];

    matrixBody.innerHTML = permissions.map(perm => {
        const row = roles.map(role => {
            const isGranted = rolePermsMap[role] && rolePermsMap[role][perm.id];
            const checkboxId = `company_role_${role}_perm_${perm.id}`;
            return `
                <td class="matrix-checkbox-cell">
                    <label class="checkbox-label">
                        <input 
                            type="checkbox" 
                            id="${checkboxId}"
                            data-role="${role}"
                            data-permission-id="${perm.id}"
                            ${isGranted ? 'checked' : ''}
                            class="company-permission-checkbox"
                        />
                        <span class="checkmark"></span>
                    </label>
                </td>
            `;
        }).join('');

        return `
            <tr>
                <td class="matrix-permission-cell">
                    <strong>${perm.resource}:${perm.action}</strong>
                    ${perm.description ? `<br><small class="text-muted">${perm.description}</small>` : ''}
                </td>
                ${row}
            </tr>
        `;
    }).join('');
}

// Setup company permissions handlers
window.setupCompanyPermissionsHandlers = function(companyId) {
    const checkboxes = document.querySelectorAll('#companyMatrix .company-permission-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            markCompanyPermissionsChanged();
        });
    });

    // Save button handler
    const saveBtn = document.getElementById('permissionsSaveBtn');
    if (saveBtn) {
        saveBtn.onclick = () => saveCompanyPermissions(companyId);
        saveBtn.style.display = 'none'; // Hide initially, show when changes made
    }

    // Copy from global button
    const copyBtn = document.getElementById('copyFromGlobalBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (confirm('Copy global permissions to this company? This will overwrite current company permissions.')) {
                if (typeof window.copyGlobalToCompany === 'function') {
                    window.copyGlobalToCompany(companyId);
                }
            }
        });
    }

    // Reset button
    const resetBtn = document.getElementById('resetCompanyPermsBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Reset company permissions to defaults? This will discard all changes.')) {
                window.permissionsState.companyChanges.clear();
                if (typeof window.loadCompanyPermissions === 'function') {
                    window.loadCompanyPermissions(companyId);
                }
            }
        });
    }
}

// Mark company permissions as changed
window.markCompanyPermissionsChanged = function() {
    const saveBtn = document.getElementById('permissionsSaveBtn');
    if (saveBtn) {
        saveBtn.style.display = 'inline-flex';
    }
}

// Save company permissions
window.saveCompanyPermissions = async function(companyId) {
    const checkboxes = document.querySelectorAll('#companyMatrix .company-permission-checkbox');
    const roles = ['admin', 'manager', 'sales_rep', 'user'];
    const saveBtn = document.getElementById('permissionsSaveBtn');

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="icon">⏳</i> Saving...';
    }

    try {
        const roleUpdates = {};

        checkboxes.forEach(checkbox => {
            const role = checkbox.dataset.role;
            const permissionId = parseInt(checkbox.dataset.permissionId);
            const granted = checkbox.checked;

            if (!roleUpdates[role]) {
                roleUpdates[role] = [];
            }

            roleUpdates[role].push({
                permission_id: permissionId,
                granted: granted
            });
        });

        // Save company permissions using correct backend endpoint
        const promises = Object.entries(roleUpdates).map(([role, permissions]) => {
            return fetch(`${API_BASE}/role-permissions/bulk-update`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    role: role,
                    company_id: parseInt(companyId),
                    permissions: permissions
                })
            });
        });

        const responses = await Promise.all(promises);
        const allOk = responses.every(r => r.ok);

        if (allOk) {
            alert('Company permissions updated successfully!');
            window.permissionsState.companyChanges.clear();
            if (saveBtn) {
                saveBtn.style.display = 'none';
            }
            if (typeof window.loadCompanyPermissions === 'function') {
                window.loadCompanyPermissions(companyId);
            }
        } else {
            const errorData = await responses.find(r => !r.ok).json();
            alert(`Error: ${errorData.detail || 'Failed to update permissions'}`);
        }
    } catch (error) {
        console.error('Error saving company permissions:', error);
        alert('Connection error. Please try again.');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="icon">💾</i> Save Changes';
        }
    }
}

// Copy global permissions to company
window.copyGlobalToCompany = async function(companyId) {
    if (!confirm('This will copy all global role permissions to this company. Continue?')) {
        return;
    }
    
    try {
        showToast('Copying permissions...', 'info');
        
        const response = await fetch(`${API_BASE}/permissions/copy-to-company/${companyId}`, {
            method: 'POST',
            headers: getHeaders()
        });
        
        if (response.ok) {
            showToast('Permissions copied successfully!', 'success');
            if (typeof window.loadCompanyPermissions === 'function') {
                window.loadCompanyPermissions(companyId);
            }
        } else {
            const data = await response.json();
            showToast(data.detail || 'Failed to copy permissions', 'error');
        }
    } catch (error) {
        console.error('Error copying permissions:', error);
        showToast('Connection error. Please try again.', 'error');
    }
}

// ==================== EXPORT FUNCTIONALITY ====================

// Export permissions to CSV
window.exportPermissionsCSV = function() {
    const permissions = window.permissionsState.permissions;
    if (!permissions || permissions.length === 0) {
        showToast('No permissions to export', 'warning');
        return;
    }
    
    // CSV header
    let csv = 'ID,Resource,Action,Description,Created At\n';
    
    // CSV rows
    permissions.forEach(perm => {
        csv += `${perm.id},"${perm.resource}","${perm.action}","${perm.description || ''}","${perm.created_at || ''}"\n`;
    });
    
    downloadFile(csv, 'permissions.csv', 'text/csv');
    showToast('Permissions exported to CSV', 'success');
}

// Export permissions to JSON
window.exportPermissionsJSON = function() {
    const permissions = window.permissionsState.permissions;
    if (!permissions || permissions.length === 0) {
        showToast('No permissions to export', 'warning');
        return;
    }
    
    const json = JSON.stringify(permissions, null, 2);
    downloadFile(json, 'permissions.json', 'application/json');
    showToast('Permissions exported to JSON', 'success');
}

// Export role permissions matrix to CSV
window.exportRolePermissionsCSV = function() {
    const permissions = window.permissionsState.permissions;
    const rolePerms = window.permissionsState.rolePermissions;
    
    if (!permissions || permissions.length === 0) {
        showToast('No permissions to export', 'warning');
        return;
    }
    
    const roles = ['admin', 'manager', 'sales_rep', 'user'];
    
    // CSV header
    let csv = 'Permission,' + roles.join(',') + '\n';
    
    // CSV rows
    permissions.forEach(perm => {
        const permName = `${perm.resource}:${perm.action}`;
        const roleValues = roles.map(role => {
            return (rolePerms[role] && rolePerms[role][perm.id]) ? 'Yes' : 'No';
        });
        csv += `"${permName}",${roleValues.join(',')}\n`;
    });
    
    downloadFile(csv, 'role_permissions_matrix.csv', 'text/csv');
    showToast('Role permissions exported to CSV', 'success');
}

// Helper function to download file
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ==================== TOAST NOTIFICATIONS ====================

// Show toast notification
window.showToast = function(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    
    // Icon based on type
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== PERMISSION DETAIL MODAL ====================

// View permission details in modal
window.viewPermissionDetails = async function(permissionId) {
    const permission = window.permissionsState.permissions.find(p => p.id === permissionId);
    if (!permission) {
        showToast('Permission not found', 'error');
        return;
    }
    
    // Create modal HTML
    const modalHtml = `
        <div id="permissionDetailModal" class="modal" style="display: flex;">
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>Permission Details</h3>
                    <button class="modal-close" onclick="closePermissionDetailModal()">×</button>
                </div>
                <div class="modal-body">
                    <div class="detail-row">
                        <label>ID:</label>
                        <span>${permission.id}</span>
                    </div>
                    <div class="detail-row">
                        <label>Resource:</label>
                        <span class="badge badge-primary">${permission.resource}</span>
                    </div>
                    <div class="detail-row">
                        <label>Action:</label>
                        <span class="badge badge-info">${permission.action}</span>
                    </div>
                    <div class="detail-row">
                        <label>Description:</label>
                        <span>${permission.description || 'No description'}</span>
                    </div>
                    <div class="detail-row">
                        <label>Created:</label>
                        <span>${permission.created_at ? new Date(permission.created_at).toLocaleString() : 'N/A'}</span>
                    </div>
                    
                    <h4 style="margin-top: 20px;">Assigned to Roles:</h4>
                    <div class="roles-list">
                        ${getRolesForPermission(permissionId)}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closePermissionDetailModal()">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Get roles that have this permission
function getRolesForPermission(permissionId) {
    const rolePerms = window.permissionsState.rolePermissions;
    const roles = ['admin', 'manager', 'sales_rep', 'user'];
    
    const assignedRoles = roles.filter(role => rolePerms[role] && rolePerms[role][permissionId]);
    
    if (assignedRoles.length === 0) {
        return '<span class="text-muted">No roles assigned</span>';
    }
    
    return assignedRoles.map(role => `<span class="badge badge-success">${role}</span>`).join(' ');
}

// Close permission detail modal
window.closePermissionDetailModal = function() {
    const modal = document.getElementById('permissionDetailModal');
    if (modal) {
        modal.remove();
    }
}

