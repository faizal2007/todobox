# Session Expiration Handler - Quick Start Guide

## Overview

The session expiration handler automatically manages user sessions in TodoBox. When users are inactive for 120 minutes, their session expires and they're redirected to the login page.

## What's Included

1. **Core Module**: `app/session_handler.py` - Main session management logic
2. **Integration**: `app/__init__.py` - Automatically initialized on app startup
3. **Tests**: `tests/test_session_handler.py` - Comprehensive test coverage
4. **Documentation**: `docs/SESSION_HANDLER.md` - Detailed reference
5. **Examples**: `app/session_handler_examples.py` - Usage examples

## Default Configuration

- **Session Timeout**: 120 minutes (2 hours) of inactivity
- **Warning Threshold**: 10 minutes before expiration
- **Check Frequency**: Every user request

## Quick Integration

### For Routes

```python
from app.session_handler import session_required

@app.route('/my-route')
@session_required
def my_route():
    return render_template('my-template.html')
```

### For Templates

```html
{% if session_warning %}
    <div class="alert alert-warning">
        Session expires in {{ remaining_time }} minutes
    </div>
{% endif %}
```

### For AJAX

```javascript
fetch('/api/check-session')
    .then(response => response.json())
    .then(data => {
        if (data.is_expired) {
            window.location.href = '/login';
        }
    });
```

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `is_session_expired()` | Check if session has expired | bool |
| `is_session_warning_time()` | Check if warning should show | bool |
| `get_remaining_time_minutes()` | Get minutes until expiration | int |
| `update_last_activity()` | Extend session | None |
| `extend_session_expiration()` | Explicitly extend session | None |

## Configuration

### Change Timeout Duration

Edit `app/session_handler.py`:

```python
class SessionExpirationHandler:
    INACTIVITY_TIMEOUT = 240  # Change from 120 to 240 minutes
    SESSION_WARNING_THRESHOLD = 15  # Change from 10 to 15 minutes
```

### Match Flask Configuration

In `app/config.py`, ensure:

```python
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=240)  # Same as timeout
```

## Common Use Cases

### Protect an Admin Route

```python
@app.route('/admin/settings')
@session_required
def admin_settings():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/settings.html')
```

### API Endpoint with Session Check

```python
@app.route('/api/todos', methods=['GET'])
def get_todos():
    from app.session_handler import check_session_expiration
    status = check_session_expiration()
    
    if status['is_expired']:
        return jsonify({'error': 'Session expired'}), 401
    
    todos = current_user.todos.all()
    return jsonify([t.to_dict() for t in todos])
```

### Keep Session Alive During Activity

```javascript
// In your main.js or dashboard script
document.addEventListener('click', function() {
    fetch('/api/keep-alive', {method: 'POST'});
});
```

## Troubleshooting

### Sessions Expiring Too Quickly

1. Check `INACTIVITY_TIMEOUT` value
2. Verify server time is correct (use `date` command)
3. Look for clock skew in logs

### Session Warning Not Showing

1. Verify context processor is working:
   ```python
   # In template: {{ session_warning }}
   ```
2. Check that `SESSION_WARNING_THRESHOLD < INACTIVITY_TIMEOUT`
3. Ensure user has been active for more than timeout minus warning

### AJAX Requests Getting 401

1. Set header: `'X-Requested-With': 'XMLHttpRequest'`
2. Handle 401 status and redirect to login
3. See example in `app/session_handler_examples.py`

## Testing

Run the test suite:

```bash
cd /storage/linux/Projects/mysandbox
python -m pytest tests/test_session_handler.py -v
```

### Manual Testing

```python
# In Python shell with app context
from app import app
from app.session_handler import SessionExpirationHandler
from datetime import datetime, timedelta

with app.app_context():
    with app.test_client() as client:
        # Login
        client.post('/login', data={'email': 'test@test.com', 'password': 'pass'})
        
        # Check status
        print(f"Expired: {SessionExpirationHandler.is_session_expired()}")
        print(f"Remaining: {SessionExpirationHandler.get_remaining_time_minutes()}")
```

## Files Structure

```
app/
├── session_handler.py              # Main module
├── session_handler_examples.py      # Usage examples
└── __init__.py                      # Initialization

docs/
└── SESSION_HANDLER.md               # Full documentation

tests/
└── test_session_handler.py          # Test suite
```

## Security Features

- ✅ Session tokens stored server-side (not tamper-able)
- ✅ Timestamps validated on every request
- ✅ Automatic expiration prevents unauthorized access
- ✅ No sensitive data exposed in client
- ✅ Handles both regular and AJAX requests

## Performance Impact

- **Negligible**: Each check is O(1) timestamp comparison
- **No database queries**: Uses Flask session (in-memory)
- **Scalable**: Works with any session backend

## Next Steps

1. **Review Full Docs**: See `docs/SESSION_HANDLER.md`
2. **Check Examples**: See `app/session_handler_examples.py`
3. **Run Tests**: See test suite for expected behavior
4. **Integrate**: Add `@session_required` to sensitive routes
5. **Monitor**: Watch logs for session expiration events

## Support

For issues or questions:
1. Check `docs/SESSION_HANDLER.md` troubleshooting section
2. Review test examples in `tests/test_session_handler.py`
3. See code examples in `app/session_handler_examples.py`
4. Check logs for detailed error messages

---

**Created**: 2026-02-01
**Module Status**: Production Ready
**Last Updated**: 2026-02-01
