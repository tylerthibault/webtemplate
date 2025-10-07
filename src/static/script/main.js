/**
 * Flask MVC Base Template - Custom JavaScript
 * Creative Portfolio Client-Side Enhancements
 * Following constitutional principles - organized asset structure
 */

// ===== GLOBAL UTILITIES =====

/**
 * Safely get CSRF token from meta tag or form
 * @returns {string|null} CSRF token or null if not found
 */
function getCSRFToken() {
    // Try meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Try hidden input as fallback
    const inputField = document.querySelector('input[name="csrf_token"]');
    if (inputField) {
        return inputField.value;
    }
    
    return null;
}

/**
 * Show alert message
 * @param {string} message - Message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {HTMLElement} container - Container to append alert to
 */
function showAlert(message, type = 'info', container = null) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    if (!container) {
        container = document.querySelector('main .container');
    }
    
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }
}

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {Object} Validation result with isValid and message properties
 */
function validatePasswordStrength(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    
    if (password.length < minLength) {
        return {
            isValid: false,
            message: `Password must be at least ${minLength} characters long.`
        };
    }
    
    if (!hasUpperCase || !hasLowerCase) {
        return {
            isValid: false,
            message: 'Password must contain both uppercase and lowercase letters.'
        };
    }
    
    if (!hasNumber) {
        return {
            isValid: false,
            message: 'Password must contain at least one number.'
        };
    }
    
    return {
        isValid: true,
        message: 'Password strength is good.'
    };
}

/**
 * Debounce function to limit execution rate
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return d.toLocaleDateString('en-US', options);
}

/**
 * Sanitize HTML to prevent XSS
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
function sanitizeHTML(html) {
    const temp = document.createElement('div');
    temp.textContent = html;
    return temp.innerHTML;
}

// ===== FORM ENHANCEMENTS =====

/**
 * Add character counter to textarea
 * @param {HTMLTextAreaElement} textarea - Textarea element
 * @param {number} maxLength - Maximum character length
 */
function addCharacterCounter(textarea, maxLength) {
    const counterId = `${textarea.id}_counter`;
    let counter = document.getElementById(counterId);
    
    if (!counter) {
        counter = document.createElement('small');
        counter.id = counterId;
        counter.className = 'form-text text-muted';
        textarea.parentNode.appendChild(counter);
    }
    
    const updateCounter = () => {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${textarea.value.length}/${maxLength} characters`;
        
        if (remaining < 0) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-muted');
        } else if (remaining < 50) {
            counter.classList.add('text-warning');
            counter.classList.remove('text-muted', 'text-danger');
        } else {
            counter.classList.add('text-muted');
            counter.classList.remove('text-warning', 'text-danger');
        }
    };
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

/**
 * Validate form fields before submission
 * @param {HTMLFormElement} form - Form element to validate
 * @returns {boolean} True if all fields are valid
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
        
        // Email validation
        if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
            input.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

// ===== SESSION MANAGEMENT =====

/**
 * Check session status and warn user before expiration
 */
async function checkSessionStatus() {
    try {
        const response = await fetch('/auth/session', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.authenticated === false) {
            window.location.href = '/login';
            return;
        }
        
        // Warn if less than 2 minutes remaining
        if (data.time_remaining < 120 && data.time_remaining > 0) {
            const minutes = Math.floor(data.time_remaining / 60);
            const seconds = data.time_remaining % 60;
            showAlert(
                `Your session will expire in ${minutes}m ${seconds}s. Please save your work.`,
                'warning'
            );
        }
    } catch (error) {
        console.error('Session check failed:', error);
    }
}

/**
 * Initialize session monitoring for authenticated pages
 */
function initSessionMonitoring() {
    const isDashboard = window.location.pathname.includes('/dashboard');
    const isAuthenticated = document.body.classList.contains('authenticated');
    
    if (isDashboard || isAuthenticated) {
        // Check session every 30 seconds
        setInterval(checkSessionStatus, 30000);
        
        // Reset session timeout on user activity
        const resetTimeout = debounce(() => {
            fetch('/auth/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': getCSRFToken()
                }
            });
        }, 1000);
        
        // Track user activity
        ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
            document.addEventListener(event, resetTimeout);
        });
    }
}

// ===== NAVIGATION ENHANCEMENTS =====

/**
 * Highlight active navigation link
 */
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (currentPath === linkPath || (linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Add smooth scroll behavior for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ===== LOADING STATES =====

/**
 * Show loading spinner on button
 * @param {HTMLButtonElement} button - Button element
 * @param {string} loadingText - Text to display while loading
 */
function showButtonLoading(button, loadingText = 'Loading...') {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${loadingText}
    `;
}

/**
 * Hide loading spinner on button
 * @param {HTMLButtonElement} button - Button element
 */
function hideButtonLoading(button) {
    button.disabled = false;
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        delete button.dataset.originalText;
    }
}

// ===== ANALYTICS HOOKS =====

/**
 * Track custom events (placeholder for analytics integration)
 * @param {string} eventName - Event name
 * @param {Object} eventData - Event data
 */
function trackEvent(eventName, eventData = {}) {
    // Placeholder for Google Analytics, Mixpanel, etc.
    console.log('Event tracked:', eventName, eventData);
    
    // Example integration:
    // if (window.gtag) {
    //     gtag('event', eventName, eventData);
    // }
}

// ===== ACCESSIBILITY ENHANCEMENTS =====

/**
 * Add skip to main content link
 */
function addSkipToMainLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'visually-hidden visually-hidden-focusable';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Ensure main content has ID
    const main = document.querySelector('main');
    if (main && !main.id) {
        main.id = 'main-content';
    }
}

/**
 * Trap focus within modal dialogs
 * @param {HTMLElement} modal - Modal element
 */
function trapFocus(modal) {
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    modal.addEventListener('keydown', function(e) {
        if (e.key !== 'Tab') return;
        
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        }
    });
}

// ===== INITIALIZATION =====

/**
 * Initialize all JavaScript enhancements on DOM ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    highlightActiveNavLink();
    initSmoothScroll();
    
    // Session monitoring
    initSessionMonitoring();
    
    // Form enhancements
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('maxlength'));
        addCharacterCounter(textarea, maxLength);
    });
    
    // Accessibility
    addSkipToMainLink();
    
    // Track page view
    trackEvent('page_view', {
        page_path: window.location.pathname,
        page_title: document.title
    });
    
    console.log('Flask MVC Base Template - JavaScript initialized');
});

// ===== EXPORT FOR TESTING =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCSRFToken,
        showAlert,
        isValidEmail,
        validatePasswordStrength,
        debounce,
        formatDate,
        sanitizeHTML,
        validateForm,
        checkSessionStatus,
        trackEvent
    };
}
