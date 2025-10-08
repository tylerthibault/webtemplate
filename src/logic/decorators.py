"""
Custom decorators for authentication and authorization.

Implements login_required decorator without Flask-Login.
Following constitutional principles - logic layer handles auth checks.
"""

from functools import wraps
from flask import redirect, url_for, jsonify, request
from src.logic.auth_service import AuthService


def login_required(f):
    """
    Decorator to require authentication for routes.

    Checks if user has valid session via AuthService.
    Redirects to login page for HTML requests, returns 401 for JSON.

    Usage:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            return render_template('dashboard.html')

    Args:
        f: Function to decorate

    Returns:
        Decorated function that checks authentication
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not AuthService.is_authenticated():
            # Check if this is a JSON request or client wants JSON response
            wants_json = (
                request.is_json
                or request.headers.get("Content-Type") == "application/json"
                or request.accept_mimetypes.best_match(
                    ["application/json", "text/html"]
                )
                == "application/json"
                or request.path.startswith("/api/")  # API endpoints always return JSON
            )

            if wants_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authentication required",
                            "authenticated": False,
                        }
                    ),
                    401,
                )

            # Redirect to login page for HTML requests
            return redirect(url_for("auth.login"))

        # User is authenticated, proceed with the request
        return f(*args, **kwargs)

    return decorated_function


def guest_only(f):
    """
    Decorator to restrict routes to non-authenticated users only.

    Redirects authenticated users to dashboard.
    Useful for login/register pages that should not be accessible when logged in.

    Usage:
        @app.route('/login')
        @guest_only
        def login():
            return render_template('login.html')

    Args:
        f: Function to decorate

    Returns:
        Decorated function that checks authentication
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if AuthService.is_authenticated():
            # User is already logged in, redirect to dashboard
            return redirect(url_for("main.dashboard"))

        # User is not authenticated, proceed with the request
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges.

    Note: This is a placeholder for future admin functionality.
    Currently just checks for authentication.

    Usage:
        @app.route('/admin/users')
        @admin_required
        def manage_users():
            return render_template('admin/users.html')

    Args:
        f: Function to decorate

    Returns:
        Decorated function that checks admin authorization
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated first
        if not AuthService.is_authenticated():
            if (
                request.is_json
                or request.headers.get("Content-Type") == "application/json"
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authentication required",
                            "authenticated": False,
                        }
                    ),
                    401,
                )

            return redirect(url_for("auth.login"))

        # TODO: Add actual admin role checking when user roles are implemented
        # For now, all authenticated users have admin access

        return f(*args, **kwargs)

    return decorated_function
