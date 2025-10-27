#!/usr/bin/env python3
"""
Test script to verify superuser functionality.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.services.user_services import UserService, AuthService
from src.models.user_model import User
from src.models.role_model import Role


def test_superuser_functionality():
    """Test superuser-related functionality."""
    print("Testing superuser functionality...")
    
    app = create_app()
    with app.app_context():
        # Check if roles exist
        roles = Role.get_all()
        print(f"Roles in database: {[role.name for role in roles]}")
        
        # Check if superuser exists
        superuser = User.find_one_by(email='superuser@example.com')
        if superuser:
            print(f"Superuser found: {superuser.email}")
            print(f"Superuser roles: {[role.name for role in superuser.roles]}")
            print(f"Has superuser role: {superuser.has_role('superuser')}")
        else:
            print("No superuser found")
        
        # Test user management methods
        users_data = UserService.get_all_users_for_management()
        print(f"Total users for management: {len(users_data)}")
        
        if users_data:
            first_user = users_data[0]
            print(f"First user sample data: {first_user}")


if __name__ == "__main__":
    test_superuser_functionality()