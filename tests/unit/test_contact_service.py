"""
Unit tests for ContactService.

Tests validation, sanitization, and contact form submission.
"""

import pytest
from src.logic.contact_service import ContactService
from src.models.contact_message import ContactMessage


class TestContactDataValidation:
    """Test contact form data validation."""
    
    def test_validate_valid_data(self, app):
        """Test validation passes for valid data."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='john.doe@example.com',
                subject='Valid Subject Here',
                message='This is a valid message with sufficient length.'
            )
            assert is_valid is True
            assert errors == {}
    
    def test_validate_empty_name(self, app):
        """Test validation fails for empty name."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='',
                email='test@example.com',
                subject='Subject',
                message='Message content'
            )
            assert is_valid is False
            assert 'name' in errors
    
    def test_validate_short_name(self, app):
        """Test validation fails for too short name."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='A',
                email='test@example.com',
                subject='Subject',
                message='Message content'
            )
            assert is_valid is False
            assert 'name' in errors
    
    def test_validate_invalid_email(self, app):
        """Test validation fails for invalid email."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='invalid-email',
                subject='Subject',
                message='Message content'
            )
            assert is_valid is False
            assert 'email' in errors
    
    def test_validate_short_subject(self, app):
        """Test validation fails for too short subject."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='test@example.com',
                subject='Hi',
                message='Message content here'
            )
            assert is_valid is False
            assert 'subject' in errors
    
    def test_validate_long_subject(self, app):
        """Test validation fails for too long subject."""
        with app.app_context():
            long_subject = 'A' * 201
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='test@example.com',
                subject=long_subject,
                message='Message content'
            )
            assert is_valid is False
            assert 'subject' in errors
    
    def test_validate_short_message(self, app):
        """Test validation fails for too short message."""
        with app.app_context():
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='test@example.com',
                subject='Valid Subject',
                message='Short'
            )
            assert is_valid is False
            assert 'message' in errors
    
    def test_validate_long_message(self, app):
        """Test validation fails for too long message."""
        with app.app_context():
            long_message = 'A' * 2001
            is_valid, errors = ContactService.validate_contact_data(
                name='John Doe',
                email='test@example.com',
                subject='Valid Subject',
                message=long_message
            )
            assert is_valid is False
            assert 'message' in errors


class TestInputSanitization:
    """Test input sanitization."""
    
    def test_sanitize_html_tags(self, app):
        """Test that HTML tags are escaped."""
        with app.app_context():
            malicious_input = '<script>alert("XSS")</script>'
            sanitized = ContactService.sanitize_input(malicious_input)
            assert '<script>' not in sanitized
            assert '&lt;script&gt;' in sanitized
    
    def test_sanitize_quotes(self, app):
        """Test that quotes are escaped."""
        with app.app_context():
            input_with_quotes = 'Hello "world" and \'friend\''
            sanitized = ContactService.sanitize_input(input_with_quotes)
            assert '&quot;' in sanitized or '&#x27;' in sanitized
    
    def test_sanitize_ampersand(self, app):
        """Test that ampersands are escaped."""
        with app.app_context():
            input_with_ampersand = 'Tom & Jerry'
            sanitized = ContactService.sanitize_input(input_with_ampersand)
            assert '&amp;' in sanitized
    
    def test_sanitize_none(self, app):
        """Test that None input is handled gracefully."""
        with app.app_context():
            sanitized = ContactService.sanitize_input(None)
            assert sanitized is None


class TestContactFormSubmission:
    """Test contact form submission."""
    
    def test_submit_valid_form(self, app):
        """Test successful form submission."""
        with app.app_context():
            result = ContactService.submit_contact_form(
                name='Test User',
                email='testuser@example.com',
                subject='Test Subject',
                message='This is a test message with sufficient length.'
            )
            
            assert result['success'] is True
            assert 'contact_id' in result
            
            # Verify message was saved
            message = ContactMessage.find_by_id(result['contact_id'])
            assert message is not None
            assert message.name == 'Test User'
    
    def test_submit_invalid_form(self, app):
        """Test form submission with invalid data."""
        with app.app_context():
            result = ContactService.submit_contact_form(
                name='A',
                email='invalid',
                subject='Hi',
                message='Short'
            )
            
            assert result['success'] is False
            assert 'errors' in result
    
    def test_submit_form_sanitizes_input(self, app):
        """Test that form submission sanitizes malicious input."""
        with app.app_context():
            result = ContactService.submit_contact_form(
                name='<script>Evil</script>',
                email='test@example.com',
                subject='Valid Subject Here',
                message='This is a message with <b>HTML tags</b> in it.'
            )
            
            if result['success']:
                message = ContactMessage.find_by_id(result['contact_id'])
                assert '<script>' not in message.name
                assert '&lt;script&gt;' in message.name


class TestMessageRetrieval:
    """Test contact message retrieval."""
    
    def test_get_message_by_id(self, app):
        """Test getting message by ID."""
        with app.app_context():
            # Submit a message
            result = ContactService.submit_contact_form(
                name='Retrieval Test',
                email='retrieve@example.com',
                subject='Retrieval Test Subject',
                message='This is a retrieval test message.'
            )
            
            message_id = result['contact_id']
            
            # Retrieve message
            message = ContactService.get_message_by_id(message_id)
            assert message is not None
            assert message.id == message_id
    
    def test_get_messages_by_email(self, app):
        """Test getting messages by email."""
        with app.app_context():
            test_email = 'multiplemsgs@example.com'
            
            # Submit multiple messages from same email
            for i in range(3):
                ContactService.submit_contact_form(
                    name='Multiple Test',
                    email=test_email,
                    subject=f'Subject {i}',
                    message=f'This is message number {i} with sufficient length.'
                )
            
            # Retrieve messages
            messages = ContactService.get_messages_by_email(test_email)
            assert len(messages) >= 3


class TestEmailTracking:
    """Test email sent tracking."""
    
    def test_mark_confirmation_sent(self, app):
        """Test marking confirmation email as sent."""
        with app.app_context():
            # Submit a message
            result = ContactService.submit_contact_form(
                name='Email Track Test',
                email='emailtrack@example.com',
                subject='Email Tracking Subject',
                message='This is an email tracking test message.'
            )
            
            message_id = result['contact_id']
            
            # Mark confirmation sent
            success = ContactService.mark_confirmation_email_sent(message_id)
            assert success is True
            
            # Verify
            message = ContactService.get_message_by_id(message_id)
            assert message.confirmation_email_sent is True
    
    def test_mark_admin_notification_sent(self, app):
        """Test marking admin notification as sent."""
        with app.app_context():
            # Submit a message
            result = ContactService.submit_contact_form(
                name='Admin Notify Test',
                email='adminnotify@example.com',
                subject='Admin Notification Subject',
                message='This is an admin notification test message.'
            )
            
            message_id = result['contact_id']
            
            # Mark notification sent
            success = ContactService.mark_admin_notification_sent(message_id)
            assert success is True
            
            # Verify
            message = ContactService.get_message_by_id(message_id)
            assert message.admin_notification_sent is True
