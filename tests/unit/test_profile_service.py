"""
Unit tests for ProfileService class.

Tests business logic for profile management including validation,
concurrent edit detection, and update operations.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.logic.profile_service import ProfileService
from src.models.user import User
from src import db


# === Test get_user_profile() ===

def test_get_user_profile_without_picture(app):
    """
    Test getting user profile excludes picture_data by default.
    
    Expected: FAIL (get_user_profile not implemented)
    """
    with app.app_context():
        # Create test user
        user = User(
            email='test@example.com',
            full_name='Test User',
            password_hash='hashed',
            bio='Test bio',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Get profile without picture
        profile = ProfileService.get_user_profile(user_id, include_picture=False)
        
        assert profile is not None
        assert profile['email'] == 'test@example.com'
        assert 'profile_picture_data' not in profile or profile['profile_picture_data'] is None


def test_get_user_profile_with_picture(app):
    """
    Test getting user profile includes picture when requested.
    
    Expected: FAIL (get_user_profile not implemented)
    """
    with app.app_context():
        user = User(
            email='test@example.com',
            full_name='Test User',
            password_hash='hashed',
            profile_picture_data='base64data',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Get profile with picture
        profile = ProfileService.get_user_profile(user_id, include_picture=True)
        
        assert profile is not None
        assert profile['profile_picture_data'] == 'base64data'


def test_get_user_profile_nonexistent_user(app):
    """
    Test getting profile for non-existent user returns None.
    
    Expected: FAIL (get_user_profile not implemented)
    """
    with app.app_context():
        profile = ProfileService.get_user_profile(99999)
        assert profile is None


# === Test update_profile() ===

def test_update_profile_full_name(app):
    """
    Test updating full_name field.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        user = User(
            email='test@example.com',
            full_name='Old Name',
            password_hash='hashed',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        current_time = user.updated_at.isoformat()
        
        data = {
            'full_name': 'New Name',
            'email': 'test@example.com'
        }
        
        result = ProfileService.update_profile(user_id, data, current_time)
        
        assert result['full_name'] == 'New Name'


def test_update_profile_email(app):
    """
    Test updating email address.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        user = User(
            email='old@example.com',
            full_name='Test',
            password_hash='hashed',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        current_time = user.updated_at.isoformat()
        
        data = {
            'full_name': 'Test',
            'email': 'new@example.com',
            'current_password': 'password'
        }
        
        result = ProfileService.update_profile(user_id, data, current_time)
        
        assert result['email'] == 'new@example.com'


def test_update_profile_bio(app):
    """
    Test updating bio field.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash='hashed',
            bio='Old bio',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        current_time = user.updated_at.isoformat()
        
        data = {
            'full_name': 'Test',
            'email': 'test@example.com',
            'bio': 'New bio content'
        }
        
        result = ProfileService.update_profile(user_id, data, current_time)
        
        assert result['bio'] == 'New bio content'


def test_update_profile_password(app):
    """
    Test password change hashes new password with bcrypt.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        import bcrypt
        old_hash = bcrypt.hashpw(b'oldpass', bcrypt.gensalt())
        
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash=old_hash.decode('utf-8'),
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        current_time = user.updated_at.isoformat()
        
        data = {
            'full_name': 'Test',
            'email': 'test@example.com',
            'current_password': 'oldpass',
            'new_password': 'NewPass123'
        }
        
        ProfileService.update_profile(user_id, data, current_time)
        
        # Verify password was changed and hashed
        updated_user = User.query.get(user_id)
        assert bcrypt.checkpw(b'NewPass123', updated_user.password_hash.encode('utf-8'))


def test_update_profile_picture(app):
    """
    Test updating profile_picture_data.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash='hashed',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        current_time = user.updated_at.isoformat()
        
        data = {
            'full_name': 'Test',
            'email': 'test@example.com',
            'profile_picture_data': 'base64encodedimage',
            'profile_picture_mime_type': 'image/jpeg'
        }
        
        result = ProfileService.update_profile(user_id, data, current_time)
        
        assert result['profile_picture_data'] == 'base64encodedimage'


def test_update_profile_updates_timestamp(app):
    """
    Test that updated_at timestamp is refreshed on update.
    
    Expected: FAIL (update_profile not implemented)
    """
    with app.app_context():
        old_time = datetime.utcnow() - timedelta(hours=1)
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash='hashed',
            updated_at=old_time
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        data = {
            'full_name': 'Updated',
            'email': 'test@example.com'
        }
        
        ProfileService.update_profile(user_id, data, old_time.isoformat())
        
        updated_user = User.query.get(user_id)
        assert updated_user.updated_at > old_time


# === Test validate_profile_data() ===

def test_validate_profile_data_valid():
    """Test validation passes for valid data."""
    data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'bio': 'Valid bio'
    }
    
    is_valid, errors = ProfileService.validate_profile_data(data)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_profile_data_empty_name():
    """Test validation fails for empty name."""
    data = {
        'full_name': '',
        'email': 'john@example.com'
    }
    
    is_valid, errors = ProfileService.validate_profile_data(data)
    assert is_valid is False
    assert 'full_name' in errors


def test_validate_profile_data_invalid_email():
    """Test validation fails for invalid email."""
    data = {
        'full_name': 'John Doe',
        'email': 'invalid-email'
    }
    
    is_valid, errors = ProfileService.validate_profile_data(data)
    assert is_valid is False
    assert 'email' in errors


def test_validate_profile_data_bio_too_long():
    """Test validation fails for bio > 500 chars."""
    data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'bio': 'x' * 501  # Exceeds 500 char limit
    }
    
    is_valid, errors = ProfileService.validate_profile_data(data)
    assert is_valid is False
    assert 'bio' in errors


def test_validate_profile_data_weak_password():
    """Test validation fails for weak password."""
    data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'new_password': 'weak'  # Too short, no uppercase/number
    }
    
    is_valid, errors = ProfileService.validate_profile_data(data)
    assert is_valid is False
    assert 'new_password' in errors or 'password' in errors


# === Test detect_concurrent_edit() ===

def test_detect_concurrent_edit_no_conflict(app):
    """Test no conflict when timestamps match."""
    with app.app_context():
        current_time = datetime.utcnow()
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash='hashed',
            updated_at=current_time
        )
        db.session.add(user)
        db.session.commit()
        
        has_conflict = ProfileService.detect_concurrent_edit(
            user,
            current_time.isoformat()
        )
        
        assert has_conflict is False


def test_detect_concurrent_edit_conflict(app):
    """Test conflict detected when user was updated after form load."""
    with app.app_context():
        current_time = datetime.utcnow()
        old_time = current_time - timedelta(hours=1)
        
        user = User(
            email='test@example.com',
            full_name='Test',
            password_hash='hashed',
            updated_at=current_time  # User was updated more recently
        )
        db.session.add(user)
        db.session.commit()
        
        # Submitted timestamp is old (form was loaded 1 hour ago)
        has_conflict = ProfileService.detect_concurrent_edit(
            user,
            old_time.isoformat()
        )
        
        assert has_conflict is True
