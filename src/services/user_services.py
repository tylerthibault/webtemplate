"""
User and Authentication Services

This module contains the business logic for user management and authentication.
Following the MVC pattern, these services handle all business rules and delegate
database operations to the models.
"""

import bcrypt
import secrets
from datetime import datetime, timedelta
from flask import session, g
from sqlalchemy.exc import IntegrityError
from src import db
from src.models.user_model import User
from src.models.coat_hanger import CoatHanger


class UserService:
    """
    Service class for user management operations.
    
    Handles all user-related business logic including CRUD operations,
    user data retrieval, and profile management. Delegates database
    operations to the User model.
    """
    
    @staticmethod
    def create_user(email, full_name, password):
        """
        Create a new user with hashed password.
        
        Args:
            email (str): User's email address
            full_name (str): User's full name
            password (str): Plain text password to be hashed
            
        Returns:
            tuple: (User object, success boolean, error message)
        """
        try:
            # Check if user already exists
            existing_user = User.find_one_by(email=email.lower().strip())
            if existing_user:
                return None, False, "A user with this email already exists"
            
            # Hash the password
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt(rounds=12)
            ).decode('utf-8')
            
            # Create user
            user = User.create(
                email=email.lower().strip(),
                full_name=full_name.strip(),
                password_hash=password_hash
            )
            
            return user, True, None
            
        except IntegrityError:
            db.session.rollback()
            return None, False, "A user with this email already exists"
        except Exception as e:
            db.session.rollback()
            return None, False, f"Error creating user: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user by their ID.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            User: User object or None if not found
        """
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """
        Retrieve a user by their email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            User: User object or None if not found
        """
        return User.find_one_by(email=email.lower().strip())
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """
        Update user profile information.
        
        Args:
            user_id (int): User's unique identifier
            **kwargs: Fields to update (full_name, email, etc.)
            
        Returns:
            tuple: (User object, success boolean, error message)
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return None, False, "User not found"
            
            # Handle email updates with uniqueness check
            if 'email' in kwargs:
                new_email = kwargs['email'].lower().strip()
                if new_email != user.email:
                    existing_user = User.find_one_by(email=new_email)
                    if existing_user:
                        return None, False, "A user with this email already exists"
                    kwargs['email'] = new_email
            
            # Strip whitespace from text fields
            if 'full_name' in kwargs:
                kwargs['full_name'] = kwargs['full_name'].strip()
            
            updated_user = user.update(**kwargs)
            return updated_user, True, None
            
        except IntegrityError:
            db.session.rollback()
            return None, False, "A user with this email already exists"
        except Exception as e:
            db.session.rollback()
            return None, False, f"Error updating user: {str(e)}"
    
    @staticmethod
    def update_user_password(user_id, current_password, new_password):
        """
        Update user's password after verifying current password.
        
        Args:
            user_id (int): User's unique identifier
            current_password (str): Current password for verification
            new_password (str): New password to set
            
        Returns:
            tuple: (success boolean, error message)
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Verify current password
            if not bcrypt.checkpw(
                current_password.encode('utf-8'), 
                user.password_hash.encode('utf-8')
            ):
                return False, "Current password is incorrect"
            
            # Hash new password
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt(rounds=12)
            ).decode('utf-8')
            
            # Update password
            user.update(password_hash=new_password_hash)
            
            # Invalidate all existing sessions for security
            AuthService.logout_all_sessions(user_id)
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating password: {str(e)}"
    
    @staticmethod
    def delete_user(user_id):
        """
        Delete a user and all associated data.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            tuple: (success boolean, error message)
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Clean up sessions first
            AuthService.logout_all_sessions(user_id)
            
            # Delete user
            user.delete()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting user: {str(e)}"
    
    @staticmethod
    def get_user_context(user_id):
        """
            Retrieve user data based off the user id and the role they have.
        """
        user = User.get_by_id(user_id)
        if not user:
            return None

        roles = [role.name for role in user.roles]
        return {
            'user': user,
            'roles': roles
        }

    @staticmethod
    def get_all_users_for_management():
        """
        Get all users with their roles for management interface.
        
        Returns:
            list: List of user dictionaries with role information
        """
        try:
            from src.models.role_model import Role
            users = User.get_all()
            users_data = []
            
            for user in users:
                user_dict = user.to_dict()
                user_dict['roles'] = [role.name for role in user.roles]
                # Ensure these fields exist, default to safe values if not
                user_dict['is_active'] = getattr(user, 'is_active', True)
                user_dict['force_password_change'] = getattr(user, 'force_password_change', False)
                users_data.append(user_dict)
            
            return users_data
            
        except Exception as e:
            return []

    @staticmethod
    def change_user_role(user_id, role_name, action='add'):
        """
        Add or remove a role from a user.
        
        Args:
            user_id (int): User's unique identifier
            role_name (str): Name of the role to add/remove
            action (str): 'add' or 'remove'
            
        Returns:
            dict: Result with success status and message
        """
        try:
            from src.models.role_model import Role
            
            user = User.get_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            role = Role.find_one_by(name=role_name)
            if not role:
                return {'success': False, 'message': 'Role not found'}
            
            if action == 'add':
                if user.has_role(role_name):
                    return {'success': False, 'message': f'User already has {role_name} role'}
                user.add_role(role)
                message = f'{role_name} role added to user'
            elif action == 'remove':
                if not user.has_role(role_name):
                    return {'success': False, 'message': f'User does not have {role_name} role'}
                user.remove_role(role)
                message = f'{role_name} role removed from user'
            else:
                return {'success': False, 'message': 'Invalid action. Use "add" or "remove"'}
            
            db.session.commit()
            return {'success': True, 'message': message}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error changing user role: {str(e)}'}

    @staticmethod
    def soft_delete_user(user_id):
        """
        Soft delete a user by setting is_active to False.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            dict: Result with success status and message
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Set is_active to False
            user.is_active = False
            
            # Also logout all sessions for this user
            AuthService.logout_all_sessions(user_id)
            
            db.session.commit()
            return {'success': True, 'message': 'User deactivated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error deactivating user: {str(e)}'}

    @staticmethod
    def reactivate_user(user_id):
        """
        Reactivate a soft-deleted user by setting is_active to True.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            dict: Result with success status and message
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Set is_active to True
            user.is_active = True
            
            db.session.commit()
            return {'success': True, 'message': 'User reactivated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error reactivating user: {str(e)}'}

    @staticmethod
    def force_password_change(user_id):
        """
        Force a user to change their password on next login.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            dict: Result with success status and message
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Set force_password_change to True
            user.force_password_change = True
            
            # Logout all sessions to force re-authentication
            AuthService.logout_all_sessions(user_id)
            
            db.session.commit()
            return {'success': True, 'message': 'User will be required to change password on next login'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error forcing password change: {str(e)}'}


class AuthService:
    """
    Service class for authentication operations.
    
    Handles user authentication, session management, and security operations
    using the custom "coat hanger" session system.
    """
    
    @staticmethod
    def authenticate_user(credentials):
        """
        Authenticate user credentials and create session.
        
        Args:
            email (str): User's email address
            password (str): Plain text password
            
        Returns:
            dict: {'user': User object, 'success': bool, 'message': str}
        """
        try:
            email = credentials.get('email', '').lower().strip()
            password = credentials.get('password', '')
            # Find user by email
            user = User.find_one_by(email=email.lower().strip())
            if not user:
                return {'user': None, 'success': False, 'message': "Invalid email or password"}
            
            # Check if user is active
            if hasattr(user, 'is_active') and not user.is_active:
                return {'user': None, 'success': False, 'message': "Account has been deactivated. Please contact an administrator."}
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return {'user': None, 'success': False, 'message': "Invalid email or password"}
            
            # Check if password change is required
            if hasattr(user, 'force_password_change') and user.force_password_change:
                return {'user': user, 'success': False, 'message': "You must change your password before continuing.", 'force_password_change': True}
            
            # Create session
            session_created = AuthService.create_session(user)
            if not session_created:
                return {'user': None, 'success': False, 'message': "Error creating session"}
            
            return {'user': user, 'success': True, 'message': None}
            
        except Exception as e:
            return {'user': None, 'success': False, 'message': f"Authentication error: {str(e)}"}
    
    @staticmethod
    def create_session(user):
        """
        Create a new session for the authenticated user.
        
        Args:
            user (User): Authenticated user object
            
        Returns:
            bool: True if session created successfully
        """
        try:
            # Generate secure session token
            session_token = secrets.token_urlsafe(32)
            
            # Prepare user data for session storage
            user_data = {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'last_login': datetime.utcnow().isoformat()
            }
            
            # Create coat hanger session record
            coat_hanger = CoatHanger.create(
                user_id=user.id,
                session_hash=session_token,
                user_data=user_data
            )
            
            # Store session token in Flask session
            session['session_token'] = session_token
            session.permanent = True  # Enable session timeout
            
            # Update user's last login timestamp
            user.update(updated_at=datetime.utcnow())
            
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def logout_user():
        """
        Logout current user by clearing session and removing from database.
        
        Returns:
            bool: True if logout successful
        """
        try:
            session_token = session.get('session_token')
            if session_token:
                # Remove session from database
                coat_hanger = CoatHanger.find_one_by(session_hash=session_token)
                if coat_hanger:
                    coat_hanger.delete()
            
            # Clear Flask session
            session.clear()
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def logout_all_sessions(user_id):
        """
        Logout all sessions for a specific user.
        
        Args:
            user_id (int): User's unique identifier
            
        Returns:
            bool: True if all sessions cleared successfully
        """
        try:
            # Remove all sessions for this user
            sessions = CoatHanger.find_by(user_id=user_id)
            for session_record in sessions:
                session_record.delete()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_current_user():
        """
        Get the currently authenticated user from session.
        
        Returns:
            User: Current user object or None if not authenticated
        """
        user_id = getattr(g, 'current_user_id', None)
        if user_id:
            return User.get_by_id(user_id)
        return None
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up expired sessions from the database.
        Should be called periodically to maintain database hygiene.
        
        Returns:
            int: Number of expired sessions removed
        """
        try:
            # Calculate timeout threshold (10 minutes)
            timeout_threshold = datetime.utcnow() - timedelta(minutes=10)
            
            # Find and delete expired sessions
            expired_sessions = CoatHanger.query.filter(
                CoatHanger.updated_at < timeout_threshold
            ).all()
            
            count = len(expired_sessions)
            for session_record in expired_sessions:
                session_record.delete()
            
            return count
            
        except Exception as e:
            db.session.rollback()
            return 0
    
    @staticmethod
    def validate_session_token(session_token):
        """
        Validate a session token and update timestamp if valid.
        
        Args:
            session_token (str): Session token to validate
            
        Returns:
            tuple: (CoatHanger object, is_valid boolean)
        """
        try:
            if not session_token:
                return None, False
            
            # Find session in database
            coat_hanger = CoatHanger.find_one_by(session_hash=session_token)
            if not coat_hanger:
                return None, False
            
            # Check if session has expired (10 minutes)
            timeout_threshold = datetime.utcnow() - timedelta(minutes=10)
            if coat_hanger.updated_at < timeout_threshold:
                # Session expired - clean up
                coat_hanger.delete()
                return None, False
            
            # Update session timestamp
            coat_hanger.update(updated_at=datetime.utcnow())
            
            return coat_hanger, True
            
        except Exception as e:
            return None, False

    @staticmethod
    def is_superuser():
        """
        Check if the current user has superuser role.
        
        Returns:
            bool: True if current user is a superuser, False otherwise
        """
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return False
            
            return current_user.has_role('superuser')
            
        except Exception:
            return False
        
    @staticmethod
    def register_user(user_data):
        """
        Register a new user with provided data.
        
        Args:
            user_data (dict): Dictionary containing user registration data
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            email = user_data.get('email', '').lower().strip()
            full_name = user_data.get('full_name', '').strip()
            password = user_data.get('password', '')
            confirm_password = user_data.get('confirm_password', '')
            
            # Basic validations
            if not email or not full_name or not password or not confirm_password:
                return {'success': False, 'message': "All fields are required"}
            
            if password != confirm_password:
                return {'success': False, 'message': "Passwords do not match"}
            
            # Create user
            user, success, error = UserService.create_user(
                email=email,
                full_name=full_name,
                password=password
            )
            
            if not success:
                return {'success': False, 'message': error}
            
            return {'success': True, 'message': "User registered successfully"}
            
        except Exception as e:
            return {'success': False, 'message': f"Registration error: {str(e)}"}
