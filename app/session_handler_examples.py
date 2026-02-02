"""
Session Expiration Handler - Usage Examples and Integration Guide

This file demonstrates how to use the session expiration handler module
in the TodoBox application.
"""

# ============================================================================
# EXAMPLE 1: Protecting Routes with Session Validation
# ============================================================================

from flask import render_template, redirect, url_for
from app.session_handler import session_required, session_extended_required

# Basic protection - simple decorator
@app.route('/dashboard')
@session_required
def dashboard():
    """
    Route with basic session validation.
    
    - Redirects unauthenticated users to login
    - Redirects expired sessions to login with warning
    - Updates last activity timestamp
    """
    return render_template('dashboard.html')


# Extended protection with warning handling
@app.route('/todos')
@session_extended_required
def list_todos():
    """
    Route with extended session validation.
    
    Better for routes that need fine-grained control over session state.
    """
    from app.session_handler import SessionExpirationHandler
    
    # Can manually check remaining time if needed
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    
    return render_template('todos.html', remaining_time=remaining)


# ============================================================================
# EXAMPLE 2: Using Session Status in Templates
# ============================================================================

"""
In your templates, the context processor automatically provides:
- session_warning: bool
- remaining_time: int (minutes)
- session_expired: bool

Usage in HTML template:

    {% if session_warning %}
        <div class="alert alert-warning alert-dismissible fade show" role="alert">
            <strong>Session Expiring Soon!</strong>
            Your session will expire in {{ remaining_time }} minutes.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endif %}
    
    {% if session_expired %}
        <div class="alert alert-danger">
            Your session has expired. Please login again.
        </div>
    {% endif %}
"""


# ============================================================================
# EXAMPLE 3: API Endpoints with Session Validation
# ============================================================================

from flask import jsonify
from app.session_handler import check_session_expiration


@app.route('/api/session-status')
def api_session_status():
    """
    API endpoint to check current session status.
    
    Returns JSON with session information that can be used by JavaScript
    to display warnings or handle expiration client-side.
    """
    status = check_session_expiration()
    
    return jsonify({
        'is_authenticated': status['is_authenticated'],
        'is_expired': status['is_expired'],
        'is_warning': status['is_warning'],
        'remaining_minutes': status['remaining_minutes']
    })


@app.route('/api/todos', methods=['GET'])
def api_list_todos():
    """
    API endpoint with session validation.
    
    Returns 401 JSON for expired sessions instead of redirecting.
    """
    status = check_session_expiration()
    
    if status['is_expired']:
        return jsonify({'error': 'Session expired'}), 401
    
    if not status['is_authenticated']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return actual data
    from app.models import Todo
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify([todo.to_dict() for todo in todos])


# ============================================================================
# EXAMPLE 4: Extending Session Manually
# ============================================================================

from app.session_handler import SessionExpirationHandler


@app.route('/api/keep-alive', methods=['POST'])
def keep_alive():
    """
    Endpoint to manually extend user session.
    
    Call this periodically from JavaScript to prevent session expiration
    during active work.
    """
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Extend the session by updating last activity
    SessionExpirationHandler.extend_session_expiration()
    
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    
    return jsonify({
        'status': 'success',
        'remaining_minutes': remaining,
        'message': f'Session extended. {remaining} minutes remaining.'
    })


# ============================================================================
# EXAMPLE 5: JavaScript Integration - Client-Side Session Monitoring
# ============================================================================

"""
In your base template or JavaScript file:

<script>
    // Check session status every 5 minutes
    setInterval(function() {
        fetch('/api/session-status')
            .then(response => response.json())
            .then(data => {
                if (data.session_expired) {
                    // Handle expired session
                    showAlert('Session expired', 'Please login again', 'danger');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else if (data.is_warning) {
                    // Show warning to user
                    showSessionWarning(data.remaining_minutes);
                }
            })
            .catch(error => console.error('Session check error:', error));
    }, 5 * 60 * 1000); // Check every 5 minutes
    
    // Function to show session warning
    function showSessionWarning(minutes) {
        const warningElement = document.getElementById('session-warning');
        if (warningElement) {
            warningElement.innerHTML = `
                <div class="alert alert-warning">
                    Your session will expire in ${minutes} minutes.
                </div>
            `;
            warningElement.style.display = 'block';
        }
    }
    
    // Call keep-alive endpoint on user action
    document.addEventListener('click', function() {
        fetch('/api/keep-alive', {method: 'POST'})
            .catch(error => console.error('Keep-alive error:', error));
    }, {once: false});
</script>
"""


# ============================================================================
# EXAMPLE 6: Custom Session Handling
# ============================================================================

from app.session_handler import SessionExpirationHandler
from datetime import datetime, timedelta


