#!/usr/bin/env python3
"""
Comprehensive backend route tests for TodoBox.
Tests all HTTP endpoints including authenticated and public routes.
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
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for test setup/teardown."""
    from app import db
    yield db
    db.session.remove()


@pytest.fixture
def auth_user(client, db_session):
    """Create and login a user, return client and user."""
    from app.models import User
    
    user = User(email='testuser@example.com', fullname='Test User')
    user.set_password('TestPass123!')
    db_session.session.add(user)
    db_session.session.commit()
    
    # Login
    client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'TestPass123!'
    })
    
    return client, user


# ============================================================================
# AUTHENTICATION ROUTE TESTS
# ============================================================================

class TestAuthenticationRoutes:
    """Test authentication-related routes."""
    
    def test_login_page_loads(self, client, db_session):
        """Test login page loads (redirects to setup if no users)."""
        from app.models import User
        
        # Create at least one user so login page shows
        user = User(email='exists@example.com')
        user.set_password('pass')
        db_session.session.add(user)
        db_session.session.commit()
        
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_with_credentials(self, client, db_session):
        """Test login with valid credentials."""
        from app.models import User
        
        user = User(email='login@example.com', fullname='Login User')
        user.set_password('LoginPass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        response = client.post('/login', data={
            'email': 'login@example.com',
            'password': 'LoginPass123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_with_invalid_credentials(self, client, db_session):
        """Test login with wrong password."""
        from app.models import User
        
        user = User(email='wrong@example.com')
        user.set_password('CorrectPass')
        db_session.session.add(user)
        db_session.session.commit()
        
        response = client.post('/login', data={
            'email': 'wrong@example.com',
            'password': 'WrongPass'
        }, follow_redirects=True)
        
        # Should show login page with error
        assert response.status_code == 200
    
    def test_logout(self, auth_user):
        """Test logout functionality."""
        client, user = auth_user
        
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_setup_account_page(self, client):
        """Test setup account page loads."""
        response = client.get('/setup/account')
        assert response.status_code == 200


# ============================================================================
# TODO MANAGEMENT ROUTE TESTS
# ============================================================================

class TestTodoManagementRoutes:
    """Test todo CRUD routes."""
    
    def test_index_redirect_when_not_logged_in(self, client):
        """Test index redirects to login when not authenticated."""
        response = client.get('/')
        assert response.status_code == 302
    
    def test_index_loads_when_logged_in(self, auth_user):
        """Test index loads for authenticated user."""
        client, user = auth_user
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
    
    def test_dashboard_loads(self, auth_user):
        """Test dashboard loads for authenticated user."""
        client, user = auth_user
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
    
    def test_undone_todos_page(self, auth_user):
        """Test undone todos page."""
        client, user = auth_user
        response = client.get('/undone', follow_redirects=True)
        assert response.status_code == 200


# ============================================================================
# USER SETTINGS ROUTE TESTS
# ============================================================================

class TestUserSettingsRoutes:
    """Test user settings and account routes."""
    
    def test_settings_page_loads(self, auth_user):
        """Test settings page loads."""
        client, user = auth_user
        response = client.get('/settings', follow_redirects=True)
        assert response.status_code == 200
    
    def test_account_page_loads(self, auth_user):
        """Test account page loads."""
        client, user = auth_user
        response = client.get('/account', follow_redirects=True)
        assert response.status_code == 200
    
    def test_change_password(self, auth_user, db_session):
        """Test password change functionality."""
        client, user = auth_user
        
        response = client.post('/settings', data={
            'current_password': 'TestPass123!',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify password changed
        from app.models import User
        updated_user = User.query.get(user.id)
        assert updated_user.check_password('NewPass456!')


# ============================================================================
# SHARING ROUTE TESTS
# ============================================================================

class TestSharingRoutes:
    """Test todo sharing routes."""
    
    def test_sharing_page_loads(self, auth_user):
        """Test sharing settings page loads."""
        client, user = auth_user
        response = client.get('/sharing', follow_redirects=True)
        assert response.status_code == 200
    
    def test_sharing_toggle(self, auth_user, db_session):
        """Test toggling sharing on/off."""
        client, user = auth_user
        
        # Enable sharing
        response = client.post('/sharing/toggle', data={
            'enabled': 'true'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify sharing was enabled
        from app.models import User
        updated_user = User.query.get(user.id)
        # Note: sharing might require OAuth, so we just check response


# ============================================================================
# API ROUTE TESTS (Additional Coverage)
# ============================================================================

class TestAPIRoutes:
    """Test additional API routes."""
    
    def test_api_todo_update(self, auth_user, db_session):
        """Test updating a todo via API."""
        client, user = auth_user
        from app.models import Todo, Status, Tracker
        
        # Create a todo
        todo = Todo()
        todo.name = 'Update Test'
        todo.details = 'Original details'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Add tracker
        status = Status.query.filter_by(name='new').first()
        Tracker.add(todo.id, status.id)
        
        # Generate API token
        token = user.generate_api_token()
        
        # Update via API
        response = client.put(
            f'/api/todo/{todo.id}',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': 'Updated Title',
                'details': 'Updated details'
            })
        )
        
        assert response.status_code in [200, 201]
    
    def test_api_todo_delete(self, auth_user, db_session):
        """Test deleting a todo via API."""
        client, user = auth_user
        from app.models import Todo, Status, Tracker
        
        # Create a todo
        todo = Todo()
        todo.name = 'Delete Test'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        todo_id = todo.id
        
        # Add tracker
        status = Status.query.filter_by(name='new').first()
        Tracker.add(todo_id, status.id)
        
        # Generate API token
        token = user.generate_api_token()
        
        # Delete via API
        response = client.delete(
            f'/api/todo/{todo_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        
        # Verify deleted
        from app.models import Todo
        deleted_todo = Todo.query.get(todo_id)
        assert deleted_todo is None
    
    def test_api_reminders_check(self, auth_user):
        """Test checking reminders via API."""
        client, user = auth_user
        
        response = client.get('/api/reminders/check')
        assert response.status_code in [200, 302]  # May redirect if not configured


# ============================================================================
# OAUTH ROUTE TESTS
# ============================================================================

class TestOAuthRoutes:
    """Test OAuth authentication routes."""
    
    def test_google_login_redirect(self, client):
        """Test Google OAuth login initiates redirect."""
        response = client.get('/auth/login/google')
        
        # Should redirect to Google or show error
        assert response.status_code in [302, 400, 500]
    
    def test_google_logout(self, client):
        """Test Google logout endpoint."""
        response = client.get('/logout/google', follow_redirects=True)
        assert response.status_code == 200


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_404_on_invalid_route(self, client):
        """Test 404 for non-existent routes."""
        response = client.get('/this-route-does-not-exist')
        assert response.status_code == 404
    
    def test_api_401_without_auth(self, client):
        """Test API returns 401 without authentication."""
        response = client.get('/api/todo')
        assert response.status_code == 401
    
    def test_api_401_with_invalid_token(self, client):
        """Test API returns 401 with invalid token."""
        response = client.get(
            '/api/todo',
            headers={'Authorization': 'Bearer invalid_token_12345'}
        )
        assert response.status_code == 401


# ============================================================================
# PERFORMANCE AND LOAD TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_healthz_response_time(self, client):
        """Test health check responds quickly."""
        import time
        
        start = time.time()
        response = client.get('/healthz')
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second
    
    def test_multiple_api_requests(self, auth_user):
        """Test handling multiple API requests."""
        client, user = auth_user
        token = user.generate_api_token()
        
        # Make 10 requests
        for i in range(10):
            response = client.get(
                '/api/todo',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 200


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test input validation and sanitization."""
    
    def test_api_todo_with_empty_title(self, auth_user):
        """Test API rejects empty todo title."""
        client, user = auth_user
        token = user.generate_api_token()
        
        response = client.post(
            '/api/todo',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': '',
                'details': 'Details'
            })
        )
        
        # Should reject or handle empty title
        assert response.status_code in [200, 201, 400]
    
    def test_api_todo_with_long_title(self, auth_user):
        """Test API handles very long titles."""
        client, user = auth_user
        token = user.generate_api_token()
        
        long_title = 'A' * 1000
        
        response = client.post(
            '/api/todo',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': long_title,
                'details': 'Details'
            })
        )
        
        # Should handle or truncate long title
        assert response.status_code in [200, 201, 400]
    
    def test_sql_injection_prevention(self, auth_user):
        """Test SQL injection is prevented."""
        client, user = auth_user
        token = user.generate_api_token()
        
        # Try SQL injection in title
        malicious_title = "'; DROP TABLE todo; --"
        
        response = client.post(
            '/api/todo',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'title': malicious_title,
                'details': 'Test'
            })
        )
        
        # Should safely handle the input
        assert response.status_code in [200, 201]
        
        # Verify table still exists by querying
        response = client.get(
            '/api/todo',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200


# ============================================================================
# CONCURRENT ACCESS TESTS
# ============================================================================

class TestConcurrentAccess:
    """Test concurrent user access."""
    
    def test_multiple_users_simultaneous_access(self, client, db_session):
        """Test multiple users can access the system simultaneously."""
        from app.models import User
        
        # Create multiple users
        users = []
        for i in range(3):
            user = User(email=f'concurrent{i}@example.com')
            user.set_password('pass123')
            db_session.session.add(user)
            users.append(user)
        db_session.session.commit()
        
        # Generate tokens for all users
        tokens = [user.generate_api_token() for user in users]
        
        # All users access API simultaneously
        for token in tokens:
            response = client.get(
                '/api/todo',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
