// Deals Page JavaScript

// Global variable for editing deal ID
if (typeof window.currentEditingDealId === 'undefined') {
    window.currentEditingDealId = null;
}

// Cache for customers list (global to avoid redeclaration)
if (typeof window.dealsCustomersList === 'undefined') {
    window.dealsCustomersList = [];
}

window.initDeals = function initDeals() {
    // Check auth before loading
    if (!authToken || !companyId) {
        console.warn('No auth token or company ID - skipping deal load');
        const table = document.getElementById('dealsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadDeals();
    loadCustomersForDealForm(); // Pre-load customers for dropdown
}

async function loadCustomersForDealForm() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers?page=1&per_page=100`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            window.dealsCustomersList = data.data || [];
        }
    } catch (error) {
        console.error('Error loading customers for deal form:', error);
    }
}

window.loadDeals = async function() {
    // Check auth before making API call
    if (!authToken || !companyId) {
        console.warn('Cannot load deals: No auth token or company ID');
        const table = document.getElementById('dealsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const search = document.getElementById('dealSearch')?.value || '';
    const stage = document.getElementById('dealStageFilter')?.value || '';
    const status = document.getElementById('dealStatusFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/deals?page=1&per_page=100`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (stage) url += `&stage=${encodeURIComponent(stage)}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error loading deals:', response.status, errorData);
            const table = document.getElementById('dealsTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Error loading deals</h3><p>Please try again</p></div>';
            }
            return;
        }
        
        const data = await response.json();
        const deals = Array.isArray(data.data) ? data.data : [];

        const table = document.getElementById('dealsTable');
        if (!table) return;

        // Initialize DataTable
        if (window.dealsTable && typeof window.dealsTable.updateData === 'function') {
            window.dealsTable.updateData(deals);
        } else {
            window.dealsTable = new DataTable('dealsTable', {
                data: deals,
                columns: [
                    {
                        key: 'deal_name',
                        label: 'Deal Name',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<strong>${escapeHtml(value || '-')}</strong>`
                    },
                    {
                        key: 'customer.name',
                        label: 'Customer',
                        sortable: true,
                        filterable: true,
                        render: (value, row) => {
                            return row.customer ? escapeHtml(row.customer.name || '-') : '-';
                        }
                    },
                    {
                        key: 'deal_value',
                        label: 'Value',
                        sortable: true,
                        type: 'currency',
                        align: 'right',
                        render: (value, row) => {
                            const currency = row.currency || '₹';
                            const symbol = currency === '₹' ? '₹' : '$';
                            return value ? `${symbol}${parseFloat(value).toLocaleString()}` : '-';
                        }
                    },
                    {
                        key: 'stage',
                        label: 'Stage',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const stage = value || 'prospect';
                            return `<span class="status-badge status-${stage}">${escapeHtml(stage.toUpperCase().replace('_', ' '))}</span>`;
                        }
                    },
                    {
                        key: 'probability',
                        label: 'Probability',
                        sortable: true,
                        align: 'center',
                        render: (value) => {
                            return value ? `${value}%` : '0%';
                        }
                    },
                    {
                        key: 'expected_close_date',
                        label: 'Close Date',
                        sortable: true,
                        type: 'date'
                    },
                    {
                        key: 'status',
                        label: 'Status',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const status = value || 'open';
                            return `<span class="status-badge status-${status}">${status.toUpperCase()}</span>`;
                        }
                    },
                    {
                        key: 'actions',
                        label: 'Actions',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            return `
                                <button class="btn-icon btn-edit" onclick="editDeal(${row.id})" title="Edit">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                                <button class="btn-icon btn-delete" onclick="deleteDeal(${row.id})" title="Delete">
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
        }
    } catch (error) {
        console.error('Error loading deals:', error);
        const table = document.getElementById('dealsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading deals</h3><p>Please try again</p></div>';
        }
    }
};

window.showDealForm = function() {
    console.log('showDealForm called');
    window.currentEditingDealId = null;
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found. Modal:', modal, 'FormContent:', formContent);
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, proceeding...');
    
    // Ensure customers are loaded
    if (window.dealsCustomersList.length === 0) {
        console.log('Loading customers for deal form...');
        loadCustomersForDealForm().then(() => {
            console.log('Customers loaded, opening modal...');
            try {
                window.openDealModal();
            } catch (error) {
                console.error('Error in showDealForm:', error);
                alert('Error opening deal form: ' + error.message);
            }
        }).catch((error) => {
            console.error('Error loading customers:', error);
            // Still try to open modal even if loading fails
            try {
                window.openDealModal();
            } catch (modalError) {
                console.error('Error opening modal:', modalError);
                alert('Error opening deal form: ' + modalError.message);
            }
        });
    } else {
        console.log('Customers already loaded, opening modal...');
        try {
            window.openDealModal();
        } catch (error) {
            console.error('Error in showDealForm:', error);
            alert('Error opening deal form: ' + error.message);
        }
    }
};

window.editDeal = async function(id) {
    window.currentEditingDealId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/deals/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            alert('Failed to load deal data');
            return;
        }
        
        const result = await response.json();
        const deal = result.data || result;
        
        // Ensure customers are loaded
        if (window.dealsCustomersList.length === 0) {
            await loadCustomersForDealForm();
        }
        
        window.openDealModal(deal);
    } catch (error) {
        console.error('Error loading deal:', error);
        alert('Error loading deal data: ' + error.message);
    }
};

window.openDealModal = function(deal = null) {
    console.log('openDealModal called, deal:', deal);
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found! Modal:', modal, 'FormContent:', formContent);
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, building form...');
    
    const isEdit = !!deal;
    const title = isEdit ? 'Edit Deal' : 'Add Deal';
    
    // Format dates for input fields
    const expectedCloseDate = deal?.expected_close_date ? new Date(deal.expected_close_date).toISOString().split('T')[0] : '';
    const actualCloseDate = deal?.actual_close_date ? new Date(deal.actual_close_date).toISOString().split('T')[0] : '';
    
    // Build customers dropdown options
    const customerOptions = window.dealsCustomersList.map(customer => 
        `<option value="${customer.id}" ${deal?.customer_id === customer.id ? 'selected' : ''}>${escapeHtml(customer.name || `Customer ${customer.id}`)}</option>`
    ).join('');
    
    formContent.innerHTML = `
        <div class="form-modal-header">
            <h2>${title}</h2>
            <button class="btn-close-modal" onclick="closeFormModal()">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
        <form id="dealForm" class="form-advanced" onsubmit="handleDealSubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Deal Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Deal Name <span class="required">*</span></label>
                        <input type="text" id="dealName" class="form-input-advanced" value="${deal?.deal_name || ''}" required>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Customer <span class="required">*</span></label>
                        <select id="dealCustomerId" class="form-select-advanced" required>
                            <option value="">Select Customer</option>
                            ${customerOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Deal Value <span class="required">*</span></label>
                        <input type="number" id="dealValue" class="form-input-advanced" value="${deal?.deal_value || ''}" step="0.01" min="0" required>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Currency</label>
                        <select id="dealCurrency" class="form-select-advanced">
                            <option value="INR" ${deal?.currency === 'INR' || !deal ? 'selected' : ''}>INR (₹)</option>
                            <option value="USD" ${deal?.currency === 'USD' ? 'selected' : ''}>USD ($)</option>
                            <option value="EUR" ${deal?.currency === 'EUR' ? 'selected' : ''}>EUR (€)</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Pipeline & Probability</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Pipeline Stage</label>
                        <select id="dealStage" class="form-select-advanced">
                            <option value="prospect" ${deal?.stage === 'prospect' || !deal ? 'selected' : ''}>Prospect</option>
                            <option value="qualified" ${deal?.stage === 'qualified' ? 'selected' : ''}>Qualified</option>
                            <option value="proposal" ${deal?.stage === 'proposal' ? 'selected' : ''}>Proposal</option>
                            <option value="negotiation" ${deal?.stage === 'negotiation' ? 'selected' : ''}>Negotiation</option>
                            <option value="closed_won" ${deal?.stage === 'closed_won' ? 'selected' : ''}>Closed Won</option>
                            <option value="closed_lost" ${deal?.stage === 'closed_lost' ? 'selected' : ''}>Closed Lost</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Win Probability (%)</label>
                        <input type="number" id="dealProbability" class="form-input-advanced" value="${deal?.probability || 0}" min="0" max="100">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Forecast Category</label>
                        <select id="dealForecastCategory" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="best_case" ${deal?.forecast_category === 'best_case' ? 'selected' : ''}>Best Case</option>
                            <option value="commit" ${deal?.forecast_category === 'commit' ? 'selected' : ''}>Commit</option>
                            <option value="most_likely" ${deal?.forecast_category === 'most_likely' ? 'selected' : ''}>Most Likely</option>
                            <option value="worst_case" ${deal?.forecast_category === 'worst_case' ? 'selected' : ''}>Worst Case</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Status</label>
                        <select id="dealStatus" class="form-select-advanced">
                            <option value="open" ${deal?.status === 'open' || !deal ? 'selected' : ''}>Open</option>
                            <option value="won" ${deal?.status === 'won' ? 'selected' : ''}>Won</option>
                            <option value="lost" ${deal?.status === 'lost' ? 'selected' : ''}>Lost</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Dates & Additional Info</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Expected Close Date</label>
                        <input type="date" id="dealExpectedCloseDate" class="form-input-advanced" value="${expectedCloseDate}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Actual Close Date</label>
                        <input type="date" id="dealActualCloseDate" class="form-input-advanced" value="${actualCloseDate}">
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Loss Reason</label>
                        <textarea id="dealLossReason" class="textarea-advanced" rows="2" placeholder="Reason if deal is lost...">${deal?.loss_reason || ''}</textarea>
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Notes</label>
                        <textarea id="dealNotes" class="textarea-advanced" rows="3" placeholder="Additional notes...">${deal?.notes || ''}</textarea>
                    </div>
                </div>
            </div>
            
            <div class="form-actions-sticky">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary" id="dealSubmitBtn">
                    ${isEdit ? 'Update Deal' : 'Create Deal'}
                </button>
            </div>
            
            <div id="dealFormError" class="error-message"></div>
        </form>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('active');
    console.log('Deal modal opened successfully');
}

window.handleDealSubmit = async function(e) {
    e.preventDefault();
    
    const errorDiv = document.getElementById('dealFormError');
    const submitBtn = document.getElementById('dealSubmitBtn');
    
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = window.currentEditingDealId ? 'Updating...' : 'Creating...';
    }
    
    try {
        const dealData = {
            deal_name: document.getElementById('dealName').value.trim(),
            customer_id: parseInt(document.getElementById('dealCustomerId').value),
            deal_value: parseFloat(document.getElementById('dealValue').value),
            currency: document.getElementById('dealCurrency').value,
            stage: document.getElementById('dealStage').value,
            probability: parseInt(document.getElementById('dealProbability').value) || 0,
            forecast_category: document.getElementById('dealForecastCategory').value || null,
            status: document.getElementById('dealStatus').value,
            expected_close_date: document.getElementById('dealExpectedCloseDate').value || null,
            actual_close_date: document.getElementById('dealActualCloseDate').value || null,
            loss_reason: document.getElementById('dealLossReason').value.trim() || null,
            notes: document.getElementById('dealNotes').value.trim() || null
        };
        
        const url = window.currentEditingDealId 
            ? `${API_BASE}/companies/${companyId}/deals/${window.currentEditingDealId}`
            : `${API_BASE}/companies/${companyId}/deals`;
        
        const method = window.currentEditingDealId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(dealData)
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
            if (window.dealsTable && typeof window.dealsTable.refresh === 'function') {
                window.dealsTable.refresh();
            } else {
                loadDeals();
            }
            if (typeof showNotification === 'function') {
                showNotification(window.currentEditingDealId ? 'Deal updated successfully!' : 'Deal created successfully!', 'success');
            }
        } else {
            if (errorDiv) {
                const errorMsg = Array.isArray(result.detail) 
                    ? result.detail.map(e => e.msg || e).join(', ')
                    : (result.detail || 'Failed to save deal');
                errorDiv.textContent = errorMsg;
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error saving deal:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = window.currentEditingDealId ? 'Update Deal' : 'Create Deal';
        }
    }
};

