from flask import Blueprint, redirect, render_template, request, jsonify, url_for, flash
# from src.logic.decorators import login_required
# TODO
from src.utils.csrf_utils import generate_csrf_token, validate_csrf_token

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - public landing page."""
    csrf_token = generate_csrf_token()
    context = {
        'csrf_token': csrf_token
    }
    return render_template('public/landing/index.html', **context)


@main_bp.route('/about')
def about():
    """About page - public information page."""
    csrf_token = generate_csrf_token()
    context = {
        'csrf_token': csrf_token
    }
    return render_template('public/about/index.html', **context)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page - public contact form."""
    if request.method == 'POST':
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token', '')
        if not validate_csrf_token(csrf_token):
            flash('Security error. Please try again.', 'danger')
            return redirect(url_for('main.contact'))
        
        # Process form data
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.contact'))
        
        # TODO: Process the contact form (save to database, send email, etc.)
        # For now, just show success message
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    # GET request - show the form
    context = {
        'csrf_token': generate_csrf_token()
    }
    return render_template('public/contact/index.html', **context)

@main_bp.route('/faq')
def faq():
    """FAQ page - public frequently asked questions."""
    csrf_token = generate_csrf_token()
    context = {
        'csrf_token': csrf_token
    }
    return render_template('public/faq/index.html', **context)


@main_bp.route('/dashboard')
# @login_required
def dashboard():
    """User dashboard - private authenticated page."""
    csrf_token = generate_csrf_token()
    # Delegate to logic layer for user data
    context = {
        'csrf_token': csrf_token
    }
    return render_template('private/dashboard/index.html', **context)


@main_bp.route('/profile')
# @login_required
def profile():
    """User profile page - private authenticated page."""
    csrf_token = generate_csrf_token()
    context = {
        'csrf_token': csrf_token
    }
    return render_template('private/profile/index.html', **context)