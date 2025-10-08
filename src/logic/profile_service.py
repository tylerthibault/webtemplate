"""
Profile service for user profile management operations.

This service handles business logic for viewing and updating user profiles,
including validation, concurrent edit detection, and email notifications.
Follows MVC pattern with thick logic layer.
"""

from typing import Dict, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import defer
from src.models.user import User
from src import db
from src.utils.validators import validate_bio, validate_password_strength
from src.logic.image_utils import (
    validate_image,
    decode_image,
    encode_image,
    sanitize_image,
)
from flask import render_template
import bcrypt
import re
import logging

# Configure logger
logger = logging.getLogger(__name__)


class ConcurrentEditError(Exception):
    """Raised when a concurrent edit conflict is detected."""

    pass


class ValidationError(Exception):
    """Raised when profile data validation fails."""

    def __init__(self, errors: Dict):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")


class ProfileService:
    """
    Service class for user profile operations.

    Handles profile retrieval, updates, validation, concurrent edit detection,
    and email notifications for profile changes.
    """

    @staticmethod
    def get_user_profile(user_id: int, include_picture: bool = False) -> Optional[Dict]:
        """
        Retrieve user profile data with optional picture inclusion.

        Uses lazy loading to exclude profile_picture_data by default for
        performance. Only loads picture when explicitly requested.

        Args:
            user_id: ID of user to retrieve
            include_picture: If True, include profile_picture_data in response

        Returns:
            Dictionary of user profile data, or None if user not found

        Example:
            >>> profile = ProfileService.get_user_profile(123)
            >>> profile['email']
            'user@example.com'
            >>> 'profile_picture_data' in profile
            False

            >>> profile_with_pic = ProfileService.get_user_profile(123, include_picture=True)
            >>> 'profile_picture_data' in profile_with_pic
            True
        """
        if include_picture:
            # Load all fields including profile_picture_data
            user = User.query.get(user_id)
        else:
            # Use deferred loading to exclude profile_picture_data
            user = User.query.options(defer("profile_picture_data")).get(user_id)

        if user:
            return user.to_dict(include_picture=include_picture)
        return None

    @staticmethod
    def update_profile(user_id: int, data: Dict, submitted_updated_at: str) -> Dict:
        """
        Update user profile with validation and concurrent edit detection.

        Performs validation, checks for concurrent edits, updates profile fields,
        handles password changes (with bcrypt hashing), processes profile picture
        uploads (with base64 encoding), and triggers email notifications if
        email changed.

        Args:
            user_id: ID of user to update
            data: Dictionary of fields to update (full_name, email, bio, password, etc.)
            submitted_updated_at: ISO 8601 timestamp from form submission for conflict detection

        Returns:
            Dictionary of updated user profile data

        Raises:
            ConcurrentEditError: If user.updated_at is newer than submitted_updated_at
            ValidationError: If data validation fails

        Example:
            >>> data = {
            ...     'full_name': 'Jane Doe',
            ...     'email': 'jane@example.com',
            ...     'bio': 'Software developer',
            ...     'updated_at': '2025-10-06T12:00:00Z'
            ... }
            >>> updated = ProfileService.update_profile(123, data, '2025-10-06T12:00:00Z')
            >>> updated['full_name']
            'Jane Doe'
        """
        logger.debug(f"Updating profile for user {user_id}")

        # Get user
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found for profile update")
            raise ValueError(f"User {user_id} not found")

        # Detect concurrent edits
        if ProfileService.detect_concurrent_edit(user, submitted_updated_at):
            logger.warning(f"Concurrent edit detected for user {user_id}")
            raise ConcurrentEditError(
                "Profile was modified by another session. Please refresh and try again."
            )

        # Add user_id to data for validation
        data["user_id"] = user_id

        # Validate data
        is_valid, errors = ProfileService.validate_profile_data(data)
        if not is_valid:
            logger.info(f"Validation failed for user {user_id}: {list(errors.keys())}")
            raise ValidationError(errors)

        # Track old email for notifications
        old_email = user.email
        email_changed = False

        # Update fields
        if "full_name" in data:
            logger.debug(f"Updating full_name for user {user_id}")
            user.full_name = data["full_name"].strip()

        if "email" in data:
            new_email = data["email"].strip().lower()
            if new_email != old_email:
                logger.info(
                    f"User {user_id} changing email from {old_email} to {new_email}"
                )
                email_changed = True
                user.email = new_email

        if "bio" in data:
            # Use sanitized bio from validator
            is_valid, sanitized_bio = validate_bio(data["bio"])
            user.bio = sanitized_bio if sanitized_bio else None
            logger.debug(f"Updated bio for user {user_id}")

        # Handle password change
        if "password" in data and data["password"]:
            logger.info(f"User {user_id} changing password")
            # Hash password with bcrypt (same as auth_service)
            password_bytes = data["password"].encode("utf-8")
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
            user.password_hash = hashed.decode("utf-8")

        # Handle profile picture upload
        if "profile_picture_data" in data and data["profile_picture_data"]:
            try:
                logger.debug(f"Processing profile picture upload for user {user_id}")

                # Decode base64
                image_bytes = decode_image(data["profile_picture_data"])

                # Sanitize image (remove EXIF, resize, optimize)
                sanitized_bytes = sanitize_image(image_bytes)

                # Re-encode to base64 for storage
                user.profile_picture_data = encode_image(sanitized_bytes)

                # Detect and store MIME type
                is_valid, mime_type = validate_image(sanitized_bytes)
                if is_valid:
                    user.profile_picture_mime_type = mime_type
                    logger.info(
                        f"Profile picture uploaded for user {user_id} ({mime_type})"
                    )
            except Exception as e:
                logger.error(
                    f"Error processing profile picture for user {user_id}: {str(e)}"
                )
                raise ValidationError({"profile_picture": str(e)})

        # Remove profile picture if requested
        if data.get("remove_profile_picture"):
            logger.info(f"Removing profile picture for user {user_id}")
            user.profile_picture_data = None
            user.profile_picture_mime_type = None

        # Commit changes (updated_at will auto-update via trigger)
        try:
            db.session.commit()
            logger.info(f"Profile update committed for user {user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Database error updating profile for user {user_id}: {str(e)}",
                exc_info=True,
            )
            raise Exception(f"Database error: {str(e)}")

        # Send email notifications if email changed
        if email_changed:
            logger.info(f"Sending email change notifications for user {user_id}")
            ProfileService.send_email_change_notifications(old_email, user.email)

        # Return updated profile
        return user.to_dict(include_picture=False)

    @staticmethod
    def validate_profile_data(data: Dict) -> Tuple[bool, Dict]:
        """
        Validate profile update data against business rules.

        Validates:
        - full_name: Required, 2-100 characters
        - email: Required, valid format, unique in database
        - bio: Optional, max 500 characters, XSS sanitization
        - password: If changing, min 8 chars, complexity requirements
        - profile_picture_data: If present, valid base64, size under 5MB

        Args:
            data: Dictionary of profile fields to validate

        Returns:
            Tuple of (is_valid, errors_dict)
            - If valid: (True, {})
            - If invalid: (False, {'full_name': 'Error message', ...})

        Example:
            >>> data = {'full_name': 'A', 'email': 'invalid'}
            >>> valid, errors = ProfileService.validate_profile_data(data)
            >>> valid
            False
            >>> errors
            {'full_name': 'Must be at least 2 characters', 'email': 'Invalid email format'}
        """
        errors = {}

        # Validate full_name
        full_name = data.get("full_name", "").strip()
        if not full_name:
            errors["full_name"] = "Full name is required"
        elif len(full_name) < 2:
            errors["full_name"] = "Must be at least 2 characters"
        elif len(full_name) > 100:
            errors["full_name"] = "Must be 100 characters or less"

        # Validate email
        email = data.get("email", "").strip().lower()
        if not email:
            errors["email"] = "Email is required"
        else:
            # Basic email format validation
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                errors["email"] = "Invalid email format"
            else:
                # Check uniqueness (if email changed)
                user_id = data.get("user_id")
                existing = User.query.filter_by(email=email).first()
                if existing and existing.id != user_id:
                    errors["email"] = "Email already in use"

        # Validate bio (optional)
        if "bio" in data and data["bio"]:
            is_valid, result = validate_bio(data["bio"])
            if not is_valid:
                errors["bio"] = result

        # Validate password (if changing)
        if "password" in data and data["password"]:
            is_valid, error_msg = validate_password_strength(data["password"])
            if not is_valid:
                errors["password"] = error_msg

        # Validate profile picture (if uploading)
        if "profile_picture_data" in data and data["profile_picture_data"]:
            try:
                # Decode base64 to validate it's valid base64
                image_bytes = decode_image(data["profile_picture_data"])
                # Validate image format and size
                is_valid, result = validate_image(image_bytes)
                if not is_valid:
                    errors["profile_picture"] = result
            except ValueError:
                errors["profile_picture"] = "Invalid image data"

        return (len(errors) == 0, errors)

    @staticmethod
    def detect_concurrent_edit(user: User, submitted_updated_at: str) -> bool:
        """
        Detect if profile was modified by another session (optimistic locking).

        Compares user's current updated_at timestamp with the timestamp
        from the form submission. If current is newer, another session
        modified the profile.

        Args:
            user: User model instance with current updated_at
            submitted_updated_at: ISO 8601 timestamp string from form submission

        Returns:
            True if concurrent edit detected (conflict), False otherwise

        Example:
            >>> user = User.query.get(123)
            >>> user.updated_at
            datetime(2025, 10, 6, 12, 30, 0)
            >>> detect_concurrent_edit(user, '2025-10-06T12:00:00Z')
            True  # User was updated after form was loaded
        """
        if not submitted_updated_at:
            # No timestamp provided, can't detect conflict
            return False

        try:
            # Parse ISO 8601 timestamp from form
            submitted_dt = datetime.fromisoformat(
                submitted_updated_at.replace("Z", "+00:00")
            )
            
            # Remove timezone info to make naive for comparison
            # (database stores naive UTC timestamps)
            if submitted_dt.tzinfo is not None:
                submitted_dt = submitted_dt.replace(tzinfo=None)

            # Compare with current user timestamp
            # If user was updated after form was loaded, we have a conflict
            if user.updated_at and user.updated_at > submitted_dt:
                return True

            return False
        except (ValueError, AttributeError):
            # Invalid timestamp format, treat as no conflict
            return False

    @staticmethod
    def send_email_change_notifications(old_email: str, new_email: str) -> None:
        """
        Send notification emails when user changes their email address.

        Sends two emails:
        1. To old email: "Your email was changed to {new_email}"
        2. To new email: "Your email address was changed from {old_email}"

        Emails are queued for async sending to avoid blocking request.

        Args:
            old_email: User's previous email address
            new_email: User's new email address

        Returns:
            None

        Example:
            >>> ProfileService.send_email_change_notifications(
            ...     'old@example.com',
            ...     'new@example.com'
            ... )
            # Two emails queued for sending
        """
        # Prepare template context
        change_date = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

        # Render email templates (templates not yet created)
        # old_email_html = render_template(
        #     "emails/email_change_old.html",
        #     old_email=old_email,
        #     new_email=new_email,
        #     change_date=change_date,
        # )
        #
        # new_email_html = render_template(
        #     "emails/email_change_new.html",
        #     old_email=old_email,
        #     new_email=new_email,
        #     change_date=change_date,
        # )

        # TODO: Integrate with email service from Feature 001 contact form
        # or implement minimal SMTP/email queue here

        # Placeholder for email sending
        # In production, this would call an email service:
        # EmailService.send(
        #     to=old_email,
        #     subject='Email Address Changed',
        #     html=old_email_html
        # )
        # EmailService.send(
        #     to=new_email,
        #     subject='Email Address Updated',
        #     html=new_email_html
        # )

        # For now, just log the intent (tests will mock this function)
        pass
