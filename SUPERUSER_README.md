# Superuser Management Features

This document describes the superuser management functionality implemented in the Flask MVC Base Template.

## Overview

The superuser management system provides administrative capabilities for managing users, roles, and system access. It follows the MVC architecture and implements proper security controls.

## Features

### User Management
- **View All Users**: Display comprehensive list of all users with their roles and status
- **Change User Roles**: Add or remove roles from users
- **Soft Delete Users**: Deactivate users without permanent deletion
- **Reactivate Users**: Restore previously deactivated users
- **Force Password Change**: Require users to change passwords on next login
- **Permanent Delete**: Hard delete users (with confirmation)

### Security Features
- **Role-Based Access**: Only users with 'superuser' role can access management features
- **CSRF Protection**: All state-changing operations protected against CSRF attacks
- **Session Management**: Automatic logout for deactivated users
- **Confirmation Dialogs**: User confirmation required for destructive operations

## Database Schema

### New User Model Fields
```python
is_active = db.Column(db.Boolean, nullable=False, default=True)
force_password_change = db.Column(db.Boolean, nullable=False, default=False)
```

### Roles
- `user`: Regular user role with basic permissions
- `admin`: Administrative role with elevated permissions  
- `superuser`: Superuser role with full system access

## Routes

All routes are prefixed with `/superuser/` and require superuser privileges:

- `GET /superuser/users` - Display user management interface
- `POST /superuser/users/<id>/change-role` - Add or remove user roles
- `POST /superuser/users/<id>/soft-delete` - Deactivate user account
- `POST /superuser/users/<id>/reactivate` - Reactivate user account
- `POST /superuser/users/<id>/force-password-change` - Force password change
- `POST /superuser/users/<id>/delete` - Permanently delete user

## Setup Instructions

### 1. Database Migration
The User model now includes `is_active` and `force_password_change` fields. For existing databases, you may need to add these columns manually:

```sql
ALTER TABLE user ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1;
ALTER TABLE user ADD COLUMN force_password_change BOOLEAN NOT NULL DEFAULT 0;
```

### 2. Seed Initial Data
Run the seeding script to create roles and test users:

```bash
python seed_db.py
```

This creates:
- Roles: user, admin, superuser
- Test superuser: superuser@example.com / Pass123!!
- Test admin users: admin1@example.com, admin2@example.com
- Test regular users: user1@example.com through user5@example.com

### 3. Access User Management
1. Login as superuser (superuser@example.com / Pass123!!)
2. Navigate to "User Management" in the side navigation
3. Use the interface to manage users and roles

## API Methods

### UserService Methods
```python
# Get all users for management interface
UserService.get_all_users_for_management()

# Change user roles
UserService.change_user_role(user_id, role_name, action='add|remove')

# Soft delete user
UserService.soft_delete_user(user_id)

# Reactivate user
UserService.reactivate_user(user_id)

# Force password change
UserService.force_password_change(user_id)
```

### AuthService Methods
```python
# Check if current user is superuser
AuthService.is_superuser()
```

## Template Integration

### Navigation
The user management link appears in the side navigation only for superusers:
```html
{% if current_user and current_user.has_role('superuser') %}
<li class="nav-button">
    <a href="{{ url_for('superuser.user_management') }}">User Management</a>
</li>
{% endif %}
```

### User Management Interface
- Responsive table with user information
- Role management dropdown for each user
- Action buttons for user management operations
- Status indicators for active/inactive users
- Confirmation dialogs for destructive operations

## Testing

Test the functionality with the provided test script:
```bash
python test_superuser.py
```

## Security Considerations

1. **Authentication**: All routes require authentication and superuser role
2. **CSRF Protection**: All forms include CSRF tokens
3. **Session Management**: Deactivated users are automatically logged out
4. **Input Validation**: All inputs are validated on both client and server side
5. **Confirmation**: Destructive operations require user confirmation

## File Structure

```
src/
├── controllers/
│   └── superuser_controller.py      # Superuser route handlers
├── services/
│   └── user_services.py             # Business logic for user management
├── models/
│   ├── user_model.py                # User model with new fields
│   └── role_model.py                # Role model and relationships
├── templates/
│   └── private/superuser/
│       └── user_management.html     # User management interface
└── utils/seed_utils/
    ├── role.py                      # Role seeding utilities
    ├── users.py                     # User seeding utilities
    └── main.py                      # Main seeding orchestrator
```

## Notes

- All operations return success/error messages via Flask flash messages
- No JSON responses - all operations use redirects following MVC pattern
- Template inheritance used for consistent UI
- Bootstrap classes used for responsive design
- Follows project coding standards and patterns