"""
Contract tests for POST /settings endpoint.

Tests verify the endpoint matches the contract specification
in contracts/post-settings.json for updating user profile data.
"""

import pytest
from datetime import datetime, timedelta
from src.models.user import User
from src import db
import bcrypt


@pytest.fixture
def authenticated_user(app, client):
    """Create authenticated user with session."""
    with app.app_context():
        password_hash = bcrypt.hashpw('TestPass123'.encode('utf-8'), bcrypt.gensalt())
        user = User(
            email='test@example.com',
            full_name='Test User',
            password_hash=password_hash.decode('utf-8'),
            bio='Original bio',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Login to create session
        client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        return user_id, client


def test_post_settings_valid_data_returns_200(authenticated_user, app):
    """
    Test successful profile update with valid data.
    
    Contract: POST /settings with valid data returns 200 with updated user
    Expected: FAIL (endpoint not fully implemented)
    """
    user_id, client = authenticated_user
    
    with app.app_context():
        user = User.query.get(user_id)
        current_timestamp = user.updated_at.isoformat() + 'Z'
    
    response = client.post('/settings/', json={
        'full_name': 'Updated Name',
        'email': 'test@example.com',
        'bio': 'Updated bio',
        'updated_at': current_timestamp
    }, headers={'X-CSRF-Token': 'test-token'})
    
    assert response.status_code == 200, \
        f"Expected 200 for valid update, got {response.status_code}"
    
    data = response.get_json()
    assert data['success'] is True
    assert data['message'] == 'Profile updated successfully'
    assert data['user']['full_name'] == 'Updated Name'
    assert data['user']['bio'] == 'Updated bio'


def test_post_settings_invalid_email_returns_400(authenticated_user, app):
    """
    Test validation error for invalid email format.
    
    Contract: Invalid email returns 400 with validation errors
    Expected: FAIL (validation not implemented)
    """
    user_id, client = authenticated_user
    
    with app.app_context():
        user = User.query.get(user_id)
        current_timestamp = user.updated_at.isoformat() + 'Z'
    
    response = client.post('/settings/', json={
        'full_name': 'Test User',
        'email': 'invalid-email',  # Invalid format
        'updated_at': current_timestamp
    }, headers={'X-CSRF-Token': 'test-token'})
    
    assert response.status_code == 400, \
        f"Expected 400 for invalid email, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data or 'errors' in data, \
        "Response should contain error information"


def test_post_settings_concurrent_edit_returns_409(authenticated_user, app):
    """
    Test concurrent edit detection with stale timestamp.
    
    Contract: Stale updated_at returns 409 Conflict with current data
    Expected: FAIL (concurrent edit detection not implemented)
    """
    user_id, client = authenticated_user
    
    # Use old timestamp to simulate concurrent edit
    stale_timestamp = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
    
    response = client.post('/settings/', json={
        'full_name': 'Updated Name',
        'email': 'test@example.com',
        'bio': 'Updated bio',
        'updated_at': stale_timestamp  # Stale timestamp
    }, headers={'X-CSRF-Token': 'test-token'})
    
    assert response.status_code == 409, \
        f"Expected 409 for concurrent edit, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data, "Conflict response should contain error"
    assert 'current_data' in data, "Conflict response should include current data"


def test_post_settings_wrong_password_returns_422(authenticated_user, app):
    """
    Test incorrect current_password returns 422.
    
    Contract: Wrong password when changing email/password returns 422
    Expected: FAIL (password verification not implemented)
    """
    user_id, client = authenticated_user
    
    with app.app_context():
        user = User.query.get(user_id)
        current_timestamp = user.updated_at.isoformat() + 'Z'
    
    response = client.post('/settings/', json={
        'full_name': 'Test User',
        'email': 'newemail@example.com',  # Email change requires password
        'current_password': 'WrongPassword123',  # Incorrect password
        'updated_at': current_timestamp
    }, headers={'X-CSRF-Token': 'test-token'})
    
    assert response.status_code == 422, \
        f"Expected 422 for wrong password, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data, "Response should contain error message"


def test_post_settings_missing_csrf_returns_403(authenticated_user, app):
    """
    Test missing CSRF token returns 403.
    
    Contract: Missing or invalid CSRF token returns 403 Forbidden
    Expected: FAIL (CSRF protection not applied to endpoint)
    """
    user_id, client = authenticated_user
    
    with app.app_context():
        user = User.query.get(user_id)
        current_timestamp = user.updated_at.isoformat() + 'Z'
    
    # Request without CSRF token header
    response = client.post('/settings/', json={
        'full_name': 'Updated Name',
        'email': 'test@example.com',
        'updated_at': current_timestamp
    })
    
    assert response.status_code == 403, \
        f"Expected 403 for missing CSRF, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data, "Response should contain error"


def test_post_settings_unauthenticated_returns_401(client):
    """
    Test unauthenticated request returns 401.
    
    Contract: POST without session returns 401 Unauthorized
    Expected: FAIL (@login_required not applied)
    """
    response = client.post('/settings/', json={
        'full_name': 'Test',
        'email': 'test@example.com',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }, headers={'X-CSRF-Token': 'test-token'})
    
    assert response.status_code == 401, \
        f"Expected 401 for unauthenticated, got {response.status_code}"


def test_post_settings_response_schema(authenticated_user, app):
    """
    Test success response matches contract schema.
    
    Contract: Success returns {success: true, message: string, user: object}
    Expected: FAIL (response schema not implemented)
    """
    user_id, client = authenticated_user
    
    with app.app_context():
        user = User.query.get(user_id)
        current_timestamp = user.updated_at.isoformat() + 'Z'
    
    response = client.post('/settings/', json={
        'full_name': 'Schema Test',
        'email': 'test@example.com',
        'bio': 'Testing schema',
        'updated_at': current_timestamp
    }, headers={'X-CSRF-Token': 'test-token'})
    
    if response.status_code == 200:
        data = response.get_json()
        
        # Required response fields
        assert 'success' in data, "Missing 'success' field"
        assert data['success'] is True, "'success' should be true"
        
        assert 'message' in data, "Missing 'message' field"
        assert isinstance(data['message'], str), "'message' should be string"
        
        assert 'user' in data, "Missing 'user' field"
        assert isinstance(data['user'], dict), "'user' should be object"
        
        # User should have updated data
        assert data['user']['full_name'] == 'Schema Test'
        assert data['user']['email'] == 'test@example.com'
        assert 'updated_at' in data['user'], "User should include updated_at"
