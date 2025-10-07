"""
Contract test for POST /auth/login endpoint.

Tests the user login API contract as defined in
specs/001-frontend-landingpage/contracts/auth-api.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json


class TestAuthLoginContract:
    """Test contract for user login endpoint."""
    
    def test_successful_login(self, client):
        """
        Test successful login with valid credentials.
        
        Contract: POST /auth/login
        Expected: 200 OK with user data and session
        """
        # Arrange - first register a user
        register_payload = {
            'email': 'logintest@example.com',
            'full_name': 'Login Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        # Act - login with correct credentials
        login_payload = {
            'email': 'logintest@example.com',
            'password': 'password123'
        }
        response = client.post(
            '/auth/login',
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['email'] == 'logintest@example.com'
        assert data['user']['full_name'] == 'Login Test'
        assert 'password' not in data['user']
    
    def test_login_with_invalid_email(self, client):
        """
        Test login with email that doesn't exist.
        
        Contract: 401 Unauthorized
        """
        # Arrange
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid email or password'
    
    def test_login_with_wrong_password(self, client):
        """
        Test login with incorrect password.
        
        Contract: 401 Unauthorized
        """
        # Arrange - register a user
        register_payload = {
            'email': 'wrongpass@example.com',
            'full_name': 'Wrong Pass Test',
            'password': 'correctpassword'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        # Act - login with wrong password
        login_payload = {
            'email': 'wrongpass@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(
            '/auth/login',
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['message'] == 'Invalid email or password'
    
    def test_login_with_missing_email(self, client):
        """
        Test login with missing email field.
        
        Contract: 400 Bad Request
        """
        # Arrange
        payload = {
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Email and password are required' in data['message']
    
    def test_login_with_missing_password(self, client):
        """
        Test login with missing password field.
        
        Contract: 400 Bad Request
        """
        # Arrange
        payload = {
            'email': 'user@example.com'
        }
        
        # Act
        response = client.post(
            '/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Email and password are required' in data['message']
    
    def test_login_creates_session(self, client):
        """
        Test that successful login creates a session.
        
        Contract: Session cookie should be set
        """
        # Arrange - register a user
        register_payload = {
            'email': 'session@example.com',
            'full_name': 'Session Test',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(register_payload),
                   content_type='application/json')
        
        # Act - login
        login_payload = {
            'email': 'session@example.com',
            'password': 'password123'
        }
        response = client.post(
            '/auth/login',
            data=json.dumps(login_payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        # Check for session cookie (Flask sets 'session' cookie)
        assert any('session' in cookie.lower() for cookie in response.headers.getlist('Set-Cookie'))