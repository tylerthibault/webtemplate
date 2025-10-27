from flask import Blueprint, render_template, request, redirect, url_for, flash
from functools import wraps
from src.services.decorators import login_required
from src.services.user_services import UserService, AuthService
from src.utils.csrf_utils import generate_csrf_token, validate_csrf_token
from src.models.role_model import Role

superuser_bp = Blueprint('superuser', __name__, url_prefix='/superuser')


def superuser_required(f):
    """Decorator to ensure user is a superuser."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not AuthService.is_superuser():
            flash('Access denied. Superuser privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@superuser_bp.route('/users')
@superuser_required
def user_management():
    """Display user management interface."""
    users_data = UserService.get_all_users_for_management()
    roles = Role.get_all()
    csrf_token = generate_csrf_token()
    return render_template(
        'private/superuser/user_management.html',
        users=users_data,
        roles=roles,
        csrf_token=csrf_token
    )


@superuser_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@superuser_required
def change_user_role(user_id):
    """Change user role (add or remove)."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Handle both URL parameter and form data for user_id
    form_user_id = request.form.get('user_id')
    if form_user_id:
        user_id = int(form_user_id)
    
    role_name = request.form.get('role_name')
    action = request.form.get('action')  # 'add' or 'remove'
    
    if not role_name or not action:
        flash('Role name and action are required', 'error')
        return redirect(url_for('superuser.user_management'))
    
    result = UserService.change_user_role(user_id, role_name, action)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/add-user-to-role', methods=['POST'])
@superuser_required
def add_user_to_role():
    """Add a user to a role via modal form."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    user_id = request.form.get('user_id')
    # Check for role_name from either dropdown or pre-selection
    role_name = request.form.get('role_name') or request.form.get('role_name_hidden')
    
    if not user_id or not role_name:
        flash('User and role selection are required', 'error')
        return redirect(url_for('superuser.user_management'))
    
    try:
        user_id = int(user_id)
        result = UserService.change_user_role(user_id, role_name, 'add')
        flash(result['message'], 'success' if result['success'] else 'error')
    except ValueError:
        flash('Invalid user ID', 'error')
    
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/users/<int:user_id>/soft-delete', methods=['POST'])
@superuser_required
def soft_delete_user(user_id):
    """Soft delete a user account."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    result = UserService.soft_delete_user(user_id)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/users/<int:user_id>/reactivate', methods=['POST'])
@superuser_required
def reactivate_user(user_id):
    """Reactivate a soft-deleted user account."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    result = UserService.reactivate_user(user_id)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/users/<int:user_id>/force-password-change', methods=['POST'])
@superuser_required
def force_password_change(user_id):
    """Force a user to change their password on next login."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    result = UserService.force_password_change(user_id)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@superuser_required
def delete_user(user_id):
    """Hard delete a user account (permanent)."""
    if not validate_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token', 'error')
        return redirect(url_for('superuser.user_management'))
    
    result = UserService.delete_user(user_id)
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('superuser.user_management'))