window.deleteDeal = async function(id) {
    showDeleteConfirmModal(
        'Delete Deal',
        'Are you sure you want to delete this deal? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/deals/${id}`, {
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
                    if (window.dealsTable && typeof window.dealsTable.refresh === 'function') {
                        window.dealsTable.refresh();
                    } else {
                        loadDeals();
                    }
                    showToast('Deal deleted successfully!', 'success');
                } else {
                    const result = await response.json();
                    showToast(result.detail || 'Failed to delete deal', 'error');
                }
            } catch (error) {
                console.error('Error deleting deal:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// ============================================
// Pipeline Kanban Board Functions
// ============================================

// Current view state
window.currentDealView = 'table';

// Switch between Table, Kanban, and Forecast views
window.switchDealView = function(view) {
    window.currentDealView = view;
    
    const tableView = document.getElementById('dealsTableView');
    const kanbanView = document.getElementById('dealsKanbanView');
    const forecastView = document.getElementById('dealsForecastView');
    const tableBtn = document.getElementById('tableViewBtn');
    const kanbanBtn = document.getElementById('kanbanViewBtn');
    const forecastBtn = document.getElementById('forecastViewBtn');
    
    // Hide all views
    tableView.style.display = 'none';
    kanbanView.style.display = 'none';
    if (forecastView) forecastView.style.display = 'none';
    
    // Remove active from all buttons
    tableBtn.classList.remove('active');
    kanbanBtn.classList.remove('active');
    if (forecastBtn) forecastBtn.classList.remove('active');
    
    if (view === 'kanban') {
        kanbanView.style.display = 'block';
        kanbanBtn.classList.add('active');
        loadPipelineView();
    } else if (view === 'forecast') {
        if (forecastView) forecastView.style.display = 'block';
        if (forecastBtn) forecastBtn.classList.add('active');
        loadForecastView();
    } else {
        tableView.style.display = 'block';
        tableBtn.classList.add('active');
        loadDeals();
    }
};

// Load Pipeline/Kanban View
window.loadPipelineView = async function() {
    if (!authToken || !companyId) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/deals/pipeline-view`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            console.error('Error loading pipeline view');
            return;
        }
        
        const result = await response.json();
        const data = result.data || {};
        
        // Update pipeline summary
        updatePipelineSummary(data.summary || {});
        
        // Render deals in kanban columns
        renderKanbanBoard(data.stages || {});
        
        // Initialize drag and drop
        initDragAndDrop();
        
        // Refresh Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading pipeline view:', error);
    }
};

// Update Pipeline Summary
function updatePipelineSummary(summary) {
    const summaryDiv = document.getElementById('pipelineSummary');
    if (!summaryDiv) return;
    
    summaryDiv.innerHTML = `
        <div class="summary-cards">
            <div class="summary-card">
                <span class="summary-label">Total Pipeline</span>
                <span class="summary-value">₹${(summary.total_value || 0).toLocaleString()}</span>
            </div>
            <div class="summary-card">
                <span class="summary-label">Weighted Value</span>
                <span class="summary-value">₹${(summary.weighted_value || 0).toLocaleString()}</span>
            </div>
            <div class="summary-card">
                <span class="summary-label">Open Deals</span>
                <span class="summary-value">${summary.total_deals || 0}</span>
            </div>
            <div class="summary-card success">
                <span class="summary-label">Win Rate</span>
                <span class="summary-value">${summary.win_rate || 0}%</span>
            </div>
        </div>
    `;
}

// Render Kanban Board
function renderKanbanBoard(stages) {
    const stageKeys = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
    
    stageKeys.forEach(stage => {
        const stageData = stages[stage] || { deals: [], count: 0, total_value: 0 };
        const cardsContainer = document.getElementById(`cards-${stage}`);
        const countEl = document.getElementById(`count-${stage}`);
        const valueEl = document.getElementById(`value-${stage}`);
        
        if (countEl) countEl.textContent = stageData.count || 0;
        if (valueEl) valueEl.textContent = `₹${(stageData.total_value || 0).toLocaleString()}`;
        
        if (cardsContainer) {
            cardsContainer.innerHTML = (stageData.deals || []).map(deal => createDealCard(deal)).join('');
        }
    });
}

// Create Deal Card HTML
function createDealCard(deal) {
    const probability = deal.probability || 0;
    const value = deal.deal_value || 0;
    const closeDate = deal.expected_close_date ? new Date(deal.expected_close_date).toLocaleDateString() : '-';
    
    return `
        <div class="kanban-card" draggable="true" data-deal-id="${deal.id}" ondragstart="handleDragStart(event)" ondragend="handleDragEnd(event)">
            <div class="card-header">
                <span class="deal-name">${escapeHtml(deal.deal_name)}</span>
                <span class="deal-probability">${probability}%</span>
            </div>
            <div class="card-body">
                <div class="deal-account">
                    <i data-lucide="building-2"></i>
                    <span>${escapeHtml(deal.customer_name || deal.account_name || '-')}</span>
                </div>
                <div class="deal-value">
                    <i data-lucide="indian-rupee"></i>
                    <span>₹${value.toLocaleString()}</span>
                </div>
                <div class="deal-date">
                    <i data-lucide="calendar"></i>
                    <span>${closeDate}</span>
                </div>
            </div>
            <div class="card-actions">
                <button class="btn-icon-sm" onclick="editDeal(${deal.id})" title="Edit">
                    <i data-lucide="edit"></i>
                </button>
                <button class="btn-icon-sm" onclick="deleteDeal(${deal.id})" title="Delete">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        </div>
    `;
}

// Drag and Drop Functions
function initDragAndDrop() {
    const columns = document.querySelectorAll('.kanban-cards');
    
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
    });
}

window.handleDragStart = function(e) {
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', e.target.dataset.dealId);
    e.dataTransfer.effectAllowed = 'move';
};

window.handleDragEnd = function(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.kanban-cards').forEach(col => col.classList.remove('drag-over'));
};

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

async function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const dealId = e.dataTransfer.getData('text/plain');
    const newStage = e.currentTarget.closest('.kanban-column').dataset.stage;
    
    if (!dealId || !newStage) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/deals/${dealId}/move-stage?new_stage=${newStage}`, {
            method: 'PUT',
            headers: getHeaders()
        });
        
        if (response.ok) {
            showToast(`Deal moved to ${newStage.replace('_', ' ')}`, 'success');
            loadPipelineView();
        } else {
            const result = await response.json();
            showToast(result.detail || 'Failed to move deal', 'error');
        }
    } catch (error) {
        console.error('Error moving deal:', error);
        showToast('Error moving deal', 'error');
    }
}

