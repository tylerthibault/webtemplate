#!/usr/bin/env python3
"""
Flask MVC Base Template - Main Application Entry Point

This file serves as the entry point for the Flask application.
Following constitutional principle of MVC separation, this file only
handles application startup and configuration loading.
"""

from src import create_app

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
