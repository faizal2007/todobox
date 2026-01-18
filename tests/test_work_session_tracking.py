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


def force_login(client, user_id):
    """Authenticate a user by storing their id in the session."""
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)
        session['_fresh'] = True


@pytest.fixture
def user_with_todo(app):
    """Provide a user id and todo id pair for tests."""
    with app.app_context():
        user = User(email='ws_fixture@example.com', fullname='WS Fixture User')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        todo = Todo(name='Fixture Todo', details='Fixture details', user_id=user.id)
        db.session.add(todo)
        db.session.commit()
        Tracker.add(todo.id, 5, datetime.now())

        return user.id, todo.id


class TestWorkSessionTracking:
    """Test the complete work session tracking flow"""
    
    def test_start_work_session(self, app, client):
        """Test starting a work session records Status 10"""
        user_id = create_test_user(app, 'start_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Start Test')
        
        force_login(client, user_id)
        
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
        
        force_login(client, user_id)
        
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
        
        force_login(client, user_id)
        
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

    def test_manual_time_entry_with_range(self, app, client):
        """Users can log manual time by providing explicit start and end."""
        user_id = create_test_user(app, 'manual_range@example.com')
        todo_id = create_test_todo(app, user_id, 'Manual Range Test')

        force_login(client, user_id)

        start_window = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        end_window = (datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M')

        response = client.post(
            f'/{todo_id}/log_manual_time',
            json={
                'mode': 'range',
                'start_time': start_window,
                'end_time': end_window,
                'user_timezone': 'UTC'
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
        assert data['session_duration_hours'] > 0
        assert data['total_work_time_hours'] >= data['session_duration_hours']

        with app.app_context():
            starts = Tracker.query.filter_by(todo_id=todo_id, status_id=10).count()
            pauses = Tracker.query.filter_by(todo_id=todo_id, status_id=11).count()
            assert starts == 1
            assert pauses == 1

    def test_manual_time_entry_with_duration(self, app, client):
        """Users can log manual time using quick duration notation."""
        user_id = create_test_user(app, 'manual_duration@example.com')
        todo_id = create_test_todo(app, user_id, 'Manual Duration Test')

        force_login(client, user_id)

        response = client.post(
            f'/{todo_id}/log_manual_time',
            json={
                'mode': 'duration',
                'duration_input': '30 m',
                'user_timezone': 'UTC'
            }
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'
        assert 0.4 < data['session_duration_hours'] < 0.6

        with app.app_context():
            starts = Tracker.query.filter_by(todo_id=todo_id, status_id=10).count()
            pauses = Tracker.query.filter_by(todo_id=todo_id, status_id=11).count()
            assert starts == 1
            assert pauses == 1
    
    def test_multiple_work_sessions(self, app, client):
        """Test multiple start-pause-resume cycles"""
        user_id = create_test_user(app, 'multi_test@example.com')
        todo_id = create_test_todo(app, user_id, 'Multi Test')
        
        force_login(client, user_id)
        
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
        
        force_login(client, user_id)
        
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
            user2_id = user2.id

            owner = User.query.filter_by(email='test@example.com').first()
            assert owner is not None
            owner_id = owner.id
            # Create a todo for test_user
            todo = Todo(name='Test Todo', details='Test', user_id=owner_id)
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
        
        # Login as user2 who does not own the todo
        force_login(client, user2_id)
        
        # Try to access owner's todo - should fail
        response = client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Should fail - unauthorized or not found
        assert response.status_code in [401, 403, 404]
    
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
        user_id, todo_id = user_with_todo
        
        force_login(client, user_id)
        
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
        user_id, todo_id = user_with_todo
        
        force_login(client, user_id)
        
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
        assert abs(actual_hours - expected_hours) < 0.05, \
            f"Expected {expected_hours} hours, got {actual_hours}"


class TestWorkSessionEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_pause_without_starting(self, app, client, user_with_todo):
        """Test pausing a todo that was never started"""
        user_id, todo_id = user_with_todo
        
        force_login(client, user_id)
        
        # Try to pause without starting
        response = client.post(f'/{todo_id}/pause', data={'_csrf_token': ''})
        
        # Should still succeed but with 0 session duration
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['session_duration_hours'] == 0
    
    def test_resume_without_pause(self, app, client, user_with_todo):
        """Test resuming without pausing (edge case)"""
        user_id, todo_id = user_with_todo
        
        force_login(client, user_id)
        
        # Start work session
        client.post(f'/{todo_id}/start', data={'_csrf_token': ''})
        
        # Try to resume without pausing (shouldn't happen in UI, but possible via API)
        response = client.post(f'/{todo_id}/resume', data={'_csrf_token': ''})
        
        # Should still work
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'Success'

    def test_elapsed_time_with_resume(self, app, client, user_with_todo):
        """
        Test the resume scenario: Start → Pause after 5s → Resume after waiting
        
        User's test case:
        - Timer starts at 00:00:05 (5 seconds elapsed)
        - Session pauses
        - User waits some time
        - User clicks resume/play button
        - Timer should show the correct elapsed time from the original start, not just time since resume
        """
        user_id, todo_id = user_with_todo
        
        force_login(client, user_id)
        
        with app.app_context():
            # Clear existing tracker data for this todo
            Tracker.query.filter(Tracker.todo_id == todo_id).delete()
            db.session.commit()
            
            # Simulate exact timeline
            now = datetime.utcnow()
            start_time = now - timedelta(seconds=11)  # Session started 11 seconds ago
            pause_time = start_time + timedelta(seconds=5)  # Paused after 5 seconds
            resume_time = now  # Resumed just now
            
            # Record events
            Tracker.add(todo_id, 10, start_time)   # START
            Tracker.add(todo_id, 11, pause_time)   # PAUSE at 5 seconds
            Tracker.add(todo_id, 12, resume_time)  # RESUME now
        
        # Call get_active_session endpoint
        response = client.get(f'/{todo_id}/get_active_session')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['is_active'] == True
        
        # The elapsed time should be approximately 5 seconds (from start to pause)
        # not 0 seconds (from resume to now)
        elapsed = data['elapsed_seconds']
        
        # Should be close to 5 seconds, allowing for small timing variations
        assert 4 <= elapsed <= 6, f"Expected ~5 seconds, got {elapsed} seconds"