@app.route('/custom-session-handler')
def custom_session_handler():
    """
    Example of custom session handling logic.
    
    Demonstrates accessing SessionExpirationHandler methods directly.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Check various session states
    is_expired = SessionExpirationHandler.is_session_expired()
    is_warning = SessionExpirationHandler.is_session_warning_time()
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    
    if is_expired:
        flash('Your session has expired. Please login again.', 'danger')
        return redirect(url_for('login'))
    
    if is_warning:
        warning_msg = f'Your session will expire in {remaining} minutes.'
        flash(warning_msg, 'warning')
    
    # Render template with session info
    return render_template('custom.html',
                          is_warning=is_warning,
                          remaining_time=remaining)


# ============================================================================
# EXAMPLE 7: AJAX Requests with Session Error Handling
# ============================================================================

"""
In JavaScript, handle session expiration for AJAX requests:

function makeAPICall(url, options = {}) {
    return fetch(url, {
        ...options,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            ...options.headers
        }
    })
    .then(response => {
        // Handle 401 Unauthorized (session expired)
        if (response.status === 401) {
            // Session expired, redirect to login
            const redirectUrl = response.json().then(data => data.redirect_url);
            return redirectUrl.then(url => {
                window.location.href = url || '/login';
            });
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    })
    .catch(error => {
        console.error('API call error:', error);
        throw error;
    });
}

// Usage:
makeAPICall('/api/todos')
    .then(todos => console.log('Todos:', todos))
    .catch(error => console.error('Failed to fetch todos:', error));
"""


# ============================================================================
# EXAMPLE 8: Logging Session Events
# ============================================================================

import logging

logger = logging.getLogger(__name__)


@app.route('/logged-route')
@session_required
def logged_route():
    """
    Example of logging session information for audit trails.
    """
    from app.session_handler import SessionExpirationHandler
    
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    
    logger.info(
        f'User {current_user.email} accessed protected route. '
        f'Session remaining: {remaining} minutes'
    )
    
    return render_template('protected.html')


# ============================================================================
# EXAMPLE 9: Conditional Session Timeout
# ============================================================================

"""
Advanced use case: Different timeouts for different user types

Modify SessionExpirationHandler or create a subclass for custom timeouts:
"""


class CustomSessionHandler(SessionExpirationHandler):
    """Custom session handler with role-based timeouts"""
    
    ADMIN_TIMEOUT = 30  # 30 minutes for admins
    USER_TIMEOUT = 120  # 120 minutes for regular users
    
    @staticmethod
    def get_user_timeout(user):
        """Get session timeout based on user role"""
        if user.is_admin:
            return CustomSessionHandler.ADMIN_TIMEOUT
        return CustomSessionHandler.USER_TIMEOUT


# Usage would require modifying the session handler initialization
# to use the custom class instead of the base SessionExpirationHandler


# ============================================================================
# EXAMPLE 10: Session Refresh on Action
# ============================================================================

from flask import request as flask_request


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """
    API endpoint that extends session on user action.
    
    This pattern keeps the session active while user is actively working.
    """
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check session status
    status = check_session_expiration()
    if status['is_expired']:
        return jsonify({'error': 'Session expired'}), 401
    
    # Extend session on successful action
    SessionExpirationHandler.extend_session_expiration()
    
    # Continue with actual logic...
    todo = db.session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        return jsonify({'error': 'Not found'}), 404
    
    # Update todo
    data = flask_request.get_json()
    if 'name' in data:
        todo.name = data['name']
    
    db.session.commit()
    
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    
    return jsonify({
        'status': 'success',
        'todo': todo.to_dict(),
        'session_remaining': remaining
    })


# ============================================================================
# CONFIGURATION AND SETUP
# ============================================================================

"""
To configure session expiration timeout, modify these values:

1. In app/session_handler.py - SessionExpirationHandler class:
   INACTIVITY_TIMEOUT = 120  # Change to desired minutes
   SESSION_WARNING_THRESHOLD = 10  # Change warning time

2. In app/config.py:
   app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
   
   Should be >= INACTIVITY_TIMEOUT for consistency

3. Session is initialized automatically by:
   - init_session_handler(app) called in app/__init__.py
   - No manual setup required
"""


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================

"""
The session handler gracefully handles edge cases:

1. Invalid session timestamp: Treated as valid, returns full timeout
2. Unauthenticated user: All checks return safe defaults (False/0)
3. Database errors: Caught and logged, doesn't break functionality
4. Missing session data: Initialized on first request
5. Clock skew: Uses datetime.utcnow() consistently

If experiencing issues:
- Check server time synchronization (NTP)
- Verify SESSION_COOKIE_SECURE matches HTTPS usage
- Review logs for session expiration events
- Test with test_client() in development
"""
