"""
Tests for user_id filtering to ensure users can only access their own todos.
"""
import pytest
import os
import sys
from datetime import datetime

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
    
    with app.app_context():
        db.create_all()
        
        # Seed required data
        from app.models import Status
        
        # Add status records manually (Status.__init__ only accepts name)
        if Status.query.count() == 0:
            status_new = Status(name='new')
            status_new.id = 5
            status_done = Status(name='done')
            status_done.id = 6
            status_failed = Status(name='failed')
            status_failed.id = 7
            status_reassign = Status(name='re-assign')
            status_reassign.id = 8
            db.session.add_all([status_new, status_done, status_failed, status_reassign])
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


def create_test_users(db):
    """Create two test users for testing isolation."""
    from app.models import User
    
    user1 = User(username='user1', email='user1@test.com')
    user1.set_password('password1')
    
    user2 = User(username='user2', email='user2@test.com')
    user2.set_password('password2')
    
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    
    return user1, user2


def create_todo_for_user(db, user, name='Test Todo'):
    """Create a todo for a specific user."""
    from app.models import Todo, Tracker
    
    todo = Todo(name=name, details='Test details', user_id=user.id)
    db.session.add(todo)
    db.session.commit()
    
    # Add tracker entry
    Tracker.add(todo.id, 5)  # Status 5 = new
    
    return todo


def login_user(client, username, password):
    """Login a user and return the response."""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


class TestUserIsolation:
    """Test that users can only access their own todos."""
    
    def test_user_cannot_delete_others_todo(self, app, client):
        """Test that a user cannot delete another user's todo."""
        from app import db
        from app.models import Todo
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'User1 Todo')
            todo_id = todo.id
            
            # Login as user2
            login_user(client, 'user2', 'password2')
            
            # Try to delete user1's todo as user2
            response = client.post(f'/{todo_id}/delete', follow_redirects=False)
            
            # Should return 404 or redirect (not delete the todo)
            assert response.status_code in [404, 302]
            
            # Verify todo still exists
            todo_check = Todo.query.get(todo_id)
            assert todo_check is not None
    
    def test_user_cannot_get_others_todo(self, app, client):
        """Test that a user cannot retrieve another user's todo."""
        from app import db
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'User1 Private Todo')
            todo_id = todo.id
            
            # Login as user2
            login_user(client, 'user2', 'password2')
            
            # Try to get user1's todo as user2
            response = client.post(f'/{todo_id}/todo')
            
            # Should return 404
            assert response.status_code == 404
            
            # Check response content
            import json
            data = json.loads(response.data)
            assert data['status'] == 'Error'
    
    def test_user_cannot_mark_others_todo_done(self, app, client):
        """Test that a user cannot mark another user's todo as done."""
        from app import db
        from app.models import Tracker
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'User1 Todo')
            todo_id = todo.id
            
            # Get initial tracker count
            initial_tracker_count = Tracker.query.filter_by(todo_id=todo_id).count()
            
            # Login as user2
            login_user(client, 'user2', 'password2')
            
            # Try to mark user1's todo as done
            response = client.post(f'/today/{todo_id}/done')
            
            # Should return 404
            assert response.status_code == 404
            
            # Verify no new tracker was added
            final_tracker_count = Tracker.query.filter_by(todo_id=todo_id).count()
            assert final_tracker_count == initial_tracker_count
    
    def test_user_cannot_update_others_todo(self, app, client):
        """Test that a user cannot update another user's todo."""
        from app import db
        from app.models import Todo
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'Original Title')
            todo_id = todo.id
            original_title = todo.name
            
            # Login as user2
            login_user(client, 'user2', 'password2')
            
            # Try to update user1's todo as user2
            response = client.post('/add', data={
                'todo_id': todo_id,
                'title': 'Hacked Title',
                'activities': 'Hacked content'
            })
            
            # Check response indicates failure
            import json
            data = json.loads(response.data)
            assert data['status'] == 'failed'
            
            # Verify todo was not modified
            todo_check = Todo.query.get(todo_id)
            assert todo_check.name == original_title
    
    def test_user_can_access_own_todo(self, app, client):
        """Test that a user can access their own todo."""
        from app import db
        
        with app.app_context():
            user1, _ = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'My Own Todo')
            todo_id = todo.id
            
            # Login as user1
            login_user(client, 'user1', 'password1')
            
            # Get own todo
            response = client.post(f'/{todo_id}/todo')
            
            # Should succeed
            assert response.status_code == 200
            
            import json
            data = json.loads(response.data)
            assert data['status'] == 'Success'
            assert data['title'] == 'My Own Todo'
    
    def test_user_can_delete_own_todo(self, app, client):
        """Test that a user can delete their own todo."""
        from app import db
        from app.models import Todo
        
        with app.app_context():
            user1, _ = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'Delete Me')
            todo_id = todo.id
            
            # Login as user1
            login_user(client, 'user1', 'password1')
            
            # Delete own todo
            response = client.post(f'/{todo_id}/delete', follow_redirects=False)
            
            # Should redirect (successful delete)
            assert response.status_code == 302
            
            # Verify todo was deleted
            todo_check = Todo.query.get(todo_id)
            assert todo_check is None
    
    def test_user_can_mark_own_todo_done(self, app, client):
        """Test that a user can mark their own todo as done."""
        from app import db
        
        with app.app_context():
            user1, _ = create_test_users(db)
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'Complete Me')
            todo_id = todo.id
            
            # Login as user1
            login_user(client, 'user1', 'password1')
            
            # Mark own todo as done
            response = client.post(f'/today/{todo_id}/done')
            
            # Should succeed
            assert response.status_code == 200
            
            import json
            data = json.loads(response.data)
            assert data['status'] == 'Success'


