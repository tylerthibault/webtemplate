
# app_config.py - Application metadata and constants
"""
Application configuration constants and metadata.
These values should be consistent across all environments.
"""

# Application Metadata
APP_NAME = "Flask MVC Base Template"
VERSION = "1.2.0"
AUTHOR = "Tyler Thibault"
DESCRIPTION = "A secure Flask web application template with MVC architecture"

# Application Constants
DEFAULT_PAGINATION = 20
SESSION_TIMEOUT = 600  # 10 minutes (used in PERMANENT_SESSION_LIFETIME)
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5

# Feature Flags
ENABLE_EMAIL_VERIFICATION = True
ENABLE_USER_REGISTRATION = True
ENABLE_PASSWORD_RESET = True

# UI/UX Settings
DEFAULT_THEME = "light"
ITEMS_PER_PAGE = 25
MAX_FILE_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB