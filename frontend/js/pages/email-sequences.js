// Email Sequences Page JavaScript

// Global variable for editing sequence ID
if (typeof window.currentEditingSequenceId === 'undefined') {
    window.currentEditingSequenceId = null;
}

window.initEmailSequences = function() {
    if (!authToken || !companyId) {
        console.warn('No auth token or company ID');
        return;
    }
    
    loadSequences();
    loadSequenceStats();
};

// Load Sequences
window.loadSequences = async function() {
    const grid = document.getElementById('sequencesGrid');
    if (!grid) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences?page=1&per_page=50`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            grid.innerHTML = '<div class="empty-state"><p>Error loading sequences</p></div>';
            return;
        }
        
        const result = await response.json();
        const sequences = result.data || [];
        
        if (sequences.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="mail" style="width:48px;height:48px;color:var(--jira-text-tertiary);"></i>
                    <h3>No Email Sequences</h3>
                    <p>Create your first email sequence to automate lead nurturing</p>
                    <button class="btn btn-primary" onclick="showSequenceForm()">
                        <i data-lucide="plus"></i> Create Sequence
                    </button>
                </div>
            `;
        } else {
            grid.innerHTML = sequences.map(seq => createSequenceCard(seq)).join('');
        }
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading sequences:', error);
        grid.innerHTML = '<div class="empty-state"><p>Error loading sequences</p></div>';
    }
};

// Create Sequence Card HTML
function createSequenceCard(seq) {
    const statusClass = seq.is_active ? 'active' : 'inactive';
    const statusText = seq.is_active ? 'Active' : 'Inactive';
    const triggerText = {
        'on_creation': 'On Lead Creation',
        'score_threshold': `Score ≥ ${seq.score_threshold || 50}`,
        'manual': 'Manual'
    }[seq.trigger_condition] || seq.trigger_condition;
    
    return `
        <div class="sequence-card">
            <div class="sequence-header">
                <div class="sequence-info">
                    <h4>${escapeHtml(seq.name)}</h4>
                    <span class="sequence-status ${statusClass}">${statusText}</span>
                </div>
                <div class="sequence-actions">
                    <button class="btn-icon-sm" onclick="editSequence(${seq.id})" title="Edit">
                        <i data-lucide="edit"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="toggleSequenceStatus(${seq.id}, ${!seq.is_active})" title="${seq.is_active ? 'Deactivate' : 'Activate'}">
                        <i data-lucide="${seq.is_active ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="btn-icon-sm danger" onclick="deleteSequence(${seq.id})" title="Delete">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
            <div class="sequence-body">
                <div class="sequence-meta">
                    <span><i data-lucide="zap"></i> ${triggerText}</span>
                    <span><i data-lucide="mail"></i> ${seq.total_emails || 5} emails</span>
                    <span><i data-lucide="calendar"></i> ${seq.duration_days || 14} days</span>
                </div>
                ${seq.description ? `<p class="sequence-desc">${escapeHtml(seq.description)}</p>` : ''}
            </div>
            <div class="sequence-footer">
                <button class="btn btn-sm btn-outline" onclick="viewSequenceEmails(${seq.id})">
                    <i data-lucide="eye"></i> View Emails
                </button>
                <button class="btn btn-sm btn-primary" onclick="enrollLeadInSequence(${seq.id})">
                    <i data-lucide="user-plus"></i> Enroll Lead
                </button>
            </div>
        </div>
    `;
}

// Load Sequence Stats
window.loadSequenceStats = async function() {
    const statsDiv = document.getElementById('sequenceStats');
    if (!statsDiv) return;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/analytics`, {
            headers: getHeaders()
        });
        
        if (!response.ok) return;
        
        const result = await response.json();
        const data = result.data || {};
        const metrics = data.email_metrics || {};
        
        statsDiv.innerHTML = `
            <div class="stats-row">
                <div class="stat-item">
                    <span class="stat-value">${data.total_sequences || 0}</span>
                    <span class="stat-label">Total Sequences</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.active_sequences || 0}</span>
                    <span class="stat-label">Active</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${metrics.total_sent || 0}</span>
                    <span class="stat-label">Emails Sent</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${metrics.open_rate || 0}%</span>
                    <span class="stat-label">Open Rate</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${metrics.click_rate || 0}%</span>
                    <span class="stat-label">Click Rate</span>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading sequence stats:', error);
    }
};

