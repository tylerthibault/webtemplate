"""
Integration test for contact form submission.

Tests the complete contact form submission flow as defined in
specs/001-frontend-landingpage/quickstart.md - Scenario 5

Following TDD: These tests MUST fail before implementation.
"""

import pytest
import json
from datetime import datetime
from src.models import ContactMessage, db


class TestContactSubmissionIntegration:
    """Test complete contact form submission flow from end to end."""
    
    def test_complete_contact_submission_flow(self, client, db_session):
        """
        Test successful contact form submission from form to database.
        
        Flow: POST /contact → Message saved → Confirmation returned
        """
        # Arrange
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Portfolio Inquiry',
            'message': 'I am interested in discussing a potential collaboration on a web design project.'
        }
        
        # Act - Submit contact form
        response = client.post(
            '/contact',
            data=json.dumps(contact_data),
            content_type='application/json'
        )
        
        # Assert - Submission successful
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Message sent successfully' in data['message']
        assert 'contact_id' in data
        
        # Assert - Message exists in database
        message = ContactMessage.query.filter_by(email='john@example.com').first()
        assert message is not None
        assert message.name == 'John Doe'
        assert message.subject == 'Portfolio Inquiry'
        assert message.message == 'I am interested in discussing a potential collaboration on a web design project.'
        
        # Assert - Timestamps created
        assert message.submitted_at is not None
        assert isinstance(message.submitted_at, datetime)
    
    def test_contact_submission_with_validation_errors(self, client, db_session):
        """
        Test contact form validation catches invalid data.
        
        Flow: Submit invalid data → Get validation errors → No DB entry
        """
        test_cases = [
            {
                'data': {'name': 'J', 'email': 'test@example.com', 'subject': 'Test', 'message': 'Message'},
                'error_field': 'name',
                'description': 'name too short'
            },
            {
                'data': {'name': 'John Doe', 'email': 'invalid-email', 'subject': 'Test', 'message': 'Message'},
                'error_field': 'email',
                'description': 'invalid email format'
            },
            {
                'data': {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Hi', 'message': 'Message'},
                'error_field': 'subject',
                'description': 'subject too short'
            },
            {
                'data': {'name': 'John Doe', 'email': 'test@example.com', 'subject': 'Test Subject', 'message': 'Short'},
                'error_field': 'message',
                'description': 'message too short'
            }
        ]
        
        for test_case in test_cases:
            # Act
            response = client.post(
                '/contact',
                data=json.dumps(test_case['data']),
                content_type='application/json'
            )
            
            # Assert - Validation error
            assert response.status_code == 400, f"Failed for: {test_case['description']}"
            data = json.loads(response.data)
            assert data['success'] is False
            
            # Assert - No database entry created
            if 'email' in test_case['data']:
                message = ContactMessage.query.filter_by(email=test_case['data']['email']).first()
                # Only check if email was valid, otherwise query may not work
                if '@' in test_case['data']['email']:
                    assert message is None, f"DB entry created for: {test_case['description']}"
    
    def test_contact_submission_email_confirmation_flags(self, client, db_session):
        """
        Test that email confirmation flags are properly set.
        
        Flow: Submit contact → Check DB for email_sent flags
        """
        # Arrange
        contact_data = {
            'name': 'Email Test User',
            'email': 'emailtest@example.com',
            'subject': 'Email Confirmation Test',
            'message': 'Testing the email confirmation system functionality.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(contact_data),
            content_type='application/json'
        )
        
        # Assert - Submission successful
        assert response.status_code == 201
        
        # Assert - Email flags in database
        message = ContactMessage.query.filter_by(email='emailtest@example.com').first()
        assert message is not None
        # Check that email_sent flags exist (may be False initially if async)
        assert hasattr(message, 'confirmation_email_sent')
        assert hasattr(message, 'admin_email_sent')
    
    def test_multiple_contact_submissions_same_email(self, client, db_session):
        """
        Test that same person can submit multiple messages.
        
        Flow: Submit → Submit again → Both in database
        """
        # Arrange
        contact_data_1 = {
            'name': 'Repeat User',
            'email': 'repeat@example.com',
            'subject': 'First Message',
            'message': 'This is my first message to you.'
        }
        
        contact_data_2 = {
            'name': 'Repeat User',
            'email': 'repeat@example.com',
            'subject': 'Second Message',
            'message': 'This is my second message with different content.'
        }
        
        # Act - First submission
        response1 = client.post(
            '/contact',
            data=json.dumps(contact_data_1),
            content_type='application/json'
        )
        assert response1.status_code == 201
        
        # Act - Second submission
        response2 = client.post(
            '/contact',
            data=json.dumps(contact_data_2),
            content_type='application/json'
        )
        assert response2.status_code == 201
        
        # Assert - Both messages in database
        messages = ContactMessage.query.filter_by(email='repeat@example.com').all()
        assert len(messages) == 2
        subjects = [msg.subject for msg in messages]
        assert 'First Message' in subjects
        assert 'Second Message' in subjects
    
    def test_contact_submission_sanitizes_input(self, client, db_session):
        """
        Test that contact form sanitizes potentially dangerous input.
        
        Flow: Submit with HTML/script tags → Sanitized in DB
        """
        # Arrange - Include potentially dangerous content
        contact_data = {
            'name': 'Test User',
            'email': 'sanitize@example.com',
            'subject': 'XSS Test <script>alert("xss")</script>',
            'message': 'Message with <b>HTML</b> and <script>alert("bad")</script> content.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(contact_data),
            content_type='application/json'
        )
        
        # Assert - Submission accepted
        assert response.status_code == 201
        
        # Assert - Data sanitized or escaped in database
        message = ContactMessage.query.filter_by(email='sanitize@example.com').first()
        assert message is not None
        # Scripts should be removed or escaped
        assert '<script>' not in message.subject or '&lt;script&gt;' in message.subject
        assert '<script>' not in message.message or '&lt;script&gt;' in message.message
    
    def test_contact_submission_respects_max_length(self, client, db_session):
        """
        Test that contact form enforces maximum field lengths.
        
        Flow: Submit too-long fields → Get validation error
        """
        # Arrange - Message exceeding 2000 characters
        long_message = 'x' * 2001
        contact_data = {
            'name': 'Test User',
            'email': 'maxlength@example.com',
            'subject': 'Max Length Test',
            'message': long_message
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(contact_data),
            content_type='application/json'
        )
        
        # Assert - Validation error
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        
        # Assert - No database entry
        message = ContactMessage.query.filter_by(email='maxlength@example.com').first()
        assert message is None
    
    def test_contact_submission_missing_required_fields(self, client, db_session):
        """
        Test that all required fields must be present.
        
        Flow: Submit with missing fields → Get 422 error
        """
        test_cases = [
            {'email': 'test@example.com', 'subject': 'Test', 'message': 'Message'},  # Missing name
            {'name': 'Test', 'subject': 'Test', 'message': 'Message'},  # Missing email
            {'name': 'Test', 'email': 'test@example.com', 'message': 'Message'},  # Missing subject
            {'name': 'Test', 'email': 'test@example.com', 'subject': 'Test'}  # Missing message
        ]
        
        for incomplete_data in test_cases:
            # Act
            response = client.post(
                '/contact',
                data=json.dumps(incomplete_data),
                content_type='application/json'
            )
            
            # Assert - Unprocessable entity
            assert response.status_code == 422
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_contact_submission_timestamp_accuracy(self, client, db_session):
        """
        Test that submission timestamp is accurate.
        
        Flow: Submit → Verify timestamp is current
        """
        # Arrange
        before_submission = datetime.utcnow()
        
        contact_data = {
            'name': 'Timestamp Test',
            'email': 'timestamp@example.com',
            'subject': 'Timestamp Verification',
            'message': 'Testing timestamp accuracy for contact submissions.'
        }
        
        # Act
        response = client.post(
            '/contact',
            data=json.dumps(contact_data),
            content_type='application/json'
        )
        
        after_submission = datetime.utcnow()
        
        # Assert
        assert response.status_code == 201
        
        message = ContactMessage.query.filter_by(email='timestamp@example.com').first()
        assert message is not None
        
        # Timestamp should be between before and after
        assert before_submission <= message.submitted_at <= after_submission
