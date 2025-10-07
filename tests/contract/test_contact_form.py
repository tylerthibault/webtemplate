"""
Contract test for POST /contact endpoint.

Tests the contact form API contract as defined in
specs/001-frontend-landingpage/contracts/contact-api.md

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json


class TestContactFormContract:
    """Test contract for contact form submission endpoint."""
    
    def test_successful_contact_submission(self, client):
        """
        Test successful contact form submission.
        
        Contract: POST /contact
        Expected: 201 Created with success message
        """
        # Arrange
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Inquiry about portfolio',
            'message': 'I am interested in discussing a potential project collaboration.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Message sent successfully' in data['message']
        assert 'confirmation email' in data['message']
        assert 'contact_id' in data
        assert isinstance(data['contact_id'], int)
    
    def test_contact_with_short_name(self, client):
        """
        Test contact form with name less than 2 characters.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange
        payload = {
            'name': 'J',  # Only 1 character
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message that is long enough.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
        assert 'name' in data['errors']
    
    def test_contact_with_invalid_email(self, client):
        """
        Test contact form with invalid email format.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange
        payload = {
            'name': 'John Doe',
            'email': 'not-an-email',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
        assert 'email' in data['errors']
    
    def test_contact_with_short_subject(self, client):
        """
        Test contact form with subject less than 5 characters.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Hi',  # Less than 5 characters
            'message': 'This is a test message.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
    
    def test_contact_with_short_message(self, client):
        """
        Test contact form with message less than 10 characters.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Short'  # Less than 10 characters
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
        assert 'message' in data['errors']
    
    def test_contact_with_missing_fields(self, client):
        """
        Test contact form with missing required fields.
        
        Contract: 422 Unprocessable Entity
        """
        # Arrange - missing subject
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'This is a test message.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 422
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Subject cannot be empty' in data['message']
    
    def test_contact_with_too_long_fields(self, client):
        """
        Test contact form with fields exceeding maximum length.
        
        Contract: 400 Bad Request with validation error
        """
        # Arrange - message too long (>2000 characters)
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'x' * 2001  # More than 2000 characters
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'errors' in data
    
    def test_contact_stores_submission_timestamp(self, client):
        """
        Test that contact submission includes timestamp.
        
        Contract: Submission timestamp should be recorded
        """
        # Arrange
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message for timestamp verification.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
        # Timestamp validation will be done in integration tests with database access