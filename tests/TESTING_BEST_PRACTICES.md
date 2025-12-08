# TodoBox Testing Best Practices

**Last Updated**: December 4, 2024  
**For**: Developers, QA Engineers, Contributors  
**Status**: Active Development Guide

## Overview

This document outlines best practices for writing and maintaining tests in the TodoBox application. Following these guidelines ensures tests are reliable, maintainable, and provide meaningful coverage.

## Testing Philosophy

### Core Principles

1. **Tests should be isolated** - Each test should be independent and not rely on other tests
2. **Tests should be deterministic** - Same input should always produce same output
3. **Tests should be fast** - Quick feedback loop encourages frequent testing
4. **Tests should be readable** - Clear test names and structure
5. **Tests should be maintainable** - Easy to update when requirements change

### Test Pyramid

```bash
        /\
       /  \      E2E Tests (Few)
      /____\     - Complete workflows
     /      \    - Browser automation
    /  Unit  \   Integration Tests (Some)
   /  Tests   \  - API endpoints
  /____________\ - Multi-component interactions
       
       Unit Tests (Many)
       - Models
       - Utilities
       - Functions
```

## Test Organization

### Directory Structure

```bash
tests/
├── __init__.py                      # Test package initialization
├── test_comprehensive.py            # Core model and API tests
├── test_backend_routes.py           # Route/endpoint tests
├── test_frontend.py                 # Frontend/template tests
├── test_security_updates.py         # Security tests
├── test_functional.py               # Functional workflow tests
├── test_user_isolation.py           # Data isolation tests
├── test_integration.py              # Integration tests
├── test_reminder_*.py               # Feature-specific tests
├── TESTING.md                       # Test running guide
└── TEST_SUMMARY.md                  # Current test status
```

### Naming Conventions

**Test Files**: `test_<feature>.py`
- `test_models.py` - Model tests
- `test_api.py` - API tests
- `test_authentication.py` - Auth tests

**Test Classes**: `Test<Feature>`
- `TestUserModel`
- `TestAPIEndpoints`
- `TestAuthentication`

**Test Methods**: `test_<what_is_tested>`
- `test_user_creation`
- `test_api_returns_todos`
- `test_login_with_valid_credentials`

### Test Structure

Use the **Arrange-Act-Assert** pattern:

```python
def test_user_creation(self, client, db_session):
    """Test that a user can be created successfully."""
    # Arrange - Set up test data
    from app.models import User
    email = 'test@example.com'
    
    # Act - Perform the action
    user = User(email=email)
    user.set_password('SecurePass123!')
    db_session.session.add(user)
    db_session.session.commit()
    
    # Assert - Verify the results
    created_user = User.query.filter_by(email=email).first()
    assert created_user is not None
    assert created_user.email == email
```

## Writing Good Tests

### Test Names Should Tell a Story

❌ Bad:
```python
def test_user(self):
    ...
```

✅ Good:
```python
def test_user_creation_with_valid_email(self):
    """Test that a user can be created with a valid email address."""
    ...
```

### Use Descriptive Assertions

❌ Bad:
```python
assert response.status_code == 200
```

✅ Good:
```python
assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
```

### Test One Thing at a Time

❌ Bad:
```python
def test_user_and_todo_and_api(self):
    # Creates user
    # Creates todo
    # Tests API
    # Tests deletion
    ...
```

✅ Good:
```python
def test_user_creation(self):
    # Only tests user creation
    ...

def test_todo_creation(self):
    # Only tests todo creation
    ...
```

### Use Fixtures for Common Setup

✅ Good:
```python
@pytest.fixture
def authenticated_user(client, db_session):
    """Create and return an authenticated user."""
    from app.models import User
    user = User(email='test@example.com')
    user.set_password('Pass123!')
    db_session.session.add(user)
    db_session.session.commit()
    
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Pass123!'
    })
    
    return user

def test_todo_creation_requires_auth(self, authenticated_user, client):
    """Test creating a todo requires authentication."""
    # User is already authenticated via fixture
    ...
```

