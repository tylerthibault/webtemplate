"""
Contact service for handling contact form submissions.

Manages contact message storage and email delivery tracking.
Following constitutional principles - thick logic layer.
"""

from datetime import datetime
from flask import current_app
from src.models.contact_message import ContactMessage
from src.utils.validation_utils import ValidationUtils
from src.utils.email_utils import EmailUtils


class ContactService:
    """
    Contact service for managing contact form submissions.
    
    Constitutional compliance: Business logic for contact operations
    including validation and email tracking.
    """
    
    # Field length constraints
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_SUBJECT_LENGTH = 5
    MAX_SUBJECT_LENGTH = 200
    MIN_MESSAGE_LENGTH = 10
    MAX_MESSAGE_LENGTH = 2000
    
    @classmethod
    def validate_contact_data(cls, name, email, subject, message):
        """
        Validate contact form input data using ValidationUtils.
        
        Args:
            name (str): Sender's name
            email (str): Sender's email
            subject (str): Message subject
            message (str): Message content
            
        Returns:
            tuple: (is_valid: bool, errors: dict)
        """
        errors = {}
        
        # Name validation
        is_valid_name, name_error = ValidationUtils.validate_name(
            name,
            min_length=cls.MIN_NAME_LENGTH,
            max_length=cls.MAX_NAME_LENGTH
        )
        if not is_valid_name:
            errors['name'] = name_error
        
        # Email validation
        is_valid_email, email_error = ValidationUtils.validate_email(email)
        if not is_valid_email:
            errors['email'] = email_error
        
        # Subject validation
        is_valid_subject, subject_error = ValidationUtils.validate_text_length(
            subject,
            field_name='Subject',
            min_length=cls.MIN_SUBJECT_LENGTH,
            max_length=cls.MAX_SUBJECT_LENGTH
        )
        if not is_valid_subject:
            errors['subject'] = subject_error
        
        # Message validation
        is_valid_message, message_error = ValidationUtils.validate_text_length(
            message,
            field_name='Message',
            min_length=cls.MIN_MESSAGE_LENGTH,
            max_length=cls.MAX_MESSAGE_LENGTH
        )
        if not is_valid_message:
            errors['message'] = message_error
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @classmethod
    def sanitize_input(cls, text):
        """
        Sanitize user input to prevent XSS attacks.
        
        Uses ValidationUtils for consistent sanitization.
        
        Args:
            text (str): Input text to sanitize
            
        Returns:
            str: Sanitized text
        """
        return ValidationUtils.sanitize_html(text)
    
    @classmethod
    def submit_contact_form(cls, name, email, subject, message):
        """
        Process contact form submission.
        
        Args:
            name (str): Sender's name
            email (str): Sender's email
            subject (str): Message subject
            message (str): Message content
            
        Returns:
            dict: Result with success status, contact_id or errors
        """
        # Validate input
        is_valid, errors = cls.validate_contact_data(name, email, subject, message)
        if not is_valid:
            return {
                'success': False,
                'errors': errors
            }
        
        try:
            # Sanitize input
            sanitized_name = cls.sanitize_input(name.strip())
            sanitized_subject = cls.sanitize_input(subject.strip())
            sanitized_message = cls.sanitize_input(message.strip())
            email_clean = email.lower().strip()
            
            # Create contact message
            contact_message = ContactMessage(
                name=sanitized_name,
                email=email_clean,
                subject=sanitized_subject,
                message=sanitized_message,
                submitted_at=datetime.utcnow()
            )
            contact_message.save()
            
            # Send email notifications
            contact_data = {
                'name': sanitized_name,
                'email': email_clean,
                'subject': sanitized_subject,
                'message': sanitized_message,
                'submitted_at': contact_message.submitted_at
            }
            
            # Send confirmation email to submitter
            confirmation_sent, confirmation_error = EmailUtils.send_contact_confirmation(
                contact_data, current_app._get_current_object()
            )
            
            # Send notification to admin
            notification_sent, notification_error = EmailUtils.send_contact_notification(
                contact_data, current_app._get_current_object()
            )
            
            # Update email sent flags
            if confirmation_sent:
                contact_message.confirmation_email_sent = True
            if notification_sent:
                contact_message.admin_notification_sent = True
            
            # Save email status updates
            contact_message.save()
            
            # Prepare response message
            response_message = 'Message sent successfully.'
            if confirmation_sent:
                response_message += ' You will receive a confirmation email shortly.'
            elif confirmation_error:
                current_app.logger.warning(f'Confirmation email failed: {confirmation_error}')
            
            return {
                'success': True,
                'message': response_message,
                'contact_id': contact_message.id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Submission failed: {str(e)}'
            }
    
    @staticmethod
    def get_message_by_id(contact_id):
        """
        Get contact message by ID.
        
        Args:
            contact_id (int): Contact message ID
            
        Returns:
            ContactMessage: Message instance or None
        """
        return ContactMessage.find_by_id(contact_id)
    
    @staticmethod
    def get_messages_by_email(email):
        """
        Get all messages from a specific email address.
        
        Args:
            email (str): Email address
            
        Returns:
            list: List of ContactMessage instances
        """
        return ContactMessage.find_by_email(email.lower().strip() if email else '')
    
    @staticmethod
    def mark_confirmation_sent(contact_id):
        """
        Mark confirmation email as sent for a contact message.
        
        Args:
            contact_id (int): Contact message ID
            
        Returns:
            dict: Result with success status
        """
        message = ContactMessage.find_by_id(contact_id)
        
        if not message:
            return {
                'success': False,
                'message': 'Contact message not found'
            }
        
        try:
            message.mark_confirmation_sent()
            return {
                'success': True,
                'message': 'Confirmation email marked as sent'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def mark_admin_notified(contact_id):
        """
        Mark admin notification email as sent for a contact message.
        
        Args:
            contact_id (int): Contact message ID
            
        Returns:
            dict: Result with success status
        """
        message = ContactMessage.find_by_id(contact_id)
        
        if not message:
            return {
                'success': False,
                'message': 'Contact message not found'
            }
        
        try:
            message.mark_admin_notified()
            return {
                'success': True,
                'message': 'Admin notification marked as sent'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def get_pending_confirmations():
        """
        Get all messages needing confirmation emails.
        
        Returns:
            list: ContactMessage instances
        """
        return ContactMessage.get_pending_confirmations()
    
    @staticmethod
    def get_pending_admin_notifications():
        """
        Get all messages needing admin notification emails.
        
        Returns:
            list: ContactMessage instances
        """
        return ContactMessage.get_pending_admin_notifications()
