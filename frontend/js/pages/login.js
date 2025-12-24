// Login Page JavaScript

function initLogin() {
    const loginForm = document.getElementById('loginFormPage');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginPage);
    }
    
    // Add input validation
    setupInputValidation('loginEmailPage', 'email');
    setupInputValidation('loginPasswordPage', 'password');
}

// Setup Input Validation
function setupInputValidation(inputId, type) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('blur', () => validateInput(input, type));
    input.addEventListener('input', () => clearInputError(input));
}

// Validate Input (Global)
window.validateInput = function(input, type) {
    const feedback = input.parentElement.querySelector('.input-feedback');
    if (!feedback) return true;
    
    let isValid = true;
    let message = '';
    
    if (type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!input.value) {
            isValid = false;
            message = 'Email is required';
        } else if (!emailRegex.test(input.value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
    } else if (type === 'password') {
        if (!input.value) {
            isValid = false;
            message = 'Password is required';
        } else if (input.value.length < 8) {
            isValid = false;
            message = 'Password must be at least 8 characters';
        }
    } else if (type === 'text') {
        if (!input.value) {
            isValid = false;
            message = 'This field is required';
        } else if (input.value.trim().length < 2) {
            isValid = false;
            message = 'Please enter at least 2 characters';
        }
    }
    
    if (isValid) {
        input.classList.remove('input-error');
        feedback.textContent = '';
    } else {
        input.classList.add('input-error');
        feedback.textContent = message;
    }
    
    return isValid;
}

// Clear Input Error (Global)
window.clearInputError = function(input) {
    input.classList.remove('input-error');
    const feedback = input.parentElement.querySelector('.input-feedback');
    if (feedback) feedback.textContent = '';
};

// Toggle Password Visibility
window.togglePassword = function(inputId, toggleId) {
    const input = document.getElementById(inputId);
    const toggle = document.getElementById(toggleId);
    if (!input || !toggle) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        toggle.innerHTML = `
            <svg class="eye-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M1 1L15 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M6.5 6.5C6.22386 6.77614 6 7.22386 6 7.5C6 8.32843 6.67157 9 7.5 9C7.77614 9 8.22386 8.77614 8.5 8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2.5 2.5C1.73 3.61 1 5.61 1 9C1 12.39 1.73 14.39 2.5 15.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5.5 5.5C4.73 6.61 4 7.61 4 9C4 10.39 4.73 11.39 5.5 12.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9.5 9.5C10.27 8.39 11 7.39 11 5.5C11 4.11 10.27 3.11 9.5 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12.5 12.5C13.27 11.39 14 9.39 14 6C14 2.61 13.27 0.61 12.5 -0.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M15 15L1 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
        `;
    } else {
        input.type = 'password';
        toggle.innerHTML = `
            <svg class="eye-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 3C4.5 3 1.73 5.61 1 9C1.73 12.39 4.5 15 8 15C11.5 15 14.27 12.39 15 9C14.27 5.61 11.5 3 8 3Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="8" cy="9" r="2.5" stroke="currentColor" stroke-width="1.5"/>
            </svg>
        `;
    }
};

async function handleLoginPage(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmailPage').value;
    const password = document.getElementById('loginPasswordPage').value;
    const errorDiv = document.getElementById('loginErrorPage');
    const submitBtn = document.getElementById('loginSubmitBtn');
    const btnText = submitBtn?.querySelector('.btn-text');
    const btnLoading = submitBtn?.querySelector('.btn-loading');

    // Validate inputs
    const emailValid = validateInput(document.getElementById('loginEmailPage'), 'email');
    const passwordValid = validateInput(document.getElementById('loginPasswordPage'), 'password');
    
    if (!emailValid || !passwordValid) {
        return;
    }

    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }

    // Show loading state
    if (submitBtn && btnText && btnLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
    }

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
            if (errorDiv) {
                errorDiv.textContent = data.detail || 'Login failed. Please check your credentials.';
                errorDiv.classList.add('show');
            }
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = 'Connection error. Please check if the server is running.';
            errorDiv.classList.add('show');
        }
    } finally {
        // Hide loading state
        if (submitBtn && btnText && btnLoading) {
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        }
    }
}

