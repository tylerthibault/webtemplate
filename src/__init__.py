"""
Flask MVC Base Template - Application Factory

This module contains the Flask application factory function.
Following constitutional principles, this module handles only
application initialization and configuration.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function.
    
    Creates and configures the Flask application instance
    following constitutional MVC principles.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///portfolio.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration for custom session management
    app.config['PERMANENT_SESSION_LIFETIME'] = 600  # 10 minutes
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Email configuration
    app.config['EMAIL_ENABLED'] = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'
    app.config['SMTP_SERVER'] = os.environ.get('SMTP_SERVER', 'localhost')
    app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT', 587))
    app.config['SMTP_USERNAME'] = os.environ.get('SMTP_USERNAME', '')
    app.config['SMTP_PASSWORD'] = os.environ.get('SMTP_PASSWORD', '')
    app.config['SMTP_USE_TLS'] = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'
    app.config['FROM_EMAIL'] = os.environ.get('FROM_EMAIL', 'noreply@example.com')
    app.config['FROM_NAME'] = os.environ.get('FROM_NAME', 'Flask Portfolio')
    app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register CSRF token context processor
    from src.utils.csrf_utils import inject_csrf_token
    app.context_processor(inject_csrf_token)
    
    # Register CLI commands
    from src.utils.background_tasks import register_commands
    register_commands(app)
    
    # Register blueprints (will be added in controller tasks)
    # Following constitutional principle: thin controllers delegate to logic layer
    from src.controllers.routes import register_blueprints
    register_blueprints(app)
    
    # Import and register models (for SQLAlchemy model discovery)
    with app.app_context():
        from src.models import User, CoatHanger, ContactMessage
        
        # Create database tables
        db.create_all()
    
    return app