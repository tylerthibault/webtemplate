"""
Authentication service for user registration, login, and session management.

Implements bcrypt password hashing and custom "coat hanger" session tracking.
This is the THICK logic layer following constitutional principles.
"""

import secrets
import hashlib
from datetime import datetime
import bcrypt
from flask import session
from src import db
from src.models.user import User
from src.models.coat_hanger import CoatHanger
from src.utils.validation_utils import ValidationUtils


class AuthService:
    """
    Authentication service handling registration, login, logout, and session management.

    Constitutional compliance: Thick logic layer containing all authentication
    business rules. Controllers delegate to this service.
    """

    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    # Name requirements
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100

    @staticmethod
    def hash_password(password):
        """
        Hash password using bcrypt with cost factor 12.

        Args:
            password (str): Plain text password

        Returns:
            str: Bcrypt hashed password (60 chars)
        """
        # bcrypt requires bytes
        password_bytes = password.encode("utf-8")
        # Generate salt and hash (cost factor 12 is default)
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
        # Return as string for database storage
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify password against bcrypt hash.

        Args:
            password (str): Plain text password to check
            password_hash (str): Bcrypt hash to verify against

        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode("utf-8")
            hash_bytes = password_hash.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False

    @staticmethod
    def generate_session_hash(user_id):
        """
        Generate secure session hash for coat hanger table.

        Uses secure random + user ID + timestamp for uniqueness.

        Args:
            user_id (int): User ID to include in hash

        Returns:
            str: 64-character hexadecimal session hash
        """
        # Combine secure random token + user ID + timestamp
        random_token = secrets.token_hex(24)
        timestamp = str(datetime.utcnow().timestamp())
        combined = f"{random_token}{user_id}{timestamp}"

        # Hash the combination to get fixed-length session hash
        session_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        return session_hash

    @classmethod
    def validate_registration_data(cls, email, password, full_name):
        """
        Validate registration input data with enhanced password strength checks.

        Args:
            email (str): Email address
            password (str): Plain text password
            full_name (str): User's full name

        Returns:
            tuple: (is_valid: bool, errors: dict)
        """
        errors = {}

        # Email validation using ValidationUtils
        is_valid_email, email_error = ValidationUtils.validate_email(email)
        if not is_valid_email:
            errors["email"] = email_error
        elif User.email_exists(email):
            errors["email"] = "Email already exists"

        # Password validation with strength requirements
        is_valid_password, password_error = ValidationUtils.validate_password_strength(
            password,
            min_length=cls.MIN_PASSWORD_LENGTH,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
            require_special=False,
        )
        if not is_valid_password:
            errors["password"] = password_error

        # Name validation using ValidationUtils
        is_valid_name, name_error = ValidationUtils.validate_name(
            full_name, min_length=cls.MIN_NAME_LENGTH, max_length=cls.MAX_NAME_LENGTH
        )
        if not is_valid_name:
            errors["name"] = name_error

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def register_user(cls, email, password, full_name):
        """
        Register a new user with hashed password.

        Args:
            email (str): User email address
            password (str): Plain text password
            full_name (str): User's full name

        Returns:
            dict: Result with success status, user data or errors
        """
        # Validate input
        is_valid, errors = cls.validate_registration_data(email, password, full_name)
        if not is_valid:
            return {"success": False, "errors": errors}

        try:
            # Hash password
            password_hash = cls.hash_password(password)

            # Create user
            user = User(
                email=email.lower().strip(),
                full_name=full_name.strip(),
                password_hash=password_hash,
            )
            user.save()

            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            }
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}

    @classmethod
    def authenticate_user(cls, email, password):
        """
        Authenticate user and create session.

        Args:
            email (str): User email address
            password (str): Plain text password

        Returns:
            dict: Result with success status, session data or error message
        """
        # Validate input
        if not email or not password:
            return {
                "success": False,
                "authenticated": False,
                "message": "Email and password are required",
            }

        # Find user
        user = User.find_by_email(email.lower().strip())
        if not user:
            return {
                "success": False,
                "authenticated": False,
                "message": "Invalid email or password",
            }

        # Verify password
        if not cls.verify_password(password, user.password_hash):
            return {
                "success": False,
                "authenticated": False,
                "message": "Invalid email or password",
            }

        # Create session
        try:
            session_data = cls.create_session(user)
            return {
                "success": True,
                "authenticated": True,
                "user": user.to_dict(),
                "expiry_in": session_data["expiry_in"],
            }
        except Exception as e:
            return {
                "success": False,
                "authenticated": False,
                "message": f"Login failed: {str(e)}",
            }

    @classmethod
    def create_session(cls, user):
        """
        Create a new session for authenticated user.

        Replaces any existing sessions for the user.

        Args:
            user (User): Authenticated user instance

        Returns:
            dict: Session data with hash and expiry time
        """
        # Delete any existing sessions for this user
        CoatHanger.delete_user_sessions(user.id)

        # Generate session hash
        session_hash = cls.generate_session_hash(user.id)

        # Create coat hanger entry
        coat_hanger = CoatHanger(
            user_id=user.id,
            session_hash=session_hash,
            user_data={
                "email": user.email,
                "full_name": user.full_name,
                "user_id": user.id,
            },
        )
        coat_hanger.save()

        # Store session hash in Flask session
        session["session_hash"] = session_hash
        session["user_id"] = user.id
        session.permanent = True  # Use PERMANENT_SESSION_LIFETIME

        return {
            "session_hash": session_hash,
            "expiry_in": CoatHanger.SESSION_TIMEOUT_SECONDS,
        }

    @classmethod
    def get_current_user(cls):
        """
        Get currently authenticated user from session.

        Returns:
            User: Authenticated user or None if not authenticated
        """
        session_hash = session.get("session_hash")
        if not session_hash:
            return None

        # Find coat hanger entry
        coat_hanger = CoatHanger.find_by_session_hash(session_hash)
        if not coat_hanger:
            # Session expired or invalid
            cls.clear_session()
            return None

        # Renew session (update timestamp)
        coat_hanger.renew()

        # Return user
        return coat_hanger.user

    @classmethod
    def check_session_status(cls):
        """
        Check current session status.

        Returns:
            dict: Session status with user data and expiry time
        """
        user = cls.get_current_user()

        if not user:
            return {"authenticated": False}

        # Get coat hanger for expiry time
        session_hash = session.get("session_hash")
        coat_hanger = CoatHanger.find_by_session_hash(session_hash)

        return {
            "authenticated": True,
            "user": user.to_dict(),
            "expiry_in": coat_hanger.time_until_expiry() if coat_hanger else 0,
        }

    @classmethod
    def logout_user(cls):
        """
        Logout current user and clear session.

        Returns:
            dict: Result with success status
        """
        session_hash = session.get("session_hash")

        if not session_hash:
            return {"success": False, "message": "No active session"}

        # Find and delete coat hanger entry
        coat_hanger = CoatHanger.find_by_session_hash(session_hash)
        if coat_hanger:
            coat_hanger.delete()

        # Clear Flask session
        cls.clear_session()

        return {"success": True, "message": "Logged out successfully"}

    @staticmethod
    def clear_session():
        """Clear all session data."""
        session.clear()

    @staticmethod
    def is_authenticated():
        """
        Check if current request has authenticated session.

        Returns:
            bool: True if authenticated, False otherwise
        """
        session_hash = session.get("session_hash")
        if not session_hash:
            return False

        coat_hanger = CoatHanger.find_by_session_hash(session_hash)
        return coat_hanger is not None
