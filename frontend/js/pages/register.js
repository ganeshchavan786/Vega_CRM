// Registration Page JavaScript

function initRegister() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Add input validation
    setupInputValidation('registerName', 'text');
    setupInputValidation('registerEmail', 'email');
    setupInputValidation('registerPassword', 'password');
    setupInputValidation('registerPasswordConfirm', 'password');
}

// Setup Input Validation
function setupInputValidation(inputId, type) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('blur', () => validateInput(input, type));
    input.addEventListener('input', () => clearInputError(input));
}

// Validate Input
function validateInput(input, type) {
    if (!input) return false;
    
    const value = input.value.trim();
    let isValid = true;
    
    if (type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(value);
    } else if (type === 'password') {
        isValid = value.length >= 8;
    } else if (type === 'text') {
        isValid = value.length >= 2;
    }
    
    if (!isValid && value.length > 0) {
        input.classList.add('input-error');
    } else {
        input.classList.remove('input-error');
    }
    
    return isValid || value.length === 0;
}

// Clear Input Error
function clearInputError(input) {
    if (input) {
        input.classList.remove('input-error');
    }
}

// Check Password Strength
window.checkPasswordStrength = function(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const password = input.value;
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    
    if (!strengthFill || !strengthText) return;
    
    let strength = 0;
    let strengthLabel = '';
    let strengthColor = '';
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    if (strength === 0) {
        strengthLabel = 'Very Weak';
        strengthColor = '#DE350B';
    } else if (strength === 1) {
        strengthLabel = 'Weak';
        strengthColor = '#FF5630';
    } else if (strength === 2) {
        strengthLabel = 'Fair';
        strengthColor = '#FFAB00';
    } else if (strength === 3) {
        strengthLabel = 'Good';
        strengthColor = '#36B37E';
    } else if (strength === 4) {
        strengthLabel = 'Strong';
        strengthColor = '#00875A';
    } else {
        strengthLabel = 'Very Strong';
        strengthColor = '#006644';
    }
    
    const percentage = (strength / 5) * 100;
    strengthFill.style.width = percentage + '%';
    strengthFill.style.background = strengthColor;
    strengthText.textContent = password.length > 0 ? strengthLabel : 'Password strength';
    strengthText.style.color = password.length > 0 ? strengthColor : 'var(--jira-text-secondary)';
};

// Check Password Match
window.checkPasswordMatch = function() {
    const password = document.getElementById('registerPassword')?.value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm')?.value;
    const matchDiv = document.getElementById('passwordMatch');
    
    if (!matchDiv) return;
    
    if (passwordConfirm.length > 0) {
        if (password === passwordConfirm) {
            matchDiv.style.display = 'flex';
            matchDiv.style.color = 'var(--jira-success)';
        } else {
            matchDiv.style.display = 'none';
        }
    } else {
        matchDiv.style.display = 'none';
    }
};

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    const errorDiv = document.getElementById('registerError');
    const submitBtn = document.getElementById('registerSubmitBtn');
    const btnText = submitBtn?.querySelector('.btn-text');
    const btnLoading = submitBtn?.querySelector('.btn-loading');
    const agreeTerms = document.getElementById('agreeTerms');

    // Validate inputs
    const nameValid = validateInput(document.getElementById('registerName'), 'text');
    const emailValid = validateInput(document.getElementById('registerEmail'), 'email');
    const passwordValid = validateInput(document.getElementById('registerPassword'), 'password');
    
    if (!nameValid || !emailValid || !passwordValid) {
        return;
    }

    if (!agreeTerms?.checked) {
        if (errorDiv) {
            errorDiv.textContent = 'Please agree to the Terms & Conditions';
            errorDiv.classList.add('show');
        }
        return;
    }

    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.classList.remove('show');
    }

    // Validate passwords match
    if (password !== passwordConfirm) {
        if (errorDiv) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.classList.add('show');
        }
        const confirmInput = document.getElementById('registerPasswordConfirm');
        if (confirmInput) {
            confirmInput.classList.add('input-error');
        }
        return;
    }

    // Show loading state
    if (submitBtn && btnText && btnLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
    }

    try {
        // Split name into first_name and last_name
        const nameParts = name.trim().split(' ');
        const first_name = nameParts[0] || name;
        const last_name = nameParts.slice(1).join(' ') || 'User';
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                first_name,
                last_name,
                email, 
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Show success message
            if (errorDiv) {
                errorDiv.textContent = '';
                errorDiv.classList.remove('show');
            }
            
            // Show success notification
            showSuccessMessage('Registration successful! Redirecting to login...');
            
            // Redirect to login after 1.5 seconds
            setTimeout(() => {
                loadPage('login');
            }, 1500);
        } else {
            if (errorDiv) {
                errorDiv.textContent = data.detail || 'Registration failed. Please try again.';
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

// Show Success Message
function showSuccessMessage(message) {
    const errorDiv = document.getElementById('registerError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show', 'success-message');
        setTimeout(() => {
            errorDiv.classList.remove('show', 'success-message');
        }, 3000);
    }
}

