// Leads Page JavaScript

// Global variable for editing lead ID
if (typeof window.currentEditingLeadId === 'undefined') {
    window.currentEditingLeadId = null;
}

function initLeads() {
    // Re-read auth from localStorage (in case global vars are stale)
    const token = localStorage.getItem('authToken');
    const company = localStorage.getItem('companyId');
    
    // Update global vars if needed
    if (token && !authToken) authToken = token;
    if (company && !companyId) companyId = company;
    
    // Check auth before loading
    if (!token || !company) {
        console.warn('No auth token or company ID - skipping lead load');
        const table = document.getElementById('leadsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadLeads();
}

window.loadLeads = async function() {
    // Check auth before making API call
    if (!authToken || !companyId) {
        console.warn('Cannot load leads: No auth token or company ID');
        const table = document.getElementById('leadsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const search = document.getElementById('leadSearch')?.value || '';
    const status = document.getElementById('leadStatusFilter')?.value || '';
    const priority = document.getElementById('leadPriorityFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/leads?page=1&per_page=100`;
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
            console.error('Error loading leads:', response.status, errorData);
            const table = document.getElementById('leadsTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Error loading leads</h3><p>Please try again</p></div>';
            }
            return;
        }
        
        const data = await response.json();
        const leads = Array.isArray(data.data) ? data.data : [];

        // Update stats cards
        if (typeof window.updateLeadStats === 'function') {
            window.updateLeadStats(leads);
        }

        const table = document.getElementById('leadsTable');
        if (!table) return;

        // Initialize DataTable
        if (window.leadsTable && typeof window.leadsTable.updateData === 'function') {
            window.leadsTable.updateData(leads);
            // Re-initialize Lucide icons after update
            if (typeof lucide !== 'undefined') {
                setTimeout(() => lucide.createIcons(), 100);
            }
        } else {
            window.leadsTable = new DataTable('leadsTable', {
                data: leads,
                columns: [
                    {
                        key: 'select',
                        label: '<input type="checkbox" id="selectAllLeads" onchange="toggleSelectAllLeads(this)" title="Select All">',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            return `<input type="checkbox" class="lead-checkbox" data-id="${row.id}" onchange="updateBulkSelection()">`;
                        }
                    },
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
                        render: (value, row) => {
                            const name = (row.first_name && row.last_name) 
                                ? `${row.first_name} ${row.last_name}` 
                                : row.lead_name || '-';
                            return `<strong>${escapeHtml(name)}</strong>`;
                        }
                    },
                    {
                        key: 'company_name',
                        label: 'Company',
                        sortable: true,
                        filterable: true
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
                        key: 'source',
                        label: 'Source',
                        sortable: true,
                        filterable: true
                    },
                    {
                        key: 'status',
                        label: 'Status',
                        sortable: true,
                        filterable: true,
                        type: 'badge',
                        render: (value, row) => {
                            const status = value || 'new';
                            return `<span class="status-badge status-${status}">${status.toUpperCase()}</span>`;
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
                        key: 'lead_score',
                        label: 'Score',
                        sortable: true,
                        type: 'number',
                        align: 'center',
                        render: (value, row) => {
                            if (value === null || value === undefined) return '<span class="score-badge score-none">-</span>';
                            return renderLeadScoreMeter(value);
                        }
                    },
                    {
                        key: 'estimated_value',
                        label: 'Value',
                        sortable: true,
                        type: 'currency',
                        format: 'INR',
                        align: 'right',
                        render: (value) => {
                            return value ? `₹${parseFloat(value).toLocaleString()}` : '-';
                        }
                    },
                    {
                        key: 'actions',
                        label: 'Actions',
                        sortable: false,
                        align: 'center',
                        render: (value, row) => {
                            const canConvert = row.lead_score >= 70 && (row.status === 'contacted' || row.status === 'qualified');
                            const leadName = row.lead_name || `${row.first_name || ''} ${row.last_name || ''}`.trim() || 'Lead';
                            return `
                                <div class="action-buttons">
                                    <button class="btn-icon btn-info" onclick="showLeadQualification(${row.id})" title="Qualification & Risk">
                                        <i data-lucide="clipboard-check" style="width:16px;height:16px"></i>
                                    </button>
                                    ${row.phone ? `<button class="btn-icon btn-whatsapp" onclick="openWhatsAppPanel(${row.id}, '${leadName.replace(/'/g, "\\'")}', '${row.phone}')" title="WhatsApp">
                                        <i data-lucide="message-circle" style="width:16px;height:16px"></i>
                                    </button>` : ''}
                                    ${canConvert ? `<button class="btn-icon btn-success" onclick="convertLead(${row.id})" title="Convert to Account">
                                        <i data-lucide="user-check" style="width:16px;height:16px"></i>
                                    </button>` : ''}
                                    <button class="btn-icon btn-edit" onclick="editLead(${row.id})" title="Edit">
                                        <i data-lucide="edit" style="width:16px;height:16px"></i>
                                    </button>
                                    <button class="btn-icon btn-delete" onclick="deleteLead(${row.id})" title="Delete">
                                        <i data-lucide="trash-2" style="width:16px;height:16px"></i>
                                    </button>
                                </div>
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
        
        // Initialize Lucide icons after DataTable renders
        if (typeof lucide !== 'undefined') {
            setTimeout(() => lucide.createIcons(), 100);
        }
    } catch (error) {
        console.error('Error loading leads:', error);
        const table = document.getElementById('leadsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading leads</h3><p>Please try again</p></div>';
        }
    }
};

window.showLeadForm = function() {
    window.currentEditingLeadId = null;
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found');
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    try {
        openLeadModal();
    } catch (error) {
        console.error('Error in showLeadForm:', error);
        alert('Error opening lead form: ' + error.message);
    }
};

window.editLead = async function(id) {
    window.currentEditingLeadId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            alert('Failed to load lead data');
            return;
        }
        
        const result = await response.json();
        const lead = result.data || result;
        
        openLeadModal(lead);
    } catch (error) {
        console.error('Error loading lead:', error);
        alert('Error loading lead data: ' + error.message);
    }
};

window.openLeadModal = function(lead = null) {
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found!');
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    const isEdit = !!lead;
    const title = isEdit ? 'Edit Lead' : 'Add Lead';
    
    // Use first_name/last_name if available, otherwise lead_name
    const firstName = lead?.first_name || '';
    const lastName = lead?.last_name || '';
    const leadName = lead?.lead_name || '';
    const displayName = leadName || (firstName && lastName ? `${firstName} ${lastName}` : '');
    
    formContent.innerHTML = `
        <div class="form-modal-header">
            <h2>${title}</h2>
            <button class="btn-close-modal" onclick="closeFormModal()">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
        <form id="leadForm" class="form-advanced" onsubmit="handleLeadSubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Basic Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">First Name</label>
                        <input type="text" id="leadFirstName" class="form-input-advanced" value="${firstName}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Last Name</label>
                        <input type="text" id="leadLastName" class="form-input-advanced" value="${lastName}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Lead Name <span class="required">*</span></label>
                        <input type="text" id="leadName" class="form-input-advanced" value="${displayName}" required>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Company Name</label>
                        <input type="text" id="leadCompanyName" class="form-input-advanced" value="${lead?.company_name || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Email</label>
                        <input type="email" id="leadEmail" class="form-input-advanced" value="${lead?.email || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Phone</label>
                        <input type="tel" id="leadPhone" class="form-input-advanced" value="${lead?.phone || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Country</label>
                        <input type="text" id="leadCountry" class="form-input-advanced" value="${lead?.country || 'India'}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Industry</label>
                        <input type="text" id="leadIndustry" class="form-input-advanced" value="${lead?.industry || ''}" placeholder="IT Services">
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Source Attribution (UTM)</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Lead Source</label>
                        <select id="leadSource" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="Website Form" ${lead?.source === 'Website Form' ? 'selected' : ''}>Website Form</option>
                            <option value="Google Ads" ${lead?.source === 'Google Ads' ? 'selected' : ''}>Google Ads</option>
                            <option value="Meta Ads" ${lead?.source === 'Meta Ads' ? 'selected' : ''}>Meta Ads</option>
                            <option value="WhatsApp Bot" ${lead?.source === 'WhatsApp Bot' ? 'selected' : ''}>WhatsApp Bot</option>
                            <option value="Email" ${lead?.source === 'Email' ? 'selected' : ''}>Email</option>
                            <option value="Referral" ${lead?.source === 'Referral' ? 'selected' : ''}>Referral</option>
                            <option value="Cold Call" ${lead?.source === 'Cold Call' ? 'selected' : ''}>Cold Call</option>
                            <option value="Manual" ${lead?.source === 'Manual' ? 'selected' : ''}>Manual</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Campaign</label>
                        <input type="text" id="leadCampaign" class="form-input-advanced" value="${lead?.campaign || ''}" placeholder="CRM-Q4-2025">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Medium</label>
                        <select id="leadMedium" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="CPC" ${lead?.medium === 'CPC' ? 'selected' : ''}>CPC</option>
                            <option value="Email" ${lead?.medium === 'Email' ? 'selected' : ''}>Email</option>
                            <option value="Social" ${lead?.medium === 'Social' ? 'selected' : ''}>Social</option>
                            <option value="Organic" ${lead?.medium === 'Organic' ? 'selected' : ''}>Organic</option>
                            <option value="Direct" ${lead?.medium === 'Direct' ? 'selected' : ''}>Direct</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Term (Search Term)</label>
                        <input type="text" id="leadTerm" class="form-input-advanced" value="${lead?.term || ''}" placeholder="crm software">
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Lead Management</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Status <span class="required">*</span></label>
                        <select id="leadStatus" class="form-select-advanced" required>
                            <option value="new" ${lead?.status === 'new' || !lead ? 'selected' : ''}>New</option>
                            <option value="contacted" ${lead?.status === 'contacted' ? 'selected' : ''}>Contacted</option>
                            <option value="qualified" ${lead?.status === 'qualified' ? 'selected' : ''}>Qualified</option>
                            <option value="unqualified" ${lead?.status === 'unqualified' ? 'selected' : ''}>Unqualified</option>
                            <option value="converted" ${lead?.status === 'converted' ? 'selected' : ''}>Converted</option>
                            <option value="recycled" ${lead?.status === 'recycled' ? 'selected' : ''}>Recycled</option>
                            <option value="disqualified" ${lead?.status === 'disqualified' ? 'selected' : ''}>Disqualified</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Stage</label>
                        <select id="leadStage" class="form-select-advanced">
                            <option value="awareness" ${lead?.stage === 'awareness' || !lead ? 'selected' : ''}>Awareness</option>
                            <option value="consideration" ${lead?.stage === 'consideration' ? 'selected' : ''}>Consideration</option>
                            <option value="decision" ${lead?.stage === 'decision' ? 'selected' : ''}>Decision</option>
                            <option value="converted" ${lead?.stage === 'converted' ? 'selected' : ''}>Converted</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Priority <span class="required">*</span></label>
                        <select id="leadPriority" class="form-select-advanced" required>
                            <option value="low" ${lead?.priority === 'low' ? 'selected' : ''}>Low</option>
                            <option value="medium" ${lead?.priority === 'medium' || !lead ? 'selected' : ''}>Medium</option>
                            <option value="high" ${lead?.priority === 'high' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Lead Score (0-100)</label>
                        <input type="number" id="leadScore" class="form-input-advanced" value="${lead?.lead_score || 0}" min="0" max="100">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Estimated Value (₹)</label>
                        <input type="number" id="leadEstimatedValue" class="form-input-advanced" value="${lead?.estimated_value || ''}" step="0.01" min="0">
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Qualification & Additional Info</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Interest Product</label>
                        <input type="text" id="leadInterestProduct" class="form-input-advanced" value="${lead?.interest_product || ''}" placeholder="CRM Software">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Budget Range</label>
                        <input type="text" id="leadBudgetRange" class="form-input-advanced" value="${lead?.budget_range || ''}" placeholder="₹5-7 Lakh">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Authority Level</label>
                        <select id="leadAuthorityLevel" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="decision_maker" ${lead?.authority_level === 'decision_maker' ? 'selected' : ''}>Decision Maker</option>
                            <option value="influencer" ${lead?.authority_level === 'influencer' ? 'selected' : ''}>Influencer</option>
                            <option value="user" ${lead?.authority_level === 'user' ? 'selected' : ''}>User</option>
                            <option value="gatekeeper" ${lead?.authority_level === 'gatekeeper' ? 'selected' : ''}>Gatekeeper</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Timeline</label>
                        <input type="text" id="leadTimeline" class="form-input-advanced" value="${lead?.timeline || ''}" placeholder="3-6 Months">
                    </div>
                    <div class="form-group-advanced form-group-full">
                        <label class="form-label">Notes</label>
                        <textarea id="leadNotes" class="textarea-advanced" rows="3" placeholder="Additional notes...">${lead?.notes || ''}</textarea>
                    </div>
                </div>
            </div>
            
            <div class="form-actions-sticky">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary" id="leadSubmitBtn">
                    ${isEdit ? 'Update Lead' : 'Create Lead'}
                </button>
            </div>
            
            <div id="leadFormError" class="error-message"></div>
        </form>
    `;
    
    modal.style.display = 'flex';
    modal.classList.add('active');
}

window.handleLeadSubmit = async function(e) {
    e.preventDefault();
    
    const errorDiv = document.getElementById('leadFormError');
    const submitBtn = document.getElementById('leadSubmitBtn');
    
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = window.currentEditingLeadId ? 'Updating...' : 'Creating...';
    }
    
    try {
        // Build lead name from first_name + last_name or use leadName field
        const firstName = document.getElementById('leadFirstName').value.trim();
        const lastName = document.getElementById('leadLastName').value.trim();
        const leadNameInput = document.getElementById('leadName').value.trim();
        const leadName = leadNameInput || (firstName && lastName ? `${firstName} ${lastName}` : firstName || lastName || 'Unknown');
        
        const leadData = {
            lead_name: leadName,
            first_name: firstName || null,
            last_name: lastName || null,
            company_name: document.getElementById('leadCompanyName').value.trim() || null,
            email: document.getElementById('leadEmail').value.trim() || null,
            phone: document.getElementById('leadPhone').value.trim() || null,
            country: document.getElementById('leadCountry').value.trim() || null,
            source: document.getElementById('leadSource').value || null,
            campaign: document.getElementById('leadCampaign').value.trim() || null,
            medium: document.getElementById('leadMedium').value || null,
            term: document.getElementById('leadTerm').value.trim() || null,
            status: document.getElementById('leadStatus').value,
            stage: document.getElementById('leadStage').value || null,
            priority: document.getElementById('leadPriority').value,
            lead_score: document.getElementById('leadScore').value ? parseInt(document.getElementById('leadScore').value) : null,
            estimated_value: document.getElementById('leadEstimatedValue').value ? parseFloat(document.getElementById('leadEstimatedValue').value) : null,
            interest_product: document.getElementById('leadInterestProduct').value.trim() || null,
            budget_range: document.getElementById('leadBudgetRange').value.trim() || null,
            authority_level: document.getElementById('leadAuthorityLevel').value || null,
            timeline: document.getElementById('leadTimeline').value.trim() || null,
            industry: document.getElementById('leadIndustry').value.trim() || null,
            notes: document.getElementById('leadNotes').value.trim() || null
        };
        
        const url = window.currentEditingLeadId 
            ? `${API_BASE}/companies/${companyId}/leads/${window.currentEditingLeadId}`
            : `${API_BASE}/companies/${companyId}/leads`;
        
        const method = window.currentEditingLeadId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(leadData)
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
            if (window.leadsTable && typeof window.leadsTable.refresh === 'function') {
                window.leadsTable.refresh();
            } else {
                loadLeads();
            }
            if (typeof showNotification === 'function') {
                showNotification(window.currentEditingLeadId ? 'Lead updated successfully!' : 'Lead created successfully!', 'success');
            }
        } else {
            // Handle different error types
            let errorMsg = 'Failed to save lead';
            let isDuplicateError = false;
            let duplicateNames = [];
            let matchReason = '';
            
            if (response.status === 409) {
                // Duplicate detection error
                isDuplicateError = true;
                if (result.detail && typeof result.detail === 'object') {
                    const duplicateInfo = result.detail;
                    duplicateNames = duplicateInfo.duplicate_lead_names || [];
                    matchReason = duplicateInfo.match_reason || 'Duplicate detected';
                    const confidence = duplicateInfo.confidence || 0;
                    
                    // Build HTML formatted error message
                    let errorHtml = '<strong>⚠️ Duplicate Lead Detected!</strong><br><br>';
                    if (duplicateNames.length > 0) {
                        errorHtml += `<strong>Similar lead(s) found:</strong> ${duplicateNames.join(', ')}<br><br>`;
                    }
                    errorHtml += `<strong>Match Reason:</strong> ${matchReason}<br>`;
                    errorHtml += `<strong>Confidence:</strong> ${confidence}%<br><br>`;
                    errorHtml += `Please check existing leads or use different email/phone.`;
                    
                    errorMsg = errorHtml;
                } else {
                    errorMsg = '<strong>⚠️ Duplicate Lead</strong><br>A lead with this email/phone/company already exists. Please check existing leads.';
                }
            } else if (result.detail) {
                // Other validation errors
                if (Array.isArray(result.detail)) {
                    errorMsg = result.detail.map(e => e.msg || e).join(', ');
                } else if (typeof result.detail === 'object' && result.detail.error) {
                    errorMsg = result.detail.error;
                } else {
                    errorMsg = result.detail;
                }
            }
            
            if (errorDiv) {
                // Use innerHTML for duplicate errors (to support HTML formatting), textContent for others
                if (isDuplicateError && errorMsg.includes('<strong>')) {
                    errorDiv.innerHTML = errorMsg;
                    errorDiv.classList.add('duplicate-error');
                } else {
                    errorDiv.textContent = errorMsg;
                    errorDiv.classList.remove('duplicate-error');
                }
                errorDiv.classList.add('show');
                // Scroll to error
                errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            
            // Also show alert for duplicate (more visible)
            if (response.status === 409) {
                // Use text version for alert
                const alertMsg = duplicateNames.length > 0
                    ? `Duplicate Lead Detected!\n\nSimilar lead(s) found: ${duplicateNames.join(', ')}\nMatch Reason: ${matchReason}\n\nPlease check existing leads or use different email/phone.`
                    : 'A lead with this email/phone/company already exists. Please check existing leads.';
                alert(alertMsg);
            }
        }
    } catch (error) {
        console.error('Error saving lead:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = window.currentEditingLeadId ? 'Update Lead' : 'Create Lead';
        }
    }
};

window.deleteLead = async function(id) {
    showDeleteConfirmModal(
        'Delete Lead',
        'Are you sure you want to delete this lead? This action cannot be undone.',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${id}`, {
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
                    if (window.leadsTable && typeof window.leadsTable.refresh === 'function') {
                        window.leadsTable.refresh();
                    } else {
                        loadLeads();
                    }
                    showToast('Lead deleted successfully!', 'success');
                } else {
                    const result = await response.json();
                    showToast(result.detail || 'Failed to delete lead', 'error');
                }
            } catch (error) {
                console.error('Error deleting lead:', error);
                showToast('Connection error. Please try again.', 'error');
            }
        }
    );
};

// Show Lead Qualification & Risk Modal
window.showLeadQualification = async function(leadId) {
    try {
        // Fetch qualification score, risk score, and conversion eligibility in parallel
        const [qualResponse, riskResponse, convResponse] = await Promise.all([
            fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}/qualification-score`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}/risk-score`, { headers: getHeaders() }),
            fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}/conversion-eligibility`, { headers: getHeaders() })
        ]);

        const qualData = await qualResponse.json();
        const riskData = await riskResponse.json();
        const convData = await convResponse.json();

        const qual = qualData.data || {};
        const risk = riskData.data?.risk_assessment || {};
        const conv = convData.data || {};

        // Build modal content
        const modalHtml = `
            <div id="qualificationModal" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:99999;" onclick="closeQualificationModal(event)">
                <div class="modal-content modal-lg" style="background:#fff;border-radius:12px;max-width:900px;width:95%;max-height:90vh;overflow-y:auto;" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3><i data-lucide="clipboard-check"></i> Lead Qualification & Risk Assessment</h3>
                        <button class="modal-close" onclick="closeQualificationModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="qual-grid">
                            <!-- BANT Score Card -->
                            <div class="qual-card">
                                <h4><i data-lucide="target"></i> BANT Qualification Score</h4>
                                <div class="score-circle ${qual.total_score >= 70 ? 'score-high' : qual.total_score >= 40 ? 'score-medium' : 'score-low'}">
                                    <span class="score-value">${qual.total_score || 0}</span>
                                    <span class="score-max">/100</span>
                                </div>
                                <div class="score-status ${qual.qualified ? 'status-qualified' : 'status-unqualified'}">
                                    ${qual.status?.toUpperCase() || 'UNQUALIFIED'}
                                </div>
                                <div class="bant-breakdown">
                                    <div class="bant-item">
                                        <span>Budget</span>
                                        <div class="progress-bar"><div class="progress" style="width:${(qual.breakdown?.budget || 0) / 25 * 100}%"></div></div>
                                        <span>${qual.breakdown?.budget || 0}/25</span>
                                    </div>
                                    <div class="bant-item">
                                        <span>Authority</span>
                                        <div class="progress-bar"><div class="progress" style="width:${(qual.breakdown?.authority || 0) / 30 * 100}%"></div></div>
                                        <span>${qual.breakdown?.authority || 0}/30</span>
                                    </div>
                                    <div class="bant-item">
                                        <span>Need</span>
                                        <div class="progress-bar"><div class="progress" style="width:${(qual.breakdown?.need || 0) / 25 * 100}%"></div></div>
                                        <span>${qual.breakdown?.need || 0}/25</span>
                                    </div>
                                    <div class="bant-item">
                                        <span>Timeline</span>
                                        <div class="progress-bar"><div class="progress" style="width:${(qual.breakdown?.timeline || 0) / 20 * 100}%"></div></div>
                                        <span>${qual.breakdown?.timeline || 0}/20</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Risk Score Card -->
                            <div class="qual-card">
                                <h4><i data-lucide="alert-triangle"></i> Risk Assessment</h4>
                                <div class="risk-badge risk-${risk.risk_level || 'medium'}">
                                    ${(risk.risk_level || 'medium').toUpperCase()} RISK
                                </div>
                                <div class="risk-score">Score: ${risk.total_score || 0}/100</div>
                                ${risk.risk_factors?.length ? `
                                <div class="risk-factors">
                                    <h5>Risk Factors:</h5>
                                    <ul>
                                        ${risk.risk_factors.map(f => `<li><i data-lucide="alert-circle"></i> ${f}</li>`).join('')}
                                    </ul>
                                </div>` : ''}
                                ${risk.recommendations?.length ? `
                                <div class="risk-recommendations">
                                    <h5>Recommendations:</h5>
                                    <ul>
                                        ${risk.recommendations.map(r => `<li><i data-lucide="lightbulb"></i> ${r}</li>`).join('')}
                                    </ul>
                                </div>` : ''}
                            </div>

                            <!-- Conversion Eligibility Card -->
                            <div class="qual-card full-width">
                                <h4><i data-lucide="user-check"></i> Conversion Eligibility</h4>
                                <div class="conversion-status ${conv.eligible ? 'eligible' : 'not-eligible'}">
                                    ${conv.eligible ? '✓ READY FOR CONVERSION' : '✗ NOT ELIGIBLE'}
                                </div>
                                <div class="criteria-list">
                                    ${Object.entries(conv.criteria || {}).map(([key, val]) => `
                                        <div class="criteria-item ${val.met ? 'met' : 'not-met'}">
                                            <i data-lucide="${val.met ? 'check-circle' : 'x-circle'}"></i>
                                            <span>${key.replace(/_/g, ' ').toUpperCase()}</span>
                                            <small>${val.message || ''}</small>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="closeQualificationModal()">Close</button>
                        <button class="btn btn-primary" onclick="qualifyLead(${leadId})">
                            <i data-lucide="check"></i> Qualify Lead
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('qualificationModal');
        if (existingModal) existingModal.remove();

        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } catch (error) {
        console.error('Error loading qualification data:', error);
        showToast('Error loading qualification data', 'error');
    }
};

window.closeQualificationModal = function(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('qualificationModal');
    if (modal) modal.remove();
};

// Qualify Lead
window.qualifyLead = async function(leadId) {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}/qualify`, {
            method: 'POST',
            headers: getHeaders()
        });

        if (response.ok) {
            showToast('Lead qualified successfully!', 'success');
            closeQualificationModal();
            loadLeads();
        } else {
            const result = await response.json();
            showToast(result.detail || 'Failed to qualify lead', 'error');
        }
    } catch (error) {
        console.error('Error qualifying lead:', error);
        showToast('Error qualifying lead', 'error');
    }
};

// Open WhatsApp Panel for Lead
window.openWhatsAppPanel = async function(leadId, leadName, phone) {
    // Remove existing panel
    const existingPanel = document.getElementById('whatsappPanel');
    if (existingPanel) existingPanel.remove();
    
    const panelHtml = `
        <div class="whatsapp-panel open" id="whatsappPanel">
            <div class="whatsapp-header">
                <h3><i data-lucide="message-circle"></i> WhatsApp</h3>
                <button class="whatsapp-close" onclick="closeWhatsAppPanel()">&times;</button>
            </div>
            <div class="whatsapp-contact">
                <div class="whatsapp-contact-name">${escapeHtml(leadName)}</div>
                <div class="whatsapp-contact-phone">${escapeHtml(phone || 'No phone')}</div>
            </div>
            <div class="whatsapp-messages" id="whatsappMessages">
                <div class="empty-state" style="text-align:center;padding:40px;color:var(--jira-text-tertiary);">
                    <i data-lucide="message-square" style="width:48px;height:48px;margin-bottom:12px;"></i>
                    <p>Start a conversation</p>
                </div>
            </div>
            <div class="whatsapp-templates">
                <label>Quick Templates</label>
                <select id="whatsappTemplate" onchange="selectWhatsAppTemplate()">
                    <option value="">Select template...</option>
                    <option value="welcome">Welcome Message</option>
                    <option value="follow_up">Follow Up</option>
                    <option value="reminder">Appointment Reminder</option>
                </select>
            </div>
            <div class="whatsapp-input">
                <input type="text" id="whatsappMessage" placeholder="Type a message..." onkeypress="if(event.key==='Enter')sendWhatsAppMessage(${leadId}, '${phone}')">
                <button class="whatsapp-send" onclick="sendWhatsAppMessage(${leadId}, '${phone}')">
                    <i data-lucide="send"></i>
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', panelHtml);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Focus on input
    document.getElementById('whatsappMessage')?.focus();
};

window.closeWhatsAppPanel = function() {
    const panel = document.getElementById('whatsappPanel');
    if (panel) {
        panel.classList.remove('open');
        setTimeout(() => panel.remove(), 300);
    }
};

window.selectWhatsAppTemplate = function() {
    const template = document.getElementById('whatsappTemplate')?.value;
    const messageInput = document.getElementById('whatsappMessage');
    
    const templates = {
        welcome: "Hello! Thank you for your interest in our services. How can we help you today?",
        follow_up: "Hi! We wanted to follow up on your inquiry. Are you available for a quick call?",
        reminder: "Hi! This is a reminder about your scheduled appointment. Please confirm your availability."
    };
    
    if (template && templates[template] && messageInput) {
        messageInput.value = templates[template];
        messageInput.focus();
    }
};

window.sendWhatsAppMessage = async function(leadId, phone) {
    const messageInput = document.getElementById('whatsappMessage');
    const message = messageInput?.value?.trim();
    
    if (!message) {
        showToast('Please enter a message', 'warning');
        return;
    }
    
    if (!phone) {
        showToast('No phone number available', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/whatsapp/send?phone=${encodeURIComponent(phone)}&message=${encodeURIComponent(message)}&lead_id=${leadId}`, {
            method: 'POST',
            headers: getHeaders()
        });
        
        if (response.ok) {
            // Add message to chat
            const messagesDiv = document.getElementById('whatsappMessages');
            if (messagesDiv) {
                const emptyState = messagesDiv.querySelector('.empty-state');
                if (emptyState) emptyState.remove();
                
                messagesDiv.innerHTML += `
                    <div class="whatsapp-message sent">
                        ${escapeHtml(message)}
                        <small style="display:block;font-size:10px;opacity:0.7;margin-top:4px;">${new Date().toLocaleTimeString()}</small>
                    </div>
                `;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            messageInput.value = '';
            document.getElementById('whatsappTemplate').value = '';
            showToast('Message sent!', 'success');
        } else {
            showToast('Failed to send message', 'error');
        }
    } catch (error) {
        console.error('Error sending WhatsApp message:', error);
        showToast('Error sending message', 'error');
    }
};

// Convert Lead to Account
window.convertLead = async function(leadId) {
    showDeleteConfirmModal(
        'Convert Lead',
        'This will convert the lead to an Account, Contact, and Opportunity. Continue?',
        async () => {
            try {
                const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}/auto-convert`, {
                    method: 'POST',
                    headers: getHeaders()
                });

                if (response.ok) {
                    const result = await response.json();
                    showToast('Lead converted successfully!', 'success');
                    loadLeads();
                } else {
                    const result = await response.json();
                    showToast(result.detail || 'Failed to convert lead', 'error');
                }
            } catch (error) {
                console.error('Error converting lead:', error);
                showToast('Error converting lead', 'error');
            }
        },
        'Convert',
        'btn-success'
    );
};

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// CSV Import Functionality
// ============================================

window.showLeadImportModal = function() {
    // Remove existing modal if any
    const existingModal = document.getElementById('leadImportModal');
    if (existingModal) existingModal.remove();
    
    const modal = document.createElement('div');
    modal.id = 'leadImportModal';
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:99999;';
    modal.innerHTML = `
        <div class="modal-container" style="max-width: 600px; background:#fff; border-radius:12px;">
            <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px 12px 0 0;">
                <h2 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Import Leads from CSV
                </h2>
                <button onclick="closeLeadImportModal()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 18px;">×</button>
            </div>
            <div class="modal-body" style="padding: 25px;">
                <!-- Step 1: Upload -->
                <div id="importStep1">
                    <div style="text-align: center; padding: 30px; border: 2px dashed #d1d5db; border-radius: 12px; background: #f9fafb; margin-bottom: 20px;">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="1.5" style="margin-bottom: 15px;">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <h3 style="margin: 0 0 10px 0; color: #1e293b;">Upload CSV File</h3>
                        <p style="color: #64748b; margin: 0 0 15px 0;">Drag and drop or click to select</p>
                        <input type="file" id="csvFileInput" accept=".csv" style="display: none;" onchange="handleCSVFileSelect(this)">
                        <button onclick="document.getElementById('csvFileInput').click()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                            Select CSV File
                        </button>
                    </div>
                    
                    <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #1d4ed8; display: flex; align-items: center; gap: 8px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                            CSV Format Requirements
                        </h4>
                        <p style="margin: 0; color: #1e40af; font-size: 0.9em;">
                            Required columns: <strong>first_name, last_name, email</strong><br>
                            Optional: phone, company_name, source, status, notes
                        </p>
                    </div>
                    
                    <button onclick="downloadSampleCSV()" style="background: white; color: #667eea; border: 2px solid #667eea; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: 500;">
                        📥 Download Sample CSV Template
                    </button>
                </div>
                
                <!-- Step 2: Preview -->
                <div id="importStep2" style="display: none;">
                    <div style="margin-bottom: 15px;">
                        <span id="csvFileName" style="font-weight: 600; color: #1e293b;"></span>
                        <span id="csvRowCount" style="color: #64748b; margin-left: 10px;"></span>
                    </div>
                    
                    <div style="max-height: 300px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 20px;">
                        <table id="csvPreviewTable" style="width: 100%; border-collapse: collapse; font-size: 0.85em;">
                            <thead id="csvPreviewHead" style="background: #f8fafc; position: sticky; top: 0;"></thead>
                            <tbody id="csvPreviewBody"></tbody>
                        </table>
                    </div>
                    
                    <div id="csvValidationErrors" style="display: none; background: #fef2f2; border: 1px solid #ef4444; border-radius: 8px; padding: 15px; margin-bottom: 15px; color: #991b1b;"></div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button onclick="resetImport()" style="flex: 1; background: white; color: #64748b; border: 1px solid #d1d5db; padding: 12px; border-radius: 8px; cursor: pointer;">
                            ← Back
                        </button>
                        <button id="importBtn" onclick="importLeadsFromCSV()" style="flex: 2; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                            Import <span id="importCount">0</span> Leads
                        </button>
                    </div>
                </div>
                
                <!-- Step 3: Progress -->
                <div id="importStep3" style="display: none; text-align: center; padding: 20px;">
                    <div class="spinner" style="width: 50px; height: 50px; border: 4px solid #e5e7eb; border-top-color: #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <h3 style="margin: 0 0 10px 0;">Importing Leads...</h3>
                    <p id="importProgress" style="color: #64748b;">0 of 0 imported</p>
                    <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 15px;">
                        <div id="importProgressBar" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: 0%; transition: width 0.3s;"></div>
                    </div>
                </div>
                
                <!-- Step 4: Complete -->
                <div id="importStep4" style="display: none; text-align: center; padding: 20px;">
                    <div style="width: 60px; height: 60px; background: #ecfdf5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    </div>
                    <h3 style="margin: 0 0 10px 0; color: #065f46;">Import Complete!</h3>
                    <p id="importResult" style="color: #64748b;"></p>
                    <button onclick="closeLeadImportModal(); loadLeads();" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; margin-top: 15px; font-weight: 600;">
                        View Leads
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add animation
    setTimeout(() => modal.classList.add('active'), 10);
};

window.closeLeadImportModal = function() {
    const modal = document.getElementById('leadImportModal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
};

// Store parsed CSV data
if (typeof window.parsedCSVData === 'undefined') {
    window.parsedCSVData = [];
}
var parsedCSVData = window.parsedCSVData;

window.handleCSVFileSelect = function(input) {
    const file = input.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        parseCSV(content, file.name);
    };
    reader.readAsText(file);
};

function parseCSV(content, fileName) {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 2) {
        showToast('CSV file is empty or has no data rows', 'error');
        return;
    }
    
    // Parse header
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
    
    // Check required columns
    const requiredColumns = ['first_name', 'last_name', 'email'];
    const missingColumns = requiredColumns.filter(col => !headers.includes(col));
    
    if (missingColumns.length > 0) {
        showToast(`Missing required columns: ${missingColumns.join(', ')}`, 'error');
        return;
    }
    
    // Parse data rows
    parsedCSVData = [];
    const errors = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length !== headers.length) continue;
        
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index]?.trim().replace(/['"]/g, '') || '';
        });
        
        // Validate email
        if (row.email && !isValidEmail(row.email)) {
            errors.push(`Row ${i}: Invalid email "${row.email}"`);
        }
        
        if (row.first_name && row.last_name && row.email) {
            parsedCSVData.push(row);
        }
    }
    
    // Show preview
    showCSVPreview(fileName, headers, errors);
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current);
    return result;
}

function showCSVPreview(fileName, headers, errors) {
    document.getElementById('importStep1').style.display = 'none';
    document.getElementById('importStep2').style.display = 'block';
    
    document.getElementById('csvFileName').textContent = fileName;
    document.getElementById('csvRowCount').textContent = `(${parsedCSVData.length} rows)`;
    document.getElementById('importCount').textContent = parsedCSVData.length;
    
    // Build preview table
    const thead = document.getElementById('csvPreviewHead');
    const tbody = document.getElementById('csvPreviewBody');
    
    thead.innerHTML = '<tr>' + headers.map(h => `<th style="padding: 10px; text-align: left; border-bottom: 2px solid #e5e7eb; white-space: nowrap;">${h}</th>`).join('') + '</tr>';
    
    tbody.innerHTML = parsedCSVData.slice(0, 10).map(row => 
        '<tr>' + headers.map(h => `<td style="padding: 8px 10px; border-bottom: 1px solid #f1f5f9;">${escapeHtml(row[h] || '-')}</td>`).join('') + '</tr>'
    ).join('');
    
    if (parsedCSVData.length > 10) {
        tbody.innerHTML += `<tr><td colspan="${headers.length}" style="padding: 10px; text-align: center; color: #64748b; font-style: italic;">... and ${parsedCSVData.length - 10} more rows</td></tr>`;
    }
    
    // Show errors if any
    const errorsDiv = document.getElementById('csvValidationErrors');
    if (errors.length > 0) {
        errorsDiv.style.display = 'block';
        errorsDiv.innerHTML = `<strong>⚠️ Warnings:</strong><br>${errors.slice(0, 5).join('<br>')}${errors.length > 5 ? `<br>... and ${errors.length - 5} more` : ''}`;
    } else {
        errorsDiv.style.display = 'none';
    }
}

window.resetImport = function() {
    document.getElementById('importStep1').style.display = 'block';
    document.getElementById('importStep2').style.display = 'none';
    document.getElementById('csvFileInput').value = '';
    parsedCSVData = [];
};

window.importLeadsFromCSV = async function() {
    if (parsedCSVData.length === 0) {
        showToast('No data to import', 'error');
        return;
    }
    
    document.getElementById('importStep2').style.display = 'none';
    document.getElementById('importStep3').style.display = 'block';
    
    let imported = 0;
    let failed = 0;
    const failedLeads = [];
    const total = parsedCSVData.length;
    
    for (let i = 0; i < parsedCSVData.length; i++) {
        const row = parsedCSVData[i];
        
        try {
            // Build lead_name from first_name + last_name
            const leadName = `${row.first_name || ''} ${row.last_name || ''}`.trim() || 'Unknown';
            
            const leadData = {
                lead_name: leadName,
                first_name: row.first_name || null,
                last_name: row.last_name || null,
                email: row.email || null,
                phone: row.phone || null,
                company_name: row.company_name || null,
                source: row.source || 'csv_import',
                status: row.status || 'new',
                notes: row.notes || null
            };
            
            const response = await fetch(`${API_BASE}/companies/${companyId}/leads`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(leadData)
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
                failedLeads.push({ name: leadName, email: row.email, reason: errorMsg });
            }
        } catch (error) {
            failed++;
            failedLeads.push({ name: `${row.first_name} ${row.last_name}`, email: row.email, reason: 'Network error' });
        }
        
        // Update progress
        const progress = Math.round(((i + 1) / total) * 100);
        document.getElementById('importProgress').textContent = `${i + 1} of ${total} processed`;
        document.getElementById('importProgressBar').style.width = `${progress}%`;
    }
    
    // Show complete
    document.getElementById('importStep3').style.display = 'none';
    document.getElementById('importStep4').style.display = 'block';
    
    let resultHtml = `<strong>${imported}</strong> leads imported successfully`;
    if (failed > 0) {
        resultHtml += `<br><span style="color: #ef4444;">${failed} failed</span>`;
        resultHtml += `<div style="margin-top:10px;text-align:left;max-height:150px;overflow-y:auto;font-size:12px;background:#fef2f2;padding:10px;border-radius:8px;">`;
        resultHtml += `<strong>Failed leads:</strong><br>`;
        failedLeads.forEach(fl => {
            resultHtml += `• ${fl.name} (${fl.email}): <span style="color:#dc2626">${fl.reason}</span><br>`;
        });
        resultHtml += `</div>`;
    }
    document.getElementById('importResult').innerHTML = resultHtml;
};

window.downloadSampleCSV = function() {
    const sampleData = `first_name,last_name,email,phone,company_name,source,status,notes
John,Doe,john.doe@example.com,+91 98765 43210,ABC Corp,website,new,Interested in our services
Jane,Smith,jane.smith@example.com,+91 87654 32109,XYZ Ltd,referral,contacted,Follow up next week
Rahul,Sharma,rahul@example.com,+91 76543 21098,Tech Solutions,social_media,qualified,Hot lead`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'lead_import_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
};

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ============================================
// Lead Score Visual Meter
// ============================================

// ============================================
// Bulk Actions Functionality
// ============================================

let selectedLeadIds = [];

window.toggleSelectAllLeads = function(checkbox) {
    const checkboxes = document.querySelectorAll('.lead-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkSelection();
};

window.updateBulkSelection = function() {
    const checkboxes = document.querySelectorAll('.lead-checkbox:checked');
    selectedLeadIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
    
    const bulkBar = document.getElementById('bulkActionsBar');
    const countSpan = document.getElementById('selectedCount');
    
    if (selectedLeadIds.length > 0) {
        bulkBar.style.display = 'flex';
        countSpan.textContent = `${selectedLeadIds.length} selected`;
    } else {
        bulkBar.style.display = 'none';
    }
    
    // Update select all checkbox state
    const allCheckboxes = document.querySelectorAll('.lead-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllLeads');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = allCheckboxes.length > 0 && selectedLeadIds.length === allCheckboxes.length;
        selectAllCheckbox.indeterminate = selectedLeadIds.length > 0 && selectedLeadIds.length < allCheckboxes.length;
    }
};

window.clearBulkSelection = function() {
    const checkboxes = document.querySelectorAll('.lead-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    
    const selectAllCheckbox = document.getElementById('selectAllLeads');
    if (selectAllCheckbox) selectAllCheckbox.checked = false;
    
    selectedLeadIds = [];
    document.getElementById('bulkActionsBar').style.display = 'none';
};

window.bulkUpdateStatus = async function(newStatus) {
    if (selectedLeadIds.length === 0) {
        showToast('No leads selected', 'warning');
        return;
    }
    
    const statusLabels = {
        'contacted': 'Contacted',
        'qualified': 'Qualified',
        'converted': 'Converted',
        'lost': 'Lost'
    };
    
    showDeleteConfirmModal(
        'Bulk Update Status',
        `Are you sure you want to mark ${selectedLeadIds.length} lead(s) as "${statusLabels[newStatus] || newStatus}"?`,
        async () => {
            let success = 0;
            let failed = 0;
            
            for (const leadId of selectedLeadIds) {
                try {
                    const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}`, {
                        method: 'PUT',
                        headers: getHeaders(),
                        body: JSON.stringify({ status: newStatus })
                    });
                    
                    if (response.ok) {
                        success++;
                    } else {
                        failed++;
                    }
                } catch (error) {
                    failed++;
                }
            }
            
            showToast(`${success} lead(s) updated${failed > 0 ? `, ${failed} failed` : ''}`, success > 0 ? 'success' : 'error');
            clearBulkSelection();
            loadLeads();
        },
        'Update',
        'btn-primary'
    );
};

window.bulkDeleteLeads = async function() {
    if (selectedLeadIds.length === 0) {
        showToast('No leads selected', 'warning');
        return;
    }
    
    showDeleteConfirmModal(
        'Delete Multiple Leads',
        `Are you sure you want to delete ${selectedLeadIds.length} lead(s)? This action cannot be undone.`,
        async () => {
            let success = 0;
            let failed = 0;
            
            for (const leadId of selectedLeadIds) {
                try {
                    const response = await fetch(`${API_BASE}/companies/${companyId}/leads/${leadId}`, {
                        method: 'DELETE',
                        headers: getHeaders()
                    });
                    
                    if (response.ok) {
                        success++;
                    } else {
                        failed++;
                    }
                } catch (error) {
                    failed++;
                }
            }
            
            showToast(`${success} lead(s) deleted${failed > 0 ? `, ${failed} failed` : ''}`, success > 0 ? 'success' : 'error');
            clearBulkSelection();
            loadLeads();
        },
        'Delete',
        'btn-danger'
    );
};

function renderLeadScoreMeter(score) {
    const numScore = parseInt(score) || 0;
    
    // Determine score category
    let category, color, bgColor, icon, label;
    
    if (numScore >= 80) {
        category = 'very-hot';
        color = '#dc2626';
        bgColor = '#fef2f2';
        icon = '🔥🔥';
        label = 'Very Hot';
    } else if (numScore >= 60) {
        category = 'hot';
        color = '#ea580c';
        bgColor = '#fff7ed';
        icon = '🔥';
        label = 'Hot';
    } else if (numScore >= 40) {
        category = 'warm';
        color = '#d97706';
        bgColor = '#fffbeb';
        icon = '🌤️';
        label = 'Warm';
    } else if (numScore >= 20) {
        category = 'cool';
        color = '#0284c7';
        bgColor = '#f0f9ff';
        icon = '❄️';
        label = 'Cool';
    } else {
        category = 'cold';
        color = '#64748b';
        bgColor = '#f8fafc';
        icon = '🥶';
        label = 'Cold';
    }
    
    return `
        <div class="lead-score-meter" title="${label} Lead - Score: ${numScore}/100" style="
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            min-width: 70px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 0.75em;
                color: ${color};
                font-weight: 600;
            ">
                <span>${icon}</span>
                <span>${numScore}</span>
            </div>
            <div style="
                width: 60px;
                height: 6px;
                background: #e5e7eb;
                border-radius: 3px;
                overflow: hidden;
            ">
                <div style="
                    width: ${numScore}%;
                    height: 100%;
                    background: linear-gradient(90deg, ${color}88, ${color});
                    border-radius: 3px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <span style="
                font-size: 0.65em;
                color: ${color};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">${label}</span>
        </div>
    `;
}