// Load Forecast View (Tab)
window.loadForecastView = async function() {
    if (!authToken || !companyId) return;
    
    try {
        const [forecastRes, trendRes] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyId}/deals/forecast`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyId}/deals/trend-analysis?months=6`, { headers: getHeaders() })
        ]);
        
        const forecastData = await forecastRes.json();
        const trendData = await trendRes.json();
        
        const forecast = forecastData.data || {};
        const trends = trendData.data || {};
        
        // Update Pipeline Forecast Cards
        document.getElementById('fc-total-pipeline').textContent = `₹${(forecast.total_pipeline || 0).toLocaleString()}`;
        document.getElementById('fc-weighted-pipeline').textContent = `₹${(forecast.weighted_pipeline || 0).toLocaleString()}`;
        document.getElementById('fc-win-rate').textContent = `${forecast.win_rate || 0}%`;
        
        // Update Forecast by Category
        const byCategory = forecast.by_category || {};
        document.getElementById('fc-best-case').textContent = `₹${(byCategory.best_case || 0).toLocaleString()}`;
        document.getElementById('fc-commit').textContent = `₹${(byCategory.commit || 0).toLocaleString()}`;
        document.getElementById('fc-most-likely').textContent = `₹${(byCategory.most_likely || 0).toLocaleString()}`;
        document.getElementById('fc-worst-case').textContent = `₹${(byCategory.worst_case || 0).toLocaleString()}`;
        
        // Update Historical Trends
        const growthRate = trends.growth_rate || 0;
        const growthEl = document.getElementById('fc-growth-rate');
        growthEl.textContent = `${growthRate >= 0 ? '+' : ''}${growthRate}%`;
        growthEl.className = `trend-value ${growthRate >= 0 ? 'positive' : 'negative'}`;
        
        document.getElementById('fc-total-won').textContent = `₹${(trends.total_won || 0).toLocaleString()}`;
        document.getElementById('fc-deals-won').textContent = trends.deals_won || 0;
        
        // Render Monthly Projections
        const projectionsDiv = document.getElementById('monthlyProjections');
        const projections = forecast.monthly_projections || [];
        
        if (projections.length > 0) {
            const maxValue = Math.max(...projections.map(p => p.projected_value || p.weighted_value || 0), 1);
            projectionsDiv.innerHTML = projections.map(p => {
                const value = p.projected_value || p.weighted_value || 0;
                const width = Math.min(100, (value / maxValue) * 100);
                return `
                    <div class="projection-row">
                        <span class="projection-month">${p.month}</span>
                        <div class="projection-bar-container">
                            <div class="projection-bar-fill" style="width: ${width}%"></div>
                        </div>
                        <span class="projection-value">₹${value.toLocaleString()}</span>
                        <span class="projection-deals">${p.deal_count || 0} deals</span>
                    </div>
                `;
            }).join('');
        } else {
            projectionsDiv.innerHTML = '<p class="empty-text">No projections available</p>';
        }
        
        // Render Monthly Trends Chart
        const trendsDiv = document.getElementById('trendsChart');
        const monthlyTrends = trends.monthly_trends || [];
        
        if (monthlyTrends.length > 0) {
            const maxWon = Math.max(...monthlyTrends.map(m => m.won_value || 0), 1);
            trendsDiv.innerHTML = `
                <div class="chart-bars">
                    ${monthlyTrends.map(m => {
                        const height = Math.min(100, (m.won_value / maxWon) * 100);
                        return `
                            <div class="chart-bar-item">
                                <div class="chart-bar-wrapper">
                                    <div class="chart-bar" style="height: ${height}%"></div>
                                </div>
                                <span class="chart-label">${m.month.split(' ')[0].substring(0, 3)}</span>
                                <span class="chart-value">₹${(m.won_value || 0).toLocaleString()}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        } else {
            trendsDiv.innerHTML = '<p class="empty-text">No trend data available</p>';
        }
        
        // Refresh Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading forecast view:', error);
        showToast('Error loading forecast data', 'error');
    }
};

