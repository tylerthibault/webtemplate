from src import create_app

"""
Application entry point for Flask MVC Base Template.
Runs the Flask application using the application factory pattern.
"""


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)