// Navigation Functions

// Load Navigation Bar
async function loadNavigation() {
    try {
        const navbarContainer = document.getElementById('navbar-container');
        if (!navbarContainer) {
            console.error('Navbar container not found');
            return;
        }
        
        const response = await fetch('components/navbar.html');
        if (!response.ok) {
            console.error('Failed to load navbar HTML');
            return;
        }
        
        const html = await response.text();
        navbarContainer.innerHTML = html;
        
        // Ensure navbar is visible - force display
        navbarContainer.style.display = 'block';
        navbarContainer.style.visibility = 'visible';
        navbarContainer.style.opacity = '1';
        navbarContainer.style.position = 'relative';
        navbarContainer.style.zIndex = '1000';
        navbarContainer.style.background = '#0052CC';
        navbarContainer.style.minHeight = '56px';
        
        // Also ensure the nav element itself is visible
        const navElement = navbarContainer.querySelector('.navbar-advanced, .navbar');
        if (navElement) {
            navElement.style.display = 'block';
            navElement.style.visibility = 'visible';
            navElement.style.background = 'linear-gradient(135deg, #0052CC 0%, #0065FF 100%)';
            navElement.style.backgroundColor = '#0052CC';
            navElement.style.width = '100%';
            navElement.style.minHeight = '56px';
        }
        
        // Force container background
        const navContainer = navbarContainer.querySelector('.nav-container-advanced, .nav-container');
        if (navContainer) {
            navContainer.style.display = 'flex';
            navContainer.style.visibility = 'visible';
        }
        
        // Setup navigation event listeners
        setupNavListeners();
        
        // Load current company name after navigation is set up
        setTimeout(() => {
            loadCurrentCompany();
        }, 100);
    } catch (error) {
        console.error('Error loading navigation:', error);
    }
}

// Setup Navigation Listeners
function setupNavListeners() {
    // Support both old and new class names
    document.querySelectorAll('.nav-link, .nav-link-advanced').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section || e.target.closest('[data-section]')?.dataset.section;
            if (section) {
                loadPage(section);
                // Close mobile menu if open
                closeMobileMenu();
            }
        });
    });

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Mobile menu toggle (support both old and new)
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
    
    // Profile dropdown toggle
    setupProfileDropdown();
    
    // Dark mode toggle
    setupDarkMode();
    
    // Company switcher
    setupCompanySwitcher();
    
    // Reports dropdown menu
    setupReportsDropdown();
}

// Setup Reports Dropdown
function setupReportsDropdown() {
    const dropdownContainer = document.querySelector('.nav-dropdown-container');
    const dropdownItems = document.querySelectorAll('.nav-dropdown-item');
    
    if (!dropdownContainer) return;
    
    // Handle dropdown item clicks
    dropdownItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const section = item.dataset.section;
            if (section && section !== 'salesreport' && section !== 'leadreport' && section !== 'activityreport') {
                loadPage(section);
                // Close dropdown
                dropdownContainer.classList.remove('active');
                closeMobileMenu();
            } else {
                // Show coming soon message for unimplemented reports
                alert('This report is coming soon!');
            }
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!dropdownContainer.contains(e.target)) {
            dropdownContainer.classList.remove('active');
        }
    });
}

// Global Sign Out Handler
window.handleSignOut = function() {
    console.log('handleSignOut called');
    
    // Close dropdown
    const profileDropdown = document.getElementById('profileDropdown');
    if (profileDropdown) profileDropdown.classList.remove('active');
    
    // Clear ALL auth data
    localStorage.removeItem('authToken');
    localStorage.removeItem('companyId');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentPage');
    sessionStorage.clear();
    
    // Clear global variables
    if (typeof window.authToken !== 'undefined') window.authToken = null;
    if (typeof window.companyId !== 'undefined') window.companyId = null;
    if (typeof window.currentUser !== 'undefined') window.currentUser = null;
    
    // Clear URL hash
    window.location.hash = '';
    
    // Redirect to VEGA CRM website login page
    window.location.href = '/website/login.html';
};

// Setup Dark Mode Toggle
function setupDarkMode() {
    const darkModeBtn = document.getElementById('darkModeBtn');
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    // Toggle dark mode on button click
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleDarkMode();
        });
    }
}

// Toggle Dark Mode
window.toggleDarkMode = function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    console.log('Dark mode:', newTheme === 'dark' ? 'ON' : 'OFF');
};

