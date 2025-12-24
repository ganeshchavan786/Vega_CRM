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
    
    if (hash && ['dashboard', 'customers', 'leads', 'deals', 'tasks', 'activities'].includes(hash)) {
        targetPage = hash;
    } else if (savedPage && ['dashboard', 'customers', 'leads', 'deals', 'tasks', 'activities'].includes(savedPage)) {
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
            const companyList = document.getElementById('companyListPage');
            if (!companyList) return;
            
            companyList.innerHTML = '';

            if (data.data.length === 0) {
                companyList.innerHTML = '<p>No companies found. Please create one via API.</p>';
                return;
            }

            data.data.forEach(company => {
                const div = document.createElement('div');
                div.className = 'company-item';
                div.innerHTML = `
                    <h3>${company.name}</h3>
                    <p>${company.email}</p>
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

// Logout - Make sure it's globally accessible
window.handleLogout = function() {
    console.log('handleLogout called');
    
    // Clear auth token
    if (typeof setAuthToken === 'function') {
        setAuthToken(null);
    } else {
        if (typeof window.authToken !== 'undefined') {
            window.authToken = null;
        }
        localStorage.removeItem('authToken');
    }
    
    // Clear company ID
    if (typeof setCompanyId === 'function') {
        setCompanyId(null);
    } else {
        if (typeof window.companyId !== 'undefined') {
            window.companyId = null;
        }
        localStorage.removeItem('companyId');
    }
    
    // Clear user data
    if (typeof window.currentUser !== 'undefined') {
        window.currentUser = null;
    }
    localStorage.removeItem('currentUser');
    
    // Hide navigation
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
        navbarContainer.style.display = 'none';
    }
    
    // Close sidebar if open
    const sidebarMenu = document.getElementById('sidebarMenu');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarMenu) sidebarMenu.classList.remove('active');
    if (sidebarOverlay) sidebarOverlay.classList.remove('active');
    
    // Load home page
    if (typeof loadPage === 'function') {
        loadPage('home');
    } else if (typeof window.loadPage === 'function') {
        window.loadPage('home');
    } else {
        window.location.href = 'index.html';
    }
};

// Show/Hide Modals
function showLoginModal() {
    document.getElementById('loginModal').classList.add('active');
}

function hideLoginModal() {
    document.getElementById('loginModal').classList.remove('active');
}

function showCompanyModal() {
    document.getElementById('companyModal').classList.add('active');
}

function hideCompanyModal() {
    document.getElementById('companyModal').classList.remove('active');
}

function hideModals() {
    hideLoginModal();
    hideCompanyModal();
}

