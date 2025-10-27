"""
Seed roles for the application.
"""

from src.models.role_model import Role
from src import db


def seed_roles():
    """Create default roles for the application."""
    print("Seeding roles...")
    
    roles_data = [
        {
            'name': 'user',
            'description': 'Regular user role with basic permissions'
        },
        {
            'name': 'admin',
            'description': 'Administrative role with elevated permissions'
        },
        {
            'name': 'superuser',
            'description': 'Superuser role with full system access'
        }
    ]
    
    for role_data in roles_data:
        # Check if role already exists
        existing_role = Role.find_one_by(name=role_data['name'])
        if not existing_role:
            try:
                role = Role.create(**role_data)
                print(f"Created role: {role.name}")
            except Exception as e:
                print(f"Error creating role {role_data['name']}: {str(e)}")
        else:
            print(f"Role {role_data['name']} already exists")
    
    print("Role seeding completed.")


if __name__ == "__main__":
    from src import create_app
    
    app = create_app()
    with app.app_context():
        seed_roles()