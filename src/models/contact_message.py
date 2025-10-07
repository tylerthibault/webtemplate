"""
ContactMessage model for storing contact form submissions.

Standalone entity for tracking messages from visitors with email delivery status.
"""

from src import db
from src.models.base_model import BaseModel


class ContactMessage(BaseModel):
    """
    Contact form submission entity.
    
    Stores messages from visitors along with email delivery tracking.
    No relationship to User model - contact form is public.
    
    Attributes:
        name (str): Sender's name (max 100 chars)
        email (str): Sender's email address (max 120 chars)
        subject (str): Message subject (max 200 chars)
        message (str): Message content (max 2000 chars)
        submitted_at (datetime): When message was submitted
        confirmation_email_sent (bool): Whether confirmation email was sent
        confirmation_email_sent_at (datetime): When confirmation email was sent
        admin_email_sent (bool): Whether admin notification email was sent
        admin_email_sent_at (datetime): When admin notification was sent
    """
    
    __tablename__ = 'contact_message'
    
    # Core fields
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)  # Up to 2000 chars
    
    # Submission tracking
    submitted_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # Email delivery tracking
    confirmation_email_sent = db.Column(db.Boolean, nullable=False, default=False)
    confirmation_email_sent_at = db.Column(db.DateTime, nullable=True)
    admin_email_sent = db.Column(db.Boolean, nullable=False, default=False)
    admin_email_sent_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        """String representation of ContactMessage."""
        return f'<ContactMessage from={self.email} subject="{self.subject[:30]}">'
    
    def to_dict(self):
        """
        Convert contact message to dictionary for JSON serialization.
        
        Returns:
            dict: Contact message data
        """
        data = super().to_dict()
        # Add email delivery status
        data['email_status'] = {
            'confirmation_sent': self.confirmation_email_sent,
            'admin_notified': self.admin_email_sent
        }
        return data
    
    def mark_confirmation_sent(self):
        """
        Mark confirmation email as sent and record timestamp.
        """
        from datetime import datetime
        self.confirmation_email_sent = True
        self.confirmation_email_sent_at = datetime.utcnow()
        self.save()
    
    def mark_admin_notified(self):
        """
        Mark admin notification email as sent and record timestamp.
        """
        from datetime import datetime
        self.admin_email_sent = True
        self.admin_email_sent_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def find_by_email(cls, email):
        """
        Find all messages from a specific email address.
        
        Args:
            email (str): Email address to search for
            
        Returns:
            list: List of ContactMessage instances
        """
        return cls.query.filter_by(email=email).order_by(cls.submitted_at.desc()).all()
    
    @classmethod
    def get_pending_confirmations(cls):
        """
        Get all messages that need confirmation emails sent.
        
        Returns:
            list: Messages with confirmation_email_sent = False
        """
        return cls.query.filter_by(confirmation_email_sent=False).all()
    
    @classmethod
    def get_pending_admin_notifications(cls):
        """
        Get all messages that need admin notification emails.
        
        Returns:
            list: Messages with admin_email_sent = False
        """
        return cls.query.filter_by(admin_email_sent=False).all()
