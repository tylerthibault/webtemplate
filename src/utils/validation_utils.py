"""
Validation utilities for form inputs.

Centralized validation functions following constitutional principles.
"""

import re
from typing import Tuple, Dict, Optional


class ValidationUtils:
    """
    Validation utilities for common input types.
    
    Constitutional compliance: Reusable validation logic
    for both client-side and server-side validation.
    """
    
    # Email validation regex (RFC 5322 simplified)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Password complexity regex patterns
    PASSWORD_UPPERCASE = re.compile(r'[A-Z]')
    PASSWORD_LOWERCASE = re.compile(r'[a-z]')
    PASSWORD_DIGIT = re.compile(r'[0-9]')
    PASSWORD_SPECIAL = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, 'Email cannot be empty'
        
        email = email.strip()
        
        if len(email) > 120:
            return False, 'Email must not exceed 120 characters'
        
        if not cls.EMAIL_REGEX.match(email):
            return False, 'Invalid email format'
        
        return True, None
    
    @classmethod
    def validate_password_strength(
        cls, 
        password: str,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
            min_length: Minimum password length (default 8)
            require_uppercase: Require uppercase letter (default True)
            require_lowercase: Require lowercase letter (default True)
            require_digit: Require digit (default True)
            require_special: Require special character (default False)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, 'Password cannot be empty'
        
        if len(password) < min_length:
            return False, f'Password must be at least {min_length} characters long'
        
        if len(password) > 128:
            return False, 'Password must not exceed 128 characters'
        
        if require_uppercase and not cls.PASSWORD_UPPERCASE.search(password):
            return False, 'Password must contain at least one uppercase letter'
        
        if require_lowercase and not cls.PASSWORD_LOWERCASE.search(password):
            return False, 'Password must contain at least one lowercase letter'
        
        if require_digit and not cls.PASSWORD_DIGIT.search(password):
            return False, 'Password must contain at least one number'
        
        if require_special and not cls.PASSWORD_SPECIAL.search(password):
            return False, 'Password must contain at least one special character'
        
        return True, None
    
    @classmethod
    def validate_name(
        cls, 
        name: str, 
        min_length: int = 2, 
        max_length: int = 100
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate name field.
        
        Args:
            name: Name to validate
            min_length: Minimum name length (default 2)
            max_length: Maximum name length (default 100)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, 'Name cannot be empty'
        
        name = name.strip()
        
        if len(name) < min_length:
            return False, f'Name must be at least {min_length} characters'
        
        if len(name) > max_length:
            return False, f'Name must not exceed {max_length} characters'
        
        # Check for invalid characters (only letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            return False, 'Name contains invalid characters'
        
        return True, None
    
    @classmethod
    def validate_text_length(
        cls,
        text: str,
        field_name: str,
        min_length: int = 1,
        max_length: int = 1000
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate text field length.
        
        Args:
            text: Text to validate
            field_name: Name of the field for error messages
            min_length: Minimum text length
            max_length: Maximum text length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, f'{field_name} cannot be empty'
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f'{field_name} must be at least {min_length} characters'
        
        if len(text) > max_length:
            return False, f'{field_name} must not exceed {max_length} characters'
        
        return True, None
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """
        Sanitize text to prevent XSS attacks.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text with HTML entities escaped
        """
        if not text:
            return text
        
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        sanitized = text
        for char, escape in replacements.items():
            sanitized = sanitized.replace(char, escape)
        
        return sanitized
    
    @classmethod
    def validate_form_data(
        cls, 
        data: dict, 
        rules: Dict[str, dict]
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate multiple form fields against rules.
        
        Args:
            data: Dictionary of field names and values
            rules: Dictionary of field names and validation rules
                   Example: {
                       'email': {'type': 'email', 'required': True},
                       'password': {'type': 'password', 'min_length': 8},
                       'name': {'type': 'name', 'min_length': 2}
                   }
                   
        Returns:
            Tuple of (is_valid, errors_dict)
        """
        errors = {}
        
        for field_name, field_rules in rules.items():
            value = data.get(field_name, '')
            
            # Check required fields
            if field_rules.get('required', False) and not value:
                errors[field_name] = f'{field_name.capitalize()} is required'
                continue
            
            # Skip validation if field is optional and empty
            if not value and not field_rules.get('required', False):
                continue
            
            # Validate based on type
            field_type = field_rules.get('type')
            
            if field_type == 'email':
                is_valid, error = cls.validate_email(value)
                if not is_valid:
                    errors[field_name] = error
            
            elif field_type == 'password':
                is_valid, error = cls.validate_password_strength(
                    value,
                    min_length=field_rules.get('min_length', 8),
                    require_uppercase=field_rules.get('require_uppercase', True),
                    require_lowercase=field_rules.get('require_lowercase', True),
                    require_digit=field_rules.get('require_digit', True),
                    require_special=field_rules.get('require_special', False)
                )
                if not is_valid:
                    errors[field_name] = error
            
            elif field_type == 'name':
                is_valid, error = cls.validate_name(
                    value,
                    min_length=field_rules.get('min_length', 2),
                    max_length=field_rules.get('max_length', 100)
                )
                if not is_valid:
                    errors[field_name] = error
            
            elif field_type == 'text':
                is_valid, error = cls.validate_text_length(
                    value,
                    field_name=field_name.capitalize(),
                    min_length=field_rules.get('min_length', 1),
                    max_length=field_rules.get('max_length', 1000)
                )
                if not is_valid:
                    errors[field_name] = error
        
        is_valid = len(errors) == 0
        return is_valid, errors