// Show Sequence Form
window.showSequenceForm = function(sequence = null) {
    window.currentEditingSequenceId = sequence?.id || null;
    
    const template = document.getElementById('sequenceFormTemplate');
    if (!template) {
        console.error('Sequence form template not found');
        return;
    }
    
    // Remove existing modal
    const existingModal = document.getElementById('sequenceFormModal');
    if (existingModal) existingModal.remove();
    
    // Clone and append template
    const modal = template.content.cloneNode(true);
    document.body.appendChild(modal);
    
    // Update title
    document.getElementById('sequenceFormTitle').textContent = sequence ? 'Edit Email Sequence' : 'Create Email Sequence';
    
    // Fill form if editing
    if (sequence) {
        document.getElementById('sequenceName').value = sequence.name || '';
        document.getElementById('triggerCondition').value = sequence.trigger_condition || 'on_creation';
        document.getElementById('scoreThreshold').value = sequence.score_threshold || 50;
        document.getElementById('totalEmails').value = sequence.total_emails || 5;
        document.getElementById('durationDays').value = sequence.duration_days || 14;
        document.getElementById('sequenceDescription').value = sequence.description || '';
        document.getElementById('sequenceActive').checked = sequence.is_active !== false;
        toggleScoreThreshold();
    }
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
};

window.closeSequenceForm = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('sequenceFormModal');
    if (modal) modal.remove();
};

window.toggleScoreThreshold = function() {
    const trigger = document.getElementById('triggerCondition')?.value;
    const group = document.getElementById('scoreThresholdGroup');
    if (group) {
        group.style.display = trigger === 'score_threshold' ? 'block' : 'none';
    }
};

// Save Sequence
window.saveSequence = async function(event) {
    event.preventDefault();
    
    const form = document.getElementById('sequenceForm');
    const formData = new FormData(form);
    
    const data = {
        name: formData.get('name'),
        trigger_condition: formData.get('trigger_condition'),
        score_threshold: parseInt(formData.get('score_threshold')) || 50,
        total_emails: parseInt(formData.get('total_emails')) || 5,
        duration_days: parseInt(formData.get('duration_days')) || 14,
        description: formData.get('description'),
        is_active: document.getElementById('sequenceActive').checked
    };
    
    try {
        const url = window.currentEditingSequenceId 
            ? `${API_BASE}/companies/${companyId}/email-sequences/${window.currentEditingSequenceId}`
            : `${API_BASE}/companies/${companyId}/email-sequences`;
        
        const response = await fetch(url, {
            method: window.currentEditingSequenceId ? 'PUT' : 'POST',
            headers: {
                ...getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast(`Sequence ${window.currentEditingSequenceId ? 'updated' : 'created'} successfully!`, 'success');
            closeSequenceForm();
            loadSequences();
            loadSequenceStats();
        } else {
            const result = await response.json();
            showToast(result.detail || 'Failed to save sequence', 'error');
        }
    } catch (error) {
        console.error('Error saving sequence:', error);
        showToast('Error saving sequence', 'error');
    }
};

// Edit Sequence
window.editSequence = async function(id) {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/${id}`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const result = await response.json();
            showSequenceForm(result.data || result);
        } else {
            showToast('Failed to load sequence', 'error');
        }
    } catch (error) {
        console.error('Error loading sequence:', error);
        showToast('Error loading sequence', 'error');
    }
};

// Toggle Sequence Status
window.toggleSequenceStatus = async function(id, activate) {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/${id}`, {
            method: 'PUT',
            headers: {
                ...getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_active: activate })
        });
        
        if (response.ok) {
            showToast(`Sequence ${activate ? 'activated' : 'deactivated'}`, 'success');
            loadSequences();
        } else {
            showToast('Failed to update sequence', 'error');
        }
    } catch (error) {
        console.error('Error updating sequence:', error);
        showToast('Error updating sequence', 'error');
    }
};

// Delete Sequence
window.deleteSequence = function(id) {
    showDeleteConfirmModal(
        'Delete Sequence',
        'Are you sure you want to delete this email sequence? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/${id}`, {
                    method: 'DELETE',
                    headers: getHeaders()
                });
                
                if (response.ok) {
                    showToast('Sequence deleted', 'success');
                    loadSequences();
                    loadSequenceStats();
                } else {
                    showToast('Failed to delete sequence', 'error');
                }
            } catch (error) {
                console.error('Error deleting sequence:', error);
                showToast('Error deleting sequence', 'error');
            }
        }
    );
};

