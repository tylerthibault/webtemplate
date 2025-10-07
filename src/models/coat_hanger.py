"""
CoatHanger model for session management.

Implements custom session tracking with 10-minute timeout.
Each session is tied to a user and contains a unique session hash.
"""

from datetime import datetime, timedelta
from src import db
from src.models.base_model import BaseModel


class CoatHanger(BaseModel):
    """
    Session tracking entity for custom authentication system.
    
    Implements "coat hanger" pattern for managing user sessions
    with automatic expiration after 10 minutes of inactivity.
    
    Attributes:
        user_id (int): Foreign key to User.id
        session_hash (str): Unique session identifier (64 chars)
        user_data (dict): Cached user information (JSON)
        user: Relationship to User model
    """
    
    __tablename__ = 'coat_hanger'
    
    # Core fields
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    session_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_data = db.Column(db.JSON, nullable=True)  # Cached user info for performance
    
    # Relationships
    user = db.relationship('User', back_populates='coat_hangers')
    
    # Session timeout constant (10 minutes in seconds)
    SESSION_TIMEOUT_SECONDS = 600
    
    def __repr__(self):
        """String representation of CoatHanger."""
        return f'<CoatHanger user_id={self.user_id} hash={self.session_hash[:8]}...>'
    
    def is_expired(self):
        """
        Check if session has expired (>10 minutes since last activity).
        
        Returns:
            bool: True if session expired, False if still active
        """
        if not self.updated_at:
            return True
        
        expiry_time = self.updated_at + timedelta(seconds=self.SESSION_TIMEOUT_SECONDS)
        return datetime.utcnow() >= expiry_time
    
    def time_until_expiry(self):
        """
        Calculate seconds remaining until session expires.
        
        Returns:
            int: Seconds until expiry, 0 if already expired
        """
        if self.is_expired():
            return 0
        
        expiry_time = self.updated_at + timedelta(seconds=self.SESSION_TIMEOUT_SECONDS)
        time_remaining = (expiry_time - datetime.utcnow()).total_seconds()
        return max(0, int(time_remaining))
    
    def renew(self):
        """
        Renew session by updating the updated_at timestamp.
        
        This resets the 10-minute timeout window.
        """
        self.updated_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def find_by_session_hash(cls, session_hash):
        """
        Find active session by session hash.
        
        Args:
            session_hash (str): Session hash to search for
            
        Returns:
            CoatHanger: Active session or None if not found/expired
        """
        coat_hanger = cls.query.filter_by(session_hash=session_hash).first()
        
        if coat_hanger and coat_hanger.is_expired():
            # Clean up expired session
            coat_hanger.delete()
            return None
        
        return coat_hanger
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """
        Remove all expired sessions from database.
        
        Should be called periodically by background task.
        
        Returns:
            int: Number of sessions deleted
        """
        cutoff_time = datetime.utcnow() - timedelta(seconds=cls.SESSION_TIMEOUT_SECONDS)
        expired_sessions = cls.query.filter(cls.updated_at < cutoff_time).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            session.delete()
        
        return count
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """
        Find active session for a specific user.
        
        Args:
            user_id (int): User ID to search for
            
        Returns:
            CoatHanger: Active session or None if not found
        """
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def delete_user_sessions(cls, user_id):
        """
        Delete all sessions for a specific user.
        
        Used during logout to clear all active sessions.
        
        Args:
            user_id (int): User ID whose sessions to delete
            
        Returns:
            int: Number of sessions deleted
        """
        sessions = cls.query.filter_by(user_id=user_id).all()
        count = len(sessions)
        
        for session in sessions:
            session.delete()
        
        return count
