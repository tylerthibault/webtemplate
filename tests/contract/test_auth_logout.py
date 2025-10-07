"""
Contract test for POST /auth/logout endpoint.

Tests the user logout API contract as defined in
specs/001-frontend-landingpage/contracts/auth-api.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json


class TestAuthLogoutContract:
    """Test contract for user logout endpoint."""
    
    def test_successful_logout(self, client):
        """
        Test successful logout of authenticated user.
        
        Contract: POST /auth/logout
        Expected: 200 OK with success message
        """
        # Arrange - register and login a user
        register_payload = {
            'email': 'logout@example.com',
            'full_name': 'Logout Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'logout@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        # Act - logout
        response = client.post('/auth/logout')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Logout successful'
    
    def test_logout_without_session(self, client):
        """
        Test logout when user is not logged in.
        
        Contract: 401 Unauthorized
        """
        # Act - attempt logout without logging in
        response = client.post('/auth/logout')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'No active session'
    
    def test_logout_clears_session(self, client):
        """
        Test that logout clears the session data.
        
        Contract: Session should be invalidated
        """
        # Arrange - register and login
        register_payload = {
            'email': 'clearsession@example.com',
            'full_name': 'Clear Session Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'clearsession@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        # Act - logout
        response = client.post('/auth/logout')
        
        # Assert - logout successful
        assert response.status_code == 200
        
        # Verify session is cleared by attempting to access protected resource
        session_response = client.get('/auth/session')
        session_data = json.loads(session_response.data)
        assert session_data['authenticated'] is False
    
    def test_logout_removes_coat_hanger_entry(self, client):
        """
        Test that logout removes the session entry from coat hanger table.
        
        Contract: Session tracking entry should be deleted
        """
        # Arrange - register and login
        register_payload = {
            'email': 'coathanger@example.com',
            'full_name': 'Coat Hanger Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        login_payload = {
            'email': 'coathanger@example.com',
            'password': 'password123'
        }
        client.post('/auth/login', data=json.dumps(login_payload),
                   content_type='application/json')
        
        # Act - logout
        response = client.post('/auth/logout')
        
        # Assert
        assert response.status_code == 200
        # Additional verification would check coat_hanger table is empty
        # This will be tested in integration tests with database access