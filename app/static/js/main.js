// Custom JavaScript for Secure Login System

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    initializeAlerts();
    initializeTooltips();
    initializePasswordStrength();
    initializeSecurityMetrics();
    initializeTheme();
}

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            }, 5000);
        }
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Password strength indicator
function initializePasswordStrength() {
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(field => {
        if (field.name === 'password' || field.name === 'new_password') {
            field.addEventListener('input', function() {
                updatePasswordStrength(this);
            });
        }
    });
}

function updatePasswordStrength(passwordField) {
    const password = passwordField.value;
    const strengthMeter = document.getElementById('password-strength');

    if (!strengthMeter) {
        // Create strength meter if it doesn't exist
        const meter = document.createElement('div');
        meter.id = 'password-strength';
        meter.className = 'password-strength-meter mt-2';
        passwordField.parentNode.appendChild(meter);
    }

    const strength = calculatePasswordStrength(password);
    displayPasswordStrength(strength);
}

function calculatePasswordStrength(password) {
    let score = 0;
    const checks = {
        length: password.length >= 8,
        lowercase: /[a-z]/.test(password),
        uppercase: /[A-Z]/.test(password),
        numbers: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    score = Object.values(checks).filter(Boolean).length;

    return {
        score: score,
        checks: checks,
        level: score < 3 ? 'weak' : score < 5 ? 'medium' : 'strong'
    };
}

function displayPasswordStrength(strength) {
    const meter = document.getElementById('password-strength');
    const colors = {
        weak: 'danger',
        medium: 'warning', 
        strong: 'success'
    };

    const labels = {
        weak: 'Weak',
        medium: 'Medium',
        strong: 'Strong'
    };

    meter.innerHTML = `
        <div class="progress" style="height: 5px;">
            <div class="progress-bar bg-${colors[strength.level]}" 
                 style="width: ${(strength.score / 5) * 100}%"></div>
        </div>
        <small class="text-${colors[strength.level]}">
            Password strength: ${labels[strength.level]}
        </small>
    `;
}

// Security metrics updates
function initializeSecurityMetrics() {
    if (document.querySelector('.admin-dashboard')) {
        updateSecurityMetrics();
        setInterval(updateSecurityMetrics, 30000); // Update every 30 seconds
    }
}

function updateSecurityMetrics() {
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            updateMetricCard('total-users', data.total_users);
            updateMetricCard('active-users', data.active_users);
            updateMetricCard('failed-logins', data.failed_logins);
            updateMetricCard('locked-users', data.locked_users);
        })
        .catch(error => {
            console.error('Error updating metrics:', error);
        });
}

function updateMetricCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        element.classList.add('updated');
        setTimeout(() => {
            element.classList.remove('updated');
        }, 1000);
    }
}

// Theme management
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    applyTheme(theme);

    // Add theme toggle if it exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

// Form validation helpers
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(input);
        }
    });

    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Security monitoring
function reportSecurityEvent(event, details) {
    fetch('/api/security-event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            event: event,
            details: details,
            timestamp: new Date().toISOString()
        })
    }).catch(error => {
        console.error('Failed to report security event:', error);
    });
}

function getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : '';
}

// Loading states
function showLoading(element) {
    element.innerHTML = '<span class="loading"></span> Loading...';
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Session management
function checkSession() {
    fetch('/api/session-check')
        .then(response => {
            if (response.status === 401) {
                showNotification('Session expired. Please log in again.', 'warning');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('Session check failed:', error);
        });
}

// Check session every 5 minutes
setInterval(checkSession, 300000);

// Prevent multiple form submissions
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');

    if (submitBtn && !submitBtn.disabled) {
        setTimeout(() => {
            submitBtn.disabled = true;
            showLoading(submitBtn);
        }, 100);
    }
});

// Enhanced security features
document.addEventListener('contextmenu', function(e) {
    // Disable right-click on sensitive elements
    if (e.target.classList.contains('no-context-menu')) {
        e.preventDefault();
    }
});

// Detect developer tools (basic detection)
let devtools = {
    open: false,
    orientation: null
};

const threshold = 160;

setInterval(() => {
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
        if (!devtools.open) {
            devtools.open = true;
            reportSecurityEvent('DEVTOOLS_OPENED', 'Developer tools detected');
        }
    } else {
        devtools.open = false;
    }
}, 500);

// Export functions for global use
window.SecureLogin = {
    showNotification,
    copyToClipboard,
    validateForm,
    reportSecurityEvent,
    showLoading,
    hideLoading
};
