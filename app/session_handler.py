"""
Session Expiration Handler Module

This module handles session expiration detection and management.
It provides decorators and utilities to redirect users to the login page
when their session has expired.

Features:
- Session expiration monitoring
- Automatic redirect to login on expiration
- AJAX/API request handling
- Session extension on user activity
- Customizable expiration messages
"""

from flask import redirect, url_for, flash, request, jsonify, session
from flask_login import current_user
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionExpirationHandler:
    """Manages session expiration and redirection logic"""
    
    # Session timeout constants
    INACTIVITY_TIMEOUT = 120  # minutes
    SESSION_WARNING_THRESHOLD = 10  # minutes before expiration to warn user
    
    @staticmethod
    def is_session_expired():
        """
        Check if the current session has expired based on inactivity.
        
        Returns:
            bool: True if session is expired, False otherwise
        """
        if not current_user.is_authenticated:
            return False
        
        # Get last activity timestamp from session
        last_activity = session.get('last_activity')
        if not last_activity:
            return False
        
        try:
            last_activity_time = datetime.fromisoformat(last_activity)
            expiration_time = last_activity_time + timedelta(minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT)
            return datetime.utcnow() > expiration_time
        except (ValueError, TypeError):
            # Invalid timestamp format
            return False
    
    @staticmethod
    def is_session_warning_time():
        """
        Check if session is about to expire (within warning threshold).
        
        Returns:
            bool: True if session is within warning threshold, False otherwise
        """
        if not current_user.is_authenticated:
            return False
        
        last_activity = session.get('last_activity')
        if not last_activity:
            return False
        
        try:
            last_activity_time = datetime.fromisoformat(last_activity)
            warning_time = last_activity_time + timedelta(
                minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT - SessionExpirationHandler.SESSION_WARNING_THRESHOLD
            )
            expiration_time = last_activity_time + timedelta(minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT)
            
            now = datetime.utcnow()
            return warning_time <= now < expiration_time
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def update_last_activity():
        """Update the last activity timestamp in the session"""
        session['last_activity'] = datetime.utcnow().isoformat()
        session.modified = True
    
    @staticmethod
    def get_remaining_time_minutes():
        """
        Get the remaining time before session expiration in minutes.
        
        Returns:
            int: Minutes remaining before expiration, or -1 if session is expired
        """
        if not current_user.is_authenticated:
            return -1
        
        last_activity = session.get('last_activity')
        if not last_activity:
            return SessionExpirationHandler.INACTIVITY_TIMEOUT
        
        try:
            last_activity_time = datetime.fromisoformat(last_activity)
            expiration_time = last_activity_time + timedelta(minutes=SessionExpirationHandler.INACTIVITY_TIMEOUT)
            remaining = (expiration_time - datetime.utcnow()).total_seconds() / 60
            return max(0, int(remaining))
        except (ValueError, TypeError):
            return SessionExpirationHandler.INACTIVITY_TIMEOUT
    
    @staticmethod
    def handle_expired_session(is_ajax=False):
        """
        Handle an expired session by redirecting to login.
        
        Args:
            is_ajax (bool): Whether the request is an AJAX request
            
        Returns:
            Response: Redirect or JSON response
        """
        # Log session expiration
        if current_user.is_authenticated:
            logger.info(f"Session expired for user: {current_user.email}")
        
        if is_ajax:
            return jsonify({
                'error': 'Session expired',
                'redirect_url': url_for('login', next=request.path)
            }), 401
        
        flash('Your session has expired. Please login again.', 'warning')
        return redirect(url_for('login', next=request.path))
    
    @staticmethod
    def extend_session_expiration():
        """Extend the session expiration by updating last activity"""
        SessionExpirationHandler.update_last_activity()


def session_required(f):
    """
    Decorator to enforce active session for route handlers.
    
    Redirects to login if session has expired.
    Works with both regular and AJAX requests.
    
    Usage:
        @app.route('/protected')
        @session_required
        def protected_route():
            return render_template('protected.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if SessionExpirationHandler.is_session_expired():
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            return SessionExpirationHandler.handle_expired_session(is_ajax=is_ajax)
        
        # Update last activity on each request
        SessionExpirationHandler.update_last_activity()
        
        return f(*args, **kwargs)
    
    return decorated_function


def session_extended_required(f):
    """
    Enhanced session decorator that also handles session warnings.
    
    Passes session warning info to template context.
    
    Usage:
        @app.route('/dashboard')
        @session_extended_required
        def dashboard():
            return render_template('dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if SessionExpirationHandler.is_session_expired():
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            return SessionExpirationHandler.handle_expired_session(is_ajax=is_ajax)
        
        # Update last activity
        SessionExpirationHandler.update_last_activity()
        
        # Call the original route
        response = f(*args, **kwargs)
        
        # Note: If the route returns template context, this won't add to it automatically.
        # For advanced usage with session warning in templates, use session context processors instead.
        
        return response
    
    return decorated_function


def session_aware_context_processor():
    """
    Context processor to pass session info to all templates.
    
    Provides:
    - session_warning: bool, True if session is about to expire
    - remaining_time: int, minutes remaining before expiration
    - session_expired: bool, True if session has already expired
    
    Usage in app/__init__.py:
        from app.session_handler import session_aware_context_processor
        app.context_processor(session_aware_context_processor)
    """
    if not current_user.is_authenticated:
        return {
            'session_warning': False,
            'remaining_time': 0,
            'session_expired': False
        }
    
    return {
        'session_warning': SessionExpirationHandler.is_session_warning_time(),
        'remaining_time': SessionExpirationHandler.get_remaining_time_minutes(),
        'session_expired': SessionExpirationHandler.is_session_expired()
    }


def init_session_handler(app):
    """
    Initialize session handler with Flask app.
    
    This function:
    1. Registers before_request handler to update activity
    2. Registers context processor for templates
    3. Sets up session-related app configuration
    
    Usage in app/__init__.py:
        from app.session_handler import init_session_handler
        
        # After app initialization
        init_session_handler(app)
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request_session_handler():
        """Update session activity timestamp and check for expiration"""
        if current_user.is_authenticated:
            # Check for session expiration
            if SessionExpirationHandler.is_session_expired():
                from flask import flash
                flash('Your session has expired. Please login again.', 'warning')
                return redirect(url_for('login'))
            
            # Update last activity timestamp
            SessionExpirationHandler.update_last_activity()
    
    # Register context processor
    app.context_processor(session_aware_context_processor)
    
    logger.info("Session handler initialized successfully")


def check_session_expiration():
    """
    Standalone function to check session expiration status.
    
    Useful for AJAX endpoints that need to validate session without redirect.
    
    Returns:
        dict: Session status information
        {
            'is_authenticated': bool,
            'is_expired': bool,
            'is_warning': bool,
            'remaining_minutes': int
        }
    """
    return {
        'is_authenticated': current_user.is_authenticated,
        'is_expired': SessionExpirationHandler.is_session_expired() if current_user.is_authenticated else False,
        'is_warning': SessionExpirationHandler.is_session_warning_time() if current_user.is_authenticated else False,
        'remaining_minutes': SessionExpirationHandler.get_remaining_time_minutes()
    }
