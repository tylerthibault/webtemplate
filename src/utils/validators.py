"""
Input validation utilities for user profile data.

Provides reusable validation functions with security considerations
for profile fields like bio and password strength.
"""

import re
from typing import Tuple


def validate_bio(bio: str) -> Tuple[bool, str]:
    """
    Validate and sanitize user bio text.
    
    Checks length constraint and performs basic XSS prevention by
    removing potentially dangerous HTML/script tags.
    
    Args:
        bio: Bio text to validate
        
    Returns:
        Tuple of (is_valid, sanitized_bio_or_error_message)
        
    Example:
        >>> validate_bio("Hello world!")
        (True, "Hello world!")
        >>> validate_bio("A" * 501)
        (False, "Bio must be 500 characters or less")
        >>> validate_bio("<script>alert('xss')</script>Hello")
        (True, "Hello")
    """
    if not bio:
        return True, ""
    
    # Check length
    if len(bio) > 500:
        return False, "Bio must be 500 characters or less"
    
    # Basic XSS sanitization - remove HTML tags
    sanitized = re.sub(r'<[^>]*>', '', bio)
    
    # Remove common script injection patterns
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    return True, sanitized.strip()


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets strength requirements.
    
    Requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message_or_empty)
        
    Example:
        >>> validate_password_strength("Password123")
        (True, "")
        >>> validate_password_strength("weak")
        (False, "Password must be at least 8 characters")
        >>> validate_password_strength("nodigits")
        (False, "Password must contain at least one digit")
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""
