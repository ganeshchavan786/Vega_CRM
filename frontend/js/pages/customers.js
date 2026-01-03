// Customers Page JavaScript

// Use window object to avoid redeclaration errors when script loads multiple times
if (typeof window.currentEditingCustomerId === 'undefined') {
    window.currentEditingCustomerId = null;
}

function initCustomers() {
    // Re-read auth from localStorage (in case global vars are stale)
    const token = localStorage.getItem('authToken');
    const company = localStorage.getItem('companyId');
    
    // Update global vars if needed
    if (token && !authToken) authToken = token;
    if (company && !companyId) companyId = company;
    
    // Check if we have valid auth before loading
    if (!token || !company) {
        console.warn('No auth token or company ID - skipping customer load');
        const table = document.getElementById('customersTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadCustomers();
}

window.loadCustomers = async function() {
    // Check auth before making API call (use global variables from config.js)
    if (!authToken || !companyId) {
        console.warn('Cannot load customers: No auth token or company ID');
        const table = document.getElementById('customersTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const search = document.getElementById('customerSearch')?.value || '';
    const status = document.getElementById('customerStatusFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/customers?page=1&per_page=100`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            console.warn('401 Unauthorized when loading customers');
            const table = document.getElementById('customersTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Session expired. Please login again.</h3></div>';
            }
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error loading customers:', response.status, errorData);
            const table = document.getElementById('customersTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Error loading customers</h3><p>Please try again</p></div>';
            }
            return;
        }
        
        const data = await response.json();
        const customers = Array.isArray(data.data) ? data.data : [];
        
        // Store customers data globally for Cards view
        window.customersData = customers;

        const table = document.getElementById('customersTable');
        if (!table) return;

        // Update stats
        if (typeof window.updateAccountStats === 'function') {
            window.updateAccountStats(customers);
        }
        
        // Initialize DataTable
        if (window.customersTable && typeof window.customersTable.updateData === 'function') {
            window.customersTable.updateData(customers);
            // Initialize Lucide icons after update
            if (typeof lucide !== 'undefined') {
                setTimeout(() => lucide.createIcons(), 100);
            }
        } else {
            window.customersTable = new DataTable('customersTable', {
                data: customers,
                columns: [
                    {
                        key: 'unique_id',
                        label: 'ID',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.85rem;">${escapeHtml(value || '-')}</code>`
                    },
                    {
                        key: 'name',
                        label: 'Name',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<strong>${escapeHtml(value || '-')}</strong>`
                    },
                    {
                        key: 'email',
                        label: 'Email',
                        sortable: true,
                        filterable: true
                    },
                    {
                        key: 'phone',
                        label: 'Phone',
                        sortable: true,
                        filterable: true
                    },
                    {
                        key: 'customer_type',
                        label: 'Type',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<span class="status-badge status-${value || 'individual'}">${escapeHtml((value || 'individual').toUpperCase())}</span>`
                    },
                    {
                        key: 'status',
                        label: 'Status',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const status = value || 'active';
                            return `<span class="status-badge status-${status}">${status.toUpperCase()}</span>`;
                        }
                    },
                    {
                        key: 'lifecycle_stage',
                        label: 'Lifecycle',
                        sortable: true,
                        align: 'center',
                        render: (value) => {
                            const stage = value || 'prospect';
                            const icons = {
                                prospect: 'target',
                                customer: 'check-circle',
                                churned: 'x-circle',
                                inactive: 'pause-circle'
                            };
                            return `<span class="lifecycle-badge ${stage}"><i data-lucide="${icons[stage] || 'circle'}" style="width:12px;height:12px;"></i> ${stage}</span>`;
                        }
                    },
                    {
                        key: 'health_score',
                        label: 'Health',
                        sortable: true,
                        align: 'center',
                        render: (value) => {
                            return renderHealthScoreMeter(value);
                        }
                    },
                    {
                        key: 'actions',
                        label: 'Actions',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            return `
                                <button class="btn-icon btn-edit" onclick="editCustomer(${row.id})" title="Edit">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                                <button class="btn-icon btn-delete" onclick="deleteCustomer(${row.id})" title="Delete">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M12 4V13.3333C12 13.687 11.8595 14.0261 11.6095 14.2761C11.3594 14.5262 11.0203 14.6667 10.6667 14.6667H5.33333C4.97971 14.6667 4.64057 14.5262 4.39052 14.2761C4.14048 14.0261 4 13.687 4 13.3333V4M6 4V2.66667C6 2.31305 6.14048 1.97391 6.39052 1.72386C6.64057 1.47381 6.97971 1.33334 7.33333 1.33334H8.66667C9.02029 1.33334 9.35943 1.47381 9.60948 1.72386C9.85952 1.97391 10 2.31305 10 2.66667V4M2 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
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
                    formats: ['csv', 'excel', 'print']
                },
                showSearch: true,
                showColumnToggle: true,
                showExport: true
            });
            // Initialize Lucide icons after DataTable creation
            if (typeof lucide !== 'undefined') {
                setTimeout(() => lucide.createIcons(), 100);
            }
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        const table = document.getElementById('customersTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading customers</h3><p>Please try again</p></div>';
        }
    }
};

// Ensure function is defined immediately when script loads
window.showCustomerForm = function() {
    console.log('showCustomerForm called');
    window.currentEditingCustomerId = null;
    
    // Verify modal elements exist
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found:', { modal: !!modal, formContent: !!formContent });
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    try {
        openCustomerModal();
    } catch (error) {
        console.error('Error in showCustomerForm:', error);
        console.error('Error stack:', error.stack);
        alert('Error opening customer form: ' + error.message);
    }
};

window.editCustomer = async function(id) {
    console.log('editCustomer called with id:', id);
    window.currentEditingCustomerId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            console.error('Failed to load customer data, status:', response.status);
            alert('Failed to load customer data');
            return;
        }
        
        const result = await response.json();
        const customer = result.data || result;
        console.log('Customer data loaded:', customer);
        
        openCustomerModal(customer);
    } catch (error) {
        console.error('Error loading customer:', error);
        alert('Error loading customer data: ' + error.message);
    }
};

// Make function global to ensure it's accessible
window.openCustomerModal = function(customer = null) {
    console.log('openCustomerModal called, customer:', customer);
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal) {
        console.error('Modal element not found!');
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    if (!formContent) {
        console.error('Form content element not found!');
        alert('Form content not found. Please refresh the page.');
        return;
    }
    
    const isEdit = !!customer;
    const title = isEdit ? 'Edit Customer' : 'Add Customer';
    console.log('Opening modal with title:', title);
    
    formContent.innerHTML = `
        <div class="form-modal-header">
            <h2>${title}</h2>
            <button class="btn-close-modal" onclick="closeFormModal()">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
        <form id="customerForm" class="form-advanced" onsubmit="handleCustomerSubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Basic Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Customer Name <span class="required">*</span></label>
                        <input type="text" id="customerName" class="form-input-advanced" value="${customer?.name || ''}" required>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Email</label>
                        <input type="email" id="customerEmail" class="form-input-advanced" value="${customer?.email || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Phone</label>
                        <input type="tel" id="customerPhone" class="form-input-advanced" value="${customer?.phone || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Secondary Phone</label>
                        <input type="tel" id="customerSecondaryPhone" class="form-input-advanced" value="${customer?.secondary_phone || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Customer Type <span class="required">*</span></label>
                        <select id="customerType" class="form-select-advanced" required>
                            <option value="individual" ${customer?.customer_type === 'individual' ? 'selected' : ''}>Individual</option>
                            <option value="business" ${customer?.customer_type === 'business' || !customer ? 'selected' : ''}>Business</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Status <span class="required">*</span></label>
                        <select id="customerStatus" class="form-select-advanced" required>
                            <option value="active" ${customer?.status === 'active' || !customer ? 'selected' : ''}>Active</option>
                            <option value="inactive" ${customer?.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                            <option value="prospect" ${customer?.status === 'prospect' ? 'selected' : ''}>Prospect</option>
                            <option value="lost" ${customer?.status === 'lost' ? 'selected' : ''}>Lost</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Business & Account Details</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Company Name</label>
                        <input type="text" id="companyName" class="form-input-advanced" value="${customer?.company_name || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Industry</label>
                        <input type="text" id="customerIndustry" class="form-input-advanced" value="${customer?.industry || ''}" placeholder="IT Services">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Company Size</label>
                        <select id="companySize" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="1-10 Employees" ${customer?.company_size === '1-10 Employees' ? 'selected' : ''}>1-10</option>
                            <option value="11-50 Employees" ${customer?.company_size === '11-50 Employees' ? 'selected' : ''}>11-50</option>
                            <option value="50-100 Employees" ${customer?.company_size === '50-100 Employees' ? 'selected' : ''}>50-100</option>
                            <option value="100-500 Employees" ${customer?.company_size === '100-500 Employees' ? 'selected' : ''}>100-500</option>
                            <option value="500+ Employees" ${customer?.company_size === '500+ Employees' ? 'selected' : ''}>500+</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Annual Revenue (₹)</label>
                        <input type="number" id="annualRevenue" class="form-input-advanced" value="${customer?.annual_revenue || ''}" placeholder="10000000">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">GSTIN</label>
                        <input type="text" id="customerGSTIN" class="form-input-advanced" value="${customer?.gstin || ''}" placeholder="27ABCDE1234F1Z5" maxlength="15">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Website</label>
                        <input type="url" id="customerWebsite" class="form-input-advanced" value="${customer?.website || ''}" placeholder="https://example.com">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Account Type</label>
                        <select id="accountType" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="customer" ${customer?.account_type === 'customer' ? 'selected' : ''}>Customer</option>
                            <option value="prospect" ${customer?.account_type === 'prospect' ? 'selected' : ''}>Prospect</option>
                            <option value="partner" ${customer?.account_type === 'partner' ? 'selected' : ''}>Partner</option>
                            <option value="competitor" ${customer?.account_type === 'competitor' ? 'selected' : ''}>Competitor</option>
                            <option value="reseller" ${customer?.account_type === 'reseller' ? 'selected' : ''}>Reseller</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Priority</label>
                        <select id="customerPriority" class="form-select-advanced">
                            <option value="low" ${customer?.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${customer?.priority === 'medium' || !customer ? 'selected' : ''}>Medium</option>
                            <option value="high" ${customer?.priority === 'high' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Health Score</label>
                        <select id="healthScore" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="green" ${customer?.health_score === 'green' ? 'selected' : ''}>Green</option>
                            <option value="yellow" ${customer?.health_score === 'yellow' ? 'selected' : ''}>Yellow</option>
                            <option value="red" ${customer?.health_score === 'red' ? 'selected' : ''}>Red</option>
                            <option value="black" ${customer?.health_score === 'black' ? 'selected' : ''}>Black</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Lifecycle Stage</label>
                        <select id="lifecycleStage" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="MQA" ${customer?.lifecycle_stage === 'MQA' ? 'selected' : ''}>MQA</option>
                            <option value="SQA" ${customer?.lifecycle_stage === 'SQA' ? 'selected' : ''}>SQA</option>
                            <option value="Customer" ${customer?.lifecycle_stage === 'Customer' ? 'selected' : ''}>Customer</option>
                            <option value="Churned" ${customer?.lifecycle_stage === 'Churned' ? 'selected' : ''}>Churned</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Address & Notes</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Address</label>
                        <textarea id="customerAddress" class="form-textarea-advanced" rows="2" style="min-height: 50px;">${customer?.address || ''}</textarea>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">City</label>
                        <input type="text" id="customerCity" class="form-input-advanced" value="${customer?.city || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">State</label>
                        <input type="text" id="customerState" class="form-input-advanced" value="${customer?.state || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Country</label>
                        <input type="text" id="customerCountry" class="form-input-advanced" value="${customer?.country || 'India'}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">ZIP Code</label>
                        <input type="text" id="customerZipCode" class="form-input-advanced" value="${customer?.zip_code || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Notes</label>
                        <textarea id="customerNotes" class="form-textarea-advanced" rows="2" placeholder="Additional notes..." style="min-height: 50px;">${customer?.notes || ''}</textarea>
                    </div>
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary" id="customerSubmitBtn">
                    ${isEdit ? 'Update Customer' : 'Create Customer'}
                </button>
            </div>
            
            <div id="customerFormError" class="error-message"></div>
        </form>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('active');
    console.log('Modal opened successfully');
}

// Make handleCustomerSubmit globally accessible
window.handleCustomerSubmit = async function(e) {
    e.preventDefault();
    
    const errorDiv = document.getElementById('customerFormError');
    const submitBtn = document.getElementById('customerSubmitBtn');
    
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = window.currentEditingCustomerId ? 'Updating...' : 'Creating...';
    }
    
    try {
        const customerData = {
            name: document.getElementById('customerName').value.trim(),
            email: document.getElementById('customerEmail').value.trim() || null,
            phone: document.getElementById('customerPhone').value.trim() || null,
            secondary_phone: document.getElementById('customerSecondaryPhone').value.trim() || null,
            customer_type: document.getElementById('customerType').value,
            status: document.getElementById('customerStatus').value,
            account_type: document.getElementById('accountType').value || null,
            priority: document.getElementById('customerPriority').value,
            company_name: document.getElementById('companyName').value.trim() || null,
            industry: document.getElementById('customerIndustry').value.trim() || null,
            company_size: document.getElementById('companySize').value || null,
            annual_revenue: document.getElementById('annualRevenue').value ? parseFloat(document.getElementById('annualRevenue').value) : null,
            gstin: document.getElementById('customerGSTIN').value.trim() || null,
            website: document.getElementById('customerWebsite').value.trim() || null,
            health_score: document.getElementById('healthScore').value || null,
            lifecycle_stage: document.getElementById('lifecycleStage').value || null,
            address: document.getElementById('customerAddress').value.trim() || null,
            city: document.getElementById('customerCity').value.trim() || null,
            state: document.getElementById('customerState').value.trim() || null,
            country: document.getElementById('customerCountry').value.trim() || null,
            zip_code: document.getElementById('customerZipCode').value.trim() || null,
            notes: document.getElementById('customerNotes').value.trim() || null
        };
        
        const url = window.currentEditingCustomerId 
            ? `${API_BASE}/companies/${companyId}/customers/${window.currentEditingCustomerId}`
            : `${API_BASE}/companies/${companyId}/customers`;
        
        const method = window.currentEditingCustomerId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(customerData)
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        const result = await response.json();
        
        if (response.ok) {
            closeFormModal();
            if (window.customersTable && typeof window.customersTable.refresh === 'function') {
                window.customersTable.refresh();
            } else {
                loadCustomers();
            }
            // Show success message (optional)
            if (typeof showNotification === 'function') {
                showNotification(window.currentEditingCustomerId ? 'Customer updated successfully!' : 'Customer created successfully!', 'success');
            }
        } else {
            if (errorDiv) {
                errorDiv.textContent = result.detail || 'Failed to save customer';
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error saving customer:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = window.currentEditingCustomerId ? 'Update Customer' : 'Create Customer';
        }
    }
}

window.deleteCustomer = async function(id) {
    // Show modern confirmation modal
    showDeleteConfirmModal(
        'Delete Customer',
        'Are you sure you want to delete this customer? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/customers/${id}`, {
                    method: 'DELETE',
                    headers: getHeaders()
                });
                
                if (response.status === 401) {
                    if (typeof handle401Error === 'function') {
                        handle401Error();
                    }
                    return;
                }
                
                if (response.ok) {
                    if (window.customersTable && typeof window.customersTable.refresh === 'function') {
                        window.customersTable.refresh();
                    } else {
                        loadCustomers();
                    }
                    showToast('Customer deleted successfully!', 'success');
                } else {
                    const result = await response.json();
                    showToast(result.detail || 'Failed to delete customer', 'error');
                }
            } catch (error) {
                console.error('Error deleting customer:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// closeFormModal is now defined globally in navigation.js
// showDeleteConfirmModal and showToast are also in navigation.js
// This is kept for backward compatibility
if (typeof window.closeFormModal === 'undefined') {
    window.closeFormModal = function() {
        const modal = document.getElementById('formModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('active');
        }
        window.currentEditingCustomerId = null;
    };
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Customer Health Score Visual Meter
// ============================================

function renderHealthScoreMeter(value) {
    if (!value) return '<span style="color: #94a3b8;">-</span>';
    
    // Health score can be: excellent, good, average, poor, at_risk
    // Or numeric value 0-100
    let score, label, color, bgColor, icon;
    
    // Handle string values
    if (typeof value === 'string') {
        const healthMap = {
            'excellent': { score: 90, label: 'Excellent', color: '#10b981', icon: '💚' },
            'good': { score: 70, label: 'Good', color: '#3b82f6', icon: '💙' },
            'average': { score: 50, label: 'Average', color: '#f59e0b', icon: '💛' },
            'poor': { score: 30, label: 'Poor', color: '#ef4444', icon: '🧡' },
            'at_risk': { score: 15, label: 'At Risk', color: '#dc2626', icon: '❤️' }
        };
        
        const health = healthMap[value.toLowerCase()] || healthMap['average'];
        score = health.score;
        label = health.label;
        color = health.color;
        icon = health.icon;
    } else {
        // Handle numeric values
        score = parseInt(value) || 0;
        
        if (score >= 80) {
            label = 'Excellent';
            color = '#10b981';
            icon = '💚';
        } else if (score >= 60) {
            label = 'Good';
            color = '#3b82f6';
            icon = '💙';
        } else if (score >= 40) {
            label = 'Average';
            color = '#f59e0b';
            icon = '💛';
        } else if (score >= 20) {
            label = 'Poor';
            color = '#ef4444';
            icon = '🧡';
        } else {
            label = 'At Risk';
            color = '#dc2626';
            icon = '❤️';
        }
    }
    
    return `
        <div class="health-score-meter" title="${label} - Health Score: ${score}%" style="
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            gap: 3px;
            min-width: 65px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 0.8em;
                color: ${color};
                font-weight: 600;
            ">
                <span>${icon}</span>
                <span>${score}%</span>
            </div>
            <div style="
                width: 50px;
                height: 6px;
                background: #e5e7eb;
                border-radius: 3px;
                overflow: hidden;
            ">
                <div style="
                    width: ${score}%;
                    height: 100%;
                    background: ${color};
                    border-radius: 3px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <span style="
                font-size: 0.6em;
                color: ${color};
                text-transform: uppercase;
                letter-spacing: 0.3px;
            ">${label}</span>
        </div>
    `;
}

// ============================================
// CSV Import Feature for Accounts
// ============================================

// Store parsed CSV data
if (typeof window.parsedAccountCSVData === 'undefined') {
    window.parsedAccountCSVData = [];
}
var parsedAccountCSVData = window.parsedAccountCSVData;

window.showAccountImportModal = function() {
    const modalHtml = `
        <div id="accountImportModal" class="modal-overlay" style="display:flex; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:99999; align-items:center; justify-content:center;">
            <div class="modal-content" style="background:white; border-radius:16px; max-width:700px; width:90%; max-height:90vh; overflow-y:auto; padding:24px;">
                <div class="form-modal-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0; font-size:1.5rem; color:#1e293b;">Import Accounts from CSV</h2>
                    <button onclick="closeAccountImportModal()" style="background:none; border:none; cursor:pointer; padding:8px;">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Step 1: Upload -->
                <div id="accountImportStep1">
                    <div style="border:2px dashed #e2e8f0; border-radius:12px; padding:40px; text-align:center; margin-bottom:20px;">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" style="margin-bottom:16px;">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <p style="color:#64748b; margin-bottom:16px;">Drag & drop your CSV file here, or click to browse</p>
                        <input type="file" id="accountCsvFile" accept=".csv" style="display:none;" onchange="handleAccountCSVUpload(event)">
                        <button onclick="document.getElementById('accountCsvFile').click()" style="background:linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color:white; border:none; padding:12px 24px; border-radius:10px; cursor:pointer; font-weight:600;">
                            Select CSV File
                        </button>
                    </div>
                    <div style="background:#f8fafc; border-radius:8px; padding:16px;">
                        <p style="font-weight:600; margin-bottom:8px; color:#1e293b;">CSV Format Requirements:</p>
                        <p style="color:#64748b; font-size:0.9rem; margin-bottom:8px;">Required columns: <code>name</code></p>
                        <p style="color:#64748b; font-size:0.9rem;">Optional: <code>email, phone, customer_type, status, company_name, industry, address, city, state, country, notes</code></p>
                        <button onclick="downloadAccountSampleCSV()" style="margin-top:12px; background:#10b981; color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:0.85rem;">
                            Download Sample CSV
                        </button>
                    </div>
                </div>
                
                <!-- Step 2: Preview -->
                <div id="accountImportStep2" style="display:none;">
                    <p style="margin-bottom:16px; color:#64748b;">Preview of data to import:</p>
                    <div id="accountCsvPreview" style="max-height:300px; overflow:auto; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:20px;"></div>
                    <div style="display:flex; gap:12px; justify-content:flex-end;">
                        <button onclick="resetAccountImport()" style="background:#e2e8f0; color:#64748b; border:none; padding:12px 24px; border-radius:10px; cursor:pointer; font-weight:600;">
                            Back
                        </button>
                        <button onclick="importAccountsFromCSV()" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); color:white; border:none; padding:12px 24px; border-radius:10px; cursor:pointer; font-weight:600;">
                            Import Accounts
                        </button>
                    </div>
                </div>
                
                <!-- Step 3: Progress -->
                <div id="accountImportStep3" style="display:none; text-align:center; padding:40px 0;">
                    <div style="width:60px; height:60px; border:4px solid #e2e8f0; border-top-color:#6366f1; border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 20px;"></div>
                    <p id="accountImportProgress" style="color:#64748b;">Importing accounts...</p>
                    <div style="width:100%; height:8px; background:#e2e8f0; border-radius:4px; margin-top:16px; overflow:hidden;">
                        <div id="accountImportProgressBar" style="width:0%; height:100%; background:linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); transition:width 0.3s;"></div>
                    </div>
                </div>
                
                <!-- Step 4: Complete -->
                <div id="accountImportStep4" style="display:none; text-align:center; padding:40px 0;">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" style="margin-bottom:16px;">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <h3 style="color:#1e293b; margin-bottom:8px;">Import Complete!</h3>
                    <p id="accountImportResult" style="color:#64748b;"></p>
                    <button onclick="closeAccountImportModal(); loadCustomers();" style="margin-top:20px; background:linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color:white; border:none; padding:12px 24px; border-radius:10px; cursor:pointer; font-weight:600;">
                        View Accounts
                    </button>
                </div>
            </div>
        </div>
        <style>
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
};

window.closeAccountImportModal = function() {
    const modal = document.getElementById('accountImportModal');
    if (modal) modal.remove();
    window.parsedAccountCSVData = [];
    parsedAccountCSVData = [];
};

window.resetAccountImport = function() {
    document.getElementById('accountImportStep1').style.display = 'block';
    document.getElementById('accountImportStep2').style.display = 'none';
    window.parsedAccountCSVData = [];
    parsedAccountCSVData = [];
};

window.handleAccountCSVUpload = function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
            alert('CSV file must have at least a header row and one data row');
            return;
        }
        
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim().replace(/^["']|["']$/g, ''));
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            if (row.name) {
                data.push(row);
            }
        }
        
        if (data.length === 0) {
            alert('No valid data found. Make sure CSV has "name" column.');
            return;
        }
        
        window.parsedAccountCSVData = data;
        parsedAccountCSVData = data;
        
        // Show preview
        let previewHtml = '<table style="width:100%; border-collapse:collapse; font-size:0.85rem;">';
        previewHtml += '<thead><tr style="background:#f8fafc;">';
        ['Name', 'Email', 'Phone', 'Type', 'Status'].forEach(h => {
            previewHtml += `<th style="padding:10px; text-align:left; border-bottom:1px solid #e2e8f0;">${h}</th>`;
        });
        previewHtml += '</tr></thead><tbody>';
        
        data.slice(0, 10).forEach(row => {
            previewHtml += '<tr>';
            previewHtml += `<td style="padding:10px; border-bottom:1px solid #e2e8f0;">${row.name || '-'}</td>`;
            previewHtml += `<td style="padding:10px; border-bottom:1px solid #e2e8f0;">${row.email || '-'}</td>`;
            previewHtml += `<td style="padding:10px; border-bottom:1px solid #e2e8f0;">${row.phone || '-'}</td>`;
            previewHtml += `<td style="padding:10px; border-bottom:1px solid #e2e8f0;">${row.customer_type || 'business'}</td>`;
            previewHtml += `<td style="padding:10px; border-bottom:1px solid #e2e8f0;">${row.status || 'active'}</td>`;
            previewHtml += '</tr>';
        });
        
        if (data.length > 10) {
            previewHtml += `<tr><td colspan="5" style="padding:10px; text-align:center; color:#64748b;">... and ${data.length - 10} more rows</td></tr>`;
        }
        
        previewHtml += '</tbody></table>';
        previewHtml += `<p style="margin-top:12px; color:#64748b; font-size:0.85rem;">Total: ${data.length} accounts to import</p>`;
        
        document.getElementById('accountCsvPreview').innerHTML = previewHtml;
        document.getElementById('accountImportStep1').style.display = 'none';
        document.getElementById('accountImportStep2').style.display = 'block';
    };
    
    reader.readAsText(file);
};

window.importAccountsFromCSV = async function() {
    if (parsedAccountCSVData.length === 0) {
        showToast('No data to import', 'error');
        return;
    }
    
    document.getElementById('accountImportStep2').style.display = 'none';
    document.getElementById('accountImportStep3').style.display = 'block';
    
    let imported = 0;
    let failed = 0;
    const failedAccounts = [];
    const total = parsedAccountCSVData.length;
    
    for (let i = 0; i < parsedAccountCSVData.length; i++) {
        const row = parsedAccountCSVData[i];
        
        try {
            const accountData = {
                name: row.name,
                email: row.email || null,
                phone: row.phone || null,
                customer_type: row.customer_type || 'business',
                status: row.status || 'active',
                company_name: row.company_name || null,
                industry: row.industry || null,
                address: row.address || null,
                city: row.city || null,
                state: row.state || null,
                country: row.country || 'India',
                notes: row.notes || null
            };
            
            const response = await fetch(`${API_BASE}/companies/${companyId}/customers`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(accountData)
            });
            
            if (response.ok) {
                imported++;
            } else {
                failed++;
                let errorMsg = 'Unknown error';
                try {
                    const errorData = await response.json();
                    if (response.status === 409) {
                        errorMsg = 'Duplicate (email/phone already exists)';
                    } else if (errorData.detail) {
                        errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
                    }
                } catch (e) {}
                failedAccounts.push({ name: row.name, email: row.email, reason: errorMsg });
            }
        } catch (error) {
            failed++;
            failedAccounts.push({ name: row.name, email: row.email, reason: 'Network error' });
        }
        
        const progress = Math.round(((i + 1) / total) * 100);
        document.getElementById('accountImportProgress').textContent = `${i + 1} of ${total} processed`;
        document.getElementById('accountImportProgressBar').style.width = `${progress}%`;
    }
    
    document.getElementById('accountImportStep3').style.display = 'none';
    document.getElementById('accountImportStep4').style.display = 'block';
    
    let resultHtml = `<strong>${imported}</strong> accounts imported successfully`;
    if (failed > 0) {
        resultHtml += `<br><span style="color: #ef4444;">${failed} failed</span>`;
        resultHtml += `<div style="margin-top:10px;text-align:left;max-height:150px;overflow-y:auto;font-size:12px;background:#fef2f2;padding:10px;border-radius:8px;">`;
        resultHtml += `<strong>Failed accounts:</strong><br>`;
        failedAccounts.forEach(fa => {
            resultHtml += `• ${fa.name} (${fa.email || 'no email'}): <span style="color:#dc2626">${fa.reason}</span><br>`;
        });
        resultHtml += `</div>`;
    }
    document.getElementById('accountImportResult').innerHTML = resultHtml;
};

window.downloadAccountSampleCSV = function() {
    const sampleData = `name,email,phone,customer_type,status,company_name,industry,address,city,state,country,notes
ABC Corporation,contact@abccorp.com,+91 98765 43210,business,active,ABC Corp,IT Services,123 Main Street,Mumbai,Maharashtra,India,Key enterprise client
XYZ Industries,info@xyz.com,+91 87654 32109,business,prospect,XYZ Industries,Manufacturing,456 Industrial Area,Pune,Maharashtra,India,Potential large account
John Smith,john@email.com,+91 76543 21098,individual,active,,Consulting,789 Park Road,Bangalore,Karnataka,India,Individual consultant`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'account_import_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
};
