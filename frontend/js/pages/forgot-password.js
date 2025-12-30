/**
 * Forgot Password Page JavaScript
 * Handles password reset flow
 */

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initForgotPasswordPage();
});

function initForgotPasswordPage() {
    // Check if there's a reset token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Verify token and show reset form
        verifyResetToken(token);
    }
    
    // Setup form handlers
    setupForgotPasswordForm();
    setupResetPasswordForm();
    setupPasswordValidation();
}

/**
 * Setup forgot password form (Step 1)
 */
function setupForgotPasswordForm() {
    const form = document.getElementById('forgotPasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('forgotEmail').value.trim();
        const submitBtn = document.getElementById('forgotSubmitBtn');
        const errorDiv = document.getElementById('forgotPasswordError');
        const successDiv = document.getElementById('forgotPasswordSuccess');
        
        // Validate email
        if (!email || !isValidEmail(email)) {
            showError(errorDiv, 'Please enter a valid email address');
            return;
        }
        
        // Show loading
        setButtonLoading(submitBtn, true);
        hideError(errorDiv);
        
        try {
            const response = await fetch('/api/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Show success message
                successDiv.style.display = 'flex';
                successDiv.innerHTML = `
                    <span>✓</span>
                    <span>If an account exists with this email, a password reset link has been sent.</span>
                `;
                
                // For development: show token if returned
                if (data.data && data.data.token) {
                    console.log('Reset Token (Dev Only):', data.data.token);
                    
                    // Show token for testing (remove in production)
                    successDiv.innerHTML += `
                        <br><br>
                        <small style="word-break: break-all;">
                            <strong>Dev Mode:</strong> Token: ${data.data.token}
                            <br>
                            <a href="#" onclick="showResetForm('${data.data.token}')" style="color: #059669; text-decoration: underline;">
                                Click here to reset password
                            </a>
                        </small>
                    `;
                }
                
                // Clear form
                form.reset();
            } else {
                showError(errorDiv, data.detail || data.message || 'Failed to process request');
            }
        } catch (error) {
            console.error('Forgot password error:', error);
            showError(errorDiv, 'Network error. Please try again.');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

/**
 * Verify reset token
 */
async function verifyResetToken(token) {
    try {
        const response = await fetch('/api/auth/verify-reset-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success && data.data.valid) {
            // Token is valid, show reset form
            showResetForm(token);
        } else {
            // Token invalid or expired
            showError(
                document.getElementById('forgotPasswordError'),
                data.data?.message || 'Invalid or expired reset link. Please request a new one.'
            );
        }
    } catch (error) {
        console.error('Token verification error:', error);
        showError(
            document.getElementById('forgotPasswordError'),
            'Failed to verify reset link. Please try again.'
        );
    }
}

/**
 * Show reset password form (Step 2)
 */
function showResetForm(token) {
    document.getElementById('forgotPasswordStep1').style.display = 'none';
    document.getElementById('forgotPasswordStep2').style.display = 'block';
    document.getElementById('forgotPasswordStep3').style.display = 'none';
    document.getElementById('resetToken').value = token;
}

/**
 * Setup reset password form (Step 2)
 */
function setupResetPasswordForm() {
    const form = document.getElementById('resetPasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const token = document.getElementById('resetToken').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmNewPassword').value;
        const submitBtn = document.getElementById('resetSubmitBtn');
        const errorDiv = document.getElementById('resetPasswordError');
        
        // Validate passwords
        if (!newPassword || newPassword.length < 8) {
            showError(errorDiv, 'Password must be at least 8 characters');
            return;
        }
        
        if (!validatePasswordStrength(newPassword)) {
            showError(errorDiv, 'Password must contain uppercase, lowercase, and a number');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showError(errorDiv, 'Passwords do not match');
            return;
        }
        
        // Show loading
        setButtonLoading(submitBtn, true);
        hideError(errorDiv);
        
        try {
            const response = await fetch('/api/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: token,
                    new_password: newPassword
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Show success step
                document.getElementById('forgotPasswordStep1').style.display = 'none';
                document.getElementById('forgotPasswordStep2').style.display = 'none';
                document.getElementById('forgotPasswordStep3').style.display = 'block';
            } else {
                showError(errorDiv, data.detail || data.message || 'Failed to reset password');
            }
        } catch (error) {
            console.error('Reset password error:', error);
            showError(errorDiv, 'Network error. Please try again.');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

/**
 * Setup password validation with visual feedback
 */
function setupPasswordValidation() {
    const passwordInput = document.getElementById('newPassword');
    const confirmInput = document.getElementById('confirmNewPassword');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            updatePasswordStrength(password);
            updatePasswordRequirements(password);
        });
    }
    
    if (confirmInput) {
        confirmInput.addEventListener('input', function() {
            const password = document.getElementById('newPassword').value;
            const confirm = this.value;
            const feedback = document.getElementById('confirmFeedback');
            
            if (confirm && password !== confirm) {
                feedback.textContent = 'Passwords do not match';
                feedback.style.color = '#ef4444';
            } else if (confirm && password === confirm) {
                feedback.textContent = '✓ Passwords match';
                feedback.style.color = '#10b981';
            } else {
                feedback.textContent = '';
            }
        });
    }
}

/**
 * Update password strength meter
 */
function updatePasswordStrength(password) {
    const strengthBar = document.getElementById('strengthBar');
    if (!strengthBar) return;
    
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    strengthBar.className = 'strength-bar';
    
    if (strength <= 1) {
        strengthBar.classList.add('weak');
    } else if (strength === 2) {
        strengthBar.classList.add('fair');
    } else if (strength === 3) {
        strengthBar.classList.add('good');
    } else {
        strengthBar.classList.add('strong');
    }
}

/**
 * Update password requirements checklist
 */
function updatePasswordRequirements(password) {
    const reqLength = document.getElementById('reqLength');
    const reqUpper = document.getElementById('reqUpper');
    const reqLower = document.getElementById('reqLower');
    const reqNumber = document.getElementById('reqNumber');
    
    if (reqLength) {
        reqLength.className = password.length >= 8 ? 'req-item valid' : 'req-item';
        reqLength.textContent = password.length >= 8 ? '✓ 8+ characters' : '✗ 8+ characters';
    }
    
    if (reqUpper) {
        reqUpper.className = /[A-Z]/.test(password) ? 'req-item valid' : 'req-item';
        reqUpper.textContent = /[A-Z]/.test(password) ? '✓ Uppercase' : '✗ Uppercase';
    }
    
    if (reqLower) {
        reqLower.className = /[a-z]/.test(password) ? 'req-item valid' : 'req-item';
        reqLower.textContent = /[a-z]/.test(password) ? '✓ Lowercase' : '✗ Lowercase';
    }
    
    if (reqNumber) {
        reqNumber.className = /[0-9]/.test(password) ? 'req-item valid' : 'req-item';
        reqNumber.textContent = /[0-9]/.test(password) ? '✓ Number' : '✗ Number';
    }
}

/**
 * Validate password strength
 */
function validatePasswordStrength(password) {
    return password.length >= 8 &&
           /[A-Z]/.test(password) &&
           /[a-z]/.test(password) &&
           /[0-9]/.test(password);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show error message
 */
function showError(element, message) {
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}

/**
 * Hide error message
 */
function hideError(element) {
    if (element) {
        element.textContent = '';
        element.style.display = 'none';
    }
}

/**
 * Set button loading state
 */
function setButtonLoading(button, isLoading) {
    if (!button) return;
    
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    
    if (isLoading) {
        button.disabled = true;
        if (btnText) btnText.style.display = 'none';
        if (btnLoading) btnLoading.style.display = 'flex';
    } else {
        button.disabled = false;
        if (btnText) btnText.style.display = 'inline';
        if (btnLoading) btnLoading.style.display = 'none';
    }
}

/**
 * Toggle password visibility
 */
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        if (button) button.classList.add('active');
    } else {
        input.type = 'password';
        if (button) button.classList.remove('active');
    }
}
