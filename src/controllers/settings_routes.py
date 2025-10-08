"""
Settings routes for user profile management.

Blueprint for personal settings page where authenticated users can view
and update their profile information (name, email, bio, password, picture).
"""

import logging
from flask import Blueprint, request, jsonify, render_template, session
from src.logic.profile_service import (
    ProfileService,
    ConcurrentEditError,
    ValidationError,
)
from src.logic.decorators import login_required
from src.utils.csrf_utils import csrf_protect
from src.models.coat_hanger import CoatHanger

# Configure logger
logger = logging.getLogger(__name__)


# Create settings blueprint
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET"])
@login_required
def get_settings():
    """
    Display personal settings page.

    Authenticated users can view their profile information including
    full name, email, bio, and profile picture.

    Returns:
        Rendered template with user profile data (HTML request)
        JSON response with user profile data (JSON request)

    Response Codes:
        200: Settings page rendered successfully
        401: User not authenticated (handled by @login_required decorator)
        404: User not found
        500: Server error

    Template Variables:
        user: Dictionary of user profile data
        csrf_token: CSRF token for form submission

    Example:
        GET /settings
        Response: HTML page with profile form
    """
    # Get user ID from session
    user_id = session.get("user_id")

    try:
        # Retrieve user profile with picture data included for preview
        user_data = ProfileService.get_user_profile(user_id, include_picture=True)

        if not user_data:
            logger.warning(f"User {user_id} not found when loading settings page")
            return jsonify({"error": "User not found"}), 404

        logger.info(f"User {user_id} accessed settings page")

        # Return JSON only for explicit API requests (Accept: application/json header)
        # Otherwise, default to HTML rendering for browser requests
        if request.is_json or request.accept_mimetypes["application/json"] > request.accept_mimetypes["text/html"]:
            return jsonify({"user": user_data}), 200

        return render_template("private/settings/index.html", user=user_data), 200

    except Exception as e:
        logger.error(
            f"Error loading settings for user {user_id}: {str(e)}", exc_info=True
        )
        return jsonify({"error": "An error occurred loading your settings"}), 500


@settings_bp.route("/", methods=["POST"])
@login_required
@csrf_protect
def update_settings():
    """
    Update user profile information.

    Accepts JSON payload with profile fields to update. Validates data,
    checks for concurrent edits, updates database, and returns updated
    profile data.

    Request Body (JSON):
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "bio": "Software developer",
            "current_password": "oldpass123" (required for email/password change),
            "new_password": "newpass456" (optional),
            "profile_picture_data": "base64-encoded-image" (optional),
            "updated_at": "2025-10-06T12:00:00Z" (for concurrent edit detection)
        }

    Returns:
        JSON response with updated user data or error messages

    Response Codes:
        200: Profile updated successfully
        400: Validation error (invalid data format)
        401: User not authenticated
        403: CSRF token missing or invalid
        409: Concurrent edit detected (profile modified by another session)
        422: Current password incorrect (for email/password changes)
        500: Internal server error

    Example Success (200):
        {
            "success": true,
            "message": "Profile updated successfully",
            "user": {
                "id": 123,
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "bio": "Software developer",
                "updated_at": "2025-10-06T12:30:00Z"
            }
        }

    Example Error (409):
        {
            "error": "Profile was modified by another session",
            "current_data": {...},
            "conflicting_fields": ["full_name", "email"]
        }
    """
    # Get user ID from session
    user_id = session.get("user_id")

    # Get request data
    data = request.get_json()
    if not data:
        logger.warning(f"User {user_id} submitted empty data to settings update")
        return jsonify({"error": "No data provided"}), 400

    # Extract submitted_updated_at for concurrent edit detection
    submitted_updated_at = data.get("updated_at", "")

    # Log the update attempt (without sensitive data)
    logger.info(f"User {user_id} attempting profile update")

    try:
        # Update profile using service layer
        updated_user = ProfileService.update_profile(
            user_id, data, submitted_updated_at
        )

        # Update Flask session with new user data
        session["user_email"] = updated_user["email"]
        session["user_name"] = updated_user["full_name"]

        # Update CoatHanger table with new cached user data
        session_hash = session.get("session_hash")
        if session_hash:
            coat_hanger = CoatHanger.find_by_session_hash(session_hash)
            if coat_hanger:
                # Update cached user data in session storage
                coat_hanger.user_data = {
                    "id": updated_user["id"],
                    "email": updated_user["email"],
                    "full_name": updated_user["full_name"],
                }
                coat_hanger.save()

        logger.info(f"User {user_id} successfully updated profile")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": updated_user,
                }
            ),
            200,
        )

    except ConcurrentEditError as e:
        # Profile was modified by another session
        logger.warning(
            f"Concurrent edit detected for user {user_id}. "
            f"Submitted timestamp: {submitted_updated_at}"
        )

        current_user = ProfileService.get_user_profile(user_id, include_picture=False)
        return jsonify({"error": str(e), "current_data": current_user}), 409

    except ValidationError as e:
        # Validation failed
        logger.info(f"Validation error for user {user_id}: {list(e.errors.keys())}")
        return jsonify({"error": "Validation failed", "errors": e.errors}), 400

    except ValueError as e:
        # User not found or other value error
        logger.error(f"ValueError updating profile for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 404

    except Exception as e:
        # Unexpected error
        logger.error(
            f"Unexpected error updating profile for user {user_id}: {str(e)}",
            exc_info=True,
        )
        return (
            jsonify(
                {
                    "error": "An unexpected error occurred",
                    "message": "Please try again later",
                }
            ),
            500,
        )
