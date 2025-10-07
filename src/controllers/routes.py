"""
Routes registration module.

Registers all blueprints with the Flask application.
Following constitutional principles - thin controllers.
"""

def register_blueprints(app):
    """
    Register all application blueprints.
    
    Args:
        app: Flask application instance
    """
    from src.controllers.auth_routes import auth_bp
    from src.controllers.main_routes import main_bp
    from src.controllers.settings_routes import settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)
