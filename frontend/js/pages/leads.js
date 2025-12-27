// Leads Page JavaScript

// Global variable for editing lead ID
if (typeof window.currentEditingLeadId === 'undefined') {
    window.currentEditingLeadId = null;
}

function initLeads() {
    // Check auth before loading
    if (!authToken || !companyId) {
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

        const table = document.getElementById('leadsTable');
        if (!table) return;

        // Initialize DataTable
        if (window.leadsTable && typeof window.leadsTable.updateData === 'function') {
            window.leadsTable.updateData(leads);
        } else {
            window.leadsTable = new DataTable('leadsTable', {
                data: leads,
                columns: [
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
                        render: (value) => {
                            return value !== null && value !== undefined ? value : '-';
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
                            return `
                                <button class="btn-icon btn-edit" onclick="editLead(${row.id})" title="Edit">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </button>
                                <button class="btn-icon btn-delete" onclick="deleteLead(${row.id})" title="Delete">
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
    if (!confirm('Are you sure you want to delete this lead? This action cannot be undone.')) {
        return;
    }
    
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
            if (typeof showNotification === 'function') {
                showNotification('Lead deleted successfully!', 'success');
            }
        } else {
            const result = await response.json();
            alert(result.detail || 'Failed to delete lead');
        }
    } catch (error) {
        console.error('Error deleting lead:', error);
        alert('Connection error. Please try again.');
    }
};

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
