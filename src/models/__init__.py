"""
Flask MVC Base Template - Models Package

This module initializes the models package and provides
database initialization utilities. Following constitutional
principles, models are thin and handle only ORM concerns.
"""

from src import db

# Import all models to ensure they're registered with SQLAlchemy
# This import pattern enables automatic model discovery
from .base_model import BaseModel
from .user import User
from .coat_hanger import CoatHanger
from .contact_message import ContactMessage

__all__ = ["db", "BaseModel", "User", "CoatHanger", "ContactMessage"]


def init_db():
    """
    Initialize database tables.

    Creates all tables defined by the models.
    Should be called during application setup.
    """
    db.create_all()


def drop_db():
    """
    Drop all database tables.

    WARNING: This will delete all data.
    Only use in development/testing.
    """
    db.drop_all()


def reset_db():
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data.
    Only use in development/testing.
    """
    drop_db()
    init_db()
