from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import app_config
from src.utils.csrf_utils import generate_csrf_token

# Load environment variables from .env file
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def configure_app(app):
    """
    Configure the Flask application with settings from both .env and app_config.
    
    Args:
        app (Flask): Flask application instance to configure
    """
    # Environment-specific configuration from .env
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = app_config.SESSION_TIMEOUT
    
    # Optional email configuration from .env
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    # Application constants from app_config - accessible via app.config
    app.config['APP_NAME'] = app_config.APP_NAME
    app.config['VERSION'] = app_config.VERSION
    app.config['AUTHOR'] = app_config.AUTHOR
    app.config['DESCRIPTION'] = app_config.DESCRIPTION
    app.config['DEFAULT_PAGINATION'] = app_config.DEFAULT_PAGINATION
    app.config['PASSWORD_MIN_LENGTH'] = app_config.PASSWORD_MIN_LENGTH
    app.config['MAX_LOGIN_ATTEMPTS'] = app_config.MAX_LOGIN_ATTEMPTS
    app.config['ENABLE_EMAIL_VERIFICATION'] = app_config.ENABLE_EMAIL_VERIFICATION
    app.config['ENABLE_USER_REGISTRATION'] = app_config.ENABLE_USER_REGISTRATION
    app.config['ENABLE_PASSWORD_RESET'] = app_config.ENABLE_PASSWORD_RESET
    app.config['DEFAULT_THEME'] = app_config.DEFAULT_THEME
    app.config['ITEMS_PER_PAGE'] = app_config.ITEMS_PER_PAGE
    app.config['MAX_FILE_UPLOAD_SIZE'] = app_config.MAX_FILE_UPLOAD_SIZE


    # Make csrf_token available globally in templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf_token)
 

def setup_template_globals(app):
    """
    Make app configuration available in Jinja templates.
    Allows usage like {{ app_name }} or {{ version }} in templates.
    
    Args:
        app (Flask): Flask application instance
    """
    @app.context_processor
    def inject_app_config():
        return {
            'app_name': app.config['APP_NAME'],
            'version': app.config['VERSION'],
            'author': app.config['AUTHOR'],
            'description': app.config['DESCRIPTION'],
            'enable_user_registration': app.config['ENABLE_USER_REGISTRATION'],
            'enable_password_reset': app.config['ENABLE_PASSWORD_RESET'],
            'default_theme': app.config['DEFAULT_THEME']
        }

def init_db(app):
    """
    Initialize database with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    blueprints = {
        'main': ('src.controllers.main', 'main_bp'),
    }
    
    for name, (module_path, blueprint_name) in blueprints.items():
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not register blueprint '{name}': {e}")

def create_app():
    """
    Application factory function that creates and configures the Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    configure_app(app)
    setup_template_globals(app)
    init_db(app)
    register_blueprints(app)
    
    return app