// Show Sequence Analytics
window.showSequenceAnalytics = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/analytics`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            showToast('Error loading analytics', 'error');
            return;
        }
        
        const result = await response.json();
        const data = result.data || {};
        const metrics = data.email_metrics || {};
        
        const modalHtml = `
            <div class="modal-overlay" id="analyticsModal" onclick="closeAnalyticsModal(event)">
                <div class="modal-content modal-lg" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i data-lucide="bar-chart-2"></i> Email Sequence Analytics</h3>
                        <button class="modal-close" onclick="closeAnalyticsModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="analytics-grid">
                            <div class="analytics-card">
                                <h4>Email Performance</h4>
                                <div class="analytics-metrics">
                                    <div class="metric-row">
                                        <span>Total Sent</span>
                                        <span class="metric-value">${metrics.total_sent || 0}</span>
                                    </div>
                                    <div class="metric-row">
                                        <span>Opens</span>
                                        <span class="metric-value">${metrics.total_opens || 0}</span>
                                    </div>
                                    <div class="metric-row">
                                        <span>Clicks</span>
                                        <span class="metric-value">${metrics.total_clicks || 0}</span>
                                    </div>
                                    <div class="metric-row">
                                        <span>Replies</span>
                                        <span class="metric-value">${metrics.total_replies || 0}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="analytics-card">
                                <h4>Engagement Rates</h4>
                                <div class="rate-bars">
                                    <div class="rate-item">
                                        <span>Open Rate</span>
                                        <div class="rate-bar"><div class="rate-fill" style="width:${metrics.open_rate || 0}%"></div></div>
                                        <span>${metrics.open_rate || 0}%</span>
                                    </div>
                                    <div class="rate-item">
                                        <span>Click Rate</span>
                                        <div class="rate-bar"><div class="rate-fill" style="width:${metrics.click_rate || 0}%"></div></div>
                                        <span>${metrics.click_rate || 0}%</span>
                                    </div>
                                    <div class="rate-item">
                                        <span>Reply Rate</span>
                                        <div class="rate-bar"><div class="rate-fill" style="width:${metrics.reply_rate || 0}%"></div></div>
                                        <span>${metrics.reply_rate || 0}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="closeAnalyticsModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        const existingModal = document.getElementById('analyticsModal');
        if (existingModal) existingModal.remove();
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Error loading analytics', 'error');
    }
};

window.closeAnalyticsModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('analyticsModal');
    if (modal) modal.remove();
};

// View Sequence Emails (placeholder)
window.viewSequenceEmails = function(id) {
    showToast('Email editor coming soon!', 'info');
};

// Enroll Lead in Sequence
window.enrollLeadInSequence = async function(sequenceId) {
    // Show lead selection modal
    const modalHtml = `
        <div class="modal-overlay" id="enrollModal" onclick="closeEnrollModal(event)">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3><i data-lucide="user-plus"></i> Enroll Lead in Sequence</h3>
                    <button class="modal-close" onclick="closeEnrollModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Select Lead</label>
                        <select id="enrollLeadSelect" class="form-select">
                            <option value="">Loading leads...</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeEnrollModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="confirmEnrollLead(${sequenceId})">
                        <i data-lucide="check"></i> Enroll
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Load leads
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/leads?page=1&per_page=100&status=new,contacted`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const result = await response.json();
            const leads = result.data || [];
            const select = document.getElementById('enrollLeadSelect');
            
            select.innerHTML = leads.length === 0 
                ? '<option value="">No leads available</option>'
                : '<option value="">Select a lead...</option>' + leads.map(l => 
                    `<option value="${l.id}">${escapeHtml(l.lead_name || l.first_name + ' ' + l.last_name)} - ${l.email || 'No email'}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading leads:', error);
    }
};

window.closeEnrollModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('enrollModal');
    if (modal) modal.remove();
};

window.confirmEnrollLead = async function(sequenceId) {
    const leadId = document.getElementById('enrollLeadSelect')?.value;
    
    if (!leadId) {
        showToast('Please select a lead', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/email-sequences/${sequenceId}/start/${leadId}`, {
            method: 'POST',
            headers: getHeaders()
        });
        
        if (response.ok) {
            showToast('Lead enrolled in sequence!', 'success');
            closeEnrollModal();
        } else {
            const result = await response.json();
            showToast(result.detail || 'Failed to enroll lead', 'error');
        }
    } catch (error) {
        console.error('Error enrolling lead:', error);
        showToast('Error enrolling lead', 'error');
    }
};

// Helper function
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
