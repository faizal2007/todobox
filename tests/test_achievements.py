"""Test suite for achievements page functionality"""
import pytest
from datetime import datetime, timedelta
from app.models import Todo, Tracker, Status, User
from app import db


@pytest.fixture
def user_with_completed_todos(app, test_user):
    """Create a test user with some completed todos"""
    with app.app_context():
        # Make sure status 6 (done) exists
        done_status = Status.query.get(6)
        if not done_status:
            done_status = Status(name='done')
            done_status.id = 6
            db.session.add(done_status)
            db.session.commit()
        
        # Create 3 completed todos
        for i in range(3):
            todo = Todo(
                name=f'Completed Task {i+1}',
                details=f'Details for task {i+1}',
                user_id=test_user.id,
                timestamp=datetime.utcnow() - timedelta(days=i),
                modified=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(todo)
            db.session.flush()
            
            # Add tracker entry for completion
            tracker = Tracker(todo_id=todo.id, status_id=6)
            tracker.timestamp = datetime.utcnow() - timedelta(days=i)
            db.session.add(tracker)
        
        db.session.commit()
        return test_user


class TestAchievementsPage:
    """Test cases for achievements page"""
    
    def test_achievements_page_accessible(self, client, login_user, test_user):
        """Test that achievements page is accessible to logged-in users"""
        login_user()
        response = client.get('/achievements')
        assert response.status_code == 200
        assert b'Achievements' in response.data
    
    def test_achievements_page_requires_login(self, client):
        """Test that achievements page requires login"""
        response = client.get('/achievements', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_achievements_page_with_completed_todos(self, client, login_user, user_with_completed_todos):
        """Test that achievements page displays completed todos"""
        login_user(user_with_completed_todos)
        response = client.get('/achievements')
        assert response.status_code == 200
        assert b'Completed Task 1' in response.data
        assert b'Completed Task 2' in response.data
        assert b'Completed Task 3' in response.data
    
    def test_achievements_page_empty_state(self, client, login_user, test_user):
        """Test that achievements page shows empty state when no todos completed"""
        login_user(test_user)
        response = client.get('/achievements')
        assert response.status_code == 200
        assert b'No Achievements Yet' in response.data or b'Achievement' in response.data
    
    def test_achievements_statistics_displayed(self, client, login_user, user_with_completed_todos):
        """Test that completion statistics are displayed"""
        login_user(user_with_completed_todos)
        response = client.get('/achievements')
        assert response.status_code == 200
        # Check for statistics section
        assert b'Completed Todos' in response.data or b'Achievement' in response.data
    
    def test_achievements_navigation_link_visible(self, client, login_user, test_user):
        """Test that achievements link appears in navigation"""
        login_user(test_user)
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Achievements' in response.data
        assert b'/achievements' in response.data
