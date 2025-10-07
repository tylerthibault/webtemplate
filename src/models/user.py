"""
User model for authentication and profile management.

Represents registered users with email, name, and hashed password.
Inherits from BaseModel for common fields and methods.
"""

from datetime import datetime
from sqlalchemy.orm import deferred
from src import db
from src.models.base_model import BaseModel


class User(BaseModel):
    """
    User entity for authentication system.
    
    Attributes:
        email (str): Unique user email address (max 120 chars)
        full_name (str): User's full name (max 100 chars)
        password_hash (str): Bcrypt hashed password (60 chars)
        bio (str): User biography (max 500 chars, optional)
        profile_picture_data (str): Base64-encoded profile picture (lazy loaded)
        profile_picture_mime_type (str): MIME type of profile picture
        updated_at (datetime): Last profile update timestamp
        coat_hangers: Relationship to CoatHanger sessions
    """
    
    __tablename__ = 'user'
    
    # Core fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)  # bcrypt produces 60 char hashes
    
    # Profile fields (Feature 003)
    bio = db.Column(db.Text, nullable=True)
    profile_picture_data = deferred(db.Column(db.Text, nullable=True))  # Lazy loaded for performance
    profile_picture_mime_type = db.Column(db.String(50), nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Relationships
    coat_hangers = db.relationship(
        'CoatHanger',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.email}>'
    
    def to_dict(self, include_picture=False):
        """
        Convert user to dictionary for JSON serialization.
        
        Args:
            include_picture (bool): If True, include profile_picture_data
            
        Returns:
            dict: User data excluding password_hash
        """
        data = super().to_dict()
        # Remove password_hash from output for security
        data.pop('password_hash', None)
        
        # Add profile fields
        data['bio'] = self.bio
        data['profile_picture_mime_type'] = self.profile_picture_mime_type
        data['updated_at'] = self.updated_at.isoformat() + 'Z' if self.updated_at else None
        
        # Include picture data only if requested (lazy loaded)
        if include_picture:
            data['profile_picture_data'] = self.profile_picture_data
        else:
            # Explicitly set to None if not including
            data['profile_picture_data'] = None
            
        return data
    
    def has_profile_picture(self):
        """
        Check if user has a profile picture.
        
        Returns:
            bool: True if user has profile picture, False otherwise
        """
        return self.profile_picture_data is not None and len(self.profile_picture_data) > 0
    
    @classmethod
    def find_by_email(cls, email):
        """
        Find user by email address.
        
        Args:
            email (str): Email address to search for
            
        Returns:
            User: User instance or None if not found
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def email_exists(cls, email):
        """
        Check if email already exists in database.
        
        Args:
            email (str): Email address to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        return cls.query.filter_by(email=email).first() is not None
