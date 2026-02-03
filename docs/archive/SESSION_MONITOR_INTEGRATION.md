# Session Monitor Integration Guide

## Overview

The client-side session monitor (`app/static/js/session-monitor.js`) provides real-time monitoring of user sessions, showing warnings before expiration and auto-logging out users when sessions expire due to inactivity.

## How It Works

### Architecture

```
User Activity (clicks, typing, etc.)
         ↓
    Activity Listener (debounced 1s)
         ↓
POST /api/keep-alive (extend session)
         ↓
Server updates last_activity timestamp
         ↓
Session remains active
```

### Session Check Flow

```
Every 60 seconds:
    ↓
GET /api/session-status
    ↓
Check if session is:
    - Active (normal operation)
    - Warning (< 10 min until expiration)
    - Expired (automatically logout)
    ↓
Display appropriate UI to user
```

## Integration Steps

### Step 1: Add Session Monitor Script to Base Template

Add the following to your `app/templates/base.html` before the closing `</body>` tag:

```html
<!-- Session Management -->
<script src="{{ url_for('static', filename='js/session-monitor.js') }}"></script>
<script>
    // Initialize session monitor for authenticated users only
    {% if current_user.is_authenticated %}
    document.addEventListener('DOMContentLoaded', function() {
        initSessionMonitor({
            checkInterval: 60000,  // Check every 60 seconds
            inactivityTimeout: 120,  // Server timeout in minutes
            warningThreshold: 10,  // Show warning 10 minutes before expiration
            enableNotifications: true,  // Show browser notifications
            showWarningModal: true,  // Show modal alert
            debug: false  // Set to true for console logging
        });
    });
    {% endif %}
</script>

<!-- Session Warning Modal Container -->
<div id="session-warning-container"></div>
```

### Step 2: Add Session Warning Container

The warning modal will be inserted into the `session-warning-container` div. You can place this anywhere in your template, but typically near the top for visibility:

```html
<!-- In header or main content area -->
<div id="session-warning-container"></div>
```

### Step 3: Add Authentication Attribute (Optional)

For more explicit control, add a data attribute to your body or main element:

```html
<body data-authenticated="{% if current_user.is_authenticated %}true{% else %}false{% endif %}">
    <!-- Your page content -->
</body>
```

## API Endpoints

### GET /api/session-status

Returns the current session status and remaining time.

**Request:**
```http
GET /api/session-status
```

**Response (Authenticated):**
```json
{
    "is_authenticated": true,
    "is_expired": false,
    "is_warning": false,
    "remaining_minutes": 90,
    "remaining_seconds": 5400,
    "message": "Session active"
}
```

**Response (Session Warning):**
```json
{
    "is_authenticated": true,
    "is_expired": false,
    "is_warning": true,
    "remaining_minutes": 8,
    "remaining_seconds": 480,
    "message": "Session active"
}
```

**Response (Session Expired):**
```json
{
    "is_authenticated": false,
    "is_expired": true,
    "is_warning": false,
    "remaining_minutes": 0,
    "remaining_seconds": 0,
    "message": "Session expired"
}
```

### POST /api/keep-alive

Extends the user's session by updating the last activity timestamp.

**Request:**
```http
POST /api/keep-alive
```

**Response:**
```json
{
    "status": "success",
    "message": "Session extended",
    "remaining_minutes": 119,
    "remaining_seconds": 7140,
    "is_authenticated": true
}
```

## Configuration Options

When initializing the session monitor, you can customize the following options:

```javascript
initSessionMonitor({
    // Time between session status checks (in milliseconds)
    checkInterval: 60000,
    
    // Total inactivity timeout on server side (in minutes)
    inactivityTimeout: 120,
    
    // Show warning when this many minutes remain (in minutes)
    warningThreshold: 10,
    
    // Show browser notifications (requires user permission)
    enableNotifications: true,
    
    // Show modal alert on warning/expiration
    showWarningModal: true,
    
    // Enable debug logging to console
    debug: false,
    
    // Custom warning message
    warningTitle: 'Session Expiring Soon',
    warningMessage: 'Your session will expire in {minutes} minutes due to inactivity. Click "Keep Session" to stay logged in.',
    
    // Custom expiration message
    expiredTitle: 'Session Expired',
    expiredMessage: 'Your session has expired due to inactivity. You will be logged out now.'
});
```

## User Activity Tracking

The session monitor automatically tracks the following user activities:

- **Mouse Events**: `mousedown`, `click`
- **Keyboard Events**: `keydown`
- **Touch Events**: `touchstart`
- **Scroll Events**: `scroll`

When any activity is detected, the session is automatically extended via the `/api/keep-alive` endpoint.

**Activity detection is debounced** to prevent excessive API calls:
- Multiple activities within 1 second are counted as a single activity
- This reduces server load while keeping the session fresh

## Warning Modal Behavior

When the session is about to expire (within 10 minutes), a modal appears with:

- **Title**: "Session Expiring Soon"
- **Time Remaining**: Displays exact remaining time in minutes and seconds
- **Keep Session Button**: Click to dismiss the modal and extend the session
- **Logout Button**: Click to logout immediately

The modal updates every second to show the remaining time as it counts down.

## Browser Notifications

If notifications are enabled and the user grants permission, the session monitor can send:

1. **Warning Notification**: When session warning is triggered (10 minutes remaining)
2. **Expiration Notification**: When session is about to expire (1 minute remaining)

