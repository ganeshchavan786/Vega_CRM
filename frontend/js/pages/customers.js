// Customers Page JavaScript

// Use window object to avoid redeclaration errors when script loads multiple times
if (typeof window.currentEditingCustomerId === 'undefined') {
    window.currentEditingCustomerId = null;
}

function initCustomers() {
    // Check if we have valid auth before loading (use global variables from config.js)
    if (!authToken || !companyId) {
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
        let url = `${API_BASE}/companies/${companyId}/customers?page=1&per_page=50`;
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
        
        const data = await response.json();

        const table = document.getElementById('customersTable');
        if (!table) return;

        if (data.data && data.data.length > 0) {
            table.innerHTML = `
                <table class="table-advanced">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Health</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(customer => `
                            <tr>
                                <td><strong>${escapeHtml(customer.name || '-')}</strong></td>
                                <td>${escapeHtml(customer.email || '-')}</td>
                                <td>${escapeHtml(customer.phone || '-')}</td>
                                <td><span class="badge badge-secondary">${escapeHtml(customer.customer_type || 'individual')}</span></td>
                                <td><span class="activity-badge badge-${customer.status || 'active'}">${escapeHtml((customer.status || 'active').toUpperCase())}</span></td>
                                <td>${customer.health_score ? `<span class="health-badge health-${customer.health_score}">${escapeHtml(customer.health_score)}</span>` : '-'}</td>
                                <td>
                                    <button class="btn-icon btn-edit" onclick="editCustomer(${customer.id})" title="Edit">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                            <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                    <button class="btn-icon btn-delete" onclick="deleteCustomer(${customer.id})" title="Delete">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M12 4V13.3333C12 13.687 11.8595 14.0261 11.6095 14.2761C11.3594 14.5262 11.0203 14.6667 10.6667 14.6667H5.33333C4.97971 14.6667 4.64057 14.5262 4.39052 14.2761C4.14048 14.0261 4 13.687 4 13.3333V4M6 4V2.66667C6 2.31305 6.14048 1.97391 6.39052 1.72386C6.64057 1.47381 6.97971 1.33334 7.33333 1.33334H8.66667C9.02029 1.33334 9.35943 1.47381 9.60948 1.72386C9.85952 1.97391 10 2.31305 10 2.66667V4M2 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            table.innerHTML = '<div class="empty-state"><h3>No customers found</h3><p>Create your first customer!</p></div>';
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
            loadCustomers();
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
    if (!confirm('Are you sure you want to delete this customer? This action cannot be undone.')) {
        return;
    }
    
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
            loadCustomers();
            if (typeof showNotification === 'function') {
                showNotification('Customer deleted successfully!', 'success');
            }
        } else {
            const result = await response.json();
            alert(result.detail || 'Failed to delete customer');
        }
    } catch (error) {
        console.error('Error deleting customer:', error);
        alert('Connection error. Please try again.');
    }
};

// closeFormModal is now defined globally in navigation.js
// This is kept for backward compatibility
if (typeof window.closeFormModal === 'undefined') {
    window.closeFormModal = function() {
        const modal = document.getElementById('formModal');
        if (modal) {
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
