from src.models.base_model import BaseModel
from src import db

class User(BaseModel):
    """User model for authentication and user management."""
    
    __tablename__ = 'user'
    
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    force_password_change = db.Column(db.Boolean, nullable=False, default=False)
    
    # Many-to-many relationship with Role model
    roles = db.relationship(
        'Role',
        secondary='user_role',
        back_populates='users',
        lazy='dynamic'
    )
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter_by(name=role_name).first() is not None
    
    def add_role(self, role):
        """Add a role to the user if not already assigned."""
        if not self.has_role(role.name):
            self.roles.append(role)
    
    def remove_role(self, role):
        """Remove a role from the user if assigned."""
        if self.has_role(role.name):
            self.roles.remove(role)

    def get_roles(self):
        """Return a list of role names assigned to the user."""
        return [role.name for role in self.roles.all()]
    
    def __repr__(self):
        return f'<User {self.email}>'