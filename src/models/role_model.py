from src import db
from src.models.base_model import BaseModel

# Association table for many-to-many relationship between User and Role
user_role = db.Table(
    'user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user._id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role._id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=db.func.now())
)

class Role(BaseModel):
    """Role model for user authorization system."""
    
    __tablename__ = 'role'
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Many-to-many relationship with User model
    users = db.relationship(
        'User',
        secondary=user_role,
        back_populates='roles',
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<Role {self.name}>'