import secrets
import hashlib
from flask import session

def generate_csrf_token():
    """Generate a CSRF token for forms."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    return session['csrf_token']

def validate_csrf_token(token):
    """Validate the submitted CSRF token."""
    if 'csrf_token' not in session:
        return False
    return secrets.compare_digest(session['csrf_token'], token)

def csrf_protect():
    """Decorator or function to protect routes from CSRF attacks."""
    from flask import request, abort
    
    if request.method == "POST":
        token = request.form.get('csrf_token', '')
        if not validate_csrf_token(token):
            abort(403)  # Forbidden