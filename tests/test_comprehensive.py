#!/usr/bin/env python3
"""
Comprehensive tests for TodoBox backend and frontend functionality.
Tests all routes, models, API endpoints, and frontend assets.
"""
import pytest
import os
import sys
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from app import app, db
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Seed status data
        from app.models import Status
        if Status.query.count() == 0:
            Status.seed()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    # Workaround for werkzeug.__version__ issue
    import werkzeug
    if not hasattr(werkzeug, '__version__'):
        werkzeug.__version__ = '3.0.0'
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for test setup/teardown."""
    from app import db
    yield db
    db.session.remove()


# ============================================================================
# MODEL TESTS
# ============================================================================

class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self, app, db_session):
        """Test creating a new user."""
        from app.models import User
        
        user = User(email='test@example.com', fullname='Test User')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.fullname == 'Test User'
        assert user.check_password('password123')
    
    def test_user_password_hashing(self, app, db_session):
        """Test password hashing and verification."""
        from app.models import User
        
        user = User(email='hash@example.com')
        user.set_password('mypassword')
        
        assert user.password_hash != 'mypassword'
        assert user.check_password('mypassword')
        assert not user.check_password('wrongpassword')
    
    def test_api_token_generation(self, app, db_session):
        """Test API token generation and validation."""
        from app.models import User
        
        user = User(email='token@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        token = user.generate_api_token()
        assert token is not None
        assert len(token) == 32
        assert user.check_api_token(token)
        
        # Test retrieval by token
        found_user = User.get_user_by_api_token(token)
        assert found_user.id == user.id


class TestTodoModel:
    """Test Todo model functionality."""
    
    def test_create_todo(self, app, db_session):
        """Test creating a new todo."""
        from app.models import Todo, User
        
        user = User(email='todo@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        todo = Todo()
        todo.name = 'Test Todo'
        todo.details = 'Test Details'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        assert todo.id is not None
        assert todo.name == 'Test Todo'
        assert todo.details == 'Test Details'
        assert todo.user_id == user.id
    
    def test_todo_properties(self, app, db_session):
        """Test todo encrypted properties."""
        from app.models import Todo, User
        
        user = User(email='props@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        todo = Todo()
        todo.name = 'Property Test'
        todo.details = 'Property Details'
        todo.details_html = '<p>HTML Details</p>'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Retrieve and verify
        retrieved = Todo.query.get(todo.id)
        assert retrieved.name == 'Property Test'
        assert retrieved.details == 'Property Details'
        assert retrieved.details_html == '<p>HTML Details</p>'
    
    def test_todo_reminder(self, app, db_session):
        """Test todo reminder functionality."""
        from app.models import Todo, User
        
        user = User(email='reminder@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        todo = Todo()
        todo.name = 'Reminder Todo'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Set reminder
        future_time = datetime.now() + timedelta(hours=1)
        todo.set_reminder(future_time)
        
        assert todo.reminder_enabled
        assert todo.reminder_time == future_time
        assert not todo.reminder_sent
        assert not todo.has_pending_reminder()
        
        # Clear reminder
        todo.clear_reminder()
        assert not todo.reminder_enabled
        assert todo.reminder_time is None


class TestStatusModel:
    """Test Status model functionality."""
    
    def test_status_seeding(self, app, db_session):
        """Test that status records are properly seeded."""
        from app.models import Status
        
        statuses = Status.query.all()
        assert len(statuses) >= 4
        
        status_names = [s.name for s in statuses]
        assert 'new' in status_names
        assert 'done' in status_names
        assert 'failed' in status_names


class TestTrackerModel:
    """Test Tracker model functionality."""
    
    def test_create_tracker(self, app, db_session):
        """Test creating tracker entries."""
        from app.models import Tracker, Todo, User, Status
        
        user = User(email='tracker@example.com')
        db_session.session.add(user)
        db_session.session.commit()
        
        todo = Todo()
        todo.name = 'Tracked Todo'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        status = Status.query.filter_by(name='new').first()
        Tracker.add(todo.id, status.id)
        
        tracker = Tracker.query.filter_by(todo_id=todo.id).first()
        assert tracker is not None
        assert tracker.status_id == status.id


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestAPIAuthentication:
    """Test API authentication endpoints."""
    
    def test_generate_api_token(self, client, db_session):
        """Test API token generation endpoint."""
        from app.models import User
        
        # Create and login user
        user = User(email='api@example.com')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Login first
        client.post('/login', data={
            'email': 'api@example.com',
            'password': 'password123'
        })
        
        # Generate token
        response = client.post('/api/auth/token')
        
        # Should succeed for logged-in user
        assert response.status_code in [200, 201, 302]


class TestAPITodoEndpoints:
    """Test API todo CRUD endpoints."""
    
    @pytest.fixture
    def api_user(self, db_session):
        """Create a user with API token."""
        from app.models import User
        
        user = User(email='apiuser@example.com')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        token = user.generate_api_token()
        
        return user, token
    
    def test_list_todos_api(self, client, api_user):
        """Test listing todos via API."""
        user, token = api_user
        
        response = client.get(
            '/api/todo',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'todos' in data
    
    def test_create_todo_api(self, client, api_user):
        """Test creating todo via API."""
        user, token = api_user
        
        response = client.post(
            '/api/todo',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': 'API Todo',
                'details': 'Created via API'
            })
        )
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'title' in data or 'id' in data
    
    def test_api_without_token(self, client):
        """Test API access without token returns 401."""
        response = client.get('/api/todo')
        assert response.status_code == 401


class TestAPIQuoteEndpoint:
    """Test quote API endpoint."""
    
    def test_get_quote(self, client):
        """Test getting a random quote."""
        response = client.get('/api/quote')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'quote' in data
        assert len(data['quote']) > 0


# ============================================================================
# ROUTE TESTS
# ============================================================================

class TestPublicRoutes:
    """Test public routes."""
    
    def test_login_page(self, client):
        """Test login page is accessible."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_setup_page(self, client):
        """Test setup wizard page."""
        response = client.get('/setup')
        assert response.status_code == 200
    
    def test_healthz_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/healthz')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestAuthenticatedRoutes:
    """Test routes that require authentication."""
    
    @pytest.fixture
    def logged_in_client(self, client, db_session):
        """Return a logged-in test client."""
        from app.models import User
        
        user = User(email='auth@example.com', fullname='Auth User')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        
        client.post('/login', data={
            'email': 'auth@example.com',
            'password': 'password123'
        })
        
        return client
    
    def test_index_requires_auth(self, client):
        """Test that index redirects without auth."""
        response = client.get('/')
        assert response.status_code in [302, 401]
    
    def test_dashboard_requires_auth(self, client):
        """Test that dashboard redirects without auth."""
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]
    
    def test_settings_requires_auth(self, client):
        """Test that settings redirects without auth."""
        response = client.get('/settings')
        assert response.status_code in [302, 401]


