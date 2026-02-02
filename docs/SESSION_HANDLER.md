# Session Expiration Handler Module

## Overview

The Session Expiration Handler module provides comprehensive session management with automatic expiration detection and handling for the TodoBox application. It tracks user activity, detects session expiration based on inactivity, and seamlessly redirects expired sessions to the login page with appropriate user feedback.

## Features

- **Automatic Session Expiration**: Tracks user inactivity and automatically expires sessions after a configured timeout period
- **Session Warning System**: Alerts users when their session is about to expire (within warning threshold)
- **Intelligent Redirect**: Handles both regular and AJAX requests with appropriate responses (HTML redirects or JSON)
- **Activity Tracking**: Updates last activity timestamp on each user action
- **Template Integration**: Provides session status context to all templates via context processor
- **Decorator Support**: Easy-to-use decorators for protecting routes with session validation
- **Logging**: Comprehensive logging for debugging and audit trails

## Configuration

### Session Timeout Constants

Located in `SessionExpirationHandler` class:

```python
INACTIVITY_TIMEOUT = 120  # minutes (2 hours) - Time before session expires
SESSION_WARNING_THRESHOLD = 10  # minutes - Time before expiration to warn user
```

These can be customized by modifying the values in `app/session_handler.py`.

### Flask Configuration

In `app/config.py`, the session lifetime is configured:

```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
```

This should match or exceed the `INACTIVITY_TIMEOUT` value.

## Core Components

### SessionExpirationHandler Class

Main class handling all session expiration logic.

#### Methods

**`is_session_expired()`**
- Returns: `bool` - True if current session has expired
- Checks last activity timestamp against inactivity timeout
- Returns False for unauthenticated users

**`is_session_warning_time()`**
- Returns: `bool` - True if session is within warning threshold
- Used to display "Your session will expire soon" messages
- Returns False for unauthenticated users

**`update_last_activity()`**
- No return value
- Updates session's last activity timestamp to current time
- Called on each user request via `before_request` handler

**`get_remaining_time_minutes()`**
- Returns: `int` - Minutes remaining before session expires
- Returns -1 if session is expired
- Returns full timeout if no activity timestamp exists

**`handle_expired_session(is_ajax=False)`**
- Returns: `Response` - Redirect or JSON response
- Parameters:
  - `is_ajax` (bool): Set to True for AJAX requests to return JSON instead of redirect
- Logs session expiration and redirects to login page
- For AJAX: Returns JSON with 401 status
- For regular: Redirects to login with flash message

**`extend_session_expiration()`**
- No return value
- Wrapper around `update_last_activity()`
- Use when explicitly extending a session (e.g., on user action)

## Decorators

### @session_required

Decorator to enforce an active session for route handlers. Checks session expiration and redirects to login if expired.

**Usage:**
```python
from app.session_handler import session_required

@app.route('/protected-route')
@session_required
def protected_route():
    return render_template('protected.html')
```

**Behavior:**
- Redirects unauthenticated users to login
- Redirects expired sessions to login with warning message
- Updates last activity timestamp
- Works with both regular and AJAX requests

### @session_extended_required

Enhanced decorator that also passes session warning information to route handlers.

**Usage:**
```python
from app.session_handler import session_extended_required

@app.route('/dashboard')
@session_extended_required
def dashboard():
    return render_template('dashboard.html')
```

**Behavior:**
- Same as `@session_required`
- Additionally handles session warning state
- Better for routes that need fine-grained session control

## Context Processor

### session_aware_context_processor()

Provides session information to all templates globally.

**Provided Context Variables:**

- `session_warning` (bool): True if session is within warning threshold
- `remaining_time` (int): Minutes remaining before session expiration
- `session_expired` (bool): True if session has already expired

**Template Usage:**
```html
{% if session_warning %}
    <div class="alert alert-warning">
        Your session will expire in {{ remaining_time }} minutes.
    </div>
{% endif %}

{% if session_expired %}
    <!-- Handle expired session display -->
{% endif %}
```

## Initialization

### init_session_handler(app)

Initializes the session handler with a Flask application.

**Called automatically in `app/__init__.py`:**
```python
from app.session_handler import init_session_handler

# After creating Flask app
init_session_handler(app)
```

**What it does:**
1. Registers `before_request` handler to check and update session activity
2. Registers context processor for template access
3. Sets up automatic session expiration checking on each request

**No manual initialization required** - already integrated in app startup.

## Utility Functions

### check_session_expiration()

Standalone function to check session status without redirecting.

**Returns:** Dictionary with session status
```python
{
    'is_authenticated': bool,      # User is logged in
    'is_expired': bool,             # Session has expired
    'is_warning': bool,             # Session within warning threshold
    'remaining_minutes': int        # Minutes until expiration
}
```

**Usage in AJAX endpoints:**
```python
from app.session_handler import check_session_expiration

@app.route('/api/session-status')
def session_status_api():
    status = check_session_expiration()
    return jsonify(status)
```

## How It Works

### Session Tracking Flow

1. **User Login**: `flask_session['last_activity']` is initialized
2. **Each Request**: 
   - `before_request` handler checks for expiration
   - If expired: Redirect to login
   - If valid: Update `last_activity` timestamp
3. **Template Rendering**: Context processor provides session info to template
4. **Session Check**: Routes can explicitly check status via decorators

