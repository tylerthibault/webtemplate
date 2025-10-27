from src import db
from src.models.user_model import User
from src.models.role_model import Role
from src.services.user_services import UserService
import logging



"""
User seeding utilities for development database setup.
"""


logger = logging.getLogger(__name__)


def seed_users():
    """
    Seeds the database with development users.
    Creates 1 superuser, 2 admins, and 5 subscribers.
    """
    try:
        # Check if users already exist
        if User.query.count() > 0:
            logger.info("Users already exist in database. Skipping user seeding.")
            return
            
        # Ensure roles exist first
        superuser_role = Role.query.filter_by(name='superuser').first()
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        if not all([superuser_role, admin_role, user_role]):
            logger.error("Required roles not found. Please seed roles first.")
            return
            
        users_data = [
            # Superuser (also has admin role)
            {
                'email': 'superuser@email.com',
                'full_name': 'Alexander Thompson',
                'password': 'Pass123!!',
                'roles': ['superuser', 'admin']
            },
            # Admin users
            {
                'email': 'admin1@email.com',
                'full_name': 'Sarah Mitchell',
                'password': 'Pass123!!',
                'roles': ['admin']
            },
            {
                'email': 'admin2@email.com',
                'full_name': 'Michael Rodriguez',
                'password': 'Pass123!!',
                'roles': ['admin']
            },
            # Subscriber users
            {
                'email': 'user1@email.com',
                'full_name': 'Emma Johnson',
                'password': 'Pass123!!',
                'roles': ['user']
            },
            {
                'email': 'user2@email.com',
                'full_name': 'David Chen',
                'password': 'Pass123!!',
                'roles': ['user']
            },
            {
                'email': 'user3@email.com',
                'full_name': 'Jessica Williams',
                'password': 'Pass123!!',
                'roles': ['user']
            },
            {
                'email': 'user4@email.com',
                'full_name': 'Ryan O\'Connor',
                'password': 'Pass123!!',
                'roles': ['user']
            },
            {
                'email': 'user5@email.com',
                'full_name': 'Sophia Garcia',
                'password': 'Pass123!!',
                'roles': ['user']
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Create user using UserService
            user, success, error = UserService.create_user(
                email=user_data['email'],
                full_name=user_data['full_name'],
                password=user_data['password']
            )
            
            if not success:
                logger.error(f"Failed to create user {user_data['email']}: {error}")
                continue
            
            # Assign roles using the many-to-many relationship
            for role_name in user_data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user.add_role(role)
                else:
                    logger.warning(f"Role '{role_name}' not found for user {user.email}")
            
            # Save the user with roles
            user.save()
            created_users.append(user)
            logger.info(f"Created user: {user.email} with roles: {user_data['roles']}")
        
        db.session.commit()
        logger.info(f"Successfully seeded {len(created_users)} users")
        
        return created_users
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding users: {str(e)}")
        raise


def clear_users():
    """
    Removes all users and their role associations from the database.
    Use with caution - this will delete all user data.
    """
    try:
        # Get all users and clear their roles first
        users = User.query.all()
        for user in users:
            # Clear roles using the relationship
            for role in user.roles.all():
                user.remove_role(role)
        
        # Delete users (role associations will be automatically cleaned up)
        User.query.delete()
        
        db.session.commit()
        logger.info("Successfully cleared all users")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error clearing users: {str(e)}")
        raise


def get_seeded_user_credentials():
    """
    Returns a dictionary of seeded user credentials for testing purposes.
    """
    return {
        'superuser': {
            'email': 'superuser@email.com',
            'password': 'Pass123!!'
        },
        'admin1': {
            'email': 'admin1@email.com',
            'password': 'Pass123!!'
        },
        'admin2': {
            'email': 'admin2@email.com',
            'password': 'Pass123!!'
        },
        'user1': {
            'email': 'user1@email.com',
            'password': 'Pass123!!'
        },
        'user2': {
            'email': 'user2@email.com',
            'password': 'Pass123!!'
        },
        'user3': {
            'email': 'user3@email.com',
            'password': 'Pass123!!'
        },
        'user4': {
            'email': 'user4@email.com',
            'password': 'Pass123!!'
        },
        'user5': {
            'email': 'user5@email.com',
            'password': 'Pass123!!'
        }
    }