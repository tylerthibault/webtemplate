from functools import wraps
from flask import session, redirect, url_for, request, g
from src.models.coat_hanger import CoatHanger
from src import db
from datetime import datetime, timedelta

def login_required(f):
    """
    Decorator that requires user authentication to access protected routes.
    
    Checks for valid session token in database and handles session timeout.
    Redirects to login page if authentication fails.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if session token exists
        session_token = session.get('session_token')
        if not session_token:
            return redirect(url_for('user.login'))
        
        # Validate session token in database
        coat_hanger = CoatHanger.query.filter_by(session_hash=session_token).first()
        if not coat_hanger:
            session.clear()
            return redirect(url_for('user.login'))
        
        # Check session timeout (10 minutes)
        timeout_threshold = datetime.utcnow() - timedelta(minutes=10)
        if coat_hanger.updated_at < timeout_threshold:
            # Session expired - clean up
            db.session.delete(coat_hanger)
            db.session.commit()
            session.clear()
            return redirect(url_for('user.login'))
        
        # Update session timestamp
        coat_hanger.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Store user info in g for use in templates and logic
        g.current_user_id = coat_hanger.user_id
        g.current_user = coat_hanger.user
        
        return f(*args, **kwargs)
    
    return decorated_function