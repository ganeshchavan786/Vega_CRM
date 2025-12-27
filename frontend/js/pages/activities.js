// Activities Page JavaScript

// Global variable for editing activity ID
if (typeof window.currentEditingActivityId === 'undefined') {
    window.currentEditingActivityId = null;
}

// Cache for related entities (global to avoid redeclaration)
if (typeof window.activitiesCustomersList === 'undefined') {
    window.activitiesCustomersList = [];
}
if (typeof window.activitiesLeadsList === 'undefined') {
    window.activitiesLeadsList = [];
}
if (typeof window.activitiesDealsList === 'undefined') {
    window.activitiesDealsList = [];
}
if (typeof window.activitiesTasksList === 'undefined') {
    window.activitiesTasksList = [];
}

window.initActivities = function() {
    // Check auth before loading
    if (!authToken || !companyId) {
        console.warn('No auth token or company ID - skipping activity load');
        const table = document.getElementById('activitiesTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadActivities();
    loadRelatedEntities(); // Pre-load for dropdowns
}

async function loadRelatedEntities() {
    try {
        // Load customers
        const customersResponse = await fetch(`${API_BASE}/companies/${companyId}/customers?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (customersResponse.ok) {
            const customersData = await customersResponse.json();
            window.activitiesCustomersList = customersData.data || [];
        }
        
        // Load leads
        const leadsResponse = await fetch(`${API_BASE}/companies/${companyId}/leads?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (leadsResponse.ok) {
            const leadsData = await leadsResponse.json();
            window.activitiesLeadsList = leadsData.data || [];
        }
        
        // Load deals
        const dealsResponse = await fetch(`${API_BASE}/companies/${companyId}/deals?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (dealsResponse.ok) {
            const dealsData = await dealsResponse.json();
            window.activitiesDealsList = dealsData.data || [];
        }
        
        // Load tasks
        const tasksResponse = await fetch(`${API_BASE}/companies/${companyId}/tasks?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (tasksResponse.ok) {
            const tasksData = await tasksResponse.json();
            window.activitiesTasksList = tasksData.data || [];
        }
    } catch (error) {
        console.error('Error loading related entities for activity form:', error);
    }
}

window.loadActivities = async function() {
    // Check auth before making API call
    if (!authToken || !companyId) {
        console.warn('Cannot load activities: No auth token or company ID');
        const table = document.getElementById('activitiesTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const type = document.getElementById('activityTypeFilter')?.value || '';
    const outcome = document.getElementById('activityOutcomeFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/activities?page=1&per_page=100`;
        if (type) url += `&activity_type=${encodeURIComponent(type)}`;
        if (outcome) url += `&outcome=${encodeURIComponent(outcome)}`;

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
            console.error('Error loading activities:', response.status, errorData);
            const table = document.getElementById('activitiesTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Error loading activities</h3><p>Please try again</p></div>';
            }
            return;
        }
        
        const data = await response.json();
        const activities = Array.isArray(data.data) ? data.data : [];

        const table = document.getElementById('activitiesTable');
        if (!table) return;

        // Initialize DataTable
        if (window.activitiesTable && typeof window.activitiesTable.updateData === 'function') {
            window.activitiesTable.updateData(activities);
        } else {
            window.activitiesTable = new DataTable('activitiesTable', {
                data: activities,
                columns: [
                    {
                        key: 'title',
                        label: 'Title',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<strong>${escapeHtml(value || '-')}</strong>`
                    },
                    {
                        key: 'activity_type',
                        label: 'Type',
                        sortable: true,
                        filterable: true,
                        render: (value) => {
                            return `<span class="status-badge status-${value || 'general'}">${escapeHtml((value || '-').toUpperCase())}</span>`;
                        }
                    },
                    {
                        key: 'activity_date',
                        label: 'Date',
                        sortable: true,
                        type: 'date'
                    },
                    {
                        key: 'description',
                        label: 'Description',
                        sortable: false,
                        filterable: true,
                        render: (value) => {
                            if (!value) return '-';
                            const shortDesc = value.length > 50 ? value.substring(0, 50) + '...' : value;
                            return `<span title="${escapeHtml(value)}">${escapeHtml(shortDesc)}</span>`;
                        }
                    },
                    {
                        key: 'duration',
                        label: 'Duration (min)',
                        sortable: true,
                        align: 'center',
                        render: (value) => {
                            return value ? `${value}` : '-';
                        }
                    },
                    {
                        key: 'outcome',
                        label: 'Outcome',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            if (!value) return '-';
                            return `<span class="status-badge status-${value}">${escapeHtml(value.replace('_', ' ').toUpperCase())}</span>`;
                        }
                    },
                    {
                        key: 'actions',
                        label: 'Actions',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            return `
                                <button class="btn-icon btn-edit" onclick="editActivity(${row.id})" title="Edit">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                                <button class="btn-icon btn-delete" onclick="deleteActivity(${row.id})" title="Delete">
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
        console.error('Error loading activities:', error);
        const table = document.getElementById('activitiesTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading activities</h3><p>Please try again</p></div>';
        }
    }
};

window.showActivityForm = function() {
    console.log('showActivityForm called');
    window.currentEditingActivityId = null;
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found. Modal:', modal, 'FormContent:', formContent);
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, proceeding...');
    
    // Ensure related entities are loaded
    if (window.activitiesCustomersList.length === 0) {
        console.log('Loading related entities...');
        loadRelatedEntities().then(() => {
            console.log('Related entities loaded, opening modal...');
            try {
                window.openActivityModal();
            } catch (error) {
                console.error('Error in showActivityForm:', error);
                alert('Error opening activity form: ' + error.message);
            }
        }).catch((error) => {
            console.error('Error loading related entities:', error);
            // Still try to open modal even if loading fails
            try {
                window.openActivityModal();
            } catch (modalError) {
                console.error('Error opening modal:', modalError);
                alert('Error opening activity form: ' + modalError.message);
            }
        });
    } else {
        console.log('Related entities already loaded, opening modal...');
        try {
            window.openActivityModal();
        } catch (error) {
            console.error('Error in showActivityForm:', error);
            alert('Error opening activity form: ' + error.message);
        }
    }
};

window.editActivity = async function(id) {
    window.currentEditingActivityId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/activities/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            alert('Failed to load activity data');
            return;
        }
        
        const result = await response.json();
        const activity = result.data || result;
        
        // Ensure related entities are loaded
        if (window.activitiesCustomersList.length === 0) {
            await loadRelatedEntities();
        }
        
        window.openActivityModal(activity);
    } catch (error) {
        console.error('Error loading activity:', error);
        alert('Error loading activity data: ' + error.message);
    }
};

// Make openActivityModal globally accessible
window.openActivityModal = function(activity = null) {
    console.log('openActivityModal called, activity:', activity);
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found! Modal:', modal, 'FormContent:', formContent);
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, building form...');
    
    const isEdit = !!activity;
    const title = isEdit ? 'Edit Activity' : 'Log Activity';
    
    // Format datetime for input field
    const activityDate = activity?.activity_date ? new Date(activity.activity_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16);
    
    // Build dropdown options
    const customerOptions = window.activitiesCustomersList.map(c => 
        `<option value="${c.id}" ${activity?.customer_id === c.id ? 'selected' : ''}>${escapeHtml(c.name || `Customer ${c.id}`)}</option>`
    ).join('');
    
    const leadOptions = window.activitiesLeadsList.map(l => {
        const leadName = (l.first_name && l.last_name) ? `${l.first_name} ${l.last_name}` : l.lead_name || `Lead ${l.id}`;
        return `<option value="${l.id}" ${activity?.lead_id === l.id ? 'selected' : ''}>${escapeHtml(leadName)}</option>`;
    }).join('');
    
    const dealOptions = window.activitiesDealsList.map(d => 
        `<option value="${d.id}" ${activity?.deal_id === d.id ? 'selected' : ''}>${escapeHtml(d.deal_name || `Deal ${d.id}`)}</option>`
    ).join('');
    
    const taskOptions = window.activitiesTasksList.map(t => 
        `<option value="${t.id}" ${activity?.task_id === t.id ? 'selected' : ''}>${escapeHtml(t.title || `Task ${t.id}`)}</option>`
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
        <form id="activityForm" class="form-advanced" onsubmit="handleActivitySubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Activity Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Activity Type <span class="required">*</span></label>
                        <select id="activityType" class="form-select-advanced" required>
                            <option value="call" ${activity?.activity_type === 'call' || !activity ? 'selected' : ''}>Call</option>
                            <option value="email" ${activity?.activity_type === 'email' ? 'selected' : ''}>Email</option>
                            <option value="meeting" ${activity?.activity_type === 'meeting' ? 'selected' : ''}>Meeting</option>
                            <option value="note" ${activity?.activity_type === 'note' ? 'selected' : ''}>Note</option>
                            <option value="status_change" ${activity?.activity_type === 'status_change' ? 'selected' : ''}>Status Change</option>
                        </select>
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Title <span class="required">*</span></label>
                        <input type="text" id="activityTitle" class="form-input-advanced" value="${activity?.title || ''}" required>
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Description</label>
                        <textarea id="activityDescription" class="textarea-advanced" rows="4" placeholder="Activity description...">${activity?.description || ''}</textarea>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Duration (minutes)</label>
                        <input type="number" id="activityDuration" class="form-input-advanced" value="${activity?.duration || ''}" min="0" placeholder="30">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Outcome</label>
                        <select id="activityOutcome" class="form-select-advanced">
                            <option value="">None</option>
                            <option value="positive" ${activity?.outcome === 'positive' ? 'selected' : ''}>Positive</option>
                            <option value="negative" ${activity?.outcome === 'negative' ? 'selected' : ''}>Negative</option>
                            <option value="neutral" ${activity?.outcome === 'neutral' ? 'selected' : ''}>Neutral</option>
                            <option value="follow_up_required" ${activity?.outcome === 'follow_up_required' ? 'selected' : ''}>Follow Up Required</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Activity Date & Time <span class="required">*</span></label>
                        <input type="datetime-local" id="activityDate" class="form-input-advanced" value="${activityDate}" required>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Related Entities (Optional)</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Customer</label>
                        <select id="activityCustomerId" class="form-select-advanced">
                            <option value="">None</option>
                            ${customerOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Lead</label>
                        <select id="activityLeadId" class="form-select-advanced">
                            <option value="">None</option>
                            ${leadOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Deal</label>
                        <select id="activityDealId" class="form-select-advanced">
                            <option value="">None</option>
                            ${dealOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Task</label>
                        <select id="activityTaskId" class="form-select-advanced">
                            <option value="">None</option>
                            ${taskOptions}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-actions-sticky">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary" id="activitySubmitBtn">
                    ${isEdit ? 'Update Activity' : 'Log Activity'}
                </button>
            </div>
            
            <div id="activityFormError" class="error-message"></div>
        </form>
    `;
    
    modal.classList.add('active');
    console.log('Modal opened successfully');
}

window.handleActivitySubmit = async function(e) {
    e.preventDefault();
    
    const errorDiv = document.getElementById('activityFormError');
    const submitBtn = document.getElementById('activitySubmitBtn');
    
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = window.currentEditingActivityId ? 'Updating...' : 'Logging...';
    }
    
    try {
        const activityDateInput = document.getElementById('activityDate').value;
        const activityDate = activityDateInput ? new Date(activityDateInput).toISOString() : new Date().toISOString();
        
        const activityData = {
            activity_type: document.getElementById('activityType').value,
            title: document.getElementById('activityTitle').value.trim(),
            description: document.getElementById('activityDescription').value.trim() || null,
            duration: document.getElementById('activityDuration').value ? parseInt(document.getElementById('activityDuration').value) : null,
            outcome: document.getElementById('activityOutcome').value || null,
            activity_date: activityDate,
            customer_id: document.getElementById('activityCustomerId').value ? parseInt(document.getElementById('activityCustomerId').value) : null,
            lead_id: document.getElementById('activityLeadId').value ? parseInt(document.getElementById('activityLeadId').value) : null,
            deal_id: document.getElementById('activityDealId').value ? parseInt(document.getElementById('activityDealId').value) : null,
            task_id: document.getElementById('activityTaskId').value ? parseInt(document.getElementById('activityTaskId').value) : null
        };
        
        const url = window.currentEditingActivityId 
            ? `${API_BASE}/companies/${companyId}/activities/${window.currentEditingActivityId}`
            : `${API_BASE}/companies/${companyId}/activities`;
        
        const method = window.currentEditingActivityId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(activityData)
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
            if (window.activitiesTable && typeof window.activitiesTable.refresh === 'function') {
                window.activitiesTable.refresh();
            } else {
                loadActivities();
            }
            if (typeof showNotification === 'function') {
                showNotification(window.currentEditingActivityId ? 'Activity updated successfully!' : 'Activity logged successfully!', 'success');
            }
        } else {
            if (errorDiv) {
                const errorMsg = Array.isArray(result.detail) 
                    ? result.detail.map(e => e.msg || e).join(', ')
                    : (result.detail || 'Failed to save activity');
                errorDiv.textContent = errorMsg;
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error saving activity:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = window.currentEditingActivityId ? 'Update Activity' : 'Log Activity';
        }
    }
};

window.deleteActivity = async function(id) {
    if (!confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/activities/${id}`, {
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
            if (window.activitiesTable && typeof window.activitiesTable.refresh === 'function') {
                window.activitiesTable.refresh();
            } else {
                loadActivities();
            }
            if (typeof showNotification === 'function') {
                showNotification('Activity deleted successfully!', 'success');
            }
        } else {
            const result = await response.json();
            alert(result.detail || 'Failed to delete activity');
        }
    } catch (error) {
        console.error('Error deleting activity:', error);
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
        window.currentEditingActivityId = null;
    };
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
