# Role-Based Navigation Documentation

## Overview
This system provides flexible role-based navigation rendering for your Flask MVC application. You can show/hide navigation sections and individual items based on user roles.

## Available Roles
- `user` - Regular user role with basic permissions
- `admin` - Administrative role with elevated permissions  
- `superuser` - Superuser role with full system access

## Implementation Methods

### Method 1: Direct Template Conditionals
The simplest approach using standard Jinja2 conditionals:

```html
<!-- Single role check -->
{% if current_user and current_user.has_role('admin') %}
<li class="nav-button">
    <a href="#">Admin Dashboard</a>
</li>
{% endif %}

<!-- Multiple role check -->
{% if current_user and (current_user.has_role('admin') or current_user.has_role('superuser')) %}
<li class="nav-button">
    <a href="#">Management Panel</a>
</li>
{% endif %}
```

### Method 2: Role Macros (Recommended)
Using the provided macros for cleaner, reusable code:

```html
{% from '00_app_components/role_macros.html' import role_section, multi_role_section, admin_or_superuser_section %}

<!-- Single role section -->
{% call role_section('admin') %}
<div>
    <h2 class="nav-heading">Admin Tools</h2>
    <ul class="nav-button-container">
        <li class="nav-button">
            <a href="#">Admin Dashboard</a>
        </li>
    </ul>
</div>
{% endcall %}

<!-- Multiple roles (match any) -->
{% call multi_role_section(['admin', 'superuser'], match_any=true) %}
<li class="nav-button">
    <a href="#">Management Panel</a>
</li>
{% endcall %}

<!-- Multiple roles (must have all) -->
{% call multi_role_section(['admin', 'user'], match_any=false) %}
<li class="nav-button">
    <a href="#">Special Admin User Panel</a>
</li>
{% endcall %}

<!-- Admin or Superuser (convenience macro) -->
{% call admin_or_superuser_section() %}
<li class="nav-button">
    <a href="#">Advanced Settings</a>
</li>
{% endcall %}
```

## Available Macros

### `role_section(required_role, current_user=current_user)`
Renders content only if the user has the specified role.

**Parameters:**
- `required_role` (string): The role name to check for
- `current_user` (User object): The current user (defaults to template's current_user)

### `multi_role_section(required_roles, current_user=current_user, match_any=true)`
Renders content based on multiple role requirements.

**Parameters:**
- `required_roles` (list): List of role names to check
- `current_user` (User object): The current user (defaults to template's current_user)
- `match_any` (boolean): If true, user needs at least one role; if false, user needs all roles

### `admin_or_superuser_section(current_user=current_user)`
Convenience macro for content that should be visible to admins or superusers.

**Parameters:**
- `current_user` (User object): The current user (defaults to template's current_user)

## Navigation Structure Example

```html
{% from '00_app_components/role_macros.html' import role_section, admin_or_superuser_section %}

<!-- Common navigation for all users -->
<div>
    <h2 class="nav-heading">Navigation</h2>
    <ul class="nav-button-container">
        <li class="nav-button">
            <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
        </li>
        <li class="nav-button">
            <a href="{{ url_for('main.profile') }}">Profile</a>
        </li>
    </ul>
</div>

<!-- Admin-specific navigation -->
{% call role_section('admin') %}
<div>
    <h2 class="nav-heading">Admin Tools</h2>
    <ul class="nav-button-container">
        <li class="nav-button">
            <a href="#">Content Management</a>
        </li>
        <li class="nav-button">
            <a href="#">User Reports</a>
        </li>
    </ul>
</div>
{% endcall %}

<!-- Superuser-specific navigation -->
{% call role_section('superuser') %}
<div>
    <h2 class="nav-heading">System Management</h2>
    <ul class="nav-button-container">
        <li class="nav-button">
            <a href="{{ url_for('superuser.user_management') }}">User Management</a>
        </li>
        <li class="nav-button">
            <a href="#">System Settings</a>
        </li>
    </ul>
</div>
{% endcall %}

<!-- Mixed section for admins and superusers -->
{% call admin_or_superuser_section() %}
<div>
    <h2 class="nav-heading">Management</h2>
    <ul class="nav-button-container">
        <!-- Different items based on specific roles -->
        {% call role_section('admin') %}
        <li class="nav-button">
            <a href="#">Admin Reports</a>
        </li>
        {% endcall %}
        
        {% call role_section('superuser') %}
        <li class="nav-button">
            <a href="#">System Logs</a>
        </li>
        {% endcall %}
    </ul>
</div>
{% endcall %}
```

## Best Practices

1. **Use macros for complex logic**: Prefer role macros over inline conditionals for maintainability
2. **Group related functionality**: Keep related navigation items in the same role-based section
3. **Provide clear section headers**: Use descriptive headings for each role-based section
4. **Test thoroughly**: Ensure navigation appears correctly for all role combinations
5. **Security note**: Role-based navigation is for UI convenience only; always enforce authorization in your controllers

## Security Considerations

- Navigation visibility is controlled client-side and should not be relied upon for security
- Always implement proper authorization checks in your route handlers using the `@login_required` decorator and role checks
- The `current_user.has_role()` method should be used in controllers to enforce access control

## Usage in Other Templates

You can use these role-based sections in any template by importing the macros:

```html
{% from '00_app_components/role_macros.html' import role_section %}

<!-- In any template -->
{% call role_section('admin') %}
<div class="admin-only-content">
    <p>This content is only visible to administrators.</p>
</div>
{% endcall %}
```