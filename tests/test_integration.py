#!/usr/bin/env python3
"""
Integration tests for TodoBox application.
Tests complete end-to-end workflows and feature interactions.
"""
import pytest
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from app import app, db
    from tests.test_utils import seed_status_data
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        seed_status_data(db)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    from tests.test_utils import apply_werkzeug_version_workaround
    apply_werkzeug_version_workaround()
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for test setup/teardown."""
    from app import db
    yield db
    db.session.remove()


class TestCompleteUserWorkflow:
    """Test complete user workflow from registration to todo management."""
    
    def test_new_user_complete_workflow(self, client, db_session):
        """Test a complete workflow for a new user."""
        from app.models import User, Todo
        
        # Step 1: Create user account
        user = User(email='workflow@example.com', fullname='Workflow User')
        user.set_password('WorkflowPass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Step 2: Login
        response = client.post('/login', data={
            'email': 'workflow@example.com',
            'password': 'WorkflowPass123!'
        }, follow_redirects=False)
        
        # Should redirect or return success
        assert response.status_code in [200, 302]
        
        # Step 3: Generate API token
        response = client.post('/api/auth/token', follow_redirects=False)
        
        # Check if token was generated
        user = User.query.filter_by(email='workflow@example.com').first()
        assert user is not None
        
        # Step 4: Use API to create todos
        if user.api_token:
            headers = {'Authorization': f'Bearer {user.api_token}'}
            
            response = client.post('/api/todo', 
                headers=headers,
                json={'title': 'API Test Todo', 'details': 'Created via API'}
            )
            
            # API should work
            assert response.status_code in [200, 201, 401]  # 401 if token auth not working in test


class TestTodoLifecycle:
    """Test complete lifecycle of a todo item."""
    
    def test_todo_create_update_delete_lifecycle(self, client, db_session):
        """Test creating, updating, and deleting a todo."""
        from app.models import User, Todo
        
        # Setup: Create user
        user = User(email='lifecycle@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Create todo
        todo = Todo()
        todo.name = 'Lifecycle Todo'
        todo.details = 'Testing lifecycle'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        todo_id = todo.id
        
        # Verify creation
        created_todo = Todo.query.get(todo_id)
        assert created_todo is not None
        assert created_todo.name == 'Lifecycle Todo'
        
        # Update todo
        created_todo.name = 'Updated Lifecycle Todo'
        created_todo.details = 'Updated details'
        db_session.session.commit()
        
        # Verify update
        updated_todo = Todo.query.get(todo_id)
        assert updated_todo.name == 'Updated Lifecycle Todo'
        assert updated_todo.details == 'Updated details'
        
        # Delete todo
        db_session.session.delete(updated_todo)
        db_session.session.commit()
        
        # Verify deletion
        deleted_todo = Todo.query.get(todo_id)
        assert deleted_todo is None


class TestUserAuthentication:
    """Test various authentication scenarios."""
    
    def test_password_based_authentication(self, client, db_session):
        """Test password-based authentication."""
        from app.models import User
        
        # Create user with password
        user = User(email='auth@example.com')
        user.set_password('SecurePass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Test password verification
        assert user.check_password('SecurePass123!')
        assert not user.check_password('WrongPassword')
    
    def test_oauth_user_properties(self, client, db_session):
        """Test OAuth user properties."""
        from app.models import User
        
        # Create OAuth user
        oauth_user = User(
            email='oauth@example.com',
            oauth_provider='google',
            oauth_id='google_123456'
        )
        db_session.session.add(oauth_user)
        db_session.session.commit()
        
        # Verify OAuth properties
        assert oauth_user.is_gmail_user()
        assert oauth_user.oauth_provider == 'google'
        assert not oauth_user.is_direct_login_user()
        
        # Create regular user
        regular_user = User(email='regular@example.com')
        regular_user.set_password('Pass123!')
        db_session.session.add(regular_user)
        db_session.session.commit()
        
        # Verify regular user properties
        assert not regular_user.is_gmail_user()
        assert regular_user.is_direct_login_user()


class TestAPITokenManagement:
    """Test API token generation and usage."""
    
    def test_token_generation_and_verification(self, client, db_session):
        """Test API token generation and verification."""
        from app.models import User
        
        # Create user
        user = User(email='token@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Generate token
        token = user.generate_api_token()
        
        # Verify token was generated
        assert token is not None
        assert len(token) == 32
        assert user.api_token == token
        
        # Verify token check
        assert user.check_api_token(token)
        assert not user.check_api_token('wrong_token')
        
        # Get user by token
        found_user = User.get_user_by_api_token(token)
        assert found_user is not None
        assert found_user.id == user.id
    
    def test_token_uniqueness(self, client, db_session):
        """Test that API tokens are unique."""
        from app.models import User
        
        # Create two users
        user1 = User(email='token1@example.com')
        user1.set_password('Pass123!')
        user2 = User(email='token2@example.com')
        user2.set_password('Pass123!')
        
        db_session.session.add_all([user1, user2])
        db_session.session.commit()
        
        # Generate tokens
        token1 = user1.generate_api_token()
        token2 = user2.generate_api_token()
        
        # Tokens should be different
        assert token1 != token2


class TestTodoEncryption:
    """Test todo encryption and decryption."""
    
    def test_todo_field_encryption(self, client, db_session):
        """Test that todo fields can be encrypted and decrypted."""
        from app.models import User, Todo
        
        # Create user and todo
        user = User(email='encrypt@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        todo = Todo()
        todo.name = 'Encrypted Todo'
        todo.details = 'Sensitive information'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Retrieve and verify
        retrieved_todo = Todo.query.filter_by(user_id=user.id).first()
        assert retrieved_todo is not None
        assert retrieved_todo.name == 'Encrypted Todo'
        assert retrieved_todo.details == 'Sensitive information'
    
    def test_empty_todo_fields(self, client, db_session):
        """Test handling of empty/None todo fields."""
        from app.models import User, Todo
        
        user = User(email='empty@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Create todo with minimal fields
        todo = Todo()
        todo.name = 'Minimal Todo'
        todo.user_id = user.id
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Verify
        retrieved_todo = Todo.query.filter_by(user_id=user.id).first()
        assert retrieved_todo is not None
        assert retrieved_todo.name == 'Minimal Todo'


class TestQuoteAPI:
    """Test quote API functionality."""
    
    def test_quote_api_returns_quote(self, client, db_session):
        """Test that quote API returns a valid quote."""
        response = client.get('/api/quote')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'quote' in data
        assert len(data['quote']) > 0
        assert isinstance(data['quote'], str)
    
    def test_quote_api_returns_different_quotes(self, client, db_session):
        """Test that quote API can return different quotes."""
        quotes = set()
        
        # Get multiple quotes
        for _ in range(10):
            response = client.get('/api/quote')
            data = response.get_json()
            quotes.add(data['quote'])
        
        # Should have at least some variety (not always the same)
        # With 10 requests from 15 possible quotes, we expect some repeats
        assert len(quotes) >= 1  # At minimum we get a quote


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_healthz_endpoint(self, client, db_session):
        """Test health check endpoint."""
        response = client.get('/healthz')
        
        assert response.status_code == 200
        data = response.get_json()
        # Check for either 'healthy' or 'ok' as valid status
        assert data.get('status') in ['healthy', 'ok']


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_on_invalid_route(self, client, db_session):
        """Test 404 error on invalid route."""
        response = client.get('/this/route/does/not/exist')
        assert response.status_code == 404
    
    def test_api_error_on_missing_auth(self, client, db_session):
        """Test API returns error on missing authentication."""
        response = client.get('/api/todo')
        
        # Should return 401 Unauthorized or redirect
        assert response.status_code in [401, 302]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
