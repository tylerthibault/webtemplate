"""
User service for user-related operations.

Handles user profile management and queries.
Following constitutional principles - thick logic layer.
"""

from src.models.user import User


class UserService:
    """
    User service for profile and user management operations.

    Constitutional compliance: Business logic for user operations
    separate from authentication concerns.
    """

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID.

        Args:
            user_id (int): User ID

        Returns:
            User: User instance or None if not found
        """
        return User.find_by_id(user_id)

    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email address.

        Args:
            email (str): Email address

        Returns:
            User: User instance or None if not found
        """
        return User.find_by_email(email.lower().strip() if email else "")

    @staticmethod
    def get_all_users():
        """
        Get all users.

        Returns:
            list: List of User instances
        """
        return User.find_all()

    @staticmethod
    def delete_user(user_id):
        """
        Delete user by ID.

        Also deletes all associated sessions (cascade).

        Args:
            user_id (int): User ID to delete

        Returns:
            dict: Result with success status
        """
        user = User.find_by_id(user_id)

        if not user:
            return {"success": False, "message": "User not found"}

        try:
            user.delete()
            return {"success": True, "message": "User deleted successfully"}
        except Exception as e:
            return {"success": False, "message": f"Delete failed: {str(e)}"}

    @staticmethod
    def update_user_profile(user_id, full_name=None):
        """
        Update user profile information.

        Args:
            user_id (int): User ID
            full_name (str, optional): New full name

        Returns:
            dict: Result with success status and updated user data
        """
        user = User.find_by_id(user_id)

        if not user:
            return {"success": False, "message": "User not found"}

        try:
            if full_name is not None:
                # Validate name
                if len(full_name.strip()) < 2:
                    return {
                        "success": False,
                        "message": "Name must be at least 2 characters",
                    }
                if len(full_name.strip()) > 100:
                    return {
                        "success": False,
                        "message": "Name must not exceed 100 characters",
                    }
                user.full_name = full_name.strip()

            user.save()

            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            return {"success": False, "message": f"Update failed: {str(e)}"}

    @staticmethod
    def user_exists(email):
        """
        Check if user with email exists.

        Args:
            email (str): Email address to check

        Returns:
            bool: True if user exists, False otherwise
        """
        return User.email_exists(email.lower().strip() if email else "")