// Setup Profile Dropdown Menu
function setupProfileDropdown() {
    const profileMenuBtn = document.getElementById('profileMenuBtn');
    const profileDropdown = document.getElementById('profileDropdown');
    
    // Toggle dropdown on profile button click
    if (profileMenuBtn && profileDropdown) {
        profileMenuBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            profileDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const container = document.querySelector('.profile-dropdown-container');
            if (container && !container.contains(e.target)) {
                profileDropdown.classList.remove('active');
            }
        });
    }
    
    // Setup admin menu link click handler
    const adminMenuLink = document.getElementById('adminMenuLink');
    if (adminMenuLink) {
        adminMenuLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (profileDropdown) profileDropdown.classList.remove('active');
            loadPage('admin');
        });
    }
    
    // Show/hide admin link based on user role
    updateAdminMenuLink();
}

// Update Admin Menu Link visibility based on user role
window.updateAdminMenuLink = function() {
    const adminMenuLink = document.getElementById('adminMenuLink');
    if (!adminMenuLink) return;
    
    const user = currentUser || JSON.parse(localStorage.getItem('currentUser') || 'null');
    
    if (user && (user.role === 'super_admin' || user.role === 'admin')) {
        adminMenuLink.style.display = 'flex';
        console.log('Admin menu link shown for role:', user.role);
    } else {
        adminMenuLink.style.display = 'none';
    }
}

// Setup Company Switcher
function setupCompanySwitcher() {
    const switcherBtn = document.getElementById('companySwitcherBtn');
    const dropdown = document.getElementById('companyDropdown');
    
    if (switcherBtn && dropdown) {
        // Toggle dropdown
        switcherBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isVisible = dropdown.style.display === 'block';
            dropdown.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                loadCompaniesForSwitcher();
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!switcherBtn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }
    
    // Load current company name
    loadCurrentCompany();
}

