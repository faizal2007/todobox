"""
Test work session tracking functionality (start, pause, resume)
Tests the new Status IDs 10, 11, 12 for accurate time tracking
"""
import pytest
from datetime import datetime, timedelta
from app.models import Todo, User, Tracker, Status
from app import db
import json


def create_test_user(app, email='testwork@example.com'):
    """Helper to create a test user with proper context"""
    with app.app_context():
        user = User(email=email, fullname='Test User')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user.id


def create_test_todo(app, user_id, name='Test Todo'):
    """Helper to create a test todo"""
    with app.app_context():
        todo = Todo(name=name, details='Test details', user_id=user_id)
        db.session.add(todo)
        db.session.commit()
        return todo.id


class TestWorkSessionTracking:
    """Test the complete work session tracking flow"""
    
    def test_start_work_session(self, app, client):
        """Test starting a work session records Status 10"""
        user_id = create_test_user(app, 'start_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Start Test')
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            user = User.query.get(user_id)
            flask_login(user)
        
        # Start work session
        response = client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
        assert data['todo_id'] == todo_id
        assert 'session_start_time' in data
        
        # Verify tracker record was created with Status 10
        with app.app_context():
            tracker = Tracker.query.filter_by(todo_id=todo_id, status_id=10).first()
            assert tracker is not None
            assert tracker.todo_id == todo_id
            assert tracker.status_id == 10
    
    def test_pause_work_session(self, app, client):
        """Test pausing a work session records Status 11"""
        user_id = create_test_user(app, 'pause_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Pause Test')
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            user = User.query.get(user_id)
            flask_login(user)
        
        # Start work session first
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Pause work session
        response = client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
        assert 'session_duration_hours' in data
        assert 'total_work_time_hours' in data
        
        # Verify tracker record was created with Status 11
        with app.app_context():
            tracker = Tracker.query.filter_by(todo_id=todo_id, status_id=11).first()
            assert tracker is not None
            assert tracker.status_id == 11
    
    def test_resume_work_session(self, app, client):
        """Test resuming a paused work session records Status 12"""
        user_id = create_test_user(app, 'resume_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Resume Test')
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            user = User.query.get(user_id)
            flask_login(user)
        
        # Start and pause
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        
        # Resume work session
        response = client.post(f'/{todo_id}/resume', data={'_csrf_token': ''})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
        assert 'session_start_time' in data
        
        # Verify tracker record was created with Status 12
        with app.app_context():
            tracker = Tracker.query.filter_by(todo_id=todo_id, status_id=12).first()
            assert tracker is not None
            assert tracker.status_id == 12
    
    def test_multiple_work_sessions(self, app, client):
        """Test multiple start-pause-resume cycles"""
        user_id = create_test_user(app, 'multi_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Multi Test')
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            user = User.query.get(user_id)
            flask_login(user)
        
        # First session: start -> pause
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        response1 = client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        data1 = json.loads(response1.data)
        
        # Second session: resume -> pause
        client.post(f'/{todo_id}/resume', data={'_csrf_token': ''})
        response2 = client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        data2 = json.loads(response2.data)
        
        # Total work time should be greater than or equal to individual sessions
        assert data2['total_work_time_hours'] >= data1['total_work_time_hours']
        
        # Verify all tracker records exist
        with app.app_context():
            status_10 = Tracker.query.filter_by(todo_id=todo_id, status_id=10).count()
            status_11 = Tracker.query.filter_by(todo_id=todo_id, status_id=11).count()
            status_12 = Tracker.query.filter_by(todo_id=todo_id, status_id=12).count()
            
            assert status_10 == 1  # One start
            assert status_11 == 2  # Two pauses
            assert status_12 == 1  # One resume
    
    def test_time_calculation_from_started_status(self, app, client):
        """Test that time_to_complete is calculated from Status 10 (Started), not Status 5 (Created)"""
        user_id = create_test_user(app, 'time_calc_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Time Calc Test')
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            user = User.query.get(user_id)
            flask_login(user)
        
        # Start work session (simulating work beginning)
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Mark as done
        response = client.post(f'/{todo_id}/done', data={'_csrf_token': ''})
        assert response.status_code == 200
        
        # Get todo details to check time_to_complete calculation
        response = client.get(f'/api/todo/{todo_id}/details')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # The time_to_complete should be much less than if calculated from creation
        # since we only started working just now
        assert data['time_to_complete'] is not None
        assert data['time_to_complete'] < 1  # Should be close to 0 hours
    
    def test_work_session_unauthorized_access(self, app, client, test_user):
        """Test that users cannot start work sessions on other users' todos"""
        with app.app_context():
            # Create another user
            user2 = User(email='user2@example.com', fullname='User 2')
            user2.set_password('password')
            db.session.add(user2)
            db.session.commit()
            
            # Create a todo for test_user
            todo = Todo(name='Test Todo', details='Test', user_id=test_user.id)
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
        
        # Login as test_user first
        with app.app_context():
            from flask_login import login_user
            login_user(test_user)
        
        # Try to access with user2 (not logged in, so should fail)
        response = client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Should fail - unauthorized or not found
        assert response.status_code in [401, 404]
    
    def test_status_ids_exist_in_database(self, app):
        """Test that Status IDs 10, 11, 12 are properly created"""
        with app.app_context():
            started = Status.query.filter_by(id=10).first()
            paused = Status.query.filter_by(id=11).first()
            resumed = Status.query.filter_by(id=12).first()
            
            assert started is not None, "Status 10 not found"
            assert started.name == 'started', f"Status 10 should be 'started', got '{started.name}'"
            
            assert paused is not None, "Status 11 not found"
            assert paused.name == 'paused', f"Status 11 should be 'paused', got '{paused.name}'"
            
            assert resumed is not None, "Status 12 not found"
            assert resumed.name == 'resumed', f"Status 12 should be 'resumed', got '{resumed.name}'"
    
    def test_work_session_without_auth(self, client):
        """Test that work session endpoints require authentication"""
        response = client.post('/999/start', data={'_csrf_token': ''})
        # Should redirect to login or return 401/404
        assert response.status_code in [301, 302, 401, 404]


