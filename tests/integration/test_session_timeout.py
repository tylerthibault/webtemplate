"""
Integration test for session timeout functionality.

Tests the 10-minute session timeout as defined in
specs/001-frontend-landingpage/quickstart.md - Scenario 4

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from src.models import User, CoatHanger, db


class TestSessionTimeoutIntegration:
    """Test session timeout and renewal functionality."""
    
    def test_session_timeout_after_10_minutes(self, client, db_session):
        """
        Test that session expires after 10 minutes of inactivity.
        
        Flow: Login → Wait/simulate 10 min → Session check fails
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'timeout@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Timeout User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'timeout@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Get the coat hanger and manually set it to 11 minutes ago
        user = User.query.filter_by(email='timeout@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger is not None
        
        # Simulate 11 minutes passing by updating the timestamp
        coat_hanger.updated_at = datetime.utcnow() - timedelta(minutes=11)
        db_session.commit()
        
        # Act - Check session status
        response = client.get('/auth/session')
        data = json.loads(response.data)
        
        # Assert - Session should be expired
        assert data['authenticated'] is False
        
        # Assert - Coat hanger should be deleted (cleanup)
        coat_hanger_after = CoatHanger.query.filter_by(user_id=user.id).first()
        assert coat_hanger_after is None
    
    def test_session_remains_active_within_timeout(self, client, db_session):
        """
        Test that session remains active within 10-minute window.
        
        Flow: Login → Check at 5 min → Still authenticated
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'active@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Active User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'active@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Simulate 5 minutes passing
        user = User.query.filter_by(email='active@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        coat_hanger.updated_at = datetime.utcnow() - timedelta(minutes=5)
        db_session.commit()
        
        # Act - Check session
        response = client.get('/auth/session')
        data = json.loads(response.data)
        
        # Assert - Session still active
        assert response.status_code == 200
        assert data['authenticated'] is True
        assert data['user']['email'] == 'active@example.com'
    
    def test_session_renewal_on_activity(self, client, db_session):
        """
        Test that session timeout renews on user activity.
        
        Flow: Login → Activity at 8 min → Wait 5 more min → Still active
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'renewal@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Renewal User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'renewal@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Simulate 8 minutes passing
        user = User.query.filter_by(email='renewal@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        old_updated_at = datetime.utcnow() - timedelta(minutes=8)
        coat_hanger.updated_at = old_updated_at
        db_session.commit()
        
        # Act - Make activity (session check renews the timer)
        activity_response = client.get('/auth/session')
        assert activity_response.status_code == 200
        
        # Get refreshed coat hanger
        db_session.refresh(coat_hanger)
        new_updated_at = coat_hanger.updated_at
        
        # Assert - Timestamp was updated (session renewed)
        assert new_updated_at > old_updated_at
        
        # Simulate 5 more minutes (13 min total, but only 5 since renewal)
        coat_hanger.updated_at = datetime.utcnow() - timedelta(minutes=5)
        db_session.commit()
        
        # Act - Check session again
        final_response = client.get('/auth/session')
        final_data = json.loads(final_response.data)
        
        # Assert - Still active because renewal reset the timer
        assert final_data['authenticated'] is True
    
    def test_session_expiry_time_in_response(self, client, db_session):
        """
        Test that session response includes time until expiry.
        
        Flow: Login → Check session → Verify expiry_in field (590-600 seconds)
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'expiry@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Expiry User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'expiry@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Act - Check session immediately
        response = client.get('/auth/session')
        data = json.loads(response.data)
        
        # Assert - Expiry time is close to 600 seconds (10 minutes)
        assert data['authenticated'] is True
        assert 'expiry_in' in data
        # Should be between 590-600 seconds (allowing for processing time)
        assert 590 <= data['expiry_in'] <= 600
    
    def test_multiple_requests_update_session_timer(self, client, db_session):
        """
        Test that each authenticated request resets the timeout timer.
        
        Flow: Login → Request 1 → Request 2 → Timestamps updated
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'updates@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Updates User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'updates@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        user = User.query.filter_by(email='updates@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        first_timestamp = coat_hanger.updated_at
        
        # Simulate small time passing
        time.sleep(0.1)
        
        # Act - Make authenticated request
        client.get('/auth/session')
        
        # Refresh and check timestamp
        db_session.refresh(coat_hanger)
        second_timestamp = coat_hanger.updated_at
        
        # Assert - Timestamp updated
        assert second_timestamp > first_timestamp
    
    def test_expired_session_redirects_to_login(self, client, db_session):
        """
        Test that expired session prevents access to protected pages.
        
        Flow: Login → Expire session → Access dashboard → Redirected
        """
        # Arrange - Register and login
        registration_data = {
            'email': 'redirect@example.com',
            'password': 'SecurePass123!',
            'full_name': 'Redirect User'
        }
        client.post(
            '/auth/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        login_data = {
            'email': 'redirect@example.com',
            'password': 'SecurePass123!'
        }
        client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Expire the session
        user = User.query.filter_by(email='redirect@example.com').first()
        coat_hanger = CoatHanger.query.filter_by(user_id=user.id).first()
        coat_hanger.updated_at = datetime.utcnow() - timedelta(minutes=11)
        db_session.commit()
        
        # Act - Try to access protected page
        response = client.get('/dashboard', follow_redirects=False)
        
        # Assert - Redirected or unauthorized
        assert response.status_code in [302, 401, 403]
