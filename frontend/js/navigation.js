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
}

// Global Sign Out Handler
window.handleSignOut = function() {
    console.log('handleSignOut called');
    
    // Close dropdown
    const profileDropdown = document.getElementById('profileDropdown');
    if (profileDropdown) profileDropdown.classList.remove('active');
    
    // Call logout function
    if (typeof window.handleLogout === 'function') {
        window.handleLogout();
    } else {
        console.error('handleLogout function not found, using fallback');
        // Fallback logout
        localStorage.removeItem('authToken');
        localStorage.removeItem('companyId');
        localStorage.removeItem('currentUser');
        const navbarContainer = document.getElementById('navbar-container');
        if (navbarContainer) navbarContainer.style.display = 'none';
        if (typeof loadPage === 'function') {
            loadPage('home');
        } else if (typeof window.loadPage === 'function') {
            window.loadPage('home');
        } else {
            window.location.href = 'index.html';
        }
    }
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
        
        // Show loaded page
        const loadedSection = pageContent.querySelector('.section');
        if (loadedSection) {
            loadedSection.classList.add('active');
            loadedSection.style.display = 'block';
        }

        // Show/hide navigation based on page
        const navbarContainer = document.getElementById('navbar-container');
        if (navbarContainer) {
            if (pageName === 'home' || pageName === 'login' || pageName === 'register' || pageName === 'company-selection') {
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
        // Remove active class
        modal.classList.remove('active');
        // Remove any inline display styles that might be set
        if (modal.style.display) {
            modal.style.removeProperty('display');
        }
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

