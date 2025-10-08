"""
Session management utilities.

Helper functions for session operations.
Complements the AuthService coat hanger pattern.
"""

from datetime import datetime, timedelta
from src.models.coat_hanger import CoatHanger


class SessionUtils:
    """
    Utility class for session management operations.

    Constitutional compliance: Utility layer for session-related helpers.
    """

    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up all expired sessions from database.

        Should be called periodically by a background task or cron job.

        Returns:
            int: Number of sessions cleaned up
        """
        return CoatHanger.cleanup_expired_sessions()

    @staticmethod
    def get_session_info(session_hash):
        """
        Get detailed information about a session.

        Args:
            session_hash (str): Session hash to look up

        Returns:
            dict: Session information or None if not found
        """
        coat_hanger = CoatHanger.find_by_session_hash(session_hash)

        if not coat_hanger:
            return None

        return {
            "user_id": coat_hanger.user_id,
            "created_at": (
                coat_hanger.created_at.isoformat() if coat_hanger.created_at else None
            ),
            "updated_at": (
                coat_hanger.updated_at.isoformat() if coat_hanger.updated_at else None
            ),
            "is_expired": coat_hanger.is_expired(),
            "time_until_expiry": coat_hanger.time_until_expiry(),
            "user_data": coat_hanger.user_data,
        }

    @staticmethod
    def get_active_sessions_count():
        """
        Get count of active (non-expired) sessions.

        Returns:
            int: Number of active sessions
        """
        cutoff_time = datetime.utcnow() - timedelta(
            seconds=CoatHanger.SESSION_TIMEOUT_SECONDS
        )
        active_sessions = CoatHanger.query.filter(
            CoatHanger.updated_at >= cutoff_time
        ).count()
        return active_sessions

    @staticmethod
    def get_user_session_count(user_id):
        """
        Get count of active sessions for a specific user.

        Args:
            user_id (int): User ID

        Returns:
            int: Number of active sessions for user
        """
        cutoff_time = datetime.utcnow() - timedelta(
            seconds=CoatHanger.SESSION_TIMEOUT_SECONDS
        )
        user_sessions = CoatHanger.query.filter(
            CoatHanger.user_id == user_id, CoatHanger.updated_at >= cutoff_time
        ).count()
        return user_sessions

    @staticmethod
    def invalidate_user_sessions(user_id):
        """
        Invalidate all sessions for a specific user.

        Useful for forced logout or password change.

        Args:
            user_id (int): User ID whose sessions to invalidate

        Returns:
            int: Number of sessions invalidated
        """
        return CoatHanger.delete_user_sessions(user_id)

    @staticmethod
    def get_session_statistics():
        """
        Get overall session statistics.

        Returns:
            dict: Session statistics
        """
        total_sessions = CoatHanger.query.count()
        active_sessions = SessionUtils.get_active_sessions_count()
        expired_sessions = total_sessions - active_sessions

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
        }