// Show Deal Forecast Modal (legacy - now redirects to tab)
window.showDealForecast = async function() {
    try {
        const [forecastRes, trendRes] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyId}/deals/forecast`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyId}/deals/trend-analysis?months=6`, { headers: getHeaders() })
        ]);
        
        const forecastData = await forecastRes.json();
        const trendData = await trendRes.json();
        
        const forecast = forecastData.data || {};
        const trends = trendData.data || {};
        
        const modalHtml = `
            <div class="modal-overlay" id="forecastModal" onclick="closeForecastModal(event)">
                <div class="modal-content modal-lg" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i data-lucide="trending-up"></i> Sales Forecast & Trends</h3>
                        <button class="modal-close" onclick="closeForecastModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="forecast-grid">
                            <!-- Forecast Summary -->
                            <div class="forecast-card">
                                <h4>Pipeline Forecast</h4>
                                <div class="forecast-metrics">
                                    <div class="metric">
                                        <span class="metric-label">Total Pipeline</span>
                                        <span class="metric-value">₹${(forecast.total_pipeline || 0).toLocaleString()}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Weighted Pipeline</span>
                                        <span class="metric-value">₹${(forecast.weighted_pipeline || 0).toLocaleString()}</span>
                                    </div>
                                    <div class="metric highlight">
                                        <span class="metric-label">Best Case</span>
                                        <span class="metric-value">₹${(forecast.by_category?.best_case || 0).toLocaleString()}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Commit</span>
                                        <span class="metric-value">₹${(forecast.by_category?.commit || 0).toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Trend Analysis -->
                            <div class="forecast-card">
                                <h4>Historical Trends (6 Months)</h4>
                                <div class="trend-metrics">
                                    <div class="metric ${(trends.growth_rate || 0) >= 0 ? 'positive' : 'negative'}">
                                        <span class="metric-label">Revenue Growth</span>
                                        <span class="metric-value">${(trends.growth_rate || 0).toFixed(1)}%</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Win Rate</span>
                                        <span class="metric-value">${(trends.win_rate || 0).toFixed(1)}%</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Total Won</span>
                                        <span class="metric-value">₹${(trends.total_won || 0).toLocaleString()}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="metric-label">Deals Won</span>
                                        <span class="metric-value">${trends.deals_won || 0}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Monthly Projections -->
                            <div class="forecast-card full-width">
                                <h4>Monthly Projections</h4>
                                <div class="projections-list">
                                    ${(forecast.monthly_projections || []).map(m => `
                                        <div class="projection-item">
                                            <span class="month">${m.month}</span>
                                            <div class="projection-bar">
                                                <div class="bar" style="width: ${Math.min(100, (m.projected_value / (forecast.total_pipeline || 1)) * 100)}%"></div>
                                            </div>
                                            <span class="value">₹${(m.projected_value || 0).toLocaleString()}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="closeForecastModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        const existingModal = document.getElementById('forecastModal');
        if (existingModal) existingModal.remove();
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading forecast:', error);
        showToast('Error loading forecast data', 'error');
    }
};

window.closeForecastModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('forecastModal');
    if (modal) modal.remove();
};

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
