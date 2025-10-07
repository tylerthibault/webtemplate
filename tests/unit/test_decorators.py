"""
Unit tests for custom decorators.

Tests login_required, guest_only, and admin_required decorators.
"""

import pytest
from flask import session
from src.logic.decorators import login_required, guest_only, admin_required
from src.logic.auth_service import AuthService


class TestLoginRequiredDecorator:
    """Test @login_required decorator."""
    
    def test_login_required_allows_authenticated(self, app, client):
        """Test that authenticated users can access protected route."""
        with app.app_context():
            # Register and login
            AuthService.register_user(
                email='decortest@example.com',
                password='DecorTest123',
                full_name='Decorator Test'
            )
            
            login_result = AuthService.authenticate_user(
                email='decortest@example.com',
                password='DecorTest123'
            )
            
            # Create a test route
            @app.route('/protected')
            @login_required
            def protected_route():
                return 'Protected content', 200
            
            # Set session and access route
            with client.session_transaction() as sess:
                sess['session_hash'] = login_result['session_hash']
            
            response = client.get('/protected')
            assert response.status_code == 200
            assert b'Protected content' in response.data
    
    def test_login_required_blocks_unauthenticated(self, app, client):
        """Test that unauthenticated users are redirected."""
        with app.app_context():
            # Create a test route
            @app.route('/protected-route')
            @login_required
            def protected_route():
                return 'Protected content', 200
            
            # Try to access without login
            response = client.get('/protected-route')
            assert response.status_code == 302  # Redirect
            assert '/login' in response.location
    
    def test_login_required_json_request(self, app, client):
        """Test that JSON requests get JSON error response."""
        with app.app_context():
            # Create a test API route
            @app.route('/api/protected')
            @login_required
            def protected_api():
                return {'data': 'secret'}, 200
            
            # Try to access without login
            response = client.get(
                '/api/protected',
                headers={'Content-Type': 'application/json'}
            )
            assert response.status_code == 401
            json_data = response.get_json()
            assert json_data['success'] is False


class TestGuestOnlyDecorator:
    """Test @guest_only decorator."""
    
    def test_guest_only_allows_unauthenticated(self, app, client):
        """Test that unauthenticated users can access guest routes."""
        with app.app_context():
            # Create a test route
            @app.route('/guest-route')
            @guest_only
            def guest_route():
                return 'Guest content', 200
            
            # Access without login
            response = client.get('/guest-route')
            assert response.status_code == 200
            assert b'Guest content' in response.data
    
    def test_guest_only_redirects_authenticated(self, app, client):
        """Test that authenticated users are redirected from guest routes."""
        with app.app_context():
            # Register and login
            AuthService.register_user(
                email='guestdecor@example.com',
                password='GuestDecor123',
                full_name='Guest Decorator Test'
            )
            
            login_result = AuthService.authenticate_user(
                email='guestdecor@example.com',
                password='GuestDecor123'
            )
            
            # Create a test route
            @app.route('/guest-only-route')
            @guest_only
            def guest_route():
                return 'Guest content', 200
            
            # Set session and try to access
            with client.session_transaction() as sess:
                sess['session_hash'] = login_result['session_hash']
            
            response = client.get('/guest-only-route')
            assert response.status_code == 302  # Redirect
            assert '/dashboard' in response.location


class TestAdminRequiredDecorator:
    """Test @admin_required decorator."""
    
    def test_admin_required_blocks_unauthenticated(self, app, client):
        """Test that unauthenticated users cannot access admin routes."""
        with app.app_context():
            # Create a test route
            @app.route('/admin-route')
            @admin_required
            def admin_route():
                return 'Admin content', 200
            
            # Try to access without login
            response = client.get('/admin-route')
            assert response.status_code == 302  # Redirect
            assert '/login' in response.location
    
    def test_admin_required_blocks_non_admin(self, app, client):
        """Test that non-admin users cannot access admin routes."""
        with app.app_context():
            # Register regular user
            AuthService.register_user(
                email='regular@example.com',
                password='Regular123',
                full_name='Regular User'
            )
            
            login_result = AuthService.authenticate_user(
                email='regular@example.com',
                password='Regular123'
            )
            
            # Create a test route
            @app.route('/admin-only-route')
            @admin_required
            def admin_route():
                return 'Admin content', 200
            
            # Set session and try to access
            with client.session_transaction() as sess:
                sess['session_hash'] = login_result['session_hash']
            
            response = client.get('/admin-only-route')
            assert response.status_code == 403  # Forbidden


class TestDecoratorChaining:
    """Test chaining multiple decorators."""
    
    def test_multiple_decorators(self, app, client):
        """Test that multiple decorators work together."""
        with app.app_context():
            # Create a route with multiple decorators
            @app.route('/multi-decorator')
            @login_required
            def multi_decorated():
                return 'Multi decorated', 200
            
            # Try without authentication
            response = client.get('/multi-decorator')
            assert response.status_code == 302  # Redirected by login_required
