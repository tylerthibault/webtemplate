"""
Authentication routes controller.

Thin controller following constitutional principles.
All business logic delegated to AuthService in logic layer.
"""

from flask import Blueprint, render_template, request, jsonify
from src.logic.auth_service import AuthService
from src.logic.decorators import login_required, guest_only

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    """
    User registration route.
    
    GET: Render registration form
    POST: Process registration with JSON data
    """
    if request.method == 'GET':
        return render_template('public/auth/register.html')
    
    # POST request - process registration
    try:
        data = request.get_json()
        
        # Extract fields
        email = data.get('email', '')
        password = data.get('password', '')
        full_name = data.get('full_name', '')
        
        # Validate required fields
        if not email or not password or not full_name:
            return jsonify({
                'success': False,
                'message': 'Email, password, and full name cannot be empty'
            }), 422
        
        # Delegate to service
        result = AuthService.register_user(email, password, full_name)
        
        # Return response
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    """
    User login route.
    
    GET: Render login form
    POST: Process login with JSON data
    """
    if request.method == 'GET':
        return render_template('public/auth/login.html')
    
    # POST request - process login
    try:
        data = request.get_json()
        
        # Extract fields
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Validate required fields
        if not email:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Email cannot be empty'
            }), 400
        
        if not password:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Password cannot be empty'
            }), 400
        
        # Delegate to service
        result = AuthService.authenticate_user(email, password)
        
        # Return response
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'authenticated': False,
            'message': f'Login error: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    User logout route.
    
    POST: Clear session and logout user
    """
    try:
        # Delegate to service
        result = AuthService.logout_user()
        
        # Return response
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500


@auth_bp.route('/session', methods=['GET'])
def session_status():
    """
    Check session status route.
    
    GET: Return current session status and user info
    """
    try:
        # Delegate to service
        result = AuthService.check_session_status()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'message': f'Session check error: {str(e)}'
        }), 500
