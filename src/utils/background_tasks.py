"""
Background tasks and scheduled jobs.

Implements periodic cleanup and maintenance tasks.
"""

import click
from flask import Flask
from src import db
from src.utils.session_utils import SessionUtils
from src.utils.seed_data import seed_database, clear_database


def register_commands(app: Flask):
    """
    Register CLI commands with Flask app.

    Args:
        app: Flask application instance
    """

    @app.cli.command("cleanup-sessions")
    def cleanup_sessions_command():
        """
        Clean up expired sessions from database.

        Usage:
            flask cleanup-sessions
        """
        with app.app_context():
            count = SessionUtils.cleanup_expired_sessions()
            click.echo(f"Cleaned up {count} expired sessions")

    @app.cli.command("session-stats")
    def session_stats_command():
        """
        Display session statistics.

        Usage:
            flask session-stats
        """
        with app.app_context():
            active_count = SessionUtils.get_active_sessions_count()
            click.echo(f"Active sessions: {active_count}")

    @app.cli.command("init-db")
    def init_db_command():
        """
        Initialize database tables.

        Usage:
            flask init-db
        """
        with app.app_context():
            db.create_all()
            click.echo("Database tables created successfully")

    @app.cli.command("drop-db")
    @click.confirmation_option(prompt="Are you sure you want to drop all tables?")
    def drop_db_command():
        """
        Drop all database tables.

        Usage:
            flask drop-db
        """
        with app.app_context():
            db.drop_all()
            click.echo("All database tables dropped")

    @app.cli.command("seed-db")
    def seed_db_command():
        """
        Seed database with sample data.

        Usage:
            flask seed-db
        """
        with app.app_context():
            result = seed_database()
            click.echo(
                f"Seeded {len(result['users'])} users and {len(result['messages'])} messages"
            )

    @app.cli.command("clear-db")
    @click.confirmation_option(prompt="Are you sure you want to clear all data?")
    def clear_db_command():
        """
        Clear all data from database (keeps tables).

        Usage:
            flask clear-db
        """
        with app.app_context():
            clear_database()
            click.echo("Database cleared successfully")


class SessionCleanupScheduler:
    """
    Scheduler for automatic session cleanup.

    Can be integrated with APScheduler or similar for production use.
    """

    @staticmethod
    def cleanup_expired_sessions(app: Flask):
        """
        Cleanup method for scheduler.

        Args:
            app: Flask application instance
        """
        with app.app_context():
            count = SessionUtils.cleanup_expired_sessions()
            app.logger.info(f"Scheduled cleanup: removed {count} expired sessions")
            return count

    @staticmethod
    def setup_scheduler(app: Flask, interval_minutes: int = 30):
        """
        Set up APScheduler for periodic session cleanup.

        Requires: pip install APScheduler

        Args:
            app: Flask application instance
            interval_minutes: Cleanup interval in minutes (default 30)
        """
        try:
            from apscheduler.schedulers.background import BackgroundScheduler

            scheduler = BackgroundScheduler()
            scheduler.add_job(
                func=lambda: SessionCleanupScheduler.cleanup_expired_sessions(app),
                trigger="interval",
                minutes=interval_minutes,
                id="session_cleanup",
                name="Clean up expired sessions",
                replace_existing=True,
            )
            scheduler.start()
            app.logger.info(
                f"Session cleanup scheduler started (every {interval_minutes} minutes)"
            )

            # Cleanup on app shutdown
            import atexit

            atexit.register(lambda: scheduler.shutdown())

        except ImportError:
            app.logger.warning(
                "APScheduler not installed. " "Install with: pip install APScheduler"
            )
