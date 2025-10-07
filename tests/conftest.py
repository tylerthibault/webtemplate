"""
Pytest configuration and fixtures for Flask MVC Base Template tests.

This module provides shared test fixtures and configuration
for all test types (contract, integration, unit).
"""

import pytest
from src import create_app, db


@pytest.fixture(scope='function')
def app():
    """
    Create and configure a Flask application for testing.
    
    Each test gets a fresh application instance with
    a temporary in-memory database.
    
    Yields:
        Flask: Configured test application instance
    """
    # Create app with test configuration
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Create application context
    with test_app.app_context():
        # Create database tables
        db.create_all()
        
        yield test_app
        
        # Cleanup: drop all tables
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create a test client for making HTTP requests.
    
    Args:
        app: Flask application fixture
        
    Returns:
        FlaskClient: Test client for making requests
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create a CLI test runner.
    
    Args:
        app: Flask application fixture
        
    Returns:
        FlaskCliRunner: CLI test runner
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Provide a database session for direct database operations.
    
    Args:
        app: Flask application fixture
        
    Returns:
        Session: SQLAlchemy database session
    """
    with app.app_context():
        yield db.session