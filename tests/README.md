# TodoBox Testing Guide

**Version:** 2.0  
**Last Updated:** December 4, 2024  
**Test Count:** 227 tests (183 passing, 80.6% pass rate)

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-html

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term

# Run merge readiness tests
python -m pytest tests/test_merge_readiness.py -v
```

## Test Organization

### Test Suites

1. **Merge Readiness Tests** (`test_merge_readiness.py`) - 24 tests ✨ NEW
   - Critical imports and dependencies
   - App initialization
   - Database models and compatibility
   - API endpoints
   - Security compliance
   - Documentation validation

2. **Security Tests** (`test_security_updates.py`) - 27 tests, 100% passing
   - XSS prevention
   - SQL injection prevention
   - Password security
   - API token security
   - Configuration security

3. **Frontend Tests** (`test_frontend.py`) - 27 tests, 100% passing
   - Static assets
   - PWA features
   - Templates
   - Responsive design
   - Accessibility

4. **Comprehensive Tests** (`test_comprehensive.py`) - 28 tests, 93% passing
   - User, Todo, Status, Tracker models
   - API endpoints
   - Routes
   - Static assets

5. **Backend Route Tests** (`test_backend_routes.py`) - 28 tests, 93% passing
   - Authentication routes
   - Todo management
   - User settings
   - OAuth routes

6. **Integration Tests** (`test_integration.py`) - 13 tests, 100% passing
   - Complete user workflows
   - Todo lifecycle
   - Authentication
   - API token management

7. **Utility Function Tests** (`test_utility_functions.py`) - 33 tests, 97% passing
   - Encryption utilities
   - Timezone utilities
   - Geolocation utilities
   - Helper utilities

8. **Functional Tests** (`test_functional.py`) - 38 tests, 74% passing
   - Authentication flows
   - Todo management
   - User isolation
   - Sharing functionality

9. **User Isolation Tests** (`test_user_isolation.py`) - 17 tests, 18% passing ⚠️
   - User data isolation
   - Shared todo access
   - Permission boundaries

10. **Workflow Tests** (`test_workflows.py`) - 12 tests, 33% passing ⚠️
    - End-to-end workflows
    - Complete user journeys

11. **Reminder Tests** - 2 tests, 0% passing ⚠️
    - Reminder auto-close
    - 30-minute intervals

## Running Tests

### Basic Commands

```bash
# All tests
python -m pytest tests/ -v

# Specific suite
python -m pytest tests/test_merge_readiness.py -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Stop on first failure
python -m pytest tests/ -x

# Run only failed tests
python -m pytest tests/ --lf
```

### Test Selection

```bash
# By keyword
python -m pytest tests/ -k "security"

# By marker (if defined)
python -m pytest tests/ -m "not slow"

# Specific test
python -m pytest tests/test_merge_readiness.py::TestCriticalFunctionality::test_user_creation_works
```

## Merge Readiness

Before merging any branch with master, run:

```bash
# Merge readiness tests
python -m pytest tests/test_merge_readiness.py -v

# Critical security tests
python -m pytest tests/test_security_updates.py tests/test_user_isolation.py -v

# Full test suite
python -m pytest tests/ -v --tb=short
```

### Merge Criteria
- ✅ Merge readiness tests: >90% passing
- ✅ Security tests: 100% passing
- ✅ Frontend tests: 100% passing
- ✅ Overall pass rate: >85%

See `MERGE_READINESS_REPORT.md` for detailed analysis.

## Test Fixtures

Common fixtures used across tests:

- **`app`** - Test Flask application with in-memory SQLite
- **`client`** - Test client for HTTP requests
- **`db_session`** - Database session for setup/teardown
- **`authenticated_user`** - Pre-authenticated test user with API token
- **`app_context`** - Application context for utility tests

## Writing New Tests

### Test Structure

```python
import pytest
from app import db
from app.models import User, Todo

class TestNewFeature:
    """Test description"""
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        # Setup code
        yield app
        # Teardown code
    
    def test_specific_behavior(self, app, client):
        """Test specific behavior description"""
        with app.app_context():
            # Arrange
            user = User(email='test@example.com', fullname='Test User')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Act
            response = client.get('/endpoint')
            
            # Assert
            assert response.status_code == 200
```

### Best Practices

1. **Isolated tests** - No dependencies between tests
2. **Clear names** - `test_user_can_login_with_valid_credentials`
3. **Single responsibility** - Test one thing per test
4. **Use fixtures** - Share setup code efficiently
5. **Mock external services** - Don't make real API calls
6. **Test edge cases** - Empty input, null values, errors
7. **Descriptive assertions** - Use meaningful error messages

### Creating Models in Tests

```python
# User
user = User(email='test@example.com', fullname='Test User')
user.set_password('password123')
db.session.add(user)
db.session.commit()

# Todo (use property setters)
todo = Todo()
todo.name = 'Test Todo'
todo.details = 'Test Details'
todo.user_id = user.id
db.session.add(todo)
db.session.commit()

# Status (use seed method)
Status.seed()
db.session.commit()
```

## Known Issues

### Current Test Failures

1. **User Isolation Tests** (14/17 failing) ⚠️ CRITICAL
   - Security concern
   - Must be fixed before merge
   - Issue: Authentication redirects or isolation logic

2. **Workflow Tests** (8/12 failing)
   - Authentication fixture issues
   - Session persistence problems

3. **Functional Tests** (15/38 failing)
   - Similar authentication issues
   - Need fixture updates

4. **Reminder Tests** (2/2 failing)
   - Database setup inconsistency

### Compatibility Issues

**Werkzeug 3.1.4 + Flask 2.3.2**
- Some test client creation fails
- Workaround: Downgrade Werkzeug to <3.0 or upgrade Flask
- Not blocking for production

## Coverage

### Well Covered (>90%)
- ✅ Security features
- ✅ Frontend assets
- ✅ API endpoints
- ✅ Utility functions
- ✅ User authentication

### Needs Improvement (<70%)
- ⚠️ User isolation
- ⚠️ Workflows
- ⚠️ Reminder functionality
- ⚠️ OAuth flows

## Continuous Integration

### Recommended CI Pipeline

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: python -m pytest tests/ -v --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Issue: "No module named 'app'"
**Solution:** Run tests from project root
```bash
cd /path/to/todobox
python -m pytest tests/
```

### Issue: "CSRF token missing"
**Solution:** Tests disable CSRF automatically in fixtures
```python
app.config['WTF_CSRF_ENABLED'] = False
```

### Issue: Database not found
**Solution:** Tests use in-memory SQLite
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
```

### Issue: Authentication not working
**Solution:** Ensure proper login in test setup
```python
client.post('/login', data={'email': 'test@example.com', 'password': 'pass'})
```

## Performance

Typical execution times:
- **All tests**: ~22 seconds
- **Single file**: ~2-5 seconds
- **Single test**: ~0.1-0.5 seconds

## Documentation

- **[MERGE_READINESS_REPORT.md](../MERGE_READINESS_REPORT.md)** - Detailed merge analysis
- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Detailed test statistics (if available)

## Contributing

When adding new tests:
1. Follow existing test patterns
2. Use descriptive test names
3. Add docstrings to test classes and methods
4. Update this guide if adding new test categories
5. Ensure tests are independent and can run in any order
6. Run the full suite before committing

---

**Need Help?**
- Run `python -m pytest tests/ --help` for pytest options
- Check test files for examples
- Review existing test patterns

**Report Issues:**
- Test failures that seem incorrect
- Missing test coverage areas
- Documentation improvements needed
