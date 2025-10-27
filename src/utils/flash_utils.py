"""
Flash Message Utilities

Helper functions for managing flash messages in the Flask MVC template.
Provides easy-to-use functions for adding different types of flash messages.
"""

from flask import flash


class FlashService:
    """
    Service class for managing flash messages.
    
    Provides methods for adding different types of flash messages with
    proper categorization for the toast notification system.
    """
    
    @staticmethod
    def success(message):
        """
        Add a success flash message.
        
        Args:
            message (str): Success message to display
        """
        flash(message, 'success')
    
    @staticmethod
    def error(message):
        """
        Add an error flash message.
        
        Args:
            message (str): Error message to display
        """
        flash(message, 'error')
    
    @staticmethod
    def warning(message):
        """
        Add a warning flash message.
        
        Args:
            message (str): Warning message to display
        """
        flash(message, 'warning')
    
    @staticmethod
    def info(message):
        """
        Add an informational flash message.
        
        Args:
            message (str): Information message to display
        """
        flash(message, 'info')
    
    @staticmethod
    def danger(message):
        """
        Add a danger flash message (alias for error).
        
        Args:
            message (str): Danger message to display
        """
        flash(message, 'danger')
    
    @staticmethod
    def form_error(message, form_name=None):
        """
        Add a form-specific error message that won't appear in toast notifications.
        These should be handled by individual forms.
        
        Args:
            message (str): Form error message to display
            form_name (str, optional): Specific form identifier
        """
        category = f"{form_name}_error" if form_name else "form_error"
        flash(message, category)
    
    @staticmethod
    def login_error(message):
        """
        Add a login-specific error message.
        
        Args:
            message (str): Login error message to display
        """
        flash(message, 'user_login_error')
    
    @staticmethod
    def register_error(message):
        """
        Add a registration-specific error message.
        
        Args:
            message (str): Registration error message to display
        """
        flash(message, 'user_register_error')
    
    @staticmethod
    def custom(message, category):
        """
        Add a custom flash message with a specific category.
        
        Args:
            message (str): Message to display
            category (str): Custom category for the message
        """
        flash(message, category)


# Convenience functions for quick access
def flash_success(message):
    """Quick success flash message."""
    FlashService.success(message)

def flash_error(message):
    """Quick error flash message."""
    FlashService.error(message)

def flash_warning(message):
    """Quick warning flash message."""
    FlashService.warning(message)

def flash_info(message):
    """Quick info flash message."""
    FlashService.info(message)

def flash_form_error(message, form_name=None):
    """Quick form error flash message."""
    FlashService.form_error(message, form_name)

def flash_login_error(message):
    """Quick login error flash message."""
    FlashService.login_error(message)

def flash_register_error(message):
    """Quick registration error flash message."""
    FlashService.register_error(message)


# Common message templates
class FlashMessages:
    """
    Pre-defined flash message templates for common scenarios.
    """
    
    # Success messages
    USER_CREATED = "Account created successfully! Welcome to {app_name}."
    USER_UPDATED = "Profile updated successfully."
    PASSWORD_CHANGED = "Password changed successfully."
    LOGIN_SUCCESS = "Welcome back! You have been logged in successfully."
    LOGOUT_SUCCESS = "You have been logged out successfully."
    
    # Error messages
    GENERIC_ERROR = "An unexpected error occurred. Please try again."
    PERMISSION_DENIED = "You don't have permission to access this resource."
    SESSION_EXPIRED = "Your session has expired. Please log in again."
    INVALID_REQUEST = "Invalid request. Please check your input and try again."
    
    # Warning messages
    UNSAVED_CHANGES = "You have unsaved changes that will be lost if you continue."
    BETA_FEATURE = "This is a beta feature. Some functionality may be limited."
    MAINTENANCE_MODE = "The system is currently under maintenance. Some features may be unavailable."
    
    # Info messages
    FEATURE_UPDATED = "This feature has been updated with new functionality."
    SCHEDULED_MAINTENANCE = "Scheduled maintenance is planned for {date}."
    NEW_FEATURES = "New features are now available! Check out what's new."
    
    @classmethod
    def format_message(cls, template, **kwargs):
        """
        Format a message template with provided variables.
        
        Args:
            template (str): Message template with placeholders
            **kwargs: Variables to substitute in the template
            
        Returns:
            str: Formatted message
        """
        return template.format(**kwargs)


# Usage examples for documentation:
"""
Example usage in controllers:

from src.utils.flash_utils import FlashService, flash_success, FlashMessages

# Using the service class
FlashService.success("Operation completed successfully!")
FlashService.error("Something went wrong.")
FlashService.warning("Please review your input.")

# Using convenience functions
flash_success("Data saved successfully!")
flash_error("Failed to save data.")

# Using predefined messages
flash_success(FlashMessages.format_message(
    FlashMessages.USER_CREATED, 
    app_name="My App"
))

# Form-specific errors (won't appear in toast)
FlashService.login_error("Invalid username or password.")
FlashService.form_error("Please fill in all required fields.", "contact")

# Custom categories
FlashService.custom("Admin notification", "admin_alert")
"""