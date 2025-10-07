"""
Main page routes controller.

Thin controller following constitutional principles.
Handles landing, about, contact pages and dashboard.
Business logic delegated to appropriate services.
"""

from flask import Blueprint, render_template, request, jsonify
from src.logic.contact_service import ContactService
from src.logic.decorators import login_required
from src.logic.auth_service import AuthService

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    """
    Landing page route.
    
    GET: Render landing page
    """
    return render_template('public/landing/index.html')


@main_bp.route('/about')
def about():
    """
    About page route.
    
    GET: Render about page
    """
    return render_template('public/about/index.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact page route.
    
    GET: Render contact form
    POST: Process contact form submission
    """
    if request.method == 'GET':
        return render_template('public/contact/index.html')
    
    # POST request - process contact form
    try:
        data = request.get_json()
        
        # Extract fields
        name = data.get('name', '')
        email = data.get('email', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        # Validate required fields
        if not name:
            return jsonify({
                'success': False,
                'message': 'Name cannot be empty'
            }), 422
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email cannot be empty'
            }), 422
        
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject cannot be empty'
            }), 422
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 422
        
        # Delegate to service
        result = ContactService.submit_contact_form(name, email, subject, message)
        
        # Return response
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Contact form error: {str(e)}'
        }), 500


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard route (requires authentication).
    
    GET: Render dashboard page
    """
    # Get current user
    user = AuthService.get_current_user()
    
    return render_template('private/dashboard/index.html', user=user)