### Expiration Logic

```
Current Time - Last Activity Time > INACTIVITY_TIMEOUT
   ↓
   Session Expired ✓
```

### Warning Logic

```
(Current Time - Last Activity Time) is between:
  INACTIVITY_TIMEOUT - SESSION_WARNING_THRESHOLD
  and
  INACTIVITY_TIMEOUT
   ↓
   Show Warning ✓
```

## JavaScript Integration

For client-side session monitoring, use the provided API endpoint:

```javascript
// Check session status
fetch('/api/session-status')
    .then(response => response.json())
    .then(data => {
        if (data.session_expired) {
            // Handle expired session
            window.location.href = '/login';
        } else if (data.is_warning) {
            // Show warning to user
            showSessionWarning(data.remaining_minutes);
        }
    });
```

## Error Handling

### Session Token Errors

If `last_activity` has invalid format:
- Treated as valid session (for backward compatibility)
- Returns full timeout as remaining time
- Does not trigger expiration

### Unauthenticated Access

All session functions safely handle unauthenticated users:
- `is_session_expired()` → `False`
- `is_session_warning_time()` → `False`
- `get_remaining_time_minutes()` → Returns full timeout value

### CSRF Integration

Existing CSRF error handlers remain unchanged and continue to work with session handler.

## Logging

Session events are logged at `app.logger`:

```
INFO: Session handler initialized successfully
INFO: Session expired for user: user@example.com
WARNING: Database error checking user count
```

Access logs via:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message here")
```

## Security Considerations

1. **Session Tokens**: ISO format timestamps stored in Flask session (server-side secure)
2. **No Client-Side Tampering**: Validation done server-side on each request
3. **Automatic Timeout**: Prevents unauthorized access via inactive sessions
4. **Activity Tracking**: Honest user activity resets timeout counter
5. **Secure Redirect**: Uses `url_for()` to generate secure URLs

## Testing

Comprehensive tests included in `tests/test_session_handler.py`:

Run tests:
```bash
pytest tests/test_session_handler.py -v
```

Test coverage includes:
- Session expiration detection
- Session warning timing
- Activity timestamp updates
- Remaining time calculations
- Redirect behavior
- Decorator functionality
- Context processor integration
- AJAX handling

## Troubleshooting

### Sessions Expiring Too Quickly

1. Check `INACTIVITY_TIMEOUT` value (default: 120 minutes)
2. Verify `PERMANENT_SESSION_LIFETIME` is >= `INACTIVITY_TIMEOUT`
3. Ensure server time is synchronized (NTP)
4. Check for clock skew between servers (if distributed)

### Sessions Not Expiring

1. Verify `init_session_handler(app)` is called
2. Check `before_request` handler is registered
3. Verify database session storage is working
4. Check Flask session configuration

### Always Getting Warnings

1. Check `SESSION_WARNING_THRESHOLD` (default: 10 minutes)
2. Verify `INACTIVITY_TIMEOUT` is reasonable
3. Ensure `last_activity` is being updated (check logs)

### AJAX Requests Not Handling Expiration

1. Set `X-Requested-With: XMLHttpRequest` header in AJAX requests
2. Handle JSON response with 401 status
3. Redirect to `/login?next={current_path}` on 401

## Examples

### Protecting a Route

```python
from app.session_handler import session_required

@app.route('/todos')
@session_required  # Add this decorator
def list_todos():
    return render_template('todos.html', todos=current_user.todos)
```

### Checking Session Status in API

```python
from app.session_handler import check_session_expiration

@app.route('/api/todos')
def api_list_todos():
    status = check_session_expiration()
    if status['is_expired']:
        return jsonify({'error': 'Session expired'}), 401
    
    # Continue with API logic
    return jsonify(todos=[...])
```

### Custom Session Handling

```python
from app.session_handler import SessionExpirationHandler

def custom_route():
    if SessionExpirationHandler.is_session_expired():
        # Custom handling for expired session
        return render_template('session_expired.html')
    
    remaining = SessionExpirationHandler.get_remaining_time_minutes()
    return render_template('dashboard.html', remaining_time=remaining)
```

### Extending Session Manually

```python
from app.session_handler import SessionExpirationHandler

@app.route('/api/keep-alive', methods=['POST'])
def keep_alive():
    """Endpoint to manually extend session"""
    SessionExpirationHandler.extend_session_expiration()
    return jsonify({'remaining_minutes': SessionExpirationHandler.get_remaining_time_minutes()})
```

## Performance

- **Minimal Overhead**: Session checks are O(1) timestamp comparisons
- **No Database Queries**: Uses Flask session (in-memory or configured backend)
- **Scalable**: Works with Flask session backends (Redis, Memcached, etc.)
- **Efficient**: No additional requests or external API calls

## Future Enhancements

Potential improvements for future versions:

1. **Configurable Timeout Per User**: Different timeout for different user roles
2. **Activity-Based Categorization**: Different timeouts for idle vs. active tracking
3. **Remember-Me Extended Session**: Longer timeout for "Remember Me" sessions
4. **Session Revocation**: Admin ability to manually expire user sessions
5. **Session History**: Tracking of login/logout times for security audit
6. **Multi-Device Session Management**: Track multiple active sessions per user

## API Reference

See inline docstrings in `app/session_handler.py` for complete API reference with type hints and detailed parameter descriptions.
