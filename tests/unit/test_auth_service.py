"""
Unit tests for AuthService.

Tests password hashing, registration validation, login, and session management.
"""

import pytest
from datetime import datetime, timedelta
from src.logic.auth_service import AuthService
from src.models.user import User
from src.models.coat_hanger import CoatHanger


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = 'TestPassword123'
        hashed = AuthService.hash_password(password)
        assert isinstance(hashed, str)
    
    def test_hash_password_different_for_same_password(self):
        """Test that hashing same password produces different hashes (salt)."""
        password = 'TestPassword123'
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test that verify_password works for correct password."""
        password = 'TestPassword123'
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that verify_password fails for incorrect password."""
        password = 'TestPassword123'
        wrong_password = 'WrongPassword456'
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_handles_invalid_hash(self):
        """Test that verify_password handles invalid hash gracefully."""
        password = 'TestPassword123'
        invalid_hash = 'not-a-valid-hash'
        assert AuthService.verify_password(password, invalid_hash) is False


class TestSessionHashGeneration:
    """Test session hash generation."""
    
    def test_generate_session_hash_returns_string(self):
        """Test that generate_session_hash returns a string."""
        user_id = 1
        session_hash = AuthService.generate_session_hash(user_id)
        assert isinstance(session_hash, str)
    
    def test_generate_session_hash_fixed_length(self):
        """Test that session hash is 64 characters (SHA256 hex)."""
        user_id = 1
        session_hash = AuthService.generate_session_hash(user_id)
        assert len(session_hash) == 64
    
    def test_generate_session_hash_unique(self):
        """Test that consecutive hashes are unique."""
        user_id = 1
        hash1 = AuthService.generate_session_hash(user_id)
        hash2 = AuthService.generate_session_hash(user_id)
        assert hash1 != hash2


class TestRegistrationValidation:
    """Test registration data validation."""
    
    def test_validate_valid_data(self, app):
        """Test validation passes for valid registration data."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='ValidPass123',
                full_name='Test User'
            )
            assert is_valid is True
            assert errors == {}
    
    def test_validate_invalid_email(self, app):
        """Test validation fails for invalid email."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='invalid-email',
                password='ValidPass123',
                full_name='Test User'
            )
            assert is_valid is False
            assert 'email' in errors
    
    def test_validate_short_password(self, app):
        """Test validation fails for too short password."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='Short1',
                full_name='Test User'
            )
            assert is_valid is False
            assert 'password' in errors
    
    def test_validate_password_no_uppercase(self, app):
        """Test validation fails for password without uppercase."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='lowercase123',
                full_name='Test User'
            )
            assert is_valid is False
            assert 'password' in errors
    
    def test_validate_password_no_lowercase(self, app):
        """Test validation fails for password without lowercase."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='UPPERCASE123',
                full_name='Test User'
            )
            assert is_valid is False
            assert 'password' in errors
    
    def test_validate_password_no_digit(self, app):
        """Test validation fails for password without digit."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='NoDigitsHere',
                full_name='Test User'
            )
            assert is_valid is False
            assert 'password' in errors
    
    def test_validate_short_name(self, app):
        """Test validation fails for too short name."""
        with app.app_context():
            is_valid, errors = AuthService.validate_registration_data(
                email='test@example.com',
                password='ValidPass123',
                full_name='A'
            )
            assert is_valid is False
            assert 'name' in errors
    
    def test_validate_existing_email(self, app):
        """Test validation fails for existing email."""
        with app.app_context():
            # Create a user first
            User(
                email='existing@example.com',
                full_name='Existing User',
                password_hash=AuthService.hash_password('Password123')
            ).save()
            
            # Try to register with same email
            is_valid, errors = AuthService.validate_registration_data(
                email='existing@example.com',
                password='ValidPass123',
                full_name='New User'
            )
            assert is_valid is False
            assert 'email' in errors


