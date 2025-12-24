// API Configuration
const API_BASE = 'http://localhost:8000/api';
let authToken = null;
let companyId = null;
let currentUser = null;

// Initialize from localStorage
function initAuth() {
    authToken = localStorage.getItem('authToken');
    companyId = localStorage.getItem('companyId');
    try {
        currentUser = JSON.parse(localStorage.getItem('currentUser'));
    } catch (e) {
        currentUser = null;
    }
}

// Call init on load
initAuth();

// Helper function to get headers (always read fresh from localStorage)
function getHeaders() {
    // Always get fresh token from localStorage
    const token = localStorage.getItem('authToken');
    if (!token) {
        console.warn('No auth token found');
        // Don't redirect here as it might cause loops, let the API call handle 401
        return {
            'Content-Type': 'application/json'
        };
    }
    // Update the global variable for consistency
    authToken = token;
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Helper to handle 401 errors (unauthorized)
// Prevent multiple redirects by using a flag
let isRedirecting401 = false;

function handle401Error() {
    // Prevent multiple redirects
    if (isRedirecting401) {
        return;
    }
    
    console.warn('401 Unauthorized - clearing auth and redirecting');
    isRedirecting401 = true;
    
    // Clear auth
    setAuthToken(null);
    setCompanyId(null);
    currentUser = null;
    localStorage.removeItem('currentUser');
    
    // Reset flag after a delay
    setTimeout(() => {
        isRedirecting401 = false;
    }, 1000);
    
    // Redirect to home/login only if not already there
    const currentHash = window.location.hash.replace('#', '');
    if (currentHash !== 'home' && currentHash !== 'login') {
        if (typeof loadPage === 'function') {
            loadPage('home');
        } else if (window.location) {
            window.location.href = '/';
        }
    }
}

// Helper to update token in memory and localStorage
function setAuthToken(token) {
    authToken = token;
    if (token) {
        localStorage.setItem('authToken', token);
    } else {
        localStorage.removeItem('authToken');
    }
}

// Helper to update company ID
function setCompanyId(id) {
    companyId = id;
    if (id) {
        localStorage.setItem('companyId', id);
    } else {
        localStorage.removeItem('companyId');
    }
}

