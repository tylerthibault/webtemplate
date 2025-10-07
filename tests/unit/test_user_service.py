"""
Unit tests for UserService.

Tests user CRUD operations and queries.
"""

import pytest
from src.logic.user_service import UserService
from src.logic.auth_service import AuthService
from src.models.user import User


class TestUserRetrieval:
    """Test user retrieval operations."""
    
    def test_get_user_by_id_exists(self, app):
        """Test getting user by ID when user exists."""
        with app.app_context():
            # Create a user
            result = AuthService.register_user(
                email='getbyid@example.com',
                password='GetById123',
                full_name='Get By ID User'
            )
            user_id = result['user_id']
            
            # Get user
            user = UserService.get_user_by_id(user_id)
            assert user is not None
            assert user.id == user_id
            assert user.email == 'getbyid@example.com'
    
    def test_get_user_by_id_not_exists(self, app):
        """Test getting user by ID when user doesn't exist."""
        with app.app_context():
            user = UserService.get_user_by_id(99999)
            assert user is None
    
    def test_get_user_by_email_exists(self, app):
        """Test getting user by email when user exists."""
        with app.app_context():
            # Create a user
            AuthService.register_user(
                email='getbyemail@example.com',
                password='GetByEmail123',
                full_name='Get By Email User'
            )
            
            # Get user
            user = UserService.get_user_by_email('getbyemail@example.com')
            assert user is not None
            assert user.email == 'getbyemail@example.com'
    
    def test_get_user_by_email_not_exists(self, app):
        """Test getting user by email when user doesn't exist."""
        with app.app_context():
            user = UserService.get_user_by_email('nonexistent@example.com')
            assert user is None
    
    def test_get_user_by_email_case_insensitive(self, app):
        """Test that email lookup is case insensitive."""
        with app.app_context():
            # Create a user
            AuthService.register_user(
                email='casetest@example.com',
                password='CaseTest123',
                full_name='Case Test User'
            )
            
            # Get user with different case
            user = UserService.get_user_by_email('CASETEST@EXAMPLE.COM')
            assert user is not None
            assert user.email == 'casetest@example.com'


class TestUserListing:
    """Test user listing operations."""
    
    def test_get_all_users(self, app):
        """Test getting all users."""
        with app.app_context():
            # Create multiple users
            for i in range(3):
                AuthService.register_user(
                    email=f'user{i}@example.com',
                    password=f'Password{i}23',
                    full_name=f'User {i}'
                )
            
            # Get all users
            users = UserService.get_all_users()
            assert len(users) >= 3
    
    def test_get_all_users_empty(self, app):
        """Test getting all users when none exist."""
        with app.app_context():
            users = UserService.get_all_users()
            assert isinstance(users, list)


class TestUserUpdates:
    """Test user update operations."""
    
    def test_update_user_name(self, app):
        """Test updating user's full name."""
        with app.app_context():
            # Create a user
            result = AuthService.register_user(
                email='updatename@example.com',
                password='UpdateName123',
                full_name='Original Name'
            )
            user_id = result['user_id']
            
            # Update name
            success = UserService.update_user_name(user_id, 'New Name')
            assert success is True
            
            # Verify update
            user = UserService.get_user_by_id(user_id)
            assert user.full_name == 'New Name'
    
    def test_update_user_name_nonexistent(self, app):
        """Test updating name for nonexistent user."""
        with app.app_context():
            success = UserService.update_user_name(99999, 'New Name')
            assert success is False
    
    def test_update_user_email(self, app):
        """Test updating user's email."""
        with app.app_context():
            # Create a user
            result = AuthService.register_user(
                email='oldemail@example.com',
                password='UpdateEmail123',
                full_name='Update Email User'
            )
            user_id = result['user_id']
            
            # Update email
            success = UserService.update_user_email(user_id, 'newemail@example.com')
            assert success is True
            
            # Verify update
            user = UserService.get_user_by_id(user_id)
            assert user.email == 'newemail@example.com'


class TestUserDeletion:
    """Test user deletion operations."""
    
    def test_delete_user_exists(self, app):
        """Test deleting existing user."""
        with app.app_context():
            # Create a user
            result = AuthService.register_user(
                email='deletetest@example.com',
                password='DeleteTest123',
                full_name='Delete Test User'
            )
            user_id = result['user_id']
            
            # Delete user
            success = UserService.delete_user(user_id)
            assert success is True
            
            # Verify deletion
            user = UserService.get_user_by_id(user_id)
            assert user is None
    
    def test_delete_user_not_exists(self, app):
        """Test deleting nonexistent user."""
        with app.app_context():
            success = UserService.delete_user(99999)
            assert success is False


class TestUserStats:
    """Test user statistics operations."""
    
    def test_get_user_count(self, app):
        """Test getting total user count."""
        with app.app_context():
            initial_count = UserService.get_user_count()
            
            # Create new users
            for i in range(3):
                AuthService.register_user(
                    email=f'countuser{i}@example.com',
                    password=f'CountUser{i}23',
                    full_name=f'Count User {i}'
                )
            
            # Check count increased
            new_count = UserService.get_user_count()
            assert new_count == initial_count + 3
