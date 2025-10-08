"""
Flask MVC Base Template - Base Model

This module provides the base model class that all other models inherit from.
Following constitutional principle III: Database Layer Standards.
All models MUST inherit from this base class.
"""

from datetime import datetime
from src import db


class BaseModel(db.Model):
    """
    Base model class for all database models.

    Provides common fields and functionality that all models should have:
    - Primary key ID field
    - Created/updated timestamp tracking
    - Common query methods

    Following constitutional principles:
    - Models are thin (ORM concerns only)
    - Consistent database patterns
    - Proper timestamp management
    """

    __abstract__ = True  # Prevent SQLAlchemy from creating a table for this class

    # Primary key field (required for all models)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Timestamp fields for audit trail
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Timestamp when record was created",
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Timestamp when record was last updated",
    )

    def save(self):
        """
        Save the model instance to the database.

        Convenience method for adding and committing the instance.
        Updates the updated_at timestamp automatically.
        """
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """
        Delete the model instance from the database.

        Removes the instance and commits the transaction.
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """
        Convert model instance to dictionary.

        Useful for JSON serialization and API responses.
        Excludes private/internal fields by default.

        Returns:
            dict: Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert datetime objects to ISO format strings
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def find_by_id(cls, record_id):
        """
        Find a record by its primary key ID.

        Args:
            record_id (int): The ID of the record to find

        Returns:
            BaseModel or None: The found record or None if not found
        """
        return cls.query.get(record_id)

    @classmethod
    def find_all(cls):
        """
        Find all records of this model type.

        Returns:
            list: List of all records
        """
        return cls.query.all()

    def __repr__(self):
        """
        String representation of the model instance.

        Returns:
            str: String representation showing class name and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