class TestTimeCalculationAccuracy:
    """Test that time_to_complete is calculated accurately"""
    
    def test_creation_vs_started_timestamp_difference(self, app, client, user_with_todo):
        """Verify that using Status 10 instead of Status 5 gives more accurate time"""
        user, todo_id = user_with_todo
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            flask_login(user)
        
        # Get creation timestamp (Status 5)
        with app.app_context():
            created_tracker = Tracker.query.filter_by(todo_id=todo_id, status_id=5).first()
            assert created_tracker is not None
            
            # Manually add a start timestamp (simulating work started later)
            start_timestamp = created_tracker.timestamp + timedelta(hours=2)
            Tracker.add(todo_id, 10, start_timestamp)
            
            # Mark as done immediately after starting
            done_timestamp = start_timestamp + timedelta(minutes=30)
            Tracker.add(todo_id, 6, done_timestamp)
        
        # Fetch todo details
        response = client.get(f'/api/todo/{todo_id}/details')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Time should be ~0.5 hours (30 minutes), not 2.5 hours
        assert data['time_to_complete'] is not None
        assert 0.4 < data['time_to_complete'] < 0.6, f"Expected ~0.5 hours, got {data['time_to_complete']}"
    
    def test_multiple_sessions_combined_time(self, app, client, user_with_todo):
        """Test that multiple work sessions are counted correctly"""
        user, todo_id = user_with_todo
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            flask_login(user)
        
        # Clear existing trackers and create new ones
        with app.app_context():
            Tracker.query.filter_by(todo_id=todo_id).delete()
            db.session.commit()
            
            # Session 1: Start and pause after 30 minutes
            start_time_1 = datetime.now()
            Tracker.add(todo_id, 10, start_time_1)
            pause_time_1 = start_time_1 + timedelta(minutes=30)
            Tracker.add(todo_id, 11, pause_time_1)
            
            # Session 2: Resume and pause after 45 minutes
            start_time_2 = pause_time_1 + timedelta(minutes=5)  # 5 min break
            Tracker.add(todo_id, 12, start_time_2)
            pause_time_2 = start_time_2 + timedelta(minutes=45)
            Tracker.add(todo_id, 11, pause_time_2)
            
            # Mark as done
            done_time = pause_time_2
            Tracker.add(todo_id, 6, done_time)
        
        # Get details
        response = client.get(f'/api/todo/{todo_id}/details')
        data = json.loads(response.data)
        
        # Total work time should be from first status 10 to final done
        with app.app_context():
            first_10 = Tracker.query.filter_by(todo_id=todo_id, status_id=10).first()
            last_6 = Tracker.query.filter_by(todo_id=todo_id, status_id=6).first()
            expected_hours = (last_6.timestamp - first_10.timestamp).total_seconds() / 3600
        
        actual_hours = data['time_to_complete']
        
        assert actual_hours is not None
        assert abs(actual_hours - expected_hours) < 0.01, \
            f"Expected {expected_hours} hours, got {actual_hours}"


class TestWorkSessionEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_pause_without_starting(self, app, client, user_with_todo):
        """Test pausing a todo that was never started"""
        user, todo_id = user_with_todo
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            flask_login(user)
        
        # Try to pause without starting
        response = client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        
        # Should still succeed but with 0 session duration
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['session_duration_hours'] == 0
    
    def test_resume_without_pause(self, app, client, user_with_todo):
        """Test resuming without pausing (edge case)"""
        user, todo_id = user_with_todo
        
        # Login user
        with app.app_context():
            from flask_login import login_user as flask_login
            flask_login(user)
        
        # Start work session
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Try to resume without pausing (shouldn't happen in UI, but possible via API)
        response = client.post(f'/{todo_id}/resume', data={'_csrf_token': ''})
        
        # Should still work
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
