// Tasks Page JavaScript

// Global variable for editing task ID
if (typeof window.currentEditingTaskId === 'undefined') {
    window.currentEditingTaskId = null;
}

// Cache for related entities (global to avoid redeclaration)
if (typeof window.tasksCustomersList === 'undefined') {
    window.tasksCustomersList = [];
}
if (typeof window.tasksLeadsList === 'undefined') {
    window.tasksLeadsList = [];
}
if (typeof window.tasksDealsList === 'undefined') {
    window.tasksDealsList = [];
}

window.initTasks = function initTasks() {
    // Check auth before loading
    if (!authToken || !companyId) {
        console.warn('No auth token or company ID - skipping task load');
        const table = document.getElementById('tasksTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadTasks();
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
            window.tasksCustomersList = customersData.data || [];
        }
        
        // Load leads
        const leadsResponse = await fetch(`${API_BASE}/companies/${companyId}/leads?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (leadsResponse.ok) {
            const leadsData = await leadsResponse.json();
            window.tasksLeadsList = leadsData.data || [];
        }
        
        // Load deals
        const dealsResponse = await fetch(`${API_BASE}/companies/${companyId}/deals?page=1&per_page=100`, {
            headers: getHeaders()
        });
        if (dealsResponse.ok) {
            const dealsData = await dealsResponse.json();
            window.tasksDealsList = dealsData.data || [];
        }
    } catch (error) {
        console.error('Error loading related entities for task form:', error);
    }
}

window.loadTasks = async function() {
    // Check auth before making API call
    if (!authToken || !companyId) {
        console.warn('Cannot load tasks: No auth token or company ID');
        const table = document.getElementById('tasksTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const search = document.getElementById('taskSearch')?.value || '';
    const status = document.getElementById('taskStatusFilter')?.value || '';
    const priority = document.getElementById('taskPriorityFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/tasks?page=1&per_page=100`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        if (priority) url += `&priority=${encodeURIComponent(priority)}`;

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
            console.error('Error loading tasks:', response.status, errorData);
            const table = document.getElementById('tasksTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Error loading tasks</h3><p>Please try again</p></div>';
            }
            return;
        }
        
        const data = await response.json();
        const tasks = Array.isArray(data.data) ? data.data : [];

        const table = document.getElementById('tasksTable');
        if (!table) return;

        // Initialize DataTable
        if (window.tasksTable && typeof window.tasksTable.updateData === 'function') {
            window.tasksTable.updateData(tasks);
        } else {
            window.tasksTable = new DataTable('tasksTable', {
                data: tasks,
                columns: [
                    {
                        key: 'unique_id',
                        label: 'ID',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:0.85rem;">${escapeHtml(value || '-')}</code>`
                    },
                    {
                        key: 'title',
                        label: 'Title',
                        sortable: true,
                        filterable: true,
                        render: (value) => `<strong>${escapeHtml(value || '-')}</strong>`
                    },
                    {
                        key: 'task_type',
                        label: 'Type',
                        sortable: true,
                        filterable: true,
                        render: (value) => {
                            return `<span class="status-badge status-${value || 'general'}">${escapeHtml((value || 'general').toUpperCase())}</span>`;
                        }
                    },
                    {
                        key: 'priority',
                        label: 'Priority',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const priority = value || 'medium';
                            return `<span class="status-badge status-${priority}">${priority.toUpperCase()}</span>`;
                        }
                    },
                    {
                        key: 'status',
                        label: 'Status',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const status = value || 'pending';
                            return `<span class="status-badge status-${status}">${escapeHtml(status.toUpperCase().replace('_', ' '))}</span>`;
                        }
                    },
                    {
                        key: 'due_date',
                        label: 'Due Date',
                        sortable: true,
                        type: 'date'
                    },
                    {
                        key: 'assigned_user.full_name',
                        label: 'Assigned To',
                        sortable: true,
                        filterable: true,
                        render: (value, row) => {
                            return row.assigned_user ? escapeHtml(row.assigned_user.full_name || row.assigned_user.email || '-') : '-';
                        }
                    },
                    {
                        key: 'actions',
                        label: 'Actions',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            let html = '';
                            if (row.status !== 'completed') {
                                html += `
                                    <button class="btn-icon btn-primary" onclick="completeTask(${row.id})" title="Complete">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M13.3333 4L6 11.3333L2.66667 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                `;
                            }
                            html += `
                                <button class="btn-icon btn-edit" onclick="editTask(${row.id})" title="Edit">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                                <button class="btn-icon btn-delete" onclick="deleteTask(${row.id})" title="Delete">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M12 4V13.3333C12 13.687 11.8595 14.0261 11.6095 14.2761C11.3594 14.5262 11.0203 14.6667 10.6667 14.6667H5.33333C4.97971 14.6667 4.64057 14.5262 4.39052 14.2761C4.14048 14.0261 4 13.687 4 13.3333V4M6 4V2.66667C6 2.31305 6.14048 1.97391 6.39052 1.72386C6.64057 1.47381 6.97971 1.33334 7.33333 1.33334H8.66667C9.02029 1.33334 9.35943 1.47381 9.60948 1.72386C9.85952 1.97391 10 2.31305 10 2.66667V4M2 4H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                            `;
                            return html;
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
        console.error('Error loading tasks:', error);
        const table = document.getElementById('tasksTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading tasks</h3><p>Please try again</p></div>';
        }
    }
};

window.showTaskForm = function() {
    console.log('showTaskForm called');
    window.currentEditingTaskId = null;
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found. Modal:', modal, 'FormContent:', formContent);
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, proceeding...');
    
    // Ensure related entities are loaded
    if (window.tasksCustomersList.length === 0) {
        console.log('Loading related entities...');
        loadRelatedEntities().then(() => {
            console.log('Related entities loaded, opening modal...');
            try {
                window.openTaskModal();
            } catch (error) {
                console.error('Error in showTaskForm:', error);
                alert('Error opening task form: ' + error.message);
            }
        }).catch((error) => {
            console.error('Error loading related entities:', error);
            // Still try to open modal even if loading fails
            try {
                window.openTaskModal();
            } catch (modalError) {
                console.error('Error opening modal:', modalError);
                alert('Error opening task form: ' + modalError.message);
            }
        });
    } else {
        console.log('Related entities already loaded, opening modal...');
        try {
            window.openTaskModal();
        } catch (error) {
            console.error('Error in showTaskForm:', error);
            alert('Error opening task form: ' + error.message);
        }
    }
};

window.editTask = async function(id) {
    window.currentEditingTaskId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            alert('Failed to load task data');
            return;
        }
        
        const result = await response.json();
        const task = result.data || result;
        
        // Ensure related entities are loaded
        if (window.tasksCustomersList.length === 0) {
            await loadRelatedEntities();
        }
        
        window.openTaskModal(task);
    } catch (error) {
        console.error('Error loading task:', error);
        alert('Error loading task data: ' + error.message);
    }
};

// Make openTaskModal globally accessible
window.openTaskModal = function(task = null) {
    console.log('openTaskModal called, task:', task);
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found! Modal:', modal, 'FormContent:', formContent);
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    console.log('Modal elements found, building form...');
    
    const isEdit = !!task;
    const title = isEdit ? 'Edit Task' : 'Add Task';
    
    // Format date for input field
    const dueDate = task?.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '';
    
    // Build dropdown options
    const customerOptions = window.tasksCustomersList.map(c => 
        `<option value="${c.id}" ${task?.customer_id === c.id ? 'selected' : ''}>${escapeHtml(c.name || `Customer ${c.id}`)}</option>`
    ).join('');
    
    const leadOptions = window.tasksLeadsList.map(l => {
        const leadName = (l.first_name && l.last_name) ? `${l.first_name} ${l.last_name}` : l.lead_name || `Lead ${l.id}`;
        return `<option value="${l.id}" ${task?.lead_id === l.id ? 'selected' : ''}>${escapeHtml(leadName)}</option>`;
    }).join('');
    
    const dealOptions = window.tasksDealsList.map(d => 
        `<option value="${d.id}" ${task?.deal_id === d.id ? 'selected' : ''}>${escapeHtml(d.deal_name || `Deal ${d.id}`)}</option>`
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
        <form id="taskForm" class="form-advanced" onsubmit="handleTaskSubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Task Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Title <span class="required">*</span></label>
                        <input type="text" id="taskTitle" class="form-input-advanced" value="${task?.title || ''}" required>
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Description</label>
                        <textarea id="taskDescription" class="textarea-advanced" rows="3" placeholder="Task description...">${task?.description || ''}</textarea>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Task Type</label>
                        <select id="taskType" class="form-select-advanced">
                            <option value="general" ${task?.task_type === 'general' || !task ? 'selected' : ''}>General</option>
                            <option value="call" ${task?.task_type === 'call' ? 'selected' : ''}>Call</option>
                            <option value="email" ${task?.task_type === 'email' ? 'selected' : ''}>Email</option>
                            <option value="meeting" ${task?.task_type === 'meeting' ? 'selected' : ''}>Meeting</option>
                            <option value="follow_up" ${task?.task_type === 'follow_up' ? 'selected' : ''}>Follow Up</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Priority</label>
                        <select id="taskPriority" class="form-select-advanced">
                            <option value="low" ${task?.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${task?.priority === 'medium' || !task ? 'selected' : ''}>Medium</option>
                            <option value="high" ${task?.priority === 'high' ? 'selected' : ''}>High</option>
                            <option value="urgent" ${task?.priority === 'urgent' ? 'selected' : ''}>Urgent</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Status</label>
                        <select id="taskStatus" class="form-select-advanced">
                            <option value="pending" ${task?.status === 'pending' || !task ? 'selected' : ''}>Pending</option>
                            <option value="in_progress" ${task?.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                            <option value="completed" ${task?.status === 'completed' ? 'selected' : ''}>Completed</option>
                            <option value="cancelled" ${task?.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Due Date & Time</label>
                        <input type="datetime-local" id="taskDueDate" class="form-input-advanced" value="${dueDate}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Assigned To <span class="required">*</span></label>
                        <input type="number" id="taskAssignedTo" class="form-input-advanced" value="${task?.assigned_to || ''}" placeholder="User ID" required>
                        <small style="color: var(--jira-text-secondary); font-size: 10px;">Note: Enter user ID (current user by default)</small>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Related Entities (Optional)</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Customer</label>
                        <select id="taskCustomerId" class="form-select-advanced">
                            <option value="">None</option>
                            ${customerOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Lead</label>
                        <select id="taskLeadId" class="form-select-advanced">
                            <option value="">None</option>
                            ${leadOptions}
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Deal</label>
                        <select id="taskDealId" class="form-select-advanced">
                            <option value="">None</option>
                            ${dealOptions}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-actions-sticky">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary" id="taskSubmitBtn">
                    ${isEdit ? 'Update Task' : 'Create Task'}
                </button>
            </div>
            
            <div id="taskFormError" class="error-message"></div>
        </form>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('active');
    console.log('Modal opened successfully');
    
    // Set assigned_to to current user if creating new task
    if (!isEdit) {
        // Try to get current user ID from token or default to 1
        const assignedToInput = document.getElementById('taskAssignedTo');
        if (assignedToInput && !assignedToInput.value) {
            assignedToInput.value = '1'; // Default to user ID 1, can be improved later
        }
    }
}

window.handleTaskSubmit = async function(e) {
    e.preventDefault();
    
    const errorDiv = document.getElementById('taskFormError');
    const submitBtn = document.getElementById('taskSubmitBtn');
    
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = window.currentEditingTaskId ? 'Updating...' : 'Creating...';
    }
    
    try {
        const dueDateInput = document.getElementById('taskDueDate').value;
        const dueDate = dueDateInput ? new Date(dueDateInput).toISOString() : null;
        
        const taskData = {
            title: document.getElementById('taskTitle').value.trim(),
            description: document.getElementById('taskDescription').value.trim() || null,
            task_type: document.getElementById('taskType').value,
            priority: document.getElementById('taskPriority').value,
            status: document.getElementById('taskStatus').value,
            due_date: dueDate,
            assigned_to: parseInt(document.getElementById('taskAssignedTo').value),
            customer_id: document.getElementById('taskCustomerId').value ? parseInt(document.getElementById('taskCustomerId').value) : null,
            lead_id: document.getElementById('taskLeadId').value ? parseInt(document.getElementById('taskLeadId').value) : null,
            deal_id: document.getElementById('taskDealId').value ? parseInt(document.getElementById('taskDealId').value) : null
        };
        
        const url = window.currentEditingTaskId 
            ? `${API_BASE}/companies/${companyId}/tasks/${window.currentEditingTaskId}`
            : `${API_BASE}/companies/${companyId}/tasks`;
        
        const method = window.currentEditingTaskId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(taskData)
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
            if (window.tasksTable && typeof window.tasksTable.refresh === 'function') {
                window.tasksTable.refresh();
            } else {
                loadTasks();
            }
            if (typeof showNotification === 'function') {
                showNotification(window.currentEditingTaskId ? 'Task updated successfully!' : 'Task created successfully!', 'success');
            }
        } else {
            if (errorDiv) {
                const errorMsg = Array.isArray(result.detail) 
                    ? result.detail.map(e => e.msg || e).join(', ')
                    : (result.detail || 'Failed to save task');
                errorDiv.textContent = errorMsg;
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error saving task:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = window.currentEditingTaskId ? 'Update Task' : 'Create Task';
        }
    }
};

window.completeTask = async function(id) {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/${id}/complete`, {
            method: 'PUT',
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (response.ok) {
            if (window.tasksTable && typeof window.tasksTable.refresh === 'function') {
                window.tasksTable.refresh();
            } else {
                loadTasks();
            }
            if (typeof showNotification === 'function') {
                showNotification('Task marked as completed!', 'success');
            }
        } else {
            const result = await response.json();
            alert(result.detail || 'Failed to complete task');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        alert('Connection error. Please try again.');
    }
};

window.deleteTask = async function(id) {
    showDeleteConfirmModal(
        'Delete Task',
        'Are you sure you want to delete this task? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/${id}`, {
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
                    if (window.tasksTable && typeof window.tasksTable.refresh === 'function') {
                        window.tasksTable.refresh();
                    } else {
                        loadTasks();
                    }
                    showToast('Task deleted successfully!', 'success');
                } else {
                    const result = await response.json();
                    showToast(result.detail || 'Failed to delete task', 'error');
                }
            } catch (error) {
                console.error('Error deleting task:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// ============================================
// Task View Switching Functions
// ============================================

window.currentTaskView = 'table';

// Switch between Table, Automation, and Overdue views
window.switchTaskView = function(view) {
    window.currentTaskView = view;
    
    const tableView = document.getElementById('tasksTableView');
    const automationView = document.getElementById('tasksAutomationView');
    const overdueView = document.getElementById('tasksOverdueView');
    const tableBtn = document.getElementById('taskTableViewBtn');
    const automationBtn = document.getElementById('taskAutomationViewBtn');
    const overdueBtn = document.getElementById('taskOverdueViewBtn');
    
    // Hide all views
    if (tableView) tableView.style.display = 'none';
    if (automationView) automationView.style.display = 'none';
    if (overdueView) overdueView.style.display = 'none';
    
    // Remove active from all buttons
    if (tableBtn) tableBtn.classList.remove('active');
    if (automationBtn) automationBtn.classList.remove('active');
    if (overdueBtn) overdueBtn.classList.remove('active');
    
    if (view === 'automation') {
        if (automationView) automationView.style.display = 'block';
        if (automationBtn) automationBtn.classList.add('active');
        loadAutomationView();
    } else if (view === 'overdue') {
        if (overdueView) overdueView.style.display = 'block';
        if (overdueBtn) overdueBtn.classList.add('active');
        loadOverdueView();
    } else {
        if (tableView) tableView.style.display = 'block';
        if (tableBtn) tableBtn.classList.add('active');
        loadTasks();
    }
};

// Load Automation View
window.loadAutomationView = async function() {
    if (!authToken || !companyId) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/automation-stats`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            showToast('Error loading automation stats', 'error');
            return;
        }
        
        const result = await response.json();
        const stats = result.data || {};
        
        // Update stat cards
        document.getElementById('auto-total-tasks').textContent = stats.total_tasks || 0;
        document.getElementById('auto-pending-tasks').textContent = stats.pending_tasks || 0;
        document.getElementById('auto-overdue-tasks').textContent = stats.overdue_tasks || 0;
        document.getElementById('auto-completed-today').textContent = stats.completed_today || 0;
        
        // Update priority bars
        const byPriority = stats.by_priority || {};
        const maxPriority = Math.max(
            byPriority.urgent || 0,
            byPriority.high || 0,
            byPriority.medium || 0,
            byPriority.low || 0,
            1
        );
        
        ['urgent', 'high', 'medium', 'low'].forEach(priority => {
            const count = byPriority[priority] || 0;
            const width = Math.min(100, (count / maxPriority) * 100);
            const bar = document.getElementById(`bar-${priority}`);
            const countEl = document.getElementById(`count-${priority}`);
            if (bar) bar.style.width = `${width}%`;
            if (countEl) countEl.textContent = count;
        });
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading automation view:', error);
        showToast('Error loading automation data', 'error');
    }
};

// Load Overdue View
window.loadOverdueView = async function() {
    if (!authToken || !companyId) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/overdue`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            showToast('Error loading overdue tasks', 'error');
            return;
        }
        
        const result = await response.json();
        const tasks = result.data?.overdue_tasks || [];
        
        // Update count badge
        document.getElementById('overdue-total-count').textContent = tasks.length;
        
        // Render overdue list
        const container = document.getElementById('overdueListContainer');
        if (!container) return;
        
        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="check-circle" style="width:64px;height:64px;color:var(--jira-success);"></i>
                    <h3>No Overdue Tasks!</h3>
                    <p>Great job! All tasks are on track.</p>
                </div>
            `;
        } else {
            container.innerHTML = tasks.map(task => `
                <div class="overdue-task-card priority-${task.priority}">
                    <div class="overdue-task-info">
                        <h4>${escapeHtml(task.title)}</h4>
                        <div class="overdue-task-meta">
                            <span class="days-badge">${task.days_overdue} days overdue</span>
                            <span class="priority-badge ${task.priority}">${task.priority}</span>
                            ${task.assigned_to ? `<span class="assigned-badge"><i data-lucide="user"></i> ${task.assigned_to}</span>` : ''}
                        </div>
                    </div>
                    <div class="overdue-task-actions">
                        <button class="btn btn-sm btn-primary" onclick="editTask(${task.id})">
                            <i data-lucide="edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-success" onclick="completeTask(${task.id})">
                            <i data-lucide="check"></i> Complete
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading overdue view:', error);
        showToast('Error loading overdue tasks', 'error');
    }
};

// Complete Task
window.completeTask = async function(taskId) {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/${taskId}/complete`, {
            method: 'PUT',
            headers: getHeaders()
        });
        
        if (response.ok) {
            showToast('Task completed!', 'success');
            loadOverdueView();
        } else {
            showToast('Failed to complete task', 'error');
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showToast('Error completing task', 'error');
    }
};

// ============================================
// Task Automation Functions (Legacy Modal - kept for compatibility)
// ============================================

// Show Task Automation Dashboard (Modal - legacy)
window.showTaskAutomationDashboard = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/automation-stats`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            showToast('Error loading automation stats', 'error');
            return;
        }
        
        const result = await response.json();
        const stats = result.data || {};
        
        const modalHtml = `
            <div class="modal-overlay" id="automationModal" onclick="closeAutomationModal(event)">
                <div class="modal-content modal-lg" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i data-lucide="zap"></i> Task Automation Dashboard</h3>
                        <button class="modal-close" onclick="closeAutomationModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <!-- Stats Cards -->
                        <div class="automation-stats-grid">
                            <div class="stat-card">
                                <i data-lucide="list-todo"></i>
                                <span class="stat-value">${stats.total_tasks || 0}</span>
                                <span class="stat-label">Total Tasks</span>
                            </div>
                            <div class="stat-card warning">
                                <i data-lucide="clock"></i>
                                <span class="stat-value">${stats.pending_tasks || 0}</span>
                                <span class="stat-label">Pending</span>
                            </div>
                            <div class="stat-card danger">
                                <i data-lucide="alert-triangle"></i>
                                <span class="stat-value">${stats.overdue_tasks || 0}</span>
                                <span class="stat-label">Overdue</span>
                            </div>
                            <div class="stat-card success">
                                <i data-lucide="check-circle"></i>
                                <span class="stat-value">${stats.completed_today || 0}</span>
                                <span class="stat-label">Completed Today</span>
                            </div>
                        </div>
                        
                        <!-- Priority Breakdown -->
                        <div class="automation-section">
                            <h4>Tasks by Priority</h4>
                            <div class="priority-bars">
                                <div class="priority-item">
                                    <span class="priority-label">Urgent</span>
                                    <div class="priority-bar urgent" style="width: ${Math.min(100, (stats.by_priority?.urgent || 0) * 10)}%"></div>
                                    <span class="priority-count">${stats.by_priority?.urgent || 0}</span>
                                </div>
                                <div class="priority-item">
                                    <span class="priority-label">High</span>
                                    <div class="priority-bar high" style="width: ${Math.min(100, (stats.by_priority?.high || 0) * 10)}%"></div>
                                    <span class="priority-count">${stats.by_priority?.high || 0}</span>
                                </div>
                                <div class="priority-item">
                                    <span class="priority-label">Medium</span>
                                    <div class="priority-bar medium" style="width: ${Math.min(100, (stats.by_priority?.medium || 0) * 10)}%"></div>
                                    <span class="priority-count">${stats.by_priority?.medium || 0}</span>
                                </div>
                                <div class="priority-item">
                                    <span class="priority-label">Low</span>
                                    <div class="priority-bar low" style="width: ${Math.min(100, (stats.by_priority?.low || 0) * 10)}%"></div>
                                    <span class="priority-count">${stats.by_priority?.low || 0}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Automation Actions -->
                        <div class="automation-section">
                            <h4>Automation Actions</h4>
                            <div class="automation-actions">
                                <button class="btn btn-primary" onclick="autoCreateTasksForLeads()">
                                    <i data-lucide="plus-circle"></i> Auto-Create Follow-up Tasks
                                </button>
                                <button class="btn btn-warning" onclick="escalateOverdueTasks()">
                                    <i data-lucide="arrow-up-circle"></i> Escalate Overdue Tasks
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="closeAutomationModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        const existingModal = document.getElementById('automationModal');
        if (existingModal) existingModal.remove();
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading automation dashboard:', error);
        showToast('Error loading automation dashboard', 'error');
    }
};

window.closeAutomationModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('automationModal');
    if (modal) modal.remove();
};

// Show Overdue Tasks
window.showOverdueTasks = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/overdue`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            showToast('Error loading overdue tasks', 'error');
            return;
        }
        
        const result = await response.json();
        const tasks = result.data?.overdue_tasks || [];
        
        const modalHtml = `
            <div class="modal-overlay" id="overdueModal" onclick="closeOverdueModal(event)">
                <div class="modal-content modal-lg" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i data-lucide="alert-triangle"></i> Overdue Tasks (${tasks.length})</h3>
                        <button class="modal-close" onclick="closeOverdueModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        ${tasks.length === 0 ? '<div class="empty-state"><p>No overdue tasks! 🎉</p></div>' : `
                        <div class="overdue-list">
                            ${tasks.map(task => `
                                <div class="overdue-item priority-${task.priority}">
                                    <div class="overdue-info">
                                        <span class="overdue-title">${escapeHtml(task.title)}</span>
                                        <span class="overdue-meta">
                                            <span class="days-overdue">${task.days_overdue} days overdue</span>
                                            <span class="priority-badge ${task.priority}">${task.priority}</span>
                                        </span>
                                    </div>
                                    <div class="overdue-actions">
                                        <button class="btn btn-sm btn-primary" onclick="editTask(${task.id}); closeOverdueModal();">Edit</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        `}
                    </div>
                    <div class="modal-footer">
                        ${tasks.length > 0 ? `<button class="btn btn-warning" onclick="escalateOverdueTasks()">
                            <i data-lucide="arrow-up-circle"></i> Escalate All
                        </button>` : ''}
                        <button class="btn btn-secondary" onclick="closeOverdueModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        const existingModal = document.getElementById('overdueModal');
        if (existingModal) existingModal.remove();
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading overdue tasks:', error);
        showToast('Error loading overdue tasks', 'error');
    }
};

window.closeOverdueModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('overdueModal');
    if (modal) modal.remove();
};

// Auto-create tasks for leads
window.autoCreateTasksForLeads = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/auto-create-for-leads?days_since_creation=7`, {
            method: 'POST',
            headers: getHeaders()
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Created ${result.data?.tasks_created || 0} follow-up tasks`, 'success');
            closeAutomationModal();
            loadTasks();
        } else {
            showToast('Failed to create tasks', 'error');
        }
    } catch (error) {
        console.error('Error creating tasks:', error);
        showToast('Error creating tasks', 'error');
    }
};

// Escalate overdue tasks
window.escalateOverdueTasks = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/tasks/escalate-overdue?escalation_days=3`, {
            method: 'POST',
            headers: getHeaders()
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Escalated ${result.data?.escalated || 0} tasks`, 'success');
            closeAutomationModal();
            closeOverdueModal();
            loadTasks();
        } else {
            showToast('Failed to escalate tasks', 'error');
        }
    } catch (error) {
        console.error('Error escalating tasks:', error);
        showToast('Error escalating tasks', 'error');
    }
};

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
