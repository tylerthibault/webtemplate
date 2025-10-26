from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src import db

"""
Base model class providing common CRUD operations for all database models.
"""


class BaseModel(db.Model):
    """
    Abstract base model class that provides common fields and CRUD operations.
    All application models should inherit from this class.
    """
    __abstract__ = True
    
    # Common fields for all models
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def save(self):
        """Save the current instance to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """Delete the current instance from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """Update the current instance with provided keyword arguments."""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new instance of the model."""
        try:
            instance = cls(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_by_id(cls, id):
        """Retrieve a record by its primary key."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Retrieve all records for this model."""
        return cls.query.all()
    
    @classmethod
    def find_by(cls, **kwargs):
        """Find records by specified criteria."""
        return cls.query.filter_by(**kwargs).all()
    
    @classmethod
    def find_one_by(cls, **kwargs):
        """Find a single record by specified criteria."""
        return cls.query.filter_by(**kwargs).first()
    
    def to_dict(self):
        """Convert model instance to dictionary representation."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'None')})>"