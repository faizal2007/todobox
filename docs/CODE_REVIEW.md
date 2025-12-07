# Code Review & Best Practices

## Executive Summary

TodoBox is a well-structured Flask learning project demonstrating good fundamentals in MVC architecture, user authentication, and database management. However, there are several areas for improvement regarding code quality, security, and maintainability.

## Identified Issues

### 🔴 Critical Issues

#### 1. Hardcoded Secrets in Configuration

**Location:** `app/config.py`

```python
SALT = '$2b$12$yLUMTIfl21FKJQpTkRQXCu'
SECRET_KEY = 'you-will-never-guess'
```

**Issue:** Sensitive values are hardcoded in source control.

**Recommendation:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

SALT = os.environ.get('SALT', 'default-salt')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
```

**Impact:** High - Security vulnerability

---

#### 2. Default Credentials Not Changed

**Location:** `app/models.py` - `User.seed()`

**Issue:** Default admin credentials (admin/admin1234) are well-known and easily guessable.

**Recommendation:**

- Change default password on first login
- Generate random initial password
- Force password change on first login
- Document in setup guide (already done in SETUP.md)

**Impact:** High - Account takeover risk

---

#### 3. SQL Injection Risk in getList Method

**Location:** `app/models.py` - Line in `Todo.getList()`

```python
def getList(type, start, end):
    # Parameters passed directly
```

**Issue:** String parameters used in query filtering could be vulnerable if not properly sanitized.

**Recommendation:** While SQLAlchemy parameterized queries provide some protection, validate input explicitly:

```python
@staticmethod
def getList(type, start, end):
    valid_types = ['today', 'tomorrow']
    if type not in valid_types:
        raise ValueError(f"Invalid type: {type}")
    # ... rest of query
```

**Impact:** Medium - Current implementation uses ORM which mitigates risk

---

#### 4. No Input Validation on Markdown Content

**Location:** `app/routes.py` - `add()` function

```python
getActivities = request.form.get("activities").strip()
getActivities_html = markdown.markdown(getActivities, extensions=['fenced_code'])
```

**Issue:** Markdown is converted to HTML without sanitization, risking XSS attacks.

**Recommendation:** Use a sanitization library:

```python
from bleach import clean
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'code', 'pre', 'blockquote', 'ul', 'ol', 'li']
getActivities_html = clean(markdown.markdown(getActivities), tags=ALLOWED_TAGS)
```

**Impact:** High - XSS vulnerability

---

### 🟠 Major Issues

#### 5. Missing Error Handling in Database Operations

**Location:** Throughout `app/routes.py`

```python
todo = Todo.query.filter_by(id=todo_id).first()
# No check if todo is None
t.name = getTitle  # Could fail if todo doesn't exist
```

**Recommendation:**

```python
todo = Todo.query.filter_by(id=todo_id).first()
if not todo:
    abort(404)
```

**Impact:** Medium - Runtime errors and poor user experience

---

#### 6. No Validation in Form Classes

**Location:** `app/forms.py` - `UpdateAccount` form

```python
class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Validation code is commented out!
```

**Issue:** Duplicate username/email validation is commented out, allowing duplicates.

**Recommendation:** Uncomment and fix:

```python
def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None and user.id != current_user.id:
        raise ValidationError('Username already taken')
```

**Impact:** High - Data integrity issue

---

#### 7. Incorrect Static Method Declaration

**Location:** `app/models.py` - `Tracker.add()`, `Status.seed()`, `User.seed()`

```python
def add(todo_id, status_id, timestamp=datetime.now()):
    # Missing @staticmethod decorator
    db.session.add(Tracker(todo_id=todo_id, status_id=status_id, timestamp=timestamp))
