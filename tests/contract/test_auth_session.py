"""
Contract test for GET /auth/session endpoint.

Tests the session status API contract as defined in
specs/001-frontend-landingpage/contracts/auth-api.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json


class TestAuthSessionContract:
    """Test contract for session status endpoint."""
    
    def test_session_authenticated(self, client):
        """
        Test session status for authenticated user.
        
        Contract: GET /auth/session
        Expected: 200 OK with authenticated status and user data
        """
        # Arrange - register and login
        register_payload = {
            'email': 'sessioncheck@example.com',
            'full_name': 'Session Check',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'sessioncheck@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        # Act - check session
        response = client.get('/auth/session')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['authenticated'] is True
        assert 'user' in data
        assert data['user']['email'] == 'sessioncheck@example.com'
        assert data['user']['full_name'] == 'Session Check'
        assert 'session_expires_in' in data
        assert isinstance(data['session_expires_in'], (int, float))
    
    def test_session_not_authenticated(self, client):
        """
        Test session status for non-authenticated user.
        
        Contract: 200 OK with authenticated: false
        """
        # Act - check session without logging in
        response = client.get('/auth/session')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['authenticated'] is False
        assert 'user' not in data
    
    def test_session_expiry_time(self, client):
        """
        Test that session expiry time is calculated correctly.
        
        Contract: session_expires_in should be in seconds (max 600)
        """
        # Arrange - register and login
        register_payload = {
            'email': 'expiry@example.com',
            'full_name': 'Expiry Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'expiry@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        # Act - check session immediately after login
        response = client.get('/auth/session')
        
        # Assert
        data = json.loads(response.data)
        assert data['authenticated'] is True
        # Session should expire in approximately 600 seconds (10 minutes)
        # Allow some margin for execution time
        assert 590 <= data['session_expires_in'] <= 600
    
    def test_session_after_logout(self, client):
        """
        Test session status after logout.
        
        Contract: Should show as not authenticated
        """
        # Arrange - register, login, then logout
        register_payload = {
            'email': 'afterlogout@example.com',
            'full_name': 'After Logout Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'afterlogout@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        client.post('/auth/logout')
        
        # Act - check session after logout
        response = client.get('/auth/session')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is False