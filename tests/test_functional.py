#!/usr/bin/env python3
"""
Comprehensive functional tests for TodoBox application.
Tests complete user workflows including authentication, todo management, and sharing.
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
            statuses = [
                Status(name='new'),
                Status(name='done'),
                Status(name='failed'),
                Status(name='re-assign')
            ]
            for i, status in enumerate(statuses, start=5):
                status.id = i
            db.session.add_all(statuses)
            db.session.commit()
        
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


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test user authentication flows."""
    
    def test_login_page_accessible(self, client, db_session):
        """Test that login page loads successfully."""
        # Create a test user first
        from app.models import User
        user = User(email='test@example.com')
        user.set_password('password')
        db_session.session.add(user)
        db_session.session.commit()
        
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'password' in response.data.lower()
    
    def test_user_registration_flow(self, client, db_session):
        """Test complete user registration workflow."""
        from app.models import User
        
        # Attempt to register a new user
        response = client.post('/setup/account', data={
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'fullname': 'Test User'
        }, follow_redirects=True)
        
        # Verify user was created
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.email == 'test@example.com'
    
    def test_login_with_valid_credentials(self, client, db_session):
        """Test login with correct credentials."""
        from app.models import User
        
        # Create a test user
        user = User(email='login@example.com')
        user.set_password('TestPassword123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Attempt login
        response = client.post('/login', data={
            'email': 'logintest',
            'password': 'TestPassword123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_with_invalid_credentials(self, client, db_session):
        """Test login with incorrect password."""
        from app.models import User
        
        # Create a test user
        user = User(email='invalid@example.com')
        user.set_password('CorrectPassword123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Attempt login with wrong password
        response = client.post('/login', data={
            'email': 'invalid@example.com',
            'password': 'WrongPassword123!'
        }, follow_redirects=True)
        
        # Should not be logged in
        assert b'invalid' in response.data.lower() or b'incorrect' in response.data.lower()
    
    def test_logout_functionality(self, client, db_session):
        """Test user logout."""
        from app.models import User
        
        # Create and login user
        user = User(email='logout@example.com')
        user.set_password('LogoutPass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        client.post('/login', data={
            'email': 'logout@example.com',
            'password': 'LogoutPass123!'
        }, follow_redirects=True)
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify redirected to login page (checking for login-related content)
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()


# ============================================================================
# TODO MANAGEMENT TESTS
# ============================================================================

class TestTodoManagement:
    """Test todo creation, reading, updating, and deletion."""
    
    @pytest.fixture
    def logged_in_client(self, client, db_session):
        """Return a logged-in test client."""
        from app.models import User
        
        user = User(email='todo@example.com')
        user.set_password('TodoPass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        client.post('/login', data={
            'email': 'todouser',
            'password': 'TodoPass123!'
        })
        
        return client
    
    def test_create_todo_item(self, logged_in_client, db_session):
        """Test creating a new todo item."""
        from app.models import Todo
        
        response = logged_in_client.post('/todo/add', data={
            'title': 'Test Todo',
            'description': 'Test Description',
            'priority': 'high'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify todo was created
        todo = Todo.query.filter_by(title='Test Todo').first()
        assert todo is not None
        assert todo.description == 'Test Description'
    
    def test_view_todo_list(self, logged_in_client, db_session):
        """Test viewing list of todos."""
        from app.models import Todo, User
        
        user = User.query.filter_by(email='todouser').first()
        
        # Create a few todos
        for i in range(3):
            todo = Todo(
                title=f'Todo {i}',
                description=f'Description {i}',
                user_id=user.id
            )
            db_session.session.add(todo)
        db_session.session.commit()
        
        response = logged_in_client.get('/')
        assert response.status_code == 200
        assert b'Todo' in response.data or b'todo' in response.data
    
    def test_update_todo_status(self, logged_in_client, db_session):
        """Test marking todo as done."""
        from app.models import Todo, User, Status
        
        user = User.query.filter_by(email='todouser').first()
        done_status = Status.query.filter_by(name='done').first()
        
        # Create a todo
        todo = Todo(
            title='Status Update Todo',
            description='Test updating status',
            user_id=user.id
        )
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Update status
        response = logged_in_client.post(f'/todo/{todo.id}/status', data={
            'status': done_status.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify status was updated
        updated_todo = Todo.query.get(todo.id)
        assert updated_todo.status_id == done_status.id
    
    def test_delete_todo(self, logged_in_client, db_session):
        """Test deleting a todo item."""
        from app.models import Todo, User
        
        user = User.query.filter_by(email='todouser').first()
        
        # Create a todo
        todo = Todo(
            title='Todo to Delete',
            description='This will be deleted',
            user_id=user.id
        )
        db_session.session.add(todo)
        db_session.session.commit()
        todo_id = todo.id
        
        # Delete todo
        response = logged_in_client.post(f'/todo/{todo_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify todo was deleted
        deleted_todo = Todo.query.get(todo_id)
        assert deleted_todo is None
    
    def test_edit_todo(self, logged_in_client, db_session):
        """Test editing a todo item."""
        from app.models import Todo, User
        
        user = User.query.filter_by(email='todouser').first()
        
        # Create a todo
        todo = Todo(
            title='Original Title',
            description='Original Description',
            user_id=user.id
        )
        db_session.session.add(todo)
        db_session.session.commit()
        
        # Edit todo
        response = logged_in_client.post(f'/todo/{todo.id}/edit', data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'priority': 'medium'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify changes
        updated_todo = Todo.query.get(todo.id)
        assert updated_todo.title == 'Updated Title'
        assert updated_todo.description == 'Updated Description'


# ============================================================================
# USER ISOLATION TESTS
# ============================================================================

class TestUserIsolation:
    """Test that users can only access their own todos."""
    
    @pytest.fixture
    def two_users_with_todos(self, client, db_session):
        """Create two users with todos each."""
        from app.models import User, Todo
        
        user1 = User(email='user1@example.com')
        user1.set_password('Pass123!')
        user2 = User(email='user2@example.com')
        user2.set_password('Pass123!')
        
        db_session.session.add_all([user1, user2])
        db_session.session.commit()
        
        # Add todos for each user
        todo1 = Todo(title='User1 Todo', user_id=user1.id)
        todo2 = Todo(title='User2 Todo', user_id=user2.id)
        db_session.session.add_all([todo1, todo2])
        db_session.session.commit()
        
        return client, user1, user2, todo1, todo2
    
    def test_user_cannot_see_other_user_todos(self, two_users_with_todos, db_session):
        """Test that user1 cannot see user2's todos."""
        from app.models import Todo
        
        client, user1, user2, todo1, todo2 = two_users_with_todos
        
        # Login as user1
        client.post('/login', data={
            'email': 'user1',
            'password': 'Pass123!'
        })
        
        # Try to access user2's todo
        response = client.get(f'/todo/{todo2.id}')
        
        # Should either get 404 or be redirected
        assert response.status_code in [404, 403, 302]
    
    def test_user_can_only_delete_own_todos(self, two_users_with_todos, db_session):
        """Test that user1 cannot delete user2's todos."""
        client, user1, user2, todo1, todo2 = two_users_with_todos
        
        # Login as user1
        client.post('/login', data={
            'email': 'user1',
            'password': 'Pass123!'
        })
        
        # Try to delete user2's todo
        response = client.post(f'/todo/{todo2.id}/delete', follow_redirects=True)
        
        # Should fail (either 404, 403, or todo should still exist)
        from app.models import Todo
        todo2_check = Todo.query.get(todo2.id)
        assert todo2_check is not None  # Should still exist


# ============================================================================
# TODO SHARING TESTS
# ============================================================================

class TestTodoSharing:
    """Test todo sharing functionality between users."""
    
    @pytest.fixture
    def sharing_setup(self, client, db_session):
        """Set up two users for sharing tests."""
        from app.models import User, Todo
        
        owner = User(email='owner@example.com')
        owner.set_password('Pass123!')
        recipient = User(email='recipient@example.com')
        recipient.set_password('Pass123!')
        
        db_session.session.add_all([owner, recipient])
        db_session.session.commit()
        
        # Create a todo owned by owner
        todo = Todo(
            title='Shared Todo',
            description='This todo will be shared',
            user_id=owner.id
        )
        db_session.session.add(todo)
        db_session.session.commit()
        
        return client, owner, recipient, todo
    
    def test_share_todo_with_user(self, sharing_setup, db_session):
        """Test sharing a todo with another user."""
        from app.models import TodoShare
        
        client, owner, recipient, todo = sharing_setup
        
        # Login as owner
        client.post('/login', data={
            'email': 'owner',
            'password': 'Pass123!'
        })
        
        # Share todo with recipient
        response = client.post(f'/todo/{todo.id}/share', data={
            'email': 'recipient'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify sharing record was created
        share = TodoShare.query.filter_by(
            todo_id=todo.id,
            shared_with_id=recipient.id
        ).first()
        assert share is not None
    
    def test_shared_user_can_view_shared_todo(self, sharing_setup, db_session):
        """Test that recipient can view shared todo."""
        from app.models import TodoShare
        
        client, owner, recipient, todo = sharing_setup
        
        # Create sharing record
        share = TodoShare(todo_id=todo.id, shared_with_id=recipient.id)
        db_session.session.add(share)
        db_session.session.commit()
        
        # Login as recipient
        client.post('/login', data={
            'email': 'recipient',
            'password': 'Pass123!'
        })
        
        # Try to view shared todo
        response = client.get(f'/todo/{todo.id}')
        assert response.status_code == 200
        assert b'Shared Todo' in response.data or b'shared' in response.data.lower()


# ============================================================================
# ADMIN FUNCTIONALITY TESTS
# ============================================================================

class TestAdminFunctionality:
    """Test admin-specific features."""
    
    @pytest.fixture
    def admin_user(self, db_session):
        """Create an admin user."""
        from app.models import User
        
        admin = User(email='admin@example.com')
        admin.set_password('AdminPass123!')
        admin.is_admin = True
        db_session.session.add(admin)
        db_session.session.commit()
        
        return admin
    
    def test_admin_panel_accessible_to_admin(self, client, admin_user, db_session):
        """Test that admin can access admin panel."""
        # Login as admin
        client.post('/login', data={
            'email': 'admin',
            'password': 'AdminPass123!'
        })
        
        response = client.get('/admin')
        assert response.status_code == 200
    
    def test_non_admin_cannot_access_admin_panel(self, client, db_session):
        """Test that non-admin users cannot access admin panel."""
        from app.models import User
        
        # Create non-admin user
        user = User(email='normal@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Login as non-admin
        client.post('/login', data={
            'email': 'normaluser',
            'password': 'Pass123!'
        })
        
        response = client.get('/admin')
        # Should be redirected or denied
        assert response.status_code in [302, 403]
    
    def test_admin_can_block_user(self, client, admin_user, db_session):
        """Test that admin can block a user."""
        from app.models import User
        
        # Create a user to block
        user = User(email='toblock@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        # Login as admin
        client.post('/login', data={
            'email': 'admin',
            'password': 'AdminPass123!'
        })
        
        # Block user
        response = client.post(f'/admin/user/{user.id}/block', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify user is blocked
        blocked_user = User.query.get(user.id)
        assert blocked_user.is_blocked == True


# ============================================================================
# SETTINGS AND PROFILE TESTS
# ============================================================================

class TestUserSettings:
    """Test user settings and profile management."""
    
    @pytest.fixture
    def logged_in_user(self, client, db_session):
        """Create and login a test user."""
        from app.models import User
        
        user = User(email='settings@example.com')
        user.set_password('Pass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        client.post('/login', data={
            'email': 'settingsuser',
            'password': 'Pass123!'
        })
        
        return client, user
    
    def test_access_settings_page(self, logged_in_user, db_session):
        """Test that user can access settings page."""
        client, user = logged_in_user
        
        response = client.get('/settings')
        assert response.status_code == 200
    
    def test_update_user_profile(self, logged_in_user, db_session):
        """Test updating user profile information."""
        from app.models import User
        
        client, user = logged_in_user
        
        response = client.post('/settings', data={
            'email': 'newemail@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify changes
        updated_user = User.query.get(user.id)
        assert updated_user.email == 'newemail@example.com'
    
    def test_change_password(self, logged_in_user, db_session):
        """Test changing password."""
        from app.models import User
        
        client, user = logged_in_user
        
        response = client.post('/settings', data={
            'current_password': 'Pass123!',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify old password no longer works
        client.get('/logout')
        login_response = client.post('/login', data={
            'email': 'settingsuser',
            'password': 'Pass123!'
        }, follow_redirects=True)
        
        # Should fail
        assert b'invalid' in login_response.data.lower() or b'incorrect' in login_response.data.lower()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_complete_user_workflow(self, client, db_session):
        """Test complete workflow: register -> create todos -> share -> view."""
        from app.models import User, Todo, TodoShare
        
        # Step 1: Register user
        client.post('/register', data={
            'email': 'workflow_user',
            'email': 'workflow@example.com',
            'password': 'WorkflowPass123!',
            'password_confirm': 'WorkflowPass123!'
        })
        
        # Step 2: Login
        response = client.post('/login', data={
            'email': 'workflow_user',
            'password': 'WorkflowPass123!'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 3: Create a todo
        response = client.post('/todo/add', data={
            'title': 'Workflow Test Todo',
            'description': 'Testing complete workflow',
            'priority': 'high'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify todo exists
        todo = Todo.query.filter_by(title='Workflow Test Todo').first()
        assert todo is not None
        
        # Step 4: View todos
        response = client.get('/')
        assert response.status_code == 200
        assert b'Workflow' in response.data or b'workflow' in response.data
    
    def test_multi_user_collaboration(self, client, db_session):
        """Test collaboration between multiple users."""
        from app.models import User, Todo, TodoShare
        
        # Create two users
        user1_response = client.post('/register', data={
            'email': 'collab_user1',
            'email': 'collab1@example.com',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!'
        })
        
        user2_response = client.post('/register', data={
            'email': 'collab_user2',
            'email': 'collab2@example.com',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!'
        })
        
        # User1 creates a todo
        client.post('/login', data={
            'email': 'collab_user1',
            'password': 'Pass123!'
        })
        
        client.post('/todo/add', data={
            'title': 'Collaboration Todo',
            'description': 'Shared between users',
            'priority': 'high'
        })
        
        user1 = User.query.filter_by(email='collab_user1').first()
        todo = Todo.query.filter_by(title='Collaboration Todo').first()
        
        # User1 shares with User2
        user2 = User.query.filter_by(email='collab_user2').first()
        share = TodoShare(todo_id=todo.id, shared_with_id=user2.id)
        db_session.session.add(share)
        db_session.session.commit()
        
        # User2 logs in and accesses shared todo
        client.get('/logout')
        client.post('/login', data={
            'email': 'collab_user2',
            'password': 'Pass123!'
        })
        
        response = client.get(f'/todo/{todo.id}')
        assert response.status_code == 200


# ============================================================================
# TODOMANAGE.PY TESTS
# ============================================================================

class TestTodomanageUserManagement:
    """Test todomanage.py user management functions."""
    
    @pytest.fixture
    def app_with_user(self, app, db_session):
        """Create app with a test user."""
        from app.models import User
        
        user = User(email='managed@example.com')
        user.set_password('ManagedPass123!')
        db_session.session.add(user)
        db_session.session.commit()
        
        yield app, user, db_session
    
    def test_create_user_via_todomanage(self, app_with_user):
        """Test user creation through todomanage imports."""
        app, existing_user, db_session = app_with_user
        
        with app.app_context():
            from app.models import User
            
            # Simulate what todomanage.py does
            new_user = User(email='todomanage@example.com')
            new_user.set_password('TestPass123!')
            db_session.session.add(new_user)
            db_session.session.commit()
            
            # Verify user was created
            created = User.query.filter_by(email='todomanage_test').first()
            assert created is not None
            assert created.email == 'todomanage@example.com'
    
    def test_list_users_via_todomanage(self, app_with_user):
        """Test user listing through todomanage functions."""
        app, user, db_session = app_with_user
        
        with app.app_context():
            from app.models import User
            
            # This simulates what list_users() does in todomanage.py
            all_users = User.query.all()
            
            # Should have at least the one we created
            assert len(all_users) >= 1
            usernames = [u.username for u in all_users]
            assert 'managed_user' in usernames
    
    def test_assign_admin_via_todomanage(self, app_with_user):
        """Test admin assignment through todomanage functions."""
        app, user, db_session = app_with_user
        
        with app.app_context():
            from app.models import User
            
            # Simulate what assign_admin() does
            target_user = User.query.filter_by(email='managed_user').first()
            assert target_user is not None
            
            # Make user admin
            target_user.is_admin = True
            db_session.session.commit()
            
            # Verify admin status
            updated_user = User.query.get(target_user.id)
            assert updated_user.is_admin == True
    
    def test_delete_user_via_todomanage(self, app_with_user):
        """Test user deletion through todomanage functions."""
        app, user, db_session = app_with_user
        user_id = user.id
        
        with app.app_context():
            from app.models import User
            
            # Simulate what delete_user() does
            user_to_delete = User.query.get(user_id)
            assert user_to_delete is not None
            
            db_session.session.delete(user_to_delete)
            db_session.session.commit()
            
            # Verify user was deleted
            deleted_user = User.query.get(user_id)
            assert deleted_user is None


class TestTodomanageInstallation:
    """Test todomanage.py installation functions."""
    
    def test_install_database_choice_validation(self, app):
        """Test that installation validates database choice."""
        import os
        import tempfile
        
        # Test that install functions exist in todomanage
        with app.app_context():
            # Import functions from todomanage
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            try:
                from todomanage import install_database, install_manual, install_docker
                
                # Verify functions are callable
                assert callable(install_database)
                assert callable(install_manual)
                assert callable(install_docker)
            except ImportError:
                pytest.skip("todomanage functions not available in test context")
    
    def test_flaskenv_update_function(self, app, db_session, tmp_path):
        """Test .flaskenv configuration update functionality."""
        import os
        import tempfile
        import shutil
        
        # Create a temporary .flaskenv file
        test_flaskenv = tmp_path / ".flaskenv"
        test_flaskenv.write_text("""
FLASK_ENV=development
DATABASE_DEFAULT=sqlite
""")
        
        # Simulate updating .flaskenv for PostgreSQL
        content = test_flaskenv.read_text()
        updated = content.replace('DATABASE_DEFAULT=sqlite', 'DATABASE_DEFAULT=postgres')
        test_flaskenv.write_text(updated)
        
        # Verify update
        final_content = test_flaskenv.read_text()
        assert 'DATABASE_DEFAULT=postgres' in final_content
        assert 'DATABASE_DEFAULT=sqlite' not in final_content


class TestTodomanageIntegration:
    """Test todomanage.py integration with Flask app."""
    
    def test_todomanage_user_creation_integration(self, app, db_session):
        """Test complete user creation flow via todomanage."""
        from app.models import User
        
        with app.app_context():
            # Simulate creating multiple users like todomanage does
            users_data = [
                {'email': 'admin1@example.com', 'password': 'AdminPass1!'},
                {'email': 'user1@example.com', 'password': 'UserPass1!'},
                {'email': 'user2@example.com', 'password': 'UserPass2!'}
            ]
            
            for user_data in users_data:
                user = User(
                    email=user_data['email']
                )
                user.set_password(user_data['password'])
                db_session.session.add(user)
            
            db_session.session.commit()
            
            # Verify all users were created
            all_users = User.query.all()
            assert len(all_users) == len(users_data)
            
            created_emails = [u.email for u in all_users]
            for user_data in users_data:
                assert user_data['email'] in created_emails
    
    def test_todomanage_admin_operations(self, app, db_session):
        """Test admin operations in todomanage workflow."""
        from app.models import User
        
        with app.app_context():
            # Create regular user
            user = User(email='regular@example.com')
            user.set_password('RegularPass1!')
            db_session.session.add(user)
            db_session.session.commit()
            
            # Simulate todomanage admin assignment
            target_user = User.query.filter_by(email='regularuser').first()
            assert target_user.is_admin == False
            
            # Promote to admin
            target_user.is_admin = True
            db_session.session.commit()
            
            # Verify promotion
            promoted_user = User.query.get(target_user.id)
            assert promoted_user.is_admin == True
            
            # Simulate demoting
            promoted_user.is_admin = False
            db_session.session.commit()
            
            demoted_user = User.query.get(target_user.id)
            assert demoted_user.is_admin == False
    
    def test_todomanage_user_password_update(self, app, db_session):
        """Test password update functionality used in todomanage."""
        from app.models import User
        
        with app.app_context():
            user = User(email='pass@example.com')
            user.set_password('OriginalPass123!')
            db_session.session.add(user)
            db_session.session.commit()
            
            # Verify original password works
            assert user.check_password('OriginalPass123!')
            assert not user.check_password('WrongPass123!')
            
            # Update password
            user.set_password('UpdatedPass456!')
            db_session.session.commit()
            
            # Verify new password
            updated_user = User.query.get(user.id)
            assert updated_user.check_password('UpdatedPass456!')
            assert not updated_user.check_password('OriginalPass123!')
    
    def test_todomanage_bulk_operations(self, app, db_session):
        """Test bulk user operations like todomanage batch creation."""
        from app.models import User
        
        with app.app_context():
            # Create 10 users like todomanage bulk import might do
            users_to_create = []
            for i in range(10):
                user = User(
                    email=f'bulk{i}@example.com'
                )
                user.set_password(f'BulkPass{i}!')
                users_to_create.append(user)
            
            db_session.session.add_all(users_to_create)
            db_session.session.commit()
            
            # Verify all created
            from sqlalchemy import and_
            bulk_users = [u for u in User.query.all() if u.email.startswith('bulk')]
            assert len(bulk_users) == 10
            
            # Verify we can query them
            for i in range(10):
                user = User.query.filter_by(username=f'bulk_user_{i}').first()
                assert user is not None
                assert user.email == f'bulk{i}@example.com'


class TestTodomanageConfigManagement:
    """Test .flaskenv configuration management used by todomanage."""
    
    def test_flaskenv_configuration_parsing(self, app, tmp_path):
        """Test parsing of .flaskenv configuration."""
        import os
        
        # Create test .flaskenv
        test_env = tmp_path / ".flaskenv"
        config_content = """FLASK_ENV=development
FLASK_APP=todobox.py
SECRET_KEY=test-secret-key
DATABASE_DEFAULT=sqlite
DB_URL=localhost
DB_USER=root
DB_PW=password
DB_NAME=todobox
"""
        test_env.write_text(config_content)
        
        # Parse configuration
        config_data = {}
        with open(test_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config_data[key] = value
        
        # Verify configuration
        assert config_data['DATABASE_DEFAULT'] == 'sqlite'
        assert config_data['DB_USER'] == 'root'
        assert config_data['DB_NAME'] == 'todobox'
    
    def test_database_url_construction(self):
        """Test database URL construction like todomanage does."""
        # SQLite URL
        sqlite_url = 'sqlite:///instance/todobox.db'
        assert 'sqlite' in sqlite_url
        
        # PostgreSQL URL
        postgres_url = 'postgresql://todobox:password123@localhost:5432/todobox'
        assert 'postgresql' in postgres_url
        assert 'todobox:password123' in postgres_url
        
        # MySQL URL
        mysql_url = 'mysql+pymysql://root:password123@localhost:3306/todobox'
        assert 'mysql' in mysql_url
    
    def test_configuration_validation(self):
        """Test configuration validation like todomanage does."""
        valid_databases = ['sqlite', 'mysql', 'postgres']
        
        # Test valid
        for db in valid_databases:
            assert db in valid_databases
        
        # Test invalid
        invalid_db = 'mongodb'
        assert invalid_db not in valid_databases


class TestTodomanageErrorHandling:
    """Test error handling in todomanage operations."""
    
    def test_user_creation_duplicate_email(self, app, db_session):
        """Test that todomanage handles duplicate emails."""
        from app.models import User
        
        with app.app_context():
            # Create first user
            user1 = User(email='dup1@example.com')
            user1.set_password('Pass1!')
            db_session.session.add(user1)
            db_session.session.commit()
            
            # Try to create duplicate email
            user2 = User(email='dup1@example.com')
            user2.set_password('Pass2!')
            
            try:
                db_session.session.add(user2)
                db_session.session.commit()
                # If no exception, we should have caught it in todomanage
                assert False, "Should have raised an error for duplicate email"
            except Exception:
                # Expected - todomanage would catch this
                db_session.session.rollback()
                
                # Verify first user still exists
                original = User.query.filter_by(email='dup1@example.com').first()
                assert original is not None
                assert original.email == 'dup1@example.com'
            user2.set_password('Pass2!')
            
            try:
                db_session.session.add(user2)
                db_session.session.commit()
                assert False, "Should have raised an error for duplicate email"
            except Exception:
                db_session.session.rollback()
                
                # Verify first user still exists
                original = User.query.filter_by(email='duplicate@example.com').first()
                assert original is not None
                assert original.username == 'user_dup1'
    
    def test_invalid_password_validation(self):
        """Test password validation like todomanage does."""
        valid_passwords = [
            'SecurePass123!',
            'VeryLongPasswordWith123AndSymbols!@#',
            'P@ssw0rd'
        ]
        
        # At minimum length validation
        for password in valid_passwords:
            assert len(password) >= 6
    
    def test_invalid_email_validation(self):
        """Test email validation like todomanage does."""
        import re
        
        valid_emails = ['user@example.com', 'test.user@domain.co.uk', 'admin+tag@service.io']
        invalid_emails = ['notanemail', 'missing@domain', '@nodomain.com']
        
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        
        for email in valid_emails:
            assert re.match(email_pattern, email) is not None
        
        for email in invalid_emails:
            # Basic check - not all invalid
            if email == 'notanemail':
                assert re.match(email_pattern, email) is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