class TestUserRegistration:
    """Test user registration."""
    
    def test_register_user_success(self, app):
        """Test successful user registration."""
        with app.app_context():
            result = AuthService.register_user(
                email='newuser@example.com',
                password='NewUser123',
                full_name='New User'
            )
            
            assert result['success'] is True
            assert 'user_id' in result
            
            # Verify user was created
            user = User.find_by_email('newuser@example.com')
            assert user is not None
            assert user.full_name == 'New User'
    
    def test_register_user_invalid_data(self, app):
        """Test registration fails with invalid data."""
        with app.app_context():
            result = AuthService.register_user(
                email='invalid-email',
                password='short',
                full_name='U'
            )
            
            assert result['success'] is False
            assert 'errors' in result


class TestUserLogin:
    """Test user authentication."""
    
    def test_authenticate_user_success(self, app):
        """Test successful authentication."""
        with app.app_context():
            # Register a user
            AuthService.register_user(
                email='logintest@example.com',
                password='LoginTest123',
                full_name='Login Test'
            )
            
            # Attempt login
            result = AuthService.authenticate_user(
                email='logintest@example.com',
                password='LoginTest123'
            )
            
            assert result['success'] is True
            assert 'user_id' in result
            assert 'session_hash' in result
    
    def test_authenticate_user_wrong_password(self, app):
        """Test authentication fails with wrong password."""
        with app.app_context():
            # Register a user
            AuthService.register_user(
                email='logintest2@example.com',
                password='CorrectPass123',
                full_name='Login Test 2'
            )
            
            # Attempt login with wrong password
            result = AuthService.authenticate_user(
                email='logintest2@example.com',
                password='WrongPass123'
            )
            
            assert result['success'] is False
            assert 'message' in result
    
    def test_authenticate_user_nonexistent(self, app):
        """Test authentication fails for nonexistent user."""
        with app.app_context():
            result = AuthService.authenticate_user(
                email='nonexistent@example.com',
                password='AnyPassword123'
            )
            
            assert result['success'] is False
            assert 'message' in result


class TestSessionManagement:
    """Test session creation and management."""
    
    def test_create_session(self, app):
        """Test session creation."""
        with app.app_context():
            # Register and login
            result = AuthService.register_user(
                email='sessiontest@example.com',
                password='SessionTest123',
                full_name='Session Test'
            )
            user_id = result['user_id']
            
            # Create session
            session_hash = AuthService.create_session(user_id)
            
            assert session_hash is not None
            assert isinstance(session_hash, str)
            
            # Verify coat hanger entry exists
            coat_hanger = CoatHanger.find_by_session_hash(session_hash)
            assert coat_hanger is not None
            assert coat_hanger.user_id == user_id
    
    def test_get_current_user(self, app, client):
        """Test getting current user from session."""
        with app.app_context():
            # Register and login
            auth_result = AuthService.register_user(
                email='currentuser@example.com',
                password='CurrentUser123',
                full_name='Current User'
            )
            
            login_result = AuthService.authenticate_user(
                email='currentuser@example.com',
                password='CurrentUser123'
            )
            
            # Set session
            with client.session_transaction() as sess:
                sess['session_hash'] = login_result['session_hash']
            
            # Get current user
            user = AuthService.get_current_user()
            assert user is not None
            assert user.email == 'currentuser@example.com'
    
    def test_logout_user(self, app):
        """Test user logout."""
        with app.app_context():
            # Register and login
            AuthService.register_user(
                email='logouttest@example.com',
                password='LogoutTest123',
                full_name='Logout Test'
            )
            
            login_result = AuthService.authenticate_user(
                email='logouttest@example.com',
                password='LogoutTest123'
            )
            session_hash = login_result['session_hash']
            
            # Logout
            result = AuthService.logout_user(session_hash)
            
            assert result['success'] is True
            
            # Verify coat hanger is deleted
            coat_hanger = CoatHanger.find_by_session_hash(session_hash)
            assert coat_hanger is None
