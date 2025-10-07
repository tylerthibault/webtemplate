"""
Contract tests for GET /settings endpoint.

Tests verify the endpoint matches the contract specification
in contracts/get-settings.json for retrieving user profile data.
"""

import pytest
from datetime import datetime
from src.models.user import User
from src import db
import bcrypt


@pytest.fixture
def authenticated_user(app, client):
    """
    Create a test user and return authenticated session.
    
    Returns:
        tuple: (user, client) with active session
    """
    with app.app_context():
        # Create test user
        password_hash = bcrypt.hashpw('TestPass123'.encode('utf-8'), bcrypt.gensalt())
        user = User(
            email='test@example.com',
            full_name='Test User',
            password_hash=password_hash.decode('utf-8'),
            bio='Test bio',
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        
        # Login to create session
        client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        
        return user, client


def test_get_settings_authenticated_returns_200(authenticated_user):
    """
    Test that authenticated user can retrieve their profile settings.
    
    Contract: GET /settings with valid session returns 200 with user data
    Expected: FAIL (endpoint returns 200 but may not have full implementation)
    """
    user, client = authenticated_user
    
    response = client.get('/settings/', headers={'Accept': 'application/json'})
    
    # Should return 200 status
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}"
    
    # Should have user data in response
    data = response.get_json()
    assert 'user' in data, "Response should contain 'user' key"
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['full_name'] == 'Test User'


def test_get_settings_unauthenticated_returns_401(client):
    """
    Test that unauthenticated request returns 401.
    
    Contract: GET /settings without session returns 401 Unauthorized
    Expected: FAIL (needs @login_required decorator)
    """
    response = client.get('/settings/', headers={'Accept': 'application/json'})
    
    assert response.status_code == 401, \
        f"Expected 401 for unauthenticated request, got {response.status_code}"
    
    data = response.get_json()
    assert 'error' in data or 'message' in data, "Error response should contain 'error' or 'message' key"


def test_get_settings_response_schema(authenticated_user):
    """
    Test that response matches contract schema.
    
    Contract: Response must include all required fields:
    - user.id (integer)
    - user.full_name (string)
    - user.email (string)
    - user.updated_at (ISO 8601 datetime)
    - user.bio (string or null)
    - user.profile_picture_data (string or null)
    
    Expected: FAIL (endpoint may not return all fields yet)
    """
    user, client = authenticated_user
    
    response = client.get('/settings/', headers={'Accept': 'application/json'})
    assert response.status_code == 200
    
    data = response.get_json()
    user_data = data['user']
    
    # Required fields
    assert 'id' in user_data, "Missing required field: id"
    assert isinstance(user_data['id'], int), "id must be integer"
    
    assert 'full_name' in user_data, "Missing required field: full_name"
    assert isinstance(user_data['full_name'], str), "full_name must be string"
    assert len(user_data['full_name']) >= 2, "full_name too short"
    
    assert 'email' in user_data, "Missing required field: email"
    assert isinstance(user_data['email'], str), "email must be string"
    assert '@' in user_data['email'], "email must be valid format"
    
    assert 'updated_at' in user_data, "Missing required field: updated_at"
    assert isinstance(user_data['updated_at'], str), "updated_at must be ISO 8601 string"
    
    # Optional fields (can be null)
    assert 'bio' in user_data, "Missing field: bio"
    assert user_data['bio'] is None or isinstance(user_data['bio'], str)
    
    assert 'profile_picture_data' in user_data, "Missing field: profile_picture_data"
    assert 'profile_picture_mime_type' in user_data, "Missing field: profile_picture_mime_type"


def test_get_settings_excludes_picture_when_none(authenticated_user):
    """
    Test that profile_picture_data is null when user has no picture.
    
    Contract: profile_picture_data should be null if not set
    Expected: FAIL (may not properly handle null pictures)
    """
    user, client = authenticated_user
    
    response = client.get('/settings/', headers={'Accept': 'application/json'})
    assert response.status_code == 200
    
    data = response.get_json()
    user_data = data['user']
    
    # User has no profile picture, should be null
    assert user_data['profile_picture_data'] is None, \
        "profile_picture_data should be null when not set"
    assert user_data['profile_picture_mime_type'] is None, \
        "profile_picture_mime_type should be null when no picture"


def test_get_settings_includes_updated_at(authenticated_user):
    """
    Test that updated_at timestamp is present for concurrent edit detection.
    
    Contract: updated_at is required field in ISO 8601 format
    Expected: FAIL (may not include timestamp yet)
    """
    user, client = authenticated_user
    
    response = client.get('/settings/', headers={'Accept': 'application/json'})
    assert response.status_code == 200
    
    data = response.get_json()
    user_data = data['user']
    
    assert 'updated_at' in user_data, "Missing updated_at field"
    
    # Should be parseable as ISO 8601
    updated_at_str = user_data['updated_at']
    try:
        datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        pytest.fail(f"updated_at '{updated_at_str}' is not valid ISO 8601 format")
