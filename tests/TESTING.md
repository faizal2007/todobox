# TodoBox Functional Tests

Comprehensive functional test suite for the TodoBox application. Tests cover authentication, todo management, user isolation, sharing, admin features, and end-to-end workflows.

## Test Coverage

### 1. **Authentication Tests** (`TestAuthentication`)

- ✅ Login page accessibility
- ✅ User registration workflow
- ✅ Login with valid credentials
- ✅ Login with invalid credentials
- ✅ Logout functionality

### 2. **Todo Management Tests** (`TestTodoManagement`)

- ✅ Create todo items
- ✅ View todo list
- ✅ Update todo status (mark as done, failed, etc.)
- ✅ Delete todo items
- ✅ Edit todo items
- ✅ Priority levels (high, medium, low)

### 3. **User Isolation Tests** (`TestUserIsolation`)

- ✅ Users cannot see other users' todos
- ✅ Users cannot delete other users' todos
- ✅ Access control enforcement

### 4. **Todo Sharing Tests** (`TestTodoSharing`)

- ✅ Share todos with other users
- ✅ Shared users can view shared todos
- ✅ Sharing permissions

### 5. **Admin Functionality Tests** (`TestAdminFunctionality`)

- ✅ Admin can access admin panel
- ✅ Non-admin users blocked from admin panel
- ✅ Admin can block users
- ✅ User management operations

### 6. **User Settings Tests** (`TestUserSettings`)

- ✅ Access settings page
- ✅ Update user profile
- ✅ Change password
- ✅ Email updates

### 7. **Integration Tests** (`TestEndToEndWorkflow`)

- ✅ Complete user workflow (register → create → share → view)
- ✅ Multi-user collaboration scenarios
- ✅ Complex workflows

## Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-html
```

## Running Tests

### Run All Tests

```bash
python tests/run_tests.py all
```

### Run Specific Test Suite

```bash
# Authentication tests only
python tests/run_tests.py auth

# Todo management tests
python tests/run_tests.py todos

# User isolation tests
python tests/run_tests.py isolation

# Sharing tests
python tests/run_tests.py sharing

# Admin tests
python tests/run_tests.py admin

# Settings tests
python tests/run_tests.py settings

# Integration tests
python tests/run_tests.py integration
```

### Advanced Options

```bash
# Verbose output
python tests/run_tests.py all --verbose

# With coverage report
python tests/run_tests.py all --coverage

# Generate HTML report
python tests/run_tests.py all --html

# Run tests matching keyword
python tests/run_tests.py all --keyword "login"

# Drop into debugger on failures
python tests/run_tests.py all --pdb
```

### Direct pytest Usage

```bash
# Run with pytest directly
pytest tests/test_functional.py -v

# Run specific test class
pytest tests/test_functional.py::TestAuthentication -v

# Run specific test
pytest tests/test_functional.py::TestAuthentication::test_login_page_accessible -v

# With coverage
pytest tests/test_functional.py --cov=app --cov-report=html

# Create HTML report
pytest tests/test_functional.py --html=report.html --self-contained-html
```

## Test Structure

### Fixtures

- **`app`** - Test Flask application instance with in-memory SQLite database
- **`client`** - Test client for making requests
- **`db_session`** - Database session for test setup/teardown
- **`logged_in_client`** - Pre-authenticated test client
- **`admin_user`** - Admin user fixture
- **`two_users_with_todos`** - Two users with sample todos
- **`sharing_setup`** - Two users set up for sharing tests

### Test Pattern

Each test follows this pattern:

1. **Arrange** - Set up test data and state
2. **Act** - Perform the operation being tested
3. **Assert** - Verify the expected outcome

## Understanding Test Output

### Verbose Output

```text
tests/test_functional.py::TestAuthentication::test_login_page_accessible PASSED
tests/test_functional.py::TestAuthentication::test_login_page_accessible FAILED
tests/test_functional.py::TestAuthentication::test_login_page_accessible SKIPPED
```

### Coverage Report

```text
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
app/__init__.py              45      2    96%    23-24
app/models.py              120      5    96%    45,67-70
app/routes.py              230     15    93%    102-115
-------------------------------------------------------
TOTAL                      395     22    94%
```

## Common Issues

### Issue: Tests fail with "No module named 'app'"

**Solution:** Run tests from the project root directory

```bash
cd /workspaces/todobox
python tests/run_tests.py
```

### Issue: "CSRF token missing" errors

**Solution:** Tests disable CSRF (`app.config['WTF_CSRF_ENABLED'] = False`)

### Issue: Database not found

**Solution:** Tests use in-memory SQLite database (`:memory:`)

### Issue: Authentication not working

**Solution:** Ensure User model has `set_password()` and password hashing methods

## Extending Tests

### Add New Test Class

```python
class TestNewFeature:
    """Test description."""
    
    def test_new_feature(self, client, db_session):
        """Test implementation."""
        # Arrange
        from app.models import User
        user = User(username='test', email='test@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Act
        response = client.get('/new-endpoint')
        
        # Assert
        assert response.status_code == 200
```

### Add New Fixture

```python
@pytest.fixture
def new_fixture(app, db_session):
    """Fixture description."""
    # Setup
    from app.models import SomeModel
    obj = SomeModel()
    db_session.session.add(obj)
    db_session.session.commit()
    
    yield obj
    
    # Teardown (if needed)
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage and exit code
python -m pytest tests/test_functional.py -v --cov=app --cov-report=xml --cov-report=term

# Fail on warnings
python -m pytest tests/test_functional.py -v --strict-markers

# Parallel execution (requires pytest-xdist)
python -m pytest tests/test_functional.py -v -n auto
```

## Performance

Test suite typically completes in:

- **All tests**: ~2-5 seconds (depends on system)
- **Single test class**: ~0.5-1 second
- **Single test**: ~0.1-0.2 seconds

## Files

- **`tests/test_functional.py`** - Main functional test suite (900+ lines)
- **`tests/run_tests.py`** - Test runner with CLI options
- **`tests/test_user_isolation.py`** - Existing user isolation tests
- **`tests/README.md`** - This file

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-html](https://pytest-html.readthedocs.io/)

## Best Practices

1. **Keep tests focused** - Each test should verify one behavior
2. **Use descriptive names** - Test names should explain what they test
3. **Use fixtures** - Share setup code across tests
4. **Mock external services** - Mock API calls, emails, etc.
5. **Test edge cases** - Include tests for invalid input, permissions, etc.
6. **Run tests frequently** - Run tests before committing changes
7. **Maintain test database** - Use fresh database for each test

## Troubleshooting

### Debug a specific test

```bash
pytest tests/test_functional.py::TestAuthentication::test_login_page_accessible -vvs
```

### Check test collection

```bash
pytest tests/test_functional.py --collect-only
```

### Run tests in specific order

```bash
pytest tests/test_functional.py -v --random-order-seed=12345
```

### Generate detailed HTML report

```bash
pytest tests/test_functional.py --html=report.html --self-contained-html -v
```
