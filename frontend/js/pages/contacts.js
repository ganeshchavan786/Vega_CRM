// Contacts Page JavaScript

// Use window object to avoid redeclaration errors when script loads multiple times
if (typeof window.currentEditingContactId === 'undefined') {
    window.currentEditingContactId = null;
}

// Cache for accounts list
if (typeof window.contactsAccountsList === 'undefined') {
    window.contactsAccountsList = [];
}

function initContacts() {
    // Check if we have valid auth before loading
    if (!authToken || !companyId) {
        console.warn('No auth token or company ID - skipping contact load');
        const table = document.getElementById('contactsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    loadAccountsForContacts();
    loadContacts();
}

async function loadAccountsForContacts() {
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/customers?page=1&per_page=100`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            window.contactsAccountsList = data.data || [];
            
            // Populate account filter dropdown
            const accountFilter = document.getElementById('contactAccountFilter');
            if (accountFilter) {
                const currentValue = accountFilter.value;
                accountFilter.innerHTML = '<option value="">All Accounts</option>' +
                    window.contactsAccountsList.map(account => 
                        `<option value="${account.id}" ${account.id == currentValue ? 'selected' : ''}>${escapeHtml(account.name)}</option>`
                    ).join('');
            }
        }
    } catch (error) {
        console.error('Error loading accounts for contacts:', error);
    }
}

window.loadContacts = async function() {
    // Check auth before making API call
    if (!authToken || !companyId) {
        console.warn('Cannot load contacts: No auth token or company ID');
        const table = document.getElementById('contactsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Please login and select a company</h3></div>';
        }
        return;
    }
    
    const search = document.getElementById('contactSearch')?.value || '';
    const accountId = document.getElementById('contactAccountFilter')?.value || '';
    
    try {
        let url = `${API_BASE}/companies/${companyId}/contacts?page=1&per_page=50`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (accountId) url += `&account_id=${encodeURIComponent(accountId)}`;

        const response = await fetch(url, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            console.warn('401 Unauthorized when loading contacts');
            const table = document.getElementById('contactsTable');
            if (table) {
                table.innerHTML = '<div class="empty-state"><h3>Session expired. Please login again.</h3></div>';
            }
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        const data = await response.json();

        const table = document.getElementById('contactsTable');
        if (!table) return;

        if (data.data && data.data.length > 0) {
            table.innerHTML = `
                <table class="table-advanced">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Job Title</th>
                            <th>Role</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Account</th>
                            <th>Primary</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(contact => `
                            <tr>
                                <td><strong>${escapeHtml(contact.name || '-')}</strong></td>
                                <td>${escapeHtml(contact.job_title || '-')}</td>
                                <td><span class="badge badge-secondary">${escapeHtml(contact.role ? contact.role.replace('_', ' ').toUpperCase() : '-')}</span></td>
                                <td>${escapeHtml(contact.email || '-')}</td>
                                <td>${escapeHtml(contact.phone || '-')}</td>
                                <td>${contact.account ? escapeHtml(contact.account.name) : '-'}</td>
                                <td>${contact.is_primary_contact ? '<span class="badge badge-green">Primary</span>' : '-'}</td>
                                <td>
                                    <button class="btn-icon btn-edit" onclick="editContact(${contact.id})" title="Edit">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M11.333 2.00001C11.5084 1.82465 11.7163 1.68571 11.9447 1.59203C12.1731 1.49835 12.4173 1.4519 12.6637 1.45564C12.9101 1.45938 13.1533 1.51324 13.3787 1.6139C13.6041 1.71456 13.8072 1.8598 13.9767 2.04134C14.1462 2.22288 14.2786 2.43706 14.3665 2.67078C14.4544 2.9045 14.4961 3.15326 14.4893 3.40289C14.4825 3.65252 14.4273 3.89824 14.3267 4.12567C14.2261 4.3531 14.0821 4.55767 13.9027 4.72801L13.333 5.33334L10.6667 2.66668L11.2363 2.06134C11.4157 1.891 11.6188 1.74576 11.8442 1.6451C12.0696 1.54444 12.3128 1.49058 12.5592 1.48684C12.8056 1.4831 13.0498 1.52955 13.2782 1.62323C13.5066 1.71691 13.7145 1.85585 13.8898 2.03121L13.333 2.66668L11.333 2.00001Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                            <path d="M9.33333 4L2.66667 10.6667V13.3333H5.33333L12 6.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                    <button class="btn-icon btn-delete" onclick="deleteContact(${contact.id})" title="Delete">
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
            table.innerHTML = '<div class="empty-state"><h3>No contacts found</h3><p>Create your first contact!</p></div>';
        }
    } catch (error) {
        console.error('Error loading contacts:', error);
        const table = document.getElementById('contactsTable');
        if (table) {
            table.innerHTML = '<div class="empty-state"><h3>Error loading contacts</h3><p>Please try again</p></div>';
        }
    }
};

window.showContactForm = function() {
    console.log('showContactForm called');
    window.currentEditingContactId = null;
    
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found');
        alert('Form elements not found. Please refresh the page.');
        return;
    }
    
    try {
        openContactModal();
    } catch (error) {
        console.error('Error in showContactForm:', error);
        alert('Error opening contact form: ' + error.message);
    }
};

window.editContact = async function(id) {
    console.log('editContact called with id:', id);
    window.currentEditingContactId = id;
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/contacts/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            console.error('Failed to load contact data, status:', response.status);
            alert('Failed to load contact data');
            return;
        }
        
        const result = await response.json();
        const contact = result.data || result;
        console.log('Contact data loaded:', contact);
        
        openContactModal(contact);
    } catch (error) {
        console.error('Error loading contact:', error);
        alert('Error loading contact data: ' + error.message);
    }
};

window.openContactModal = function(contact = null) {
    console.log('openContactModal called, contact:', contact);
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (!modal || !formContent) {
        console.error('Modal elements not found!');
        alert('Form modal not found. Please refresh the page.');
        return;
    }
    
    const isEdit = !!contact;
    const title = isEdit ? 'Edit Contact' : 'Add Contact';
    
    formContent.innerHTML = `
        <div class="form-modal-header">
            <h2>${title}</h2>
            <button class="btn-close-modal" onclick="closeFormModal()">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
        <form id="contactForm" class="form-advanced" onsubmit="handleContactSubmit(event)">
            <div class="form-section-advanced">
                <h3 class="form-section-title">Basic Information</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Contact Name <span class="required">*</span></label>
                        <input type="text" id="contactName" class="form-input-advanced" value="${contact?.name || ''}" required>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Job Title</label>
                        <input type="text" id="contactJobTitle" class="form-input-advanced" value="${contact?.job_title || ''}" placeholder="Manager">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Role</label>
                        <select id="contactRole" class="form-select-advanced">
                            <option value="">Select Role</option>
                            <option value="decision_maker" ${contact?.role === 'decision_maker' ? 'selected' : ''}>Decision Maker</option>
                            <option value="influencer" ${contact?.role === 'influencer' ? 'selected' : ''}>Influencer</option>
                            <option value="user" ${contact?.role === 'user' ? 'selected' : ''}>User</option>
                            <option value="gatekeeper" ${contact?.role === 'gatekeeper' ? 'selected' : ''}>Gatekeeper</option>
                            <option value="champion" ${contact?.role === 'champion' ? 'selected' : ''}>Champion</option>
                            <option value="economic_buyer" ${contact?.role === 'economic_buyer' ? 'selected' : ''}>Economic Buyer</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Email</label>
                        <input type="email" id="contactEmail" class="form-input-advanced" value="${contact?.email || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Phone</label>
                        <input type="tel" id="contactPhone" class="form-input-advanced" value="${contact?.phone || ''}">
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Account <span class="required">*</span></label>
                        <select id="contactAccountId" class="form-select-advanced" required>
                            <option value="">Select Account</option>
                            ${window.contactsAccountsList.map(account => 
                                `<option value="${account.id}" ${contact?.account_id === account.id ? 'selected' : ''}>${escapeHtml(account.name)}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-section-advanced">
                <h3 class="form-section-title">Communication & Influence</h3>
                <div class="form-group-grid">
                    <div class="form-group-advanced">
                        <label class="form-label">Preferred Channel</label>
                        <select id="contactPreferredChannel" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="email" ${contact?.preferred_channel === 'email' ? 'selected' : ''}>Email</option>
                            <option value="whatsapp" ${contact?.preferred_channel === 'whatsapp' ? 'selected' : ''}>WhatsApp</option>
                            <option value="phone" ${contact?.preferred_channel === 'phone' ? 'selected' : ''}>Phone</option>
                            <option value="sms" ${contact?.preferred_channel === 'sms' ? 'selected' : ''}>SMS</option>
                            <option value="linkedin" ${contact?.preferred_channel === 'linkedin' ? 'selected' : ''}>LinkedIn</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">Influence Score</label>
                        <select id="contactInfluenceScore" class="form-select-advanced">
                            <option value="">Select</option>
                            <option value="high" ${contact?.influence_score === 'high' ? 'selected' : ''}>High</option>
                            <option value="medium" ${contact?.influence_score === 'medium' ? 'selected' : ''}>Medium</option>
                            <option value="low" ${contact?.influence_score === 'low' ? 'selected' : ''}>Low</option>
                        </select>
                    </div>
                    <div class="form-group-advanced">
                        <label class="form-label">
                            <input type="checkbox" id="contactIsPrimary" ${contact?.is_primary_contact ? 'checked' : ''} style="margin-right: 8px;">
                            Primary Contact
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeFormModal()">Cancel</button>
                <button type="submit" class="btn-primary">${isEdit ? 'Update' : 'Create'} Contact</button>
            </div>
        </form>
    `;
    
    modal.classList.add('active');
    console.log('Modal opened successfully');
};

window.handleContactSubmit = async function(event) {
    event.preventDefault();
    
    const accountId = document.getElementById('contactAccountId').value;
    if (!accountId) {
        alert('Please select an account');
        return;
    }
    
    const contactData = {
        name: document.getElementById('contactName').value,
        job_title: document.getElementById('contactJobTitle').value || null,
        role: document.getElementById('contactRole').value || null,
        email: document.getElementById('contactEmail').value || null,
        phone: document.getElementById('contactPhone').value || null,
        account_id: parseInt(accountId),
        preferred_channel: document.getElementById('contactPreferredChannel').value || null,
        influence_score: document.getElementById('contactInfluenceScore').value || null,
        is_primary_contact: document.getElementById('contactIsPrimary').checked
    };
    
    try {
        const isEdit = !!window.currentEditingContactId;
        const url = isEdit 
            ? `${API_BASE}/companies/${companyId}/contacts/${window.currentEditingContactId}`
            : `${API_BASE}/companies/${companyId}/contacts`;
        
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                ...getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contactData)
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.detail || 'Failed to save contact');
            return;
        }
        
        const result = await response.json();
        console.log('Contact saved:', result);
        
        closeFormModal();
        loadContacts();
        loadAccountsForContacts(); // Refresh account list
    } catch (error) {
        console.error('Error saving contact:', error);
        alert('Error saving contact: ' + error.message);
    }
};

window.deleteContact = async function(id) {
    if (!confirm('Are you sure you want to delete this contact?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}/contacts/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            if (typeof handle401Error === 'function') {
                handle401Error();
            }
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.detail || 'Failed to delete contact');
            return;
        }
        
        loadContacts();
    } catch (error) {
        console.error('Error deleting contact:', error);
        alert('Error deleting contact: ' + error.message);
    }
};

// Make init function global
window.initContacts = initContacts;

