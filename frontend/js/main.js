// Main Application Entry Point

// Setup modal click-outside-to-close (runs early)
function setupModalClose() {
    const formModal = document.getElementById('formModal');
    if (formModal && !formModal.hasAttribute('data-listener-added')) {
        formModal.setAttribute('data-listener-added', 'true');
        formModal.addEventListener('click', function(e) {
            // Close if clicking on the modal backdrop (not the content)
            if (e.target === formModal) {
                if (typeof window.closeFormModal === 'function') {
                    window.closeFormModal();
                }
            }
        });
        console.log('Modal click-outside-to-close setup complete');
    }
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Load dark mode preference early
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    // Setup modal close functionality
    setupModalClose();
    // Ensure config.js has initialized (wait a bit if needed)
    if (typeof API_BASE === 'undefined') {
        console.warn('API_BASE not defined, waiting for config.js...');
        setTimeout(() => {
            initializeApp();
        }, 100);
        return;
    }
    
    initializeApp();
});

function initializeApp() {
    // Check if page-content is empty, if so load home page
    const pageContent = document.getElementById('page-content');
    
    // Only load navigation if user is authenticated and has company selected
    if (authToken && companyId) {
        loadNavigation();
    } else {
        // Hide navbar on home page
        const navbarContainer = document.getElementById('navbar-container');
        if (navbarContainer) {
            navbarContainer.style.display = 'none';
        }
    }
    
    // Check auth and load appropriate page
    // If no auth token, home page is already shown in HTML
    if (authToken) {
        checkAuth();
    } else {
        // Home page is already in HTML, just ensure it's visible
        const homeSection = document.getElementById('home');
        if (homeSection) {
            homeSection.classList.add('active');
        }
    }
}

