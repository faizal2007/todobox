# TodoBox Testing Guide

Comprehensive testing guide for the TodoBox application. Tests cover authentication, API endpoints, routes, models, security, utility functions, and complete workflows.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-html

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
```

## Test Overview

**Total Tests**: 227  
**Passing**: 183 (80.6%)  
**Test Files**: 12  
**Coverage**: Comprehensive backend and utility coverage

## Test Suites

### 1. Utility Function Tests (`test_utility_functions.py`) - NEW ✨
**33 tests, 32 passing (97%)**

Tests for all utility modules:
- **Encryption utilities** - Text encryption/decryption, key derivation
- **Timezone utilities** - Timezone conversion, user local time
- **Geolocation utilities** - IP detection, timezone detection
- **Email services** - Configuration checks
- **Helper utilities** - MomentJS, date formatting

```bash
python -m pytest tests/test_utility_functions.py -v
```

### 2. Workflow Tests (`test_workflows.py`) - NEW ✨
**12 tests, 4 passing (33%)**

End-to-end workflow testing:
- User registration → login → todo creation
- Complete todo lifecycle (create → update → complete → delete)
- API token generation → usage → revocation
- Settings and profile management
- Dashboard viewing and statistics
- Error recovery scenarios

```bash
python -m pytest tests/test_workflows.py -v
```

### 3. Comprehensive Tests (`test_comprehensive.py`)
**28 tests, 26 passing (93%)**

- User, Todo, Status, Tracker models
- API endpoints (auth, CRUD, quotes)
- Public and authenticated routes
- Static assets and CSS
- Security features

```bash
python -m pytest tests/test_comprehensive.py -v
```

### 4. Backend Route Tests (`test_backend_routes.py`)
**28 tests, 26 passing (93%)**

- Authentication routes
- Todo management routes
- User settings routes
- Sharing routes
- OAuth routes
- Error handling
- Performance tests

```bash
python -m pytest tests/test_backend_routes.py -v
```

### 5. Frontend Tests (`test_frontend.py`)
**27 tests, 27 passing (100%)**

- Static asset validation
- PWA features (service worker, manifest)
- Template existence checks
- Responsive design
- Accessibility
- Security headers

```bash
python -m pytest tests/test_frontend.py -v
```

### 6. Security Tests (`test_security_updates.py`)
**27 tests, 27 passing (100%)**

- XSS prevention
- SQL injection prevention
- Password security
- API token security
- Form validation
- CSRF protection

```bash
python -m pytest tests/test_security_updates.py -v
```

### 7. Functional Tests (`test_functional.py`)
**38 tests, 28 passing (74%)**

- Complete authentication flows
- Todo management
- User isolation
- Todo sharing
- Admin functionality

```bash
python -m pytest tests/test_functional.py -v
```

### 8. User Isolation Tests (`test_user_isolation.py`)
**17 tests, 3 passing (18%)**

- User data isolation
- Shared todo access
- Todo encryption
- Permission boundaries

```bash
python -m pytest tests/test_user_isolation.py -v
```

## Running Tests

### Basic Commands

```bash
# All tests
python -m pytest tests/ -v

# Specific file
python -m pytest tests/test_utility_functions.py -v

# Specific class
python -m pytest tests/test_comprehensive.py::TestUserModel -v

# Specific test
python -m pytest tests/test_comprehensive.py::TestUserModel::test_create_user -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Verbose with output
python -m pytest tests/ -vv -s

# Stop on first failure
python -m pytest tests/ -x

# Run failed tests only
python -m pytest tests/ --lf
```

### Advanced Options

```bash
# Parallel execution (requires pytest-xdist)
python -m pytest tests/ -n auto

# Generate HTML report
python -m pytest tests/ --html=report.html --self-contained-html

# With markers
python -m pytest tests/ -m "not slow"

# Debug mode
python -m pytest tests/ --pdb

# Coverage with missing lines
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## Test Fixtures

- **`app`** - Test Flask application with in-memory SQLite
- **`client`** - Test client for making HTTP requests
- **`db_session`** - Database session for setup/teardown
- **`authenticated_user`** - Pre-authenticated test user
- **`app_context`** - Application context for utility tests

## Writing Tests

### Test Structure

```python
class TestNewFeature:
    """Test description"""
    
    def test_specific_behavior(self, app, client):
        """Test specific behavior description"""
        with app.app_context():
            # Arrange - Setup
            user = User(email='test@example.com')
            db.session.add(user)
            db.session.commit()
            
            # Act - Execute
            response = client.get('/endpoint')
            
            # Assert - Verify
            assert response.status_code == 200
            assert 'expected' in response.data.decode()
```

### Best Practices

1. **Isolated tests** - No dependencies between tests
2. **Clear names** - `test_user_can_login_with_valid_credentials`
3. **One assertion per test** - Focus on single behavior
4. **Use fixtures** - Share setup code
5. **Mock external services** - Don't make real API calls
6. **Test edge cases** - Empty input, null values, errors
7. **Descriptive assertions** - Use meaningful error messages

## Coverage Areas

### ✅ Well Covered (90%+)
- User authentication
- API endpoints
- Security features
- Frontend assets
- Utility functions (NEW)
- Encryption/decryption (NEW)
- Timezone handling (NEW)

### ⚠️ Partial Coverage (50-90%)
- Todo workflows
- User settings
- OAuth flows
- Reminder functionality

### ❌ Needs Coverage (<50%)
- CLI commands
- Database migrations
- Email sending
- Background jobs

## Common Issues

### Issue: Tests fail with "No module named 'app'"
**Solution:** Run tests from project root
```bash
cd /path/to/todobox
python -m pytest tests/
```

### Issue: "CSRF token missing" errors
**Solution:** Tests disable CSRF automatically
```python
app.config['WTF_CSRF_ENABLED'] = False
```

### Issue: Database not found
**Solution:** Tests use in-memory SQLite (`:memory:`)

### Issue: Authentication not working
**Solution:** Ensure proper login in test setup
```python
client.post('/login', data={'email': 'test@example.com', 'password': 'pass'})
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=xml --cov-report=term

# Fail on warnings
python -m pytest tests/ --strict-markers

# Set time limit
timeout 300 python -m pytest tests/
```

## Test Performance

Typical execution times:
- **All tests**: ~22 seconds
- **Single file**: ~2-5 seconds
- **Single test**: ~0.1-0.5 seconds

## Documentation Files

- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Detailed test statistics and status
- **[TESTING_BEST_PRACTICES.md](TESTING_BEST_PRACTICES.md)** - In-depth testing guidelines
- **[README.md](README.md)** - Quick reference guide

## Recent Updates

### December 4, 2024
- ✨ Added 48 new tests (37 passing)
- ✨ Comprehensive utility function testing
- ✨ End-to-end workflow testing
- 📈 Increased total tests to 227
- 📈 Pass rate improved to 80.6%
- 📚 Updated documentation
- 🐛 Fixed duplicate content in TEST_SUMMARY.md

### December 3, 2024
- Created security test suite (27 tests, 100% passing)
- Fixed werkzeug compatibility
- Improved test infrastructure

---

**Last Updated**: December 4, 2024  
**Test Count**: 227 tests  
**Pass Rate**: 80.6% (183/227)  
**Coverage**: Comprehensive backend, utilities, and workflows