Users can grant notification permission through the browser's permission prompt.

## Automatic Logout

When the session expires:

1. User sees "Session Expired" modal
2. After 3 seconds, user is automatically redirected to `/login`
3. Session cookies are cleared
4. Flash message explains the logout reason

## Tab Visibility Handling

The session monitor is smart about tab visibility:

- **Tab becomes visible**: Immediately checks session status
- **Tab hidden**: Pauses polling to reduce server load
- **Tab becomes visible again**: Resumes polling from where it left off

This prevents unnecessary API calls when the user isn't actively using the application.

## Testing the Integration

### Manual Testing Checklist

- [ ] Load a page as authenticated user
- [ ] Verify session monitor script loads (check browser console)
- [ ] Wait 10 minutes without activity
- [ ] Verify warning modal appears
- [ ] Click "Keep Session" and verify modal closes
- [ ] Do nothing when warning appears
- [ ] Wait for auto-logout and verify redirect to login

### Browser Console Debugging

Enable debug mode to see detailed logging:

```javascript
initSessionMonitor({
    debug: true
});
```

Console output will show:
- Session status checks
- Activity events detected
- Keep-alive requests sent
- Warning/expiration events

### Network Monitoring

Use browser DevTools to monitor API calls:

1. Open DevTools Network tab
2. Filter by `/api/session-status` and `/api/keep-alive`
3. Verify timing and response codes
4. Check response payloads

## Security Considerations

### CSRF Protection

The `/api/session-status` endpoint uses `@csrf.exempt` because:
- It's a read-only GET request with no side effects
- Does not modify any server state
- Returns only session status information

The `/api/keep-alive` endpoint uses `@csrf.exempt` because:
- Activity tokens are not secrets
- Session extension is a normal user operation
- Explicit Flask-Login protection via `@login_required`

### Session Hijacking Prevention

- Never store sensitive data in session that could be exposed
- Always use HTTPS in production
- Use secure session cookie flags in production
- Implement additional authentication for sensitive operations

### Rate Limiting (Recommended)

Consider adding rate limiting to prevent abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: current_user.id if current_user.is_authenticated else 'anon')

@app.route('/api/session-status', methods=['GET'])
@limiter.limit("60/minute")  # Max 60 requests per minute per user
def get_session_status():
    # ...
```

## Troubleshooting

### Session Monitor Not Loading

**Problem**: Script doesn't load or JavaScript errors appear

**Solutions**:
1. Verify script path is correct: `{{ url_for('static', filename='js/session-monitor.js') }}`
2. Check browser console for 404 errors
3. Verify JavaScript syntax with developer tools
4. Check that initialization code runs after DOM is ready

### Warning Never Appears

**Problem**: User is inactive but no warning appears

**Solutions**:
1. Enable debug mode to see session status checks
2. Verify `/api/session-status` endpoint returns `"is_warning": true`
3. Check that modal container exists: `<div id="session-warning-container"></div>`
4. Verify `showWarningModal: true` in initialization options

### Session Doesn't Extend on Activity

**Problem**: Activities are detected but session doesn't extend

**Solutions**:
1. Verify `/api/keep-alive` endpoint is accessible
2. Check for JavaScript errors in console
3. Verify user is authenticated (`current_user.is_authenticated`)
4. Check that session handler module is properly initialized

### Modal Shows but Doesn't Update Time

**Problem**: Modal appears but countdown doesn't update

**Solutions**:
1. Verify JavaScript `setInterval` is working
2. Check that modal is being inserted into DOM correctly
3. Look for JavaScript errors in console
4. Verify `session-warning-container` div exists

## Example Implementation

Here's a complete example of integrating the session monitor into a base template:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}TodoBox{% endblock %}</title>
    <!-- Other head content -->
</head>
<body>
    <nav class="navbar">
        <!-- Navigation content -->
    </nav>

    <div id="session-warning-container"></div>

    <main>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer>
        <!-- Footer content -->
    </footer>

    <!-- Session Management -->
    <script src="{{ url_for('static', filename='js/session-monitor.js') }}"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            {% if current_user.is_authenticated %}
            initSessionMonitor({
                checkInterval: 60000,
                inactivityTimeout: 120,
                warningThreshold: 10,
                enableNotifications: true,
                showWarningModal: true,
                debug: {% if config.DEBUG %}true{% else %}false{% endif %}
            });
            {% endif %}
        });
    </script>
</body>
</html>
```

## Performance Optimization

### Reduce Check Frequency

For applications with many users, increase the check interval:

```javascript
initSessionMonitor({
    checkInterval: 120000  // Check every 2 minutes instead of 1
});
```

### Disable Unnecessary Features

For minimal overhead:

```javascript
initSessionMonitor({
    enableNotifications: false,
    showWarningModal: false,
    debug: false
});
```

### Conditional Initialization

Only initialize for certain user roles:

```javascript
{% if current_user.is_authenticated and not current_user.is_admin %}
initSessionMonitor({
    // config options
});
{% endif %}
```

## Related Documentation

- [Session Handler Reference](./SESSION_HANDLER.md)
- [Session Handler Quick Start](./SESSION_HANDLER_QUICKSTART.md)
- [Session Handler Architecture](./SESSION_HANDLER_ARCHITECTURE.md)

## Support

For issues or questions about the session monitor:

1. Check the [Troubleshooting](#troubleshooting) section
2. Enable debug mode and check console logs
3. Review related documentation files
4. Check the GitHub issues for similar problems
