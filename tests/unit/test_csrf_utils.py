"""
Unit tests for CSRF utilities.

Tests token generation, validation, and rotation.
"""

import pytest
from flask import session
from src.utils.csrf_utils import CSRFUtils, csrf_protect


class TestTokenGeneration:
    """Test CSRF token generation."""
    
    def test_generate_csrf_token(self, app, client):
        """Test generating a new CSRF token."""
        with client.session_transaction() as sess:
            token = CSRFUtils.generate_csrf_token()
            assert token is not None
            assert isinstance(token, str)
            assert len(token) == 64  # 32 bytes = 64 hex chars
            assert token == sess['_csrf_token']
    
    def test_generate_unique_tokens(self, app, client):
        """Test that generated tokens are unique."""
        with client.session_transaction() as sess:
            token1 = CSRFUtils.generate_csrf_token()
            token2 = CSRFUtils.generate_csrf_token()
            assert token1 != token2


class TestTokenRetrieval:
    """Test CSRF token retrieval."""
    
    def test_get_existing_token(self, app, client):
        """Test getting existing token from session."""
        with client.session_transaction() as sess:
            # Generate a token first
            original_token = CSRFUtils.generate_csrf_token()
            
            # Get the same token
            retrieved_token = CSRFUtils.get_csrf_token()
            assert retrieved_token == original_token
    
    def test_get_token_generates_if_missing(self, app, client):
        """Test that get_csrf_token generates token if none exists."""
        with client.session_transaction() as sess:
            # Ensure no token exists
            sess.pop('_csrf_token', None)
            
            # Get token should generate new one
            token = CSRFUtils.get_csrf_token()
            assert token is not None
            assert token == sess['_csrf_token']


class TestTokenValidation:
    """Test CSRF token validation."""
    
    def test_validate_correct_token(self, app, client):
        """Test validation passes for correct token."""
        with client.session_transaction() as sess:
            token = CSRFUtils.generate_csrf_token()
            assert CSRFUtils.validate_csrf_token(token) is True
    
    def test_validate_incorrect_token(self, app, client):
        """Test validation fails for incorrect token."""
        with client.session_transaction() as sess:
            CSRFUtils.generate_csrf_token()
            wrong_token = 'a' * 64
            assert CSRFUtils.validate_csrf_token(wrong_token) is False
    
    def test_validate_empty_token(self, app, client):
        """Test validation fails for empty token."""
        with client.session_transaction() as sess:
            CSRFUtils.generate_csrf_token()
            assert CSRFUtils.validate_csrf_token('') is False
            assert CSRFUtils.validate_csrf_token(None) is False
    
    def test_validate_without_session_token(self, app, client):
        """Test validation fails when no session token exists."""
        with client.session_transaction() as sess:
            sess.pop('_csrf_token', None)
            assert CSRFUtils.validate_csrf_token('some-token') is False


class TestTokenClearing:
    """Test CSRF token clearing."""
    
    def test_clear_csrf_token(self, app, client):
        """Test clearing CSRF token from session."""
        with client.session_transaction() as sess:
            # Generate a token
            CSRFUtils.generate_csrf_token()
            assert '_csrf_token' in sess
            
            # Clear token
            CSRFUtils.clear_csrf_token()
            assert '_csrf_token' not in sess
    
    def test_clear_when_no_token(self, app, client):
        """Test clearing when no token exists doesn't error."""
        with client.session_transaction() as sess:
            sess.pop('_csrf_token', None)
            # Should not raise exception
            CSRFUtils.clear_csrf_token()


class TestTokenRotation:
    """Test CSRF token rotation."""
    
    def test_rotate_csrf_token(self, app, client):
        """Test rotating CSRF token generates new token."""
        with client.session_transaction() as sess:
            original_token = CSRFUtils.generate_csrf_token()
            new_token = CSRFUtils.rotate_csrf_token()
            
            assert new_token != original_token
            assert sess['_csrf_token'] == new_token


class TestCSRFProtectDecorator:
    """Test @csrf_protect decorator."""
    
    def test_csrf_protect_allows_valid_token(self, app, client):
        """Test that valid CSRF token allows request."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-protected', methods=['POST'])
            @csrf_protect
            def protected_route():
                return {'success': True}, 200
            
            # Generate token
            with client.session_transaction() as sess:
                token = CSRFUtils.generate_csrf_token()
            
            # Make request with valid token
            response = client.post(
                '/csrf-protected',
                json={'csrf_token': token}
            )
            assert response.status_code == 200
    
    def test_csrf_protect_blocks_invalid_token(self, app, client):
        """Test that invalid CSRF token blocks request."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-protected-2', methods=['POST'])
            @csrf_protect
            def protected_route():
                return {'success': True}, 200
            
            # Generate token but send wrong one
            with client.session_transaction() as sess:
                CSRFUtils.generate_csrf_token()
            
            # Make request with invalid token
            response = client.post(
                '/csrf-protected-2',
                json={'csrf_token': 'wrong-token'}
            )
            assert response.status_code == 403
    
    def test_csrf_protect_blocks_missing_token(self, app, client):
        """Test that missing CSRF token blocks request."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-protected-3', methods=['POST'])
            @csrf_protect
            def protected_route():
                return {'success': True}, 200
            
            # Make request without token
            response = client.post(
                '/csrf-protected-3',
                json={'data': 'test'}
            )
            assert response.status_code == 403
    
    def test_csrf_protect_allows_get_requests(self, app, client):
        """Test that GET requests bypass CSRF protection."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-protected-get', methods=['GET', 'POST'])
            @csrf_protect
            def protected_route():
                return {'success': True}, 200
            
            # GET should work without token
            response = client.get('/csrf-protected-get')
            assert response.status_code == 200
    
    def test_csrf_protect_checks_form_data(self, app, client):
        """Test that CSRF protection checks form data."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-form', methods=['POST'])
            @csrf_protect
            def form_route():
                return 'Form submitted', 200
            
            # Generate token
            with client.session_transaction() as sess:
                token = CSRFUtils.generate_csrf_token()
            
            # Submit form with token
            response = client.post(
                '/csrf-form',
                data={'csrf_token': token, 'name': 'Test'}
            )
            assert response.status_code == 200
    
    def test_csrf_protect_checks_headers(self, app, client):
        """Test that CSRF protection checks X-CSRF-Token header."""
        with app.app_context():
            # Create a protected route
            @app.route('/csrf-header', methods=['POST'])
            @csrf_protect
            def header_route():
                return {'success': True}, 200
            
            # Generate token
            with client.session_transaction() as sess:
                token = CSRFUtils.generate_csrf_token()
            
            # Send token in header
            response = client.post(
                '/csrf-header',
                headers={'X-CSRF-Token': token}
            )
            assert response.status_code == 200