## Model Testing

### Todo Model Tests

```python
def test_todo_name_property(self, db_session):
    """Test todo name encryption/decryption."""
    from app.models import Todo, User
    
    # Create user and todo
    user = User(email='test@example.com')
    db_session.session.add(user)
    db_session.session.commit()
    
    todo = Todo()
    todo.name = 'Test Todo'
    todo.user_id = user.id
    db_session.session.add(todo)
    db_session.session.commit()
    
    # Retrieve and verify encryption works
    retrieved = Todo.query.first()
    assert retrieved.name == 'Test Todo'
```

### User Model Tests

```python
def test_password_hashing(self, db_session):
    """Test that passwords are hashed, not stored plaintext."""
    from app.models import User
    
    user = User(email='test@example.com')
    user.set_password('MySecretPassword123!')
    
    # Password should be hashed
    assert user.password_hash != 'MySecretPassword123!'
    
    # Should verify correctly
    assert user.check_password('MySecretPassword123!')
    assert not user.check_password('WrongPassword')
```

## API Testing

### Test All HTTP Methods

```python
class TestTodoAPI:
    """Test Todo API endpoints."""
    
    def test_list_todos_get(self, client, api_token):
        """Test GET /api/todo returns todo list."""
        headers = {'Authorization': f'Bearer {api_token}'}
        response = client.get('/api/todo', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'todos' in data
    
    def test_create_todo_post(self, client, api_token):
        """Test POST /api/todo creates new todo."""
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        data = {'title': 'New Todo', 'details': 'Test details'}
        
        response = client.post('/api/todo', headers=headers, json=data)
        
        assert response.status_code == 201
        result = response.get_json()
        assert result['title'] == 'New Todo'
```

### Test Authentication

```python
def test_api_requires_authentication(self, client):
    """Test that API endpoints require authentication."""
    response = client.get('/api/todo')
    
    # Should return 401 Unauthorized or redirect
    assert response.status_code in [401, 302]

def test_api_rejects_invalid_token(self, client):
    """Test that API rejects invalid tokens."""
    headers = {'Authorization': 'Bearer invalid_token_here'}
    response = client.get('/api/todo', headers=headers)
    
    assert response.status_code == 401
```

## Security Testing

### Test XSS Prevention

```python
def test_xss_script_injection_blocked(self, client, authenticated_user):
    """Test that script injection is blocked."""
    malicious_input = '<script>alert("XSS")</script>'
    
    # Try to create todo with malicious content
    response = client.post('/add', data={
        'name': malicious_input,
        'details': 'Normal content'
    })
    
    # Verify script was sanitized
    from app.models import Todo
    todo = Todo.query.filter_by(user_id=authenticated_user.id).first()
    assert '<script>' not in todo.name
    assert 'alert' not in todo.name
```

### Test SQL Injection Prevention

```python
def test_sql_injection_prevention(self, client):
    """Test that SQL injection attempts are blocked."""
    malicious_input = "'; DROP TABLE user; --"
    
    # Should not break or execute SQL
    from app.models import Todo
    try:
        Todo.getList(malicious_input, None, None)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Invalid type" in str(e)
```

## Integration Testing

### Test Complete Workflows

```python
def test_complete_user_workflow(self, client, db_session):
    """Test complete user workflow from signup to todo creation."""
    from app.models import User, Todo
    
    # Step 1: Create account
    user = User(email='workflow@example.com')
    user.set_password('Pass123!')
    db_session.session.add(user)
    db_session.session.commit()
    
    # Step 2: Login
    response = client.post('/login', data={
        'email': 'workflow@example.com',
        'password': 'Pass123!'
    })
    assert response.status_code in [200, 302]
    
    # Step 3: Create todo
    todo = Todo()
    todo.name = 'First Todo'
    todo.user_id = user.id
    db_session.session.add(todo)
    db_session.session.commit()
    
    # Step 4: Verify todo exists
    todos = Todo.query.filter_by(user_id=user.id).all()
    assert len(todos) == 1
    assert todos[0].name == 'First Todo'
```

