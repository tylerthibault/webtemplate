"""
Integration test for authentication flow (login/logout).

Tests the complete authentication process as defined in
specs/001-frontend-landingpage/quickstart.md - Scenario 3

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json
from src.models import User, CoatHanger, db


class TestAuthFlowIntegration:
    """Test complete login/logout flow from end to end."""
    
    def test_complete_login_logout_flow(self, client, db_session):
        """
        Test full authentication cycle: register → login → logout.
        
        Flow: Register → Login → Verify session → Logout → Session cleared
        """
        # Arrange - Register a user first
        registration_data = {
            'email': 'authflow@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Auth Flow User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Act - Login
        login_data = {
            'email': 'authflow@example.com',
            'password': 'SecurePass123!'
        }
        login_response = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert - Login successful
        assert login_response.status_code == 200
        login_result = json.loads(login_response.data)
        assert login_result['success'] is True
        assert login_result['authenticated'] is True
        
        # Assert - Session exists in database (coat hanger)
        user = User.query.filter_by(email='authflow@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger is not None
        
        # Act - Check session status
        session_response = client.get('/auth/session')
        session_data = json.loads(session_response.data)
        assert session_data['authenticated'] is True
        assert session_data['user']['email'] == 'authflow@example.com'
        
        # Act - Logout
        logout_response = client.post('/auth/logout')
        
        # Assert - Logout successful
        assert logout_response.status_code == 200
        logout_data = json.loads(logout_response.data)
        assert logout_data['success'] is True
        
        # Assert - Session cleared from database
        coat_hanger_after_logout = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger_after_logout is None
        
        # Assert - Session check returns not authenticated
        final_session_response = client.get('/auth/session')
        final_session_data = json.loads(final_session_response.data)
        assert final_session_data['authenticated'] is False
    
    def test_login_with_wrong_password(self, client, db_session):
        """
        Test login failure with incorrect password.
        
        Flow: Register → Attempt login with wrong password → Get error
        """
        # Arrange - Register user
        registration_data = {
            'email': 'wrongpass@example.com',
            'password': 'CorrectPass123!',
            'full_name': 'Wrong Pass User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Act - Attempt login with wrong password
        login_data = {
            'email': 'wrongpass@example.com',
            'password': 'WrongPassword456!'
        }
        response = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert - Login failed
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['authenticated'] is False
        
        # Assert - No session created
        user = User.query.filter_by(email='wrongpass@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger is None
    
    def test_login_with_nonexistent_email(self, client, db_session):
        """
        Test login failure with email that doesn't exist.
        
        Flow: Attempt login with unregistered email → Get error
        """
        # Act
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['authenticated'] is False
    
    def test_logout_without_active_session(self, client, db_session):
        """
        Test logout when no session exists.
        
        Flow: Attempt logout without being logged in → Get error
        """
        # Act
        response = client.post('/auth/logout')
        
        # Assert
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_multiple_logins_same_user(self, client, db_session):
        """
        Test that multiple logins replace the previous session.
        
        Flow: Login → Login again → Only one session exists
        """
        # Arrange - Register user
        registration_data = {
            'email': 'multilogin@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Multi Login User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Act - First login
        login_data = {
            'email': 'multilogin@example.com',
            'password': 'SecurePass123!'
        }
        first_login = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        assert first_login.status_code == 200
        
        # Act - Second login (should replace first session)
        second_login = client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        assert second_login.status_code == 200
        
        # Assert - Only one coat hanger entry exists
        user = User.query.filter_by(email='multilogin@example.com').first()
        coat_hangers = CoatHanger.query.filter_by(user_id=user.id).all()
        assert len(coat_hangers) == 1
    
    def test_session_persistence_across_requests(self, client, db_session):
        """
        Test that session persists across multiple requests.
        
        Flow: Login → Multiple authenticated requests → All succeed
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'persistence@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Persistence User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'persistence@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Act - Make multiple session checks
        for _ in range(3):
            response = client.get('/auth/session')
            data = json.loads(response.data)
            
            # Assert - All checks show authenticated
            assert response.status_code == 200
            assert data['authenticated'] is True
            assert data['user']['email'] == 'persistence@example.com'
    
    def test_login_updates_coat_hanger_timestamp(self, client, db_session):
        """
        Test that login creates/updates coat hanger with timestamp.
        
        Flow: Login → Verify coat hanger created_at and updated_at
        """
        # Arrange - Register user
        registration_data = {
            'email': 'timestamp@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Timestamp User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        # Act - Login
        login_data = {
            'email': 'timestamp@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert - Coat hanger has timestamps
        user = User.query.filter_by(email='timestamp@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger is not None
        assert coat_hanger.created_at is not None
        assert coat_hanger.updated_at is not None
