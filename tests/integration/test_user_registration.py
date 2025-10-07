"""
Integration test for user registration flow.

Tests the complete user registration process as defined in
specs/001-frontend-landingpage/quickstart.md - Scenario 2

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json
from src.models import User, db


class TestUserRegistrationIntegration:
    """Test complete user registration flow from end to end."""
    
    def test_complete_registration_flow(self, client, db_session):
        """
        Test successful user registration from form to database.
        
        Flow: POST /auth/register → User created → Session established
        """
        # Arrange
        registration_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'full_name': 'John Doe'
        }
        
        # Act - Register user
        response = client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Assert - Registration successful
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user_id' in data
        
        # Assert - User exists in database
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.full_name == 'John Doe'
        assert user.email == 'newuser@example.com'
        
        # Assert - Password is hashed (not plaintext)
        assert user.password_hash != 'SecurePass123!'
        assert len(user.password_hash) > 20  # bcrypt hashes are long
        
        # Assert - User can login immediately after registration
        login_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        }
        login_response = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        assert login_response.status_code == 200
    
    def test_registration_prevents_duplicate_email(self, client, db_session):
        """
        Test that duplicate email registration is prevented.
        
        Flow: Register user → Attempt duplicate → Get error
        """
        # Arrange - First registration
        user_data = {
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'full_name': 'First User'
        }
        
        # Act - Register first user
        first_response = client.post(
            '/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        assert first_response.status_code == 201
        
        # Act - Attempt duplicate registration
        duplicate_data = {
            'email': 'duplicate@example.com',  # Same email
            'password': 'DifferentPass456!',
            'full_name': 'Second User'
        }
        second_response = client.post(
            '/auth/register',
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )
        
        # Assert - Duplicate prevented
        assert second_response.status_code == 400
        response_data = json.loads(second_response.data)
        assert response_data['success'] is False
        assert 'already exists' in response_data['message'].lower()
        
        # Assert - Only one user in database
        users = User.query.filter_by(email='duplicate@example.com').all()
        assert len(users) == 1
        assert users[0].full_name == 'First User'
    
    def test_registration_validation_all_fields(self, client, db_session):
        """
        Test comprehensive validation during registration.
        
        Flow: Submit invalid data → Get specific validation errors
        """
        test_cases = [
            {
                'data': {'email': '', 'password': 'Pass123!', 'full_name': 'John Doe'},
                'expected_error': 'email'
            },
            {
                'data': {'email': 'test@example.com', 'password': '', 'full_name': 'John Doe'},
                'expected_error': 'password'
            },
            {
                'data': {'email': 'test@example.com', 'password': 'Pass123!', 'full_name': ''},
                'expected_error': 'name'
            },
            {
                'data': {'email': 'invalid-email', 'password': 'Pass123!', 'full_name': 'John Doe'},
                'expected_error': 'email'
            },
            {
                'data': {'email': 'test@example.com', 'password': '123', 'full_name': 'John Doe'},
                'expected_error': 'password'
            }
        ]
        
        for test_case in test_cases:
            # Act
            response = client.post(
                '/auth/register',
                data=json.dumps(test_case['data']),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code in [400, 422]
            data = json.loads(response.data)
            assert data['success'] is False
            # Error message should mention the problematic field
            assert test_case['expected_error'] in str(data).lower()
    
    def test_registration_creates_timestamps(self, client, db_session):
        """
        Test that registration creates proper timestamps.
        
        Flow: Register user → Verify created_at and updated_at timestamps
        """
        # Arrange
        user_data = {
            'email': 'timestamp@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Timestamp User'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        
        # Check database for timestamps
        user = User.query.filter_by(email='timestamp@example.com').first()
        assert user is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        # Both timestamps should be very close (within 1 second)
        time_diff = abs((user.updated_at - user.created_at).total_seconds())
        assert time_diff < 1
    
    def test_registration_password_bcrypt_hashing(self, client, db_session):
        """
        Test that passwords are hashed using bcrypt.
        
        Flow: Register user → Verify bcrypt hash format
        """
        # Arrange
        user_data = {
            'email': 'bcrypt@example.com',
            'password': 'TestPassword123!',
            'full_name': 'Bcrypt User'
        }
        
        # Act
        response = client.post(
            '/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        
        # Check password hash format
        user = User.query.filter_by(email='bcrypt@example.com').first()
        assert user is not None
        # bcrypt hashes start with $2b$ (Python bcrypt)
        assert user.password_hash.startswith('$2b$')
        # bcrypt hashes are 60 characters
        assert len(user.password_hash) == 60