## Common Pitfalls and Solutions

### Pitfall: Database State Leakage

❌ Problem:
```python
def test_user_count(self):
    # Assumes no users exist
    assert User.query.count() == 0  # Fails if previous test created users
```

✅ Solution:
```python
@pytest.fixture
def clean_db(db_session):
    """Ensure clean database for each test."""
    db_session.session.query(User).delete()
    db_session.session.commit()
    yield
    db_session.session.query(User).delete()
    db_session.session.commit()

def test_user_count(self, clean_db):
    # Now safe to assume clean state
    assert User.query.count() == 0
```

### Pitfall: Hardcoded Routes

❌ Problem:
```python
response = client.get('/todo/list')  # Route might change
```

✅ Solution:
```python
from flask import url_for
response = client.get(url_for('todo_list'))  # Uses route name
```

### Pitfall: Not Testing Edge Cases

❌ Problem:
```python
def test_user_creation(self):
    # Only tests happy path
    user = User(email='test@example.com')
    assert user is not None
```

✅ Solution:
```python
def test_user_creation_with_valid_email(self):
    # Happy path
    ...

def test_user_creation_with_invalid_email(self):
    # Test invalid email
    ...

def test_user_creation_with_duplicate_email(self):
    # Test duplicate email
    ...

def test_user_creation_with_empty_email(self):
    # Test empty email
    ...
```

## Test Maintenance

### When to Update Tests

1. **Feature Changes**: Update tests when requirements change
2. **Bug Fixes**: Add tests that reproduce the bug before fixing
3. **Refactoring**: Update tests if interfaces change
4. **Security Updates**: Add tests for security fixes

### Handling Flaky Tests

1. **Identify**: Mark tests that fail intermittently
2. **Investigate**: Find root cause (timing, dependencies, state)
3. **Fix**: Make test deterministic
4. **Remove**: If can't fix, remove or disable with clear reason

### Test Coverage Goals

- **Critical paths**: 100% coverage
- **Business logic**: 90%+ coverage
- **Overall application**: 80%+ coverage
- **UI/Templates**: Basic coverage sufficient

## Running Tests

### During Development

```bash
# Run specific test file
pytest tests/test_integration.py -v

# Run specific test
pytest tests/test_integration.py::TestUserAuthentication::test_password_based_authentication -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Before Committing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term --cov-report=html

# Check for warnings
pytest tests/ -v --strict-warnings
```

### In CI/CD

```bash
# Fast feedback - run unit tests first
pytest tests/test_comprehensive.py tests/test_security_updates.py -v

# Then integration tests
pytest tests/test_integration.py tests/test_functional.py -v

# Finally full suite
pytest tests/ -v --cov=app --cov-report=xml
```

## Continuous Improvement

### Review Tests Regularly

- **Monthly**: Review and update outdated tests
- **Per Feature**: Add tests for new features
- **Per Bug**: Add regression tests for bug fixes
- **Per Quarter**: Review coverage and identify gaps

### Metrics to Track

- Test count and pass rate
- Code coverage percentage
- Test execution time
- Flaky test count
- Tests per feature

## Resources

### Internal Documentation

- [TEST_SUMMARY.md](TEST_SUMMARY.md) - Current test status
- [TESTING.md](TESTING.md) - How to run tests
- [SECURITY_PATCHES.md](../docs/SECURITY_PATCHES.md) - Security test requirements

### External Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

## Conclusion

Good tests are an investment that pays dividends in:
- **Confidence** in code changes
- **Documentation** of expected behavior
- **Regression prevention**
- **Faster development** through quick feedback

Follow these best practices to maintain a healthy, reliable test suite that supports rapid development while maintaining quality.

---

**Remember**: A test that doesn't run is worthless. A test that always passes is worthless. A test that fails randomly is worse than worthless. Write tests that provide value!
