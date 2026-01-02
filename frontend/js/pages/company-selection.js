// Company Selection Page JavaScript

let allCompanies = [];

function initCompanySelection() {
    loadCompanies();
}

// Also support camelCase
function initCompanyselection() {
    loadCompanies();
}

// Load Companies with Advanced UI
window.loadCompanies = async function() {
    const companyList = document.getElementById('companyListPage');
    const loadingDiv = document.getElementById('companyLoading');
    const emptyDiv = document.getElementById('companyEmpty');
    const errorDiv = document.getElementById('companyErrorPage');
    
    if (!companyList) return;
    
    // Show loading
    if (loadingDiv) loadingDiv.style.display = 'flex';
    if (emptyDiv) emptyDiv.style.display = 'none';
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }
    companyList.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/companies?per_page=500`, {
            headers: getHeaders()
        });
        const data = await response.json();

        if (response.ok) {
            allCompanies = data.data || [];
            
            // Hide loading
            if (loadingDiv) loadingDiv.style.display = 'none';
            
            if (allCompanies.length === 0) {
                // Show empty state
                if (emptyDiv) emptyDiv.style.display = 'block';
                return;
            }
            
            // Render companies
            renderCompanies(allCompanies);
        } else {
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (errorDiv) {
                errorDiv.textContent = data.detail || 'Failed to load companies';
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    }
};

// Render Companies with Advanced Cards
function renderCompanies(companies) {
    const companyList = document.getElementById('companyListPage');
    if (!companyList) return;
    
    companyList.innerHTML = companies.map(company => `
        <div class="company-card-advanced" onclick="selectCompany(${company.id})">
            <div class="company-card-header">
                <div class="company-icon">
                    <span>${company.name.charAt(0).toUpperCase()}</span>
                </div>
                <div class="company-info">
                    <h3>${company.name}</h3>
                    <p class="company-email">${company.email || 'No email'}</p>
                </div>
                <div class="company-select-icon">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
            <div class="company-card-footer">
                <span class="company-badge">Active</span>
                <span class="company-id">ID: ${company.id}</span>
            </div>
        </div>
    `).join('');
}

// Filter Companies
window.filterCompanies = function() {
    const searchInput = document.getElementById('companySearchInput');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase().trim();
    const emptyDiv = document.getElementById('companyEmpty');
    
    if (searchTerm === '') {
        renderCompanies(allCompanies);
        if (emptyDiv && allCompanies.length > 0) {
            emptyDiv.style.display = 'none';
        }
        return;
    }
    
    const filtered = allCompanies.filter(company => 
        company.name.toLowerCase().includes(searchTerm) ||
        (company.email && company.email.toLowerCase().includes(searchTerm))
    );
    
    renderCompanies(filtered);
    
    // Show empty if no results
    if (emptyDiv) {
        emptyDiv.style.display = filtered.length === 0 ? 'block' : 'none';
    }
};

// Show Create Company Modal
window.showCreateCompanyModal = function() {
    // Remove existing modal if any
    const existingModal = document.getElementById('createCompanyModal');
    if (existingModal) existingModal.remove();
    
    // Create modal HTML
    const modal = document.createElement('div');
    modal.id = 'createCompanyModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        backdrop-filter: blur(4px);
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 480px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
            animation: modalSlideIn 0.3s ease;
        ">
            <!-- Header -->
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 24px;
                color: white;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="
                            width: 48px;
                            height: 48px;
                            background: rgba(255,255,255,0.2);
                            border-radius: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 24px;
                        ">🏢</div>
                        <div>
                            <h2 style="margin: 0; font-size: 20px; font-weight: 600;">Create New Company</h2>
                            <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">Set up your workspace</p>
                        </div>
                    </div>
                    <button onclick="closeCreateCompanyModal()" style="
                        background: rgba(255,255,255,0.2);
                        border: none;
                        width: 36px;
                        height: 36px;
                        border-radius: 8px;
                        color: white;
                        font-size: 20px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">&times;</button>
                </div>
            </div>
            
            <!-- Form -->
            <form id="createCompanyForm" onsubmit="handleCreateCompany(event)" style="padding: 24px;">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 14px;">
                        Company Name <span style="color: #ef4444;">*</span>
                    </label>
                    <input type="text" id="companyName" placeholder="e.g., Acme Corporation" required style="
                        width: 100%;
                        padding: 12px 16px;
                        border: 2px solid #e5e7eb;
                        border-radius: 10px;
                        font-size: 15px;
                        box-sizing: border-box;
                        transition: border-color 0.2s, box-shadow 0.2s;
                        outline: none;
                    " onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102,126,234,0.1)'" onblur="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none'">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 14px;">
                        Company Email
                    </label>
                    <input type="email" id="companyEmail" placeholder="contact@company.com" style="
                        width: 100%;
                        padding: 12px 16px;
                        border: 2px solid #e5e7eb;
                        border-radius: 10px;
                        font-size: 15px;
                        box-sizing: border-box;
                        transition: border-color 0.2s, box-shadow 0.2s;
                        outline: none;
                    " onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102,126,234,0.1)'" onblur="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none'">
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                    <div>
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 14px;">
                            Phone
                        </label>
                        <input type="tel" id="companyPhone" placeholder="+91 98765 43210" style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e5e7eb;
                            border-radius: 10px;
                            font-size: 15px;
                            box-sizing: border-box;
                            transition: border-color 0.2s;
                            outline: none;
                        " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 14px;">
                            Website
                        </label>
                        <input type="url" id="companyWebsite" placeholder="www.company.com" style="
                            width: 100%;
                            padding: 12px 16px;
                            border: 2px solid #e5e7eb;
                            border-radius: 10px;
                            font-size: 15px;
                            box-sizing: border-box;
                            transition: border-color 0.2s;
                            outline: none;
                        " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'">
                    </div>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 14px;">
                        Address
                    </label>
                    <textarea id="companyAddress" rows="2" placeholder="Enter company address" style="
                        width: 100%;
                        padding: 12px 16px;
                        border: 2px solid #e5e7eb;
                        border-radius: 10px;
                        font-size: 15px;
                        box-sizing: border-box;
                        resize: none;
                        font-family: inherit;
                        transition: border-color 0.2s;
                        outline: none;
                    " onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#e5e7eb'"></textarea>
                </div>
                
                <div id="createCompanyError" style="
                    color: #dc2626;
                    background: #fef2f2;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    font-size: 14px;
                    display: none;
                "></div>
                
                <!-- Buttons -->
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button type="button" onclick="closeCreateCompanyModal()" style="
                        padding: 12px 24px;
                        border: 2px solid #e5e7eb;
                        background: white;
                        border-radius: 10px;
                        cursor: pointer;
                        font-size: 15px;
                        font-weight: 500;
                        color: #64748b;
                        transition: all 0.2s;
                    " onmouseover="this.style.borderColor='#cbd5e1'; this.style.background='#f8fafc'" onmouseout="this.style.borderColor='#e5e7eb'; this.style.background='white'">Cancel</button>
                    <button type="submit" id="createCompanyBtn" style="
                        padding: 12px 28px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        font-size: 15px;
                        font-weight: 600;
                        transition: all 0.2s;
                        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
                    " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.5)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 14px rgba(102, 126, 234, 0.4)'">
                        <span class="btn-text">Create Company</span>
                        <span class="btn-loading" style="display: none;">Creating...</span>
                    </button>
                </div>
            </form>
        </div>
    `;
    
    // Add animation keyframes
    if (!document.getElementById('modalAnimationStyles')) {
        const style = document.createElement('style');
        style.id = 'modalAnimationStyles';
        style.textContent = `
            @keyframes modalSlideIn {
                from { opacity: 0; transform: scale(0.95) translateY(-10px); }
                to { opacity: 1; transform: scale(1) translateY(0); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeCreateCompanyModal();
    });
    
    // Focus first input
    setTimeout(() => document.getElementById('companyName')?.focus(), 100);
};

// Close Create Company Modal
window.closeCreateCompanyModal = function() {
    const modal = document.getElementById('createCompanyModal');
    if (modal) {
        modal.remove();
    }
};

// Handle Create Company Form Submit
window.handleCreateCompany = async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('companyName')?.value.trim();
    const email = document.getElementById('companyEmail')?.value.trim();
    const phone = document.getElementById('companyPhone')?.value.trim();
    const address = document.getElementById('companyAddress')?.value.trim();
    const errorDiv = document.getElementById('createCompanyError');
    const submitBtn = document.getElementById('createCompanyBtn');
    
    if (!name) {
        if (errorDiv) {
            errorDiv.textContent = 'Company name is required';
            errorDiv.classList.add('show');
        }
        return;
    }
    
    // Show loading
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').style.display = 'none';
        submitBtn.querySelector('.btn-loading').style.display = 'inline';
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getHeaders()
            },
            body: JSON.stringify({
                name,
                email: email || null,
                phone: phone || null,
                address: address || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Close modal
            closeCreateCompanyModal();
            
            // Show success message
            alert('Company created successfully!');
            
            // Reload companies list
            loadCompanies();
        } else {
            if (errorDiv) {
                errorDiv.textContent = data.detail || 'Failed to create company';
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        console.error('Error creating company:', error);
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.add('show');
        }
    } finally {
        // Hide loading
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').style.display = 'inline';
            submitBtn.querySelector('.btn-loading').style.display = 'none';
        }
    }
};

