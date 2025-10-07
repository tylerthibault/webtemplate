"""
Contract test for POST /auth/register endpoint.

Tests the user registration API contract as defined in
specs/001-frontend-landingpage/contracts/auth-api.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json


class TestAuthRegisterContract:
    """Test contract for user registration endpoint."""
    
    def test_successful_registration(self, client):
        """
        Test successful user registration with valid data.
        
        Contract: POST /auth/register
        Expected: 201 Created with user data
        """
        # Arrange
        payload = {
            'email': 'newuser@example.com',
            'full_name': 'John Doe',
            'password': 'securepass123'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Account created successfully'
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
        assert data['user']['full_name'] == 'John Doe'
        assert 'id' in data['user']
        assert 'password' not in data['user']  # Password should not be returned
    
    def test_registration_with_duplicate_email(self, client):
        """
        Test registration with email that already exists.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange - create first user
        payload = {
            'email': 'duplicate@example.com',
            'full_name': 'First User',
            'password': 'password123'
        }
        client.post('/auth/register', data=json.dumps(payload), 
                   content_type='application/json')
        
        # Act - try to register with same email
        payload['full_name'] = 'Second User'
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
        assert 'email' in data['errors']
    
    def test_registration_with_invalid_email(self, client):
        """
        Test registration with invalid email format.
        
        Contract: 422 Unprocessable Entity
        """
        # Arrange
        payload = {
            'email': 'not-an-email',
            'full_name': 'John Doe',
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 422
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid email format' in data['message']
    
    def test_registration_with_short_password(self, client):
        """
        Test registration with password less than 8 characters.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange
        payload = {
            'email': 'user@example.com',
            'full_name': 'John Doe',
            'password': 'short'  # Less than 8 characters
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
        assert 'password' in data['errors']
    
    def test_registration_with_missing_fields(self, client):
        """
        Test registration with missing required fields.
        
        Contract: 400 Bad Request
        """
        # Arrange - missing password
        payload = {
            'email': 'user@example.com',
            'full_name': 'John Doe'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_registration_with_invalid_name_length(self, client):
        """
        Test registration with full name that's too short or too long.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange - name too short (1 character)
        payload = {
            'email': 'user@example.com',
            'full_name': 'J',
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
    
    def test_response_headers(self, client):
        """
        Test that proper security headers are returned.
        
        Contract: Security headers required
        """
        # Arrange
        payload = {
            'email': 'user@example.com',
            'full_name': 'John Doe',
            'password': 'password123'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.content_type == 'application/json'
        # Additional security headers can be tested here