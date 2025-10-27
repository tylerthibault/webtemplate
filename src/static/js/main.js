/**
 * Custom Modal System for Flask Application
 * 
 * A lightweight, accessible modal system that doesn't depend on Bootstrap.
 * Supports keyboard navigation, focus management, and customizable behaviors.
 */

class AppModal {
    constructor(element) {
        this.element = element;
        this.id = element.id;
        this.backdrop = element.querySelector('.app-modal-backdrop');
        this.dialog = element.querySelector('.app-modal-dialog');
        this.closeButtons = element.querySelectorAll('[data-modal-close]');
        this.submitButtons = element.querySelectorAll('[data-modal-submit]');
        
        // Configuration from data attributes
        this.config = {
            backdropClose: element.dataset.modalBackdrop !== 'false',
            escapeClose: element.dataset.modalEscape !== 'false'
        };
        
        // State
        this.isOpen = false;
        this.lastFocusedElement = null;
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.bindEvents();
        
        // Set up ARIA attributes
        this.setupAccessibility();
    }
    
    bindEvents() {
        // Close button clicks
        this.closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
            });
        });
        
        // Submit button clicks
        this.submitButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSubmit(button);
            });
        });
        
        // Backdrop click
        if (this.config.backdropClose) {
            this.backdrop.addEventListener('click', () => {
                this.close();
            });
        }
        
        // Prevent dialog click from closing modal
        this.dialog.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Keyboard events
        this.element.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
    }
    
    setupAccessibility() {
        // Set initial hidden state
        this.element.setAttribute('aria-hidden', 'true');
        
        // Ensure focusable elements have proper tabindex when hidden
        this.updateTabindex(false);
    }
    
    updateTabindex(visible) {
        const focusableElements = this.element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        focusableElements.forEach(element => {
            if (visible) {
                element.removeAttribute('tabindex');
            } else {
                element.setAttribute('tabindex', '-1');
            }
        });
    }
    
    handleKeydown(e) {
        if (!this.isOpen) return;
        
        switch (e.key) {
            case 'Escape':
                if (this.config.escapeClose) {
                    e.preventDefault();
                    this.close();
                }
                break;
                
            case 'Tab':
                this.handleTabKey(e);
                break;
        }
    }
    
    handleTabKey(e) {
        const focusableElements = this.element.querySelectorAll(
            'button:not([disabled]), [href]:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]):not([disabled])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    handleSubmit(button) {
        // Emit custom event
        const submitEvent = new CustomEvent('modalSubmit', {
            detail: {
                modal: this,
                button: button,
                modalId: this.id
            },
            bubbles: true,
            cancelable: true
        });
        
        this.element.dispatchEvent(submitEvent);
        
        // If event wasn't prevented, handle form submission
        if (!submitEvent.defaultPrevented) {
            const form = this.element.querySelector('form');
            if (form) {
                this.handleFormSubmit(form, button);
            }
        }
    }
    
    handleFormSubmit(form, button) {
        // Prevent double submission
        button.disabled = true;
        
        // Add loading state if needed
        const originalText = button.textContent;
        button.textContent = button.dataset.loadingText || 'Submitting...';
        
        // Emit form submit event
        const formSubmitEvent = new CustomEvent('modalFormSubmit', {
            detail: {
                modal: this,
                form: form,
                button: button,
                modalId: this.id
            },
            bubbles: true,
            cancelable: true
        });
        
        form.dispatchEvent(formSubmitEvent);
        
        // Reset button state after a delay (in case of errors)
        setTimeout(() => {
            button.disabled = false;
            button.textContent = originalText;
        }, 3000);
    }
    
    open() {
        if (this.isOpen) return;
        
        // Store currently focused element
        this.lastFocusedElement = document.activeElement;
        
        // Show modal
        this.element.style.display = 'block';
        
        // Force reflow
        this.element.offsetHeight;
        
        // Add show class for animation
        this.element.classList.add('app-modal-show');
        
        // Update accessibility
        this.element.setAttribute('aria-hidden', 'false');
        this.updateTabindex(true);
        
        // Focus first focusable element
        this.focusFirstElement();
        
        // Add body class to prevent scrolling
        document.body.classList.add('app-modal-open');
        
        // Set state
        this.isOpen = true;
        
        // Emit open event
        this.element.dispatchEvent(new CustomEvent('modalOpen', {
            detail: { modal: this, modalId: this.id },
            bubbles: true
        }));
    }
    
    close() {
        if (!this.isOpen) return;
        
        // Remove show class for animation
        this.element.classList.remove('app-modal-show');
        
        // Wait for animation to complete
        setTimeout(() => {
            if (!this.isOpen) return; // Check if modal was reopened during animation
            
            // Hide modal
            this.element.style.display = 'none';
            
            // Update accessibility
            this.element.setAttribute('aria-hidden', 'true');
            this.updateTabindex(false);
            
            // Remove body class
            document.body.classList.remove('app-modal-open');
            
            // Restore focus
            if (this.lastFocusedElement) {
                this.lastFocusedElement.focus();
                this.lastFocusedElement = null;
            }
            
            // Set state
            this.isOpen = false;
            
            // Emit close event
            this.element.dispatchEvent(new CustomEvent('modalClose', {
                detail: { modal: this, modalId: this.id },
                bubbles: true
            }));
            
        }, 200); // Match CSS transition duration
    }
    
    focusFirstElement() {
        const focusableElements = this.element.querySelectorAll(
            'button:not([disabled]), [href]:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"]):not([disabled])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        } else {
            this.dialog.focus();
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    // Static methods for managing multiple modals
    static closeAll() {
        AppModal.instances.forEach(modal => {
            if (modal.isOpen) {
                modal.close();
            }
        });
    }
    
    static getModal(id) {
        return AppModal.instances.find(modal => modal.id === id);
    }
}

// Store all modal instances
AppModal.instances = [];

// Modal Manager
const ModalManager = {
    init() {
        // Initialize all existing modals
        document.querySelectorAll('.app-modal').forEach(element => {
            const modal = new AppModal(element);
            AppModal.instances.push(modal);
        });
        
        // Set up global event listeners
        this.bindGlobalEvents();
    },
    
    bindGlobalEvents() {
        // Handle modal trigger buttons
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal-target]');
            if (trigger) {
                e.preventDefault();
                const targetId = trigger.dataset.modalTarget;
                const modal = AppModal.getModal(targetId);
                if (modal) {
                    modal.open();
                }
            }
            
            // Handle close buttons
            const closeButton = e.target.closest('[data-modal-close]');
            if (closeButton) {
                e.preventDefault();
                const targetId = closeButton.dataset.modalClose;
                const modal = AppModal.getModal(targetId);
                if (modal) {
                    modal.close();
                }
            }
        });
        
        // Handle ESC key globally
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Close the topmost modal
                const openModals = AppModal.instances.filter(modal => modal.isOpen);
                if (openModals.length > 0) {
                    const topModal = openModals[openModals.length - 1];
                    if (topModal.config.escapeClose) {
                        topModal.close();
                    }
                }
            }
        });
    },
    
    // Public API methods
    open(id) {
        const modal = AppModal.getModal(id);
        if (modal) {
            modal.open();
            return modal;
        }
        console.warn(`Modal with id "${id}" not found`);
        return null;
    },
    
    close(id) {
        if (id) {
            const modal = AppModal.getModal(id);
            if (modal) {
                modal.close();
                return modal;
            }
            console.warn(`Modal with id "${id}" not found`);
        } else {
            AppModal.closeAll();
        }
        return null;
    },
    
    toggle(id) {
        const modal = AppModal.getModal(id);
        if (modal) {
            modal.toggle();
            return modal;
        }
        console.warn(`Modal with id "${id}" not found`);
        return null;
    },
    
    // Create a modal dynamically
    create(config) {
        const {
            id,
            title = '',
            body = '',
            size = 'md',
            type = 'primary',
            showClose = true,
            footerButtons = [],
            backdropClose = true,
            escapeClose = true
        } = config;
        
        // Create modal HTML
        const modalHTML = `
            <div class="app-modal" id="${id}" role="dialog" aria-labelledby="${id}-title" aria-describedby="${id}-body" aria-modal="true" data-modal-backdrop="${backdropClose}" data-modal-escape="${escapeClose}" style="display: none;">
                <div class="app-modal-backdrop"></div>
                <div class="app-modal-container">
                    <div class="app-modal-dialog app-modal-${size} app-modal-${type}">
                        ${title || showClose ? `
                        <div class="app-modal-header">
                            ${title ? `<h3 class="app-modal-title" id="${id}-title">${title}</h3>` : ''}
                            ${showClose ? `
                            <button type="button" class="app-modal-close-btn" data-modal-close="${id}" aria-label="Close modal">
                                <svg class="app-modal-close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                </svg>
                            </button>
                            ` : ''}
                        </div>
                        ` : ''}
                        <div class="app-modal-body" id="${id}-body">${body}</div>
                        ${footerButtons.length > 0 ? `
                        <div class="app-modal-footer">
                            ${footerButtons.map(button => `
                                <button type="button" class="app-modal-btn app-modal-btn-${button.type || 'secondary'}" 
                                    ${button.action === 'close' ? `data-modal-close="${id}"` : ''}
                                    ${button.action === 'submit' ? `data-modal-submit="${id}"` : ''}
                                    ${button.id ? `id="${button.id}"` : ''}
                                    ${button.disabled ? 'disabled' : ''}>
                                    ${button.text}
                                </button>
                            `).join('')}
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Add to DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Initialize modal
        const element = document.getElementById(id);
        const modal = new AppModal(element);
        AppModal.instances.push(modal);
        
        return modal;
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        ModalManager.init();
    });
} else {
    ModalManager.init();
}

// Expose to global scope
window.AppModal = AppModal;
window.ModalManager = ModalManager;