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
        const response = await fetch(`${API_BASE}/companies`, {
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

