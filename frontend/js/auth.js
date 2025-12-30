// Authentication Functions

// Check Authentication
function checkAuth() {
    if (!authToken) {
        loadPage('home');
        return;
    }
    
    if (!companyId) {
        loadPage('company-selection');
        return;
    }
    
    // Preserve current page on refresh - check URL hash first
    const hash = window.location.hash.replace('#', '');
    const savedPage = localStorage.getItem('currentPage');
    
    // Priority: URL hash > saved page > dashboard
    let targetPage = 'dashboard';
    
    // All valid pages that should persist on refresh
    const validPages = ['dashboard', 'customers', 'contacts', 'leads', 'deals', 'tasks', 'activities', 'admin', 'permissions', 'accountreport'];
    
    if (hash && validPages.includes(hash)) {
        targetPage = hash;
    } else if (savedPage && validPages.includes(savedPage)) {
        targetPage = savedPage;
    }
    
    loadPage(targetPage);
    
    // Update URL hash
    if (hash !== targetPage) {
        window.location.hash = targetPage;
    }
}

// Login Handler
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            const token = data.data.access_token;
            if (typeof setAuthToken === 'function') {
                setAuthToken(token);
            } else {
                authToken = token;
                localStorage.setItem('authToken', token);
            }
            currentUser = data.data.user;
            if (currentUser) {
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
            }
            // Update user email in navbar if it exists
            const userEmailEl = document.getElementById('userEmail');
            if (userEmailEl) {
                userEmailEl.textContent = currentUser.email;
            }
            // Load company selection page
            loadPage('company-selection');
        } else {
            errorDiv.textContent = data.detail || 'Login failed';
            errorDiv.classList.add('show');
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error. Is server running?';
        errorDiv.classList.add('show');
    }
}

// Load Companies (for company selection page)
window.loadCompanies = async function() {
    try {
        const response = await fetch(`${API_BASE}/companies`, {
            headers: getHeaders()
        });
        const data = await response.json();

        if (response.ok) {
            // Support both element IDs
            const companyList = document.getElementById('companyListPage') || document.getElementById('companyList');
            if (!companyList) {
                console.error('Company list element not found');
                return;
            }
            
            companyList.innerHTML = '';

            if (!data.data || data.data.length === 0) {
                companyList.innerHTML = '<p>No companies found. Please create one via API.</p>';
                return;
            }

            data.data.forEach(company => {
                const div = document.createElement('div');
                div.className = 'company-item';
                div.innerHTML = `
                    <h3>${company.name}</h3>
                    <p>${company.email || 'No email'}</p>
                `;
                div.onclick = () => selectCompany(company.id);
                companyList.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading companies:', error);
    }
};

// Select Company
window.selectCompany = function(id) {
    if (typeof setCompanyId === 'function') {
        setCompanyId(id);
    } else {
        companyId = id;
        localStorage.setItem('companyId', id);
    }
    loadPage('dashboard');
};

// Logout Handler
window.logout = function() {
    // Clear ALL localStorage items related to auth
    localStorage.removeItem('authToken');
    localStorage.removeItem('companyId');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentPage');
    
    // Clear session storage too
    sessionStorage.clear();
    
    // Clear global variables
    if (typeof window.authToken !== 'undefined') window.authToken = null;
    if (typeof window.companyId !== 'undefined') window.companyId = null;
    if (typeof window.currentUser !== 'undefined') window.currentUser = null;
    
    // Use setters if available
    if (typeof setAuthToken === 'function') setAuthToken(null);
    if (typeof setCompanyId === 'function') setCompanyId(null);
    
    // Clear URL hash
    window.location.hash = '';
    
    // Redirect to VEGA CRM website login page (not app)
    window.location.href = '/website/login.html';
};

// Show/Hide Modals
function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
    }
}

function hideLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function showCompanyModal() {
    const modal = document.getElementById('companyModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        // Load companies when modal is shown
        loadCompanies();
    }
}

function hideCompanyModal() {
    const modal = document.getElementById('companyModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

function hideModals() {
    hideLoginModal();
    hideCompanyModal();
}

