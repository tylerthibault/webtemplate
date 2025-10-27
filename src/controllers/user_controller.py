from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from src.services.user_services import UserService, AuthService
from src.services.decorators import login_required
from src.utils.csrf_utils import generate_csrf_token, validate_csrf_token
from src.models.coat_hanger import CoatHanger

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route - delegates to auth service"""
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('user.login'))
        
        credentials = {
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        
        result = AuthService.authenticate_user(credentials)
        if result['success']:
            return redirect(url_for('main.dashboard'))
        else:
            flash(result['message'], 'error')
    
    csrf_token = generate_csrf_token()
    return render_template('public/auth/login/index.html', csrf_token=csrf_token)


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route - delegates to auth service"""
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('user.register'))
        
        user_data = {
            'email': request.form.get('email'),
            'full_name': request.form.get('full_name'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password')
        }
        
        result = AuthService.register_user(user_data)
        if result['success']:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user.login'))
        else:
            flash(result['message'], 'error')
    
    csrf_token = generate_csrf_token()
    return render_template('public/auth/register/index.html', csrf_token=csrf_token)




@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page - profile updates"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('user.settings'))
        
        update_data = {
            'full_name': request.form.get('full_name'),
            'email': request.form.get('email'),
            'current_password': request.form.get('current_password'),
            'new_password': request.form.get('new_password'),
            'confirm_password': request.form.get('confirm_password')
        }
        
        result = UserService.update_user_profile(user_id, update_data)
        if result['success']:
            flash('Settings updated successfully!', 'success')
        else:
            flash(result['message'], 'error')
        
        return redirect(url_for('user.settings'))
    
    user_data = UserService.get_user_profile(user_id)
    csrf_token = generate_csrf_token()
    return render_template('private/user/settings.html', 
                         user=user_data, csrf_token=csrf_token)


@user_bp.route('/logout')
@login_required
def logout():
    """User logout - clears session and coat hanger"""
    user_id = session.get('user_id')
    AuthService.logout_user(user_id)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@user_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route - initiates password reset process"""
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('user.forgot_password'))
        
        email = request.form.get('email')
        result = AuthService.initiate_password_reset(email)
        if result['success']:
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('user.login'))
        else:
            flash(result['message'], 'error')
    
    csrf_token = generate_csrf_token()
    return render_template('public/auth/forgot_password/index.html', csrf_token=csrf_token)