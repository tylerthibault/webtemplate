from src.models.base_model import BaseModel
from src import db

class CoatHanger(BaseModel):
    """
    Session management model for custom authentication system.
    
    This model implements a "coat hanger" pattern where session tokens
    are stored in the database for secure session management.
    """
    
    __tablename__ = 'coat_hanger'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user._id'), nullable=False)
    session_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_data = db.Column(db.JSON)  # Store serialized user data for quick access
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CoatHanger user_id={self.user_id}, session_hash={self.session_hash[:8]}...>'
    

    @staticmethod
    def generate_session_token(user):
        """Generate a new session token for the given user."""
        import hashlib
        import os
        raw_token = f"{user.id}-{os.urandom(16).hex()}"
        session_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return session_hash
    
    @property
    def user(self):
        """Return the associated user object."""
        from src.models.user_model import User
        return User.query.get(self.user_id)