class TestAPIUserIsolation:
    """Test that API endpoints enforce user isolation."""
    
    def test_api_get_todos_returns_only_own_todos(self, app, client):
        """Test that API returns only the authenticated user's todos."""
        from app import db
        from app.models import User
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Generate API tokens
            token1 = user1.generate_api_token()
            token2 = user2.generate_api_token()
            
            # Create todos for both users
            create_todo_for_user(db, user1, 'User1 API Todo')
            create_todo_for_user(db, user2, 'User2 API Todo')
            
            # Get todos as user1
            response = client.get('/api/todo', headers={
                'Authorization': f'Bearer {token1}'
            })
            
            assert response.status_code == 200
            
            import json
            data = json.loads(response.data)
            
            # Should only see user1's todo
            assert len(data['todos']) == 1
            assert data['todos'][0]['title'] == 'User1 API Todo'
    
    def test_api_cannot_update_others_todo(self, app, client):
        """Test that API cannot update another user's todo."""
        from app import db
        from app.models import Todo
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Generate API token for user2
            token2 = user2.generate_api_token()
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'User1 Protected Todo')
            todo_id = todo.id
            
            # Try to update user1's todo using user2's token
            import json
            response = client.put(
                f'/api/todo/{todo_id}',
                headers={
                    'Authorization': f'Bearer {token2}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({'title': 'Hacked via API'})
            )
            
            # Should return 404
            assert response.status_code == 404
            
            # Verify todo was not modified
            todo_check = Todo.query.get(todo_id)
            assert todo_check.name == 'User1 Protected Todo'
    
    def test_api_cannot_delete_others_todo(self, app, client):
        """Test that API cannot delete another user's todo."""
        from app import db
        from app.models import Todo
        
        with app.app_context():
            user1, user2 = create_test_users(db)
            
            # Generate API token for user2
            token2 = user2.generate_api_token()
            
            # Create a todo for user1
            todo = create_todo_for_user(db, user1, 'User1 Protected Todo')
            todo_id = todo.id
            
            # Try to delete user1's todo using user2's token
            response = client.delete(
                f'/api/todo/{todo_id}',
                headers={'Authorization': f'Bearer {token2}'}
            )
            
            # Should return 404
            assert response.status_code == 404
            
            # Verify todo still exists
            todo_check = Todo.query.get(todo_id)
            assert todo_check is not None