// Load Current Company Name
window.loadCurrentCompany = async function() {
    if (!companyId) {
        const companyNameEl = document.getElementById('currentCompanyName');
        if (companyNameEl) {
            companyNameEl.textContent = 'Select Company';
        }
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/companies/${companyId}`, {
            headers: getHeaders()
        });
        const data = await response.json();
        
        if (response.ok && data.data) {
            const companyNameEl = document.getElementById('currentCompanyName');
            const companyIconEl = document.getElementById('currentCompanyIcon');
            
            if (companyNameEl) {
                companyNameEl.textContent = data.data.name;
            }
            if (companyIconEl && data.data.name) {
                companyIconEl.textContent = data.data.name.charAt(0).toUpperCase();
            }
        }
    } catch (error) {
        console.error('Error loading current company:', error);
    }
};

// Load Companies for Switcher Dropdown
async function loadCompaniesForSwitcher() {
    const dropdownList = document.getElementById('companyDropdownList');
    if (!dropdownList) return;
    
    dropdownList.innerHTML = '<div class="company-dropdown-loading">Loading companies...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/companies`, {
            headers: getHeaders()
        });
        const data = await response.json();
        
        if (response.ok && data.data) {
            if (data.data.length === 0) {
                dropdownList.innerHTML = '<div class="company-dropdown-empty">No companies available</div>';
                return;
            }
            
            dropdownList.innerHTML = data.data.map(company => {
                const isActive = company.id == companyId;
                return `
                    <div class="company-dropdown-item ${isActive ? 'active' : ''}" onclick="switchCompany(${company.id})">
                        <div class="company-dropdown-icon">${company.name.charAt(0).toUpperCase()}</div>
                        <div class="company-dropdown-info">
                            <div class="company-dropdown-name">${company.name}</div>
                            <div class="company-dropdown-email">${company.email || 'No email'}</div>
                        </div>
                        ${isActive ? '<div class="company-dropdown-check">✓</div>' : ''}
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        dropdownList.innerHTML = '<div class="company-dropdown-error">Failed to load companies</div>';
    }
}

// Switch Company
window.switchCompany = function(newCompanyId) {
    if (newCompanyId == companyId) {
        // Same company, just close dropdown
        const dropdown = document.getElementById('companyDropdown');
        if (dropdown) dropdown.style.display = 'none';
        return;
    }
    
    companyId = newCompanyId;
    localStorage.setItem('companyId', newCompanyId);
    
    // Close dropdown
    const dropdown = document.getElementById('companyDropdown');
    if (dropdown) dropdown.style.display = 'none';
    
    // Update current company name
    loadCurrentCompany();
    
    // Reload current page to refresh data
    const currentSection = document.querySelector('.section.active')?.id || 'dashboard';
    loadPage(currentSection);
};

// Close mobile menu
function closeMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    if (navMenu) {
        navMenu.classList.remove('active');
    }
    if (mobileMenuToggle) {
        mobileMenuToggle.classList.remove('active');
    }
}

// Load Page (Global function)
window.loadPage = async function(pageName) {
    try {
        // Save current page to localStorage
        if (pageName && pageName !== 'home' && pageName !== 'login' && pageName !== 'register' && pageName !== 'company-selection') {
            localStorage.setItem('currentPage', pageName);
            window.location.hash = pageName;
        }
        
        const pageContent = document.getElementById('page-content');
        if (!pageContent) return;
        
        // Hide current sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });
        
        // Load page HTML
        const response = await fetch(`pages/${pageName}.html`);
        const html = await response.text();
        pageContent.innerHTML = html;
        
        // Execute inline scripts in loaded HTML (important for full page forms)
        const scripts = pageContent.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            if (oldScript.src) {
                newScript.src = oldScript.src;
            } else {
                newScript.textContent = oldScript.textContent;
            }
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
        
        // Show loaded page
        const loadedSection = pageContent.querySelector('.section');
        if (loadedSection) {
            loadedSection.classList.add('active');
            loadedSection.style.display = 'block';
        }

        // Show/hide navigation based on page
        const navbarContainer = document.getElementById('navbar-container');
        // Pages that should hide the main CRM navbar (full page forms)
        const hideNavbarPages = ['home', 'login', 'register', 'company-selection', 'add-customer', 'add-contact', 'add-lead', 'add-deal', 'add-task', 'add-activity', 'add-user', 'add-role', 'add-company', 'settings'];
        if (navbarContainer) {
            if (hideNavbarPages.includes(pageName)) {
                navbarContainer.style.display = 'none';
                // Allow scrolling on all pages
                document.body.classList.remove('auth-page-active');
            } else {
                // Show navbar for dashboard and other pages
                navbarContainer.style.display = 'block';
                navbarContainer.style.visibility = 'visible';
                navbarContainer.style.opacity = '1';
                navbarContainer.style.position = 'relative';
                navbarContainer.style.zIndex = '1000';
                document.body.classList.remove('auth-page-active');
                // Load navigation if not loaded
                if (!navbarContainer.innerHTML.trim() || !navbarContainer.querySelector('.navbar-advanced, .navbar')) {
                    await loadNavigation();
                }
                // Update active navigation (support both old and new class names)
                setTimeout(() => {
                    document.querySelectorAll('.nav-link, .nav-link-advanced').forEach(l => l.classList.remove('active'));
                    const activeLink = document.querySelector(`[data-section="${pageName}"]`);
                    if (activeLink) activeLink.classList.add('active');
                }, 150);
            }
        }

        // Load page-specific JavaScript
        // Remove old scripts first to avoid conflicts (check base filename, not query params)
        document.querySelectorAll('script[src*="js/pages/"]').forEach(oldScript => {
            const src = oldScript.src;
            // Remove if it's the same page (ignore query parameters)
            if (src.includes(`js/pages/${pageName}.js`)) {
                oldScript.remove();
            }
        });
        
        const script = document.createElement('script');
        // Add cache-busting timestamp to force fresh load
        const timestamp = new Date().getTime();
        script.src = `js/pages/${pageName}.js?t=${timestamp}`;
        
        // Set script loading to async but ensure it completes
        script.async = false;
        
        script.onload = () => {
            console.log(`Page script loaded: ${pageName}.js`);
            
            // Wait a bit for script to fully execute
            setTimeout(() => {
                // Initialize page - handle both camelCase and hyphenated names
                const initFuncName = `init${pageName.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}`;
                const initFuncName2 = `init${pageName.charAt(0).toUpperCase() + pageName.slice(1)}`;
                
                // Verify function exists before calling
                if (typeof window[initFuncName] === 'function') {
                    console.log(`Calling ${initFuncName}()`);
                    window[initFuncName]();
                } else if (typeof window[initFuncName2] === 'function') {
                    console.log(`Calling ${initFuncName2}()`);
                    window[initFuncName2]();
                } else {
                    console.warn(`No init function found for ${pageName} (tried ${initFuncName}, ${initFuncName2})`);
                }
                
                // Verify and ensure form functions are available
                const formFunctions = {
                    'customers': 'showCustomerForm',
                    'contacts': 'showContactForm',
                    'tasks': 'showTaskForm',
                    'activities': 'showActivityForm',
                    'leads': 'showLeadForm',
                    'deals': 'showDealForm'
                };
                
                const formFunctionName = formFunctions[pageName];
                if (formFunctionName) {
                    if (typeof window[formFunctionName] === 'function') {
                        console.log(`✓ ${formFunctionName} is defined and ready`);
                        
                        // Ensure all Add buttons have correct onclick
                        const buttons = document.querySelectorAll('button.btn-primary, button.btn-advanced');
                        buttons.forEach(btn => {
                            const text = btn.textContent.trim();
                            const onclick = btn.getAttribute('onclick');
                            
                            // Check if this is an Add/Log button
                            if ((text.includes('Add') || text.includes('Log')) && 
                                (!onclick || !onclick.includes(formFunctionName))) {
                                btn.setAttribute('onclick', `window.${formFunctionName} && window.${formFunctionName}()`);
                                console.log(`✓ Updated Add button onclick: ${formFunctionName}`);
                            }
                        });
                    } else {
                        console.error(`✗ ${formFunctionName} is NOT defined after script load!`);
                    }
                }
            }, 100);
        };
        script.onerror = (error) => {
            console.error(`Failed to load script: js/pages/${pageName}.js`, error);
        };
        document.body.appendChild(script);

        // Remove old page scripts
        document.querySelectorAll('script[src^="js/pages/"]').forEach(oldScript => {
            if (oldScript.src !== script.src) {
                oldScript.remove();
            }
        });

    } catch (error) {
        console.error(`Error loading page ${pageName}:`, error);
    }
};

// Global function to close form modal
window.closeFormModal = function() {
    console.log('closeFormModal called');
    const modal = document.getElementById('formModal');
    const formContent = document.getElementById('formContent');
    
    if (modal) {
        // Remove active class and hide modal
        modal.classList.remove('active');
        modal.style.display = 'none';
        console.log('Modal closed successfully');
    } else {
        console.error('Modal element not found!');
    }
    
    // Clear form content after a brief delay to allow animation
    setTimeout(() => {
        if (formContent) {
            formContent.innerHTML = '';
        }
    }, 200);
    
    // Clear editing IDs
    if (typeof window.currentEditingCustomerId !== 'undefined') {
        window.currentEditingCustomerId = null;
    }
    if (typeof window.currentEditingLeadId !== 'undefined') {
        window.currentEditingLeadId = null;
    }
    if (typeof window.currentEditingDealId !== 'undefined') {
        window.currentEditingDealId = null;
    }
    if (typeof window.currentEditingTaskId !== 'undefined') {
        window.currentEditingTaskId = null;
    }
    if (typeof window.currentEditingActivityId !== 'undefined') {
        window.currentEditingActivityId = null;
    }
    if (typeof window.currentEditingContactId !== 'undefined') {
        window.currentEditingContactId = null;
    }
};

// Setup modal click-outside-to-close functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup click-outside-to-close for form modal
    const formModal = document.getElementById('formModal');
    if (formModal) {
        formModal.addEventListener('click', function(e) {
            // Close if clicking on the modal backdrop (not the content)
            if (e.target === formModal) {
                window.closeFormModal();
            }
        });
        console.log('Modal click-outside-to-close setup complete');
    }
    
    // Also setup on window load in case DOMContentLoaded already fired
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        const formModal2 = document.getElementById('formModal');
        if (formModal2 && !formModal2.hasAttribute('data-listener-added')) {
            formModal2.setAttribute('data-listener-added', 'true');
            formModal2.addEventListener('click', function(e) {
                if (e.target === formModal2) {
                    window.closeFormModal();
                }
            });
        }
    }
});

// Global Toast Notification Function
window.showToast = function(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    
    // Icon based on type
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

// Global Delete Confirmation Modal
window.showDeleteConfirmModal = function(title, message, onConfirm) {
    // Remove existing modal if any
    const existingModal = document.getElementById('deleteConfirmModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modalHtml = `
        <div id="deleteConfirmModal" class="modal delete-confirm-modal" style="display: flex;">
            <div class="modal-content delete-confirm-content">
                <div class="delete-confirm-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#dc3545" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                </div>
                <h3 class="delete-confirm-title">${title}</h3>
                <p class="delete-confirm-message">${message}</p>
                <div class="delete-confirm-actions">
                    <button class="btn btn-secondary" onclick="closeDeleteConfirmModal()">Cancel</button>
                    <button class="btn btn-danger" id="confirmDeleteBtn">Delete</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Add event listener to confirm button
    document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
        const btn = document.getElementById('confirmDeleteBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-small"></span> Deleting...';
        
        await onConfirm();
        closeDeleteConfirmModal();
    });
    
    // Close on backdrop click
    document.getElementById('deleteConfirmModal').addEventListener('click', (e) => {
        if (e.target.id === 'deleteConfirmModal') {
            closeDeleteConfirmModal();
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeDeleteConfirmModal();
            document.removeEventListener('keydown', escHandler);
        }
    });
};

window.closeDeleteConfirmModal = function() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.remove();
    }
};