```

**Issue:** Methods lack `@staticmethod` decorator, causing them to fail when called on class.

**Recommendation:**

```python
@staticmethod
def add(todo_id, status_id, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
    # ... rest of method
```

**Impact:** Medium - Code works but violates Python conventions

---

#### 8. Mutable Default Arguments

**Location:** `app/models.py` - `Tracker.add()`

```python
def add(todo_id, status_id, timestamp=datetime.now()):
```

**Issue:** `datetime.now()` is evaluated once at function definition, not at each call.

**Recommendation:**

```python
@staticmethod
def add(todo_id, status_id, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
```

**Impact:** Medium - Can cause unexpected behavior

---

#### 9. No CSRF Token Validation Evidence

**Location:** Form templates and routes

**Issue:** While CSRF protection is configured, it should be explicitly verified on all POST routes.

**Recommendation:** Ensure all forms use `{{ csrf_token() }}` (already implemented in most places).

**Impact:** Medium - Currently protected but should be verified

---

## 🟡 Minor Issues

### 10. Inconsistent String Formatting

**Location:** Throughout `app/routes.py`

```python
start = '{} {}'.format(query_date, '00:00')  # Old style
# vs.
f'{query_date} 00:00'  # f-string style
```

**Recommendation:** Use f-strings consistently (Python 3.6+)

**Impact:** Low - Code style

---

### 11. No Logging

**Location:** Entire application

**Issue:** No logging configured for debugging or monitoring.

**Recommendation:**

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f'User {user_id} logged in')
```

**Impact:** Low - Affects debugging and production monitoring

---

### 12. No Exception Handling in Route Handlers

**Location:** `app/routes.py` - All route functions

```python
user = User.query.filter_by(username=form.username.data).first()
# No try-except
```

**Recommendation:** Wrap database operations:

```python
try:
    user = User.query.filter_by(username=form.username.data).first()
except Exception as e:
    logger.error(f"Database error: {e}")
    flash('An error occurred. Please try again.')
    return redirect(url_for('login'))
```

**Impact:** Low - Improves error handling and debugging

---

#### 13. Magic Numbers Without Comments

**Location:** Throughout routes

```python
Tracker.add(t.id, 1, tomorrow)  # What do 1 and 2 mean?
todo.status_id != 1
todo.status_id == 2
```

**Recommendation:** Use named constants:

```python
STATUS_NEW = 1
STATUS_DONE = 2
STATUS_FAILED = 3
STATUS_REASSIGN = 4

Tracker.add(t.id, STATUS_NEW, tomorrow)
```

**Impact:** Low - Affects code readability

---

#### 14. Hardcoded String Literals

**Location:** `app/config.py`

```python
TITLE = 'My Sandbox'
DATABASE_NAME = 'todobox.db'
```

**Recommendation:** Move to environment variables for multi-environment support.

**Impact:** Low - Affects configuration management

---

#### 15. Missing Type Hints

**Location:** Throughout application

```python
def getList(type, start, end):  # No type hints
```

**Recommendation:**

```python
from typing import List, Optional, Query as SQLQuery

@staticmethod
def getList(type: str, start: str, end: str) -> SQLQuery:
```

**Impact:** Low - Improves IDE support and documentation

---

## Code Quality Metrics

### Maintainability

| Aspect | Rating | Comments |
|--------|--------|----------|
| Structure | ⭐⭐⭐⭐ | Clear MVC pattern |
| Readability | ⭐⭐⭐ | Some inconsistencies |
| Testability | ⭐⭐ | Few tests, tight coupling |
| Documentation | ⭐⭐⭐⭐ | Good (with this guide) |
| Security | ⭐⭐⭐ | Several concerns identified |

## Recommended Fixes (Priority Order)

### Phase 1: Security (Immediate)

1. Remove hardcoded secrets
2. Add HTML sanitization for Markdown
3. Validate unique username/email
4. Add error handling for missing records

### Phase 2: Reliability (Short-term)

1. Add @staticmethod decorators
2. Fix mutable default arguments
3. Add logging
4. Add exception handling

### Phase 3: Code Quality (Medium-term)

1. Add type hints
2. Use constants for status IDs
3. Add unit tests
4. Consistent string formatting

### Phase 4: Enhancements (Long-term)

1. Add logging framework
2. Add caching
3. API versioning
4. Rate limiting

## Testing Recommendations

### Unit Tests Needed

- User model methods (set_password, check_password)
- Form validation (UpdateAccount, ChangePassword)
- Todo retrieval logic (getList)

### Integration Tests Needed

- Full login flow
- Todo CRUD operations
- Account management workflows

### Security Tests

- CSRF token validation
- SQL injection attempts
- XSS payload handling

### Example Test

```python
import pytest
from app import app, db
from app.models import User

def test_user_set_password():
    user = User(username='test', email='test@example.com')
    user.set_password('password123')
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')
```

## Dependencies to Update

### Security Updates

- `Werkzeug`: 2.3.6 → Latest
- `Flask`: 2.3.2 → Latest
- `SQLAlchemy`: 1.4.17 → 2.x (if compatible)

### Recommended Additions

```text
bleach==6.0.0          # HTML sanitization
python-validators==1.0 # Better validation
gunicorn==21.0.0       # Production server
python-dotenv==1.0.0   # Environment variables
```

## Best Practices Applied

✅ **Good:**

- MVC architecture pattern
- SQLAlchemy ORM usage
- Flask-Login for authentication
- CSRF protection enabled
- Password hashing (Werkzeug)
- Database migrations with Alembic
- Form validation with WTForms

## Best Practices Missing

❌ **Improve:**

- Input sanitization (especially HTML)
- Type hints
- Logging
- Exception handling
- Unit tests
- Secret management
- Error pages
- Rate limiting

## Conclusion

TodoBox is a solid learning project with proper fundamentals. The main areas requiring attention are security (secrets, input sanitization) and code hygiene (type hints, logging, exception handling). The recommended fixes are prioritized by security impact and ease of implementation.
