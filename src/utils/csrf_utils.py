"""
CSRF (Cross-Site Request Forgery) protection utilities.

Custom CSRF implementation using Flask sessions.
No Flask-WTF dependency - following constitutional principles.
"""

import secrets
from flask import session


class CSRFUtils:
    """
    CSRF protection utilities for form submissions.
    
    Constitutional compliance: Custom implementation without Flask-WTF.
    Uses Flask sessions to store and validate CSRF tokens.
    """
    
    CSRF_TOKEN_LENGTH = 32
    CSRF_SESSION_KEY = '_csrf_token'
    
    @classmethod
    def generate_csrf_token(cls):
        """
        Generate a new CSRF token and store in session.
        
        Returns:
            str: CSRF token (hex string)
        """
        token = secrets.token_hex(cls.CSRF_TOKEN_LENGTH)
        session[cls.CSRF_SESSION_KEY] = token
        return token
    
    @classmethod
    def get_csrf_token(cls):
        """
        Get current CSRF token from session or generate new one.
        
        Returns:
            str: CSRF token
        """
        if cls.CSRF_SESSION_KEY not in session:
            return cls.generate_csrf_token()
        return session[cls.CSRF_SESSION_KEY]
    
    @classmethod
    def validate_csrf_token(cls, token):
        """
        Validate CSRF token against session token.
        
        Args:
            token (str): Token to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not token:
            return False
        
        session_token = session.get(cls.CSRF_SESSION_KEY)
        if not session_token:
            return False
        
        # Use secrets.compare_digest for timing attack protection
        return secrets.compare_digest(token, session_token)
    
    @classmethod
    def clear_csrf_token(cls):
        """
        Clear CSRF token from session.
        
        Useful after form submission or logout.
        """
        session.pop(cls.CSRF_SESSION_KEY, None)
    
    @classmethod
    def rotate_csrf_token(cls):
        """
        Generate new CSRF token (rotation for security).
        
        Should be called after successful form submission.
        
        Returns:
            str: New CSRF token
        """
        return cls.generate_csrf_token()


def csrf_protect(f):
    """
    Decorator to protect routes with CSRF validation.
    
    Usage:
        @app.route('/submit', methods=['POST'])
        @csrf_protect
        def submit_form():
            # Process form
            pass
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function with CSRF protection
    """
    from functools import wraps
    from flask import request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only check CSRF for state-changing methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get token from request
            token = None
            
            # Check JSON body
            if request.is_json:
                token = request.json.get('csrf_token')
            # Check form data
            elif request.form:
                token = request.form.get('csrf_token')
            # Check headers
            else:
                token = request.headers.get('X-CSRF-Token')
            
            # Validate token
            if not CSRFUtils.validate_csrf_token(token):
                if request.is_json or request.headers.get('Content-Type') == 'application/json':
                    return jsonify({
                        'success': False,
                        'message': 'CSRF token validation failed'
                    }), 403
                
                # For HTML forms, could redirect or show error page
                return 'CSRF token validation failed', 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def inject_csrf_token():
    """
    Context processor to inject CSRF token into all templates.
    
    Register with Flask app:
        app.context_processor(inject_csrf_token)
    
    Returns:
        dict: Context with csrf_token function
    """
    return {
        'csrf_token': CSRFUtils.get_csrf_token
    }
