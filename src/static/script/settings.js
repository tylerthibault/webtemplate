/**
 * Personal Settings Page JavaScript
 * 
 * Handles:
 * - Profile picture preview and upload
 * - Bio character counter
 * - Form validation
 * - Unsaved changes warning
 * - AJAX form submission
 * - Concurrent edit conflict detection
 */

(function() {
    'use strict';

    // DOM Elements
    const form = document.getElementById('settingsForm');
    const profilePictureInput = document.getElementById('profilePictureInput');
    const profilePicturePreview = document.getElementById('profilePicturePreview');
    const uploadButton = document.getElementById('uploadButton');
    const removePictureButton = document.getElementById('removePictureButton');
    const pictureError = document.getElementById('pictureError');
    const bioTextarea = document.getElementById('bio');
    const bioCounter = document.getElementById('bioCounter');
    const saveButton = document.getElementById('saveButton');
    const saveButtonText = document.getElementById('saveButtonText');
    const saveButtonSpinner = document.getElementById('saveButtonSpinner');
    const cancelButton = document.getElementById('cancelButton');
    const successMessage = document.getElementById('successMessage');
    const errorContainer = document.getElementById('errorContainer');
    const conflictWarning = document.getElementById('conflictWarning');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');

    // State
    let formChanged = false;
    let profilePictureBase64 = null;
    let removePictureFlag = false;

    /**
     * Initialize page functionality
     */
    function init() {
        setupEventListeners();
        updateBioCounter();
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Profile picture upload
        uploadButton.addEventListener('click', () => {
            profilePictureInput.click();
        });

        profilePictureInput.addEventListener('change', handleProfilePictureChange);

        if (removePictureButton) {
            removePictureButton.addEventListener('click', handleRemovePicture);
        }

        // Bio character counter
        bioTextarea.addEventListener('input', updateBioCounter);

        // Form change tracking
        form.addEventListener('input', handleFormChange);

        // Form submission
        form.addEventListener('submit', handleFormSubmit);

        // Cancel button
        cancelButton.addEventListener('click', handleCancel);

        // Password confirmation validation
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);

        // Unsaved changes warning
        window.addEventListener('beforeunload', handleBeforeUnload);
    }

    /**
     * Handle profile picture file selection
     */
    function handleProfilePictureChange(event) {
        const file = event.target.files[0];
        
        if (!file) {
            return;
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            showPictureError('Please select a JPEG, PNG, or GIF image');
            profilePictureInput.value = '';
            return;
        }

        // Validate file size (5MB max)
        const maxSize = 5 * 1024 * 1024; // 5MB in bytes
        if (file.size > maxSize) {
            showPictureError('Image must be smaller than 5MB');
            profilePictureInput.value = '';
            return;
        }

        // Clear any previous errors
        hidePictureError();

        // Read and preview file
        const reader = new FileReader();
        
        reader.onload = function(e) {
            // Extract base64 data (remove data:image/...;base64, prefix)
            const base64Data = e.target.result.split(',')[1];
            profilePictureBase64 = base64Data;
            
            // Update preview
            if (profilePicturePreview.tagName === 'IMG') {
                profilePicturePreview.src = e.target.result;
            } else {
                // Replace placeholder div with img
                const img = document.createElement('img');
                img.id = 'profilePicturePreview';
                img.src = e.target.result;
                img.alt = 'Profile Picture';
                img.className = 'profile-picture-preview rounded-circle';
                profilePicturePreview.parentNode.replaceChild(img, profilePicturePreview);
            }

            // Clear remove flag if set
            removePictureFlag = false;

            // Mark form as changed
            formChanged = true;
        };

        reader.onerror = function() {
            showPictureError('Failed to read image file');
            profilePictureInput.value = '';
        };

        reader.readAsDataURL(file);
    }

    /**
     * Handle remove picture button click
     */
    function handleRemovePicture() {
        // Set remove flag
        removePictureFlag = true;
        profilePictureBase64 = null;

        // Replace image with placeholder
        const placeholder = document.createElement('div');
        placeholder.id = 'profilePicturePreview';
        placeholder.className = 'profile-picture-placeholder rounded-circle mx-auto';
        placeholder.innerHTML = '<span>No Picture</span>';
        
        const currentPreview = document.getElementById('profilePicturePreview');
        currentPreview.parentNode.replaceChild(placeholder, currentPreview);

        // Clear file input
        profilePictureInput.value = '';

        // Mark form as changed
        formChanged = true;
    }

    /**
     * Show picture error message
     */
    function showPictureError(message) {
        pictureError.textContent = message;
        pictureError.classList.remove('d-none');
    }

    /**
     * Hide picture error message
     */
    function hidePictureError() {
        pictureError.classList.add('d-none');
    }

    /**
     * Update bio character counter
     */
    function updateBioCounter() {
        const length = bioTextarea.value.length;
        const max = 500;
        
        bioCounter.textContent = `${length}/${max}`;

        // Update color based on remaining characters
        bioCounter.classList.remove('text-warning', 'text-danger');
        
        if (length > max * 0.9) {
            bioCounter.classList.add('text-danger');
        } else if (length > max * 0.8) {
            bioCounter.classList.add('text-warning');
        }
    }

    /**
     * Handle form input changes
     */
    function handleFormChange() {
        formChanged = true;
        form.classList.add('form-changed');
    }

    /**
     * Validate password match
     */
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.setCustomValidity('Passwords do not match');
            confirmPasswordInput.classList.add('is-invalid');
            
            const feedback = confirmPasswordInput.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = 'Passwords do not match';
            }
        } else {
            confirmPasswordInput.setCustomValidity('');
            confirmPasswordInput.classList.remove('is-invalid');
        }
    }

    /**
     * Handle form submission
     */
    async function handleFormSubmit(event) {
        event.preventDefault();

        // Validate password match
        validatePasswordMatch();
        
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        // Disable submit button and show spinner
        setSubmitting(true);

        // Hide previous messages
        hideMessages();

        // Gather form data
        const formData = {
            full_name: document.getElementById('full_name').value.trim(),
            email: document.getElementById('email').value.trim(),
            bio: bioTextarea.value.trim(),
            updated_at: document.getElementById('updated_at').value,
            csrf_token: document.getElementById('csrf_token').value
        };

        // Add password if changed
        const password = passwordInput.value;
        if (password) {
            formData.password = password;
        }

        // Add profile picture if uploaded
        if (profilePictureBase64) {
            formData.profile_picture_data = profilePictureBase64;
        }

        // Add remove picture flag if set
        if (removePictureFlag) {
            formData.remove_profile_picture = true;
        }

        try {
            // Submit to server
            const response = await fetch('/settings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': formData.csrf_token
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Success
                handleSuccess(data);
            } else if (response.status === 409) {
                // Concurrent edit conflict
                handleConflict(data);
            } else if (response.status === 400) {
                // Validation errors
                handleValidationErrors(data.errors);
            } else {
                // Other error
                handleError(data.error || 'An unexpected error occurred');
            }
        } catch (error) {
            handleError('Network error. Please check your connection and try again.');
        } finally {
            setSubmitting(false);
        }
    }

    /**
     * Handle successful form submission
     */
    function handleSuccess(data) {
        // Show success message
        successMessage.classList.remove('d-none');
        
        // Update hidden updated_at field
        document.getElementById('updated_at').value = data.user.updated_at;

        // Reset form changed state
        formChanged = false;
        form.classList.remove('form-changed');

        // Clear password fields
        passwordInput.value = '';
        confirmPasswordInput.value = '';

        // Reset profile picture upload state
        profilePictureBase64 = null;
        removePictureFlag = false;
        profilePictureInput.value = '';

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Hide success message after 5 seconds
        setTimeout(() => {
            successMessage.classList.add('d-none');
        }, 5000);
    }

    /**
     * Handle concurrent edit conflict
     */
    function handleConflict(data) {
        conflictWarning.classList.remove('d-none');
        
        // Scroll to warning
        conflictWarning.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Handle validation errors
     */
    function handleValidationErrors(errors) {
        if (!errors) return;

        const errorHTML = '<div class="alert alert-danger"><strong>Please correct the following errors:</strong><ul>' +
            Object.entries(errors).map(([field, message]) => {
                // Also mark individual fields as invalid
                const input = document.getElementById(field);
                if (input) {
                    input.classList.add('is-invalid');
                    const feedback = input.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = message;
                    }
                }
                return `<li>${message}</li>`;
            }).join('') +
            '</ul></div>';

        errorContainer.innerHTML = errorHTML;
        errorContainer.classList.remove('d-none');

        // Scroll to errors
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Handle general error
     */
    function handleError(message) {
        const errorHTML = `<div class="alert alert-danger">${message}</div>`;
        errorContainer.innerHTML = errorHTML;
        errorContainer.classList.remove('d-none');
        
        // Scroll to error
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Hide all messages
     */
    function hideMessages() {
        successMessage.classList.add('d-none');
        errorContainer.classList.add('d-none');
        errorContainer.innerHTML = '';
        conflictWarning.classList.add('d-none');

        // Clear field-level validation
        const inputs = form.querySelectorAll('.is-invalid');
        inputs.forEach(input => input.classList.remove('is-invalid'));
    }

    /**
     * Set form submitting state
     */
    function setSubmitting(submitting) {
        saveButton.disabled = submitting;
        
        if (submitting) {
            saveButtonText.classList.add('d-none');
            saveButtonSpinner.classList.remove('d-none');
        } else {
            saveButtonText.classList.remove('d-none');
            saveButtonSpinner.classList.add('d-none');
        }
    }

    /**
     * Handle cancel button click
     */
    function handleCancel() {
        if (formChanged) {
            const confirmed = confirm('You have unsaved changes. Are you sure you want to cancel?');
            if (confirmed) {
                window.location.href = '/dashboard';
            }
        } else {
            window.location.href = '/dashboard';
        }
    }

    /**
     * Handle beforeunload event (unsaved changes warning)
     */
    function handleBeforeUnload(event) {
        if (formChanged) {
            event.preventDefault();
            event.returnValue = ''; // Required for Chrome
            return '';
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