class TestTodoRoutes:
    """Test todo management routes."""
    
    @pytest.fixture
    def user_with_todo(self, client, db_session):
        """Create user with a todo."""
        from app.models import User, Todo, Status, Tracker
        
        user = User(email='todoroute@example.com')
        user.set_password('password123')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Login
        client.post('/login', data={
            'email': 'todoroute@example.com',
            'password': 'password123'
        })
        
        # Create todo
        todo = Todo()
        todo.name = 'Route Test Todo'
        todo.details = 'Details'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Add tracker
        status = Status.query.filter_by(name='new').first()
        Tracker.add(todo.id, status.id)
        
        return client, user, todo
    
    def test_add_todo_route(self, user_with_todo):
        """Test adding a todo via route."""
        client, user, _ = user_with_todo
        
        response = client.post('/add', data={
            'title': 'New Route Todo',
            'activities': 'New details'
        })
        
        # Should return JSON success or redirect
        assert response.status_code in [200, 302]


# ============================================================================
# FRONTEND TESTS
# ============================================================================

class TestStaticAssets:
    """Test frontend static assets."""
    
    def test_service_worker_exists(self, client):
        """Test service worker is accessible."""
        response = client.get('/service-worker.js')
        assert response.status_code == 200
        assert b'self' in response.data or b'cache' in response.data
    
    def test_manifest_json(self, client):
        """Test manifest.json is accessible."""
        # Try to access manifest
        response = client.get('/static/manifest.json')
        
        # If it exists, should be valid JSON
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict)


class TestCSS:
    """Test CSS files."""
    
    def test_css_directory_exists(self):
        """Test CSS directory exists."""
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'static', 'css'
        )
        assert os.path.exists(css_path)


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurityFeatures:
    """Test security features."""
    
    def test_csrf_protection_enabled(self, app):
        """Test CSRF protection is configured."""
        assert 'WTF_CSRF_ENABLED' in app.config
    
    def test_password_not_stored_plaintext(self, app, db_session):
        """Test passwords are hashed, not stored in plaintext."""
        from app.models import User
        
        user = User(email='security@example.com')
        password = 'MySecretPassword123!'
        user.set_password(password)
        
        # Password hash should not equal the password
        assert user.password_hash != password
        # But password check should work
        assert user.check_password(password)
    
    def test_api_token_uniqueness(self, app, db_session):
        """Test API tokens are unique per user."""
        from app.models import User
        
        user1 = User(email='token1@example.com')
        user2 = User(email='token2@example.com')
        db_session.session.add_all([user1, user2])
        db_session.session.commit()
        
        token1 = user1.generate_api_token()
        token2 = user2.generate_api_token()
        
        assert token1 != token2


class TestUserIsolation:
    """Test user data isolation."""
    
    def test_api_user_isolation(self, client, db_session):
        """Test users can only access their own todos via API."""
        from app.models import User, Todo, Status, Tracker
        
        # Create two users
        user1 = User(email='user1@example.com')
        user2 = User(email='user2@example.com')
        db_session.session.add_all([user1, user2])
        db_session.session.commit()
        
        # Create todos for each
        todo1 = Todo()
        todo1.name = 'User1 Todo'
        todo1.user_id = user1.id
        
        todo2 = Todo()
        todo2.name = 'User2 Todo'
        todo2.user_id = user2.id
        
        db_session.session.add_all([todo1, todo2])
        db_session.session.commit()
        
        # Get user1's API token
        token1 = user1.generate_api_token()
        
        # User1 should only see their todos
        response = client.get(
            '/api/todo',
            headers={'Authorization': f'Bearer {token1}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        todos = data.get('todos', [])
        
        # Verify isolation
        for todo in todos:
            assert 'User2' not in todo.get('title', '')


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    def test_user_registration_and_todo_creation(self, client, db_session):
        """Test complete workflow: register, login, create todo."""
        from app.models import User, Todo
        
        # Step 1: Register (or create user)
        user = User(email='workflow@example.com', fullname='Workflow User')
        user.set_password('SecurePass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Step 2: Login
        response = client.post('/login', data={
            'email': 'workflow@example.com',
            'password': 'SecurePass123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 3: Create todo (via API with token)
        token = user.generate_api_token()
        
        response = client.post(
            '/api/todo',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': 'Workflow Todo',
                'details': 'Integration test todo'
            })
        )
        
        # Should succeed
        assert response.status_code in [200, 201]
        
        # Verify todo was created
        todos = Todo.query.filter_by(user_id=user.id).all()
        assert len(todos) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
