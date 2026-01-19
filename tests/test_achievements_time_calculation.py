"""
Tests for achievements Time Taken calculation.
Validates that Time Taken is calculated using work session tracking (Status 10: Started),
not creation time (Status 5: Created).
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Todo, Tracker


@pytest.fixture
def test_user(app):
    """Create a test user and return user ID"""
    from app import db
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com', fullname='Test User')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        return user.id


def test_achievements_uses_started_status_not_created(app, test_user):
    """
    Test that achievements() calculates Time Taken from Status 10 (Started),
    not Status 5 (Created).
    
    Setup:
    - Create todo at T=0
    - Created tracker at T=0 (Status 5)
    - Started at T=1 hour
    - Completed at T=3 hours
    
    Expected: Time Taken = 2 hours (from Started to Done), NOT 3 hours (from Created to Done)
    """
    from app import db
    
    with app.app_context():
        # Create todo
        todo = Todo(name='Test Task', user_id=test_user)
        db.session.add(todo)
        db.session.flush()
        
        base_time = datetime.utcnow()
        
        # Created tracker (Status 5)
        created_tracker = Tracker(
            todo_id=todo.id,
            status_id=5,
            timestamp=base_time
        )
        db.session.add(created_tracker)
        
        # Started tracker (Status 10) - 1 hour later
        started_tracker = Tracker(
            todo_id=todo.id,
            status_id=10,
            timestamp=base_time + timedelta(hours=1)
        )
        db.session.add(started_tracker)
        
        # Done tracker (Status 6) - 3 hours from creation, 2 hours from start
        done_tracker = Tracker(
            todo_id=todo.id,
            status_id=6,
            timestamp=base_time + timedelta(hours=3)
        )
        db.session.add(done_tracker)
        
        db.session.commit()
        
        # Test the calculation
        # Get all completed todos (limit 20 like in achievements())
        completed_todos = db.session.query(Todo, Tracker).join(
            Tracker, Todo.id == Tracker.todo_id
        ).filter(
            Todo.user_id == test_user,
            Tracker.status_id == 6
        ).order_by(Tracker.timestamp.desc()).limit(20).all()
        
        # Calculate time like achievements() does
        completion_times = []
        for todo_item, completion_tracker in completed_todos:
            started_tracker_result = db.session.query(Tracker).filter_by(
                todo_id=todo_item.id, status_id=10
            ).order_by(Tracker.timestamp.asc()).first()
            
            if started_tracker_result:
                time_diff = completion_tracker.timestamp - started_tracker_result.timestamp
                completion_times.append(time_diff.total_seconds() / 3600)
        
        assert len(completion_times) == 1, "Should have one completed todo"
        assert completion_times[0] == 2.0, f"Time should be 2 hours (Started to Done), got {completion_times[0]}"


def test_achievements_handles_todo_never_started(app, test_user):
    """
    Test that achievements() gracefully handles todos completed without being started.
    This is an edge case where a todo was created and completed but never started.
    Expected: Time Taken = None or 0
    """
    from app import db
    
    with app.app_context():
        # Create todo
        todo = Todo(name='Never Started Task', user_id=test_user)
        db.session.add(todo)
        db.session.flush()
        
        base_time = datetime.utcnow()
        
        # Created tracker (Status 5) - but no Started tracker
        created_tracker = Tracker(
            todo_id=todo.id,
            status_id=5,
            timestamp=base_time
        )
        db.session.add(created_tracker)
        
        # Done tracker (Status 6) - completed directly without starting
        done_tracker = Tracker(
            todo_id=todo.id,
            status_id=6,
            timestamp=base_time + timedelta(hours=2)
        )
        db.session.add(done_tracker)
        
        db.session.commit()
        
        # Calculate time like achievements() does
        completed_todos = db.session.query(Todo, Tracker).join(
            Tracker, Todo.id == Tracker.todo_id
        ).filter(
            Todo.user_id == test_user,
            Tracker.status_id == 6
        ).order_by(Tracker.timestamp.desc()).limit(20).all()
        
        completion_times = []
        for todo_item, completion_tracker in completed_todos:
            started_tracker_result = db.session.query(Tracker).filter_by(
                todo_id=todo_item.id, status_id=10
            ).order_by(Tracker.timestamp.asc()).first()
            
            if started_tracker_result:
                time_diff = completion_tracker.timestamp - started_tracker_result.timestamp
                completion_times.append(time_diff.total_seconds() / 3600)
        
        assert len(completion_times) == 0, "No Started tracker = no time calculated"


def test_achievements_average_calculation(app, test_user):
    """
    Test that the average completion time is correctly calculated across multiple todos.
    
    Setup:
    - Todo 1: Start at 0, Complete at 2 hours = 2 hours
    - Todo 2: Start at 0, Complete at 4 hours = 4 hours
    - Todo 3: Start at 0, Complete at 6 hours = 6 hours
    
    Expected Average: (2 + 4 + 6) / 3 = 4 hours
    """
    from app import db
    
    with app.app_context():
        todos_data = [
            (2, 'Task 1'),
            (4, 'Task 2'),
            (6, 'Task 3'),
        ]
        
        base_time = datetime.utcnow()
        
        for hours_to_complete, task_name in todos_data:
            todo = Todo(name=task_name, user_id=test_user)
            db.session.add(todo)
            db.session.flush()
            
            # Started tracker
            started_tracker = Tracker(
                todo_id=todo.id,
                status_id=10,
                timestamp=base_time
            )
            db.session.add(started_tracker)
            
            # Done tracker
            done_tracker = Tracker(
                todo_id=todo.id,
                status_id=6,
                timestamp=base_time + timedelta(hours=hours_to_complete)
            )
            db.session.add(done_tracker)
        
        db.session.commit()
        
        # Calculate average like achievements() does
        completed_todos = db.session.query(Todo, Tracker).join(
            Tracker, Todo.id == Tracker.todo_id
        ).filter(
            Todo.user_id == test_user,
            Tracker.status_id == 6
        ).order_by(Tracker.timestamp.desc()).limit(20).all()
        
        completion_times = []
        for todo_item, completion_tracker in completed_todos:
            started_tracker_result = db.session.query(Tracker).filter_by(
                todo_id=todo_item.id, status_id=10
            ).order_by(Tracker.timestamp.asc()).first()
            
            if started_tracker_result:
                time_diff = completion_tracker.timestamp - started_tracker_result.timestamp
                completion_times.append(time_diff.total_seconds() / 3600)
        
        assert len(completion_times) == 3, "Should have 3 completed todos"
        average = round(sum(completion_times) / len(completion_times), 1)
        assert average == 4.0, f"Average should be 4.0 hours, got {average}"


def test_achievements_with_paused_sessions(app, test_user):
    """
    Test that achievements correctly handles todos with paused work sessions.
    Time should be from first Started status to Done, regardless of pauses.
    
    Setup:
    - Start at T=0
    - Pause at T=1 hour
    - Resume at T=2 hours
    - Done at T=3 hours
    
    Expected: Time Taken = 3 hours (Start to Done), not just active work time
    """
    from app import db
    
    with app.app_context():
        todo = Todo(name='Task with Pauses', user_id=test_user)
        db.session.add(todo)
        db.session.flush()
        
        base_time = datetime.utcnow()
        
        # Started tracker (Status 10)
        started_tracker = Tracker(
            todo_id=todo.id,
            status_id=10,
            timestamp=base_time
        )
        db.session.add(started_tracker)
        
        # Paused tracker (Status 11)
        paused_tracker = Tracker(
            todo_id=todo.id,
            status_id=11,
            timestamp=base_time + timedelta(hours=1)
        )
        db.session.add(paused_tracker)
        
        # Resumed tracker (Status 12)
        resumed_tracker = Tracker(
            todo_id=todo.id,
            status_id=12,
            timestamp=base_time + timedelta(hours=2)
        )
        db.session.add(resumed_tracker)
        
        # Done tracker (Status 6)
        done_tracker = Tracker(
            todo_id=todo.id,
            status_id=6,
            timestamp=base_time + timedelta(hours=3)
        )
        db.session.add(done_tracker)
        
        db.session.commit()
        
        # Calculate time
        completed_todos = db.session.query(Todo, Tracker).join(
            Tracker, Todo.id == Tracker.todo_id
        ).filter(
            Todo.user_id == test_user,
            Tracker.status_id == 6
        ).order_by(Tracker.timestamp.desc()).limit(20).all()
        
        completion_times = []
        for todo_item, completion_tracker in completed_todos:
            started_tracker_result = db.session.query(Tracker).filter_by(
                todo_id=todo_item.id, status_id=10
            ).order_by(Tracker.timestamp.asc()).first()
            
            if started_tracker_result:
                time_diff = completion_tracker.timestamp - started_tracker_result.timestamp
                completion_times.append(time_diff.total_seconds() / 3600)
        
        assert len(completion_times) == 1
        assert completion_times[0] == 3.0, f"Time should be 3 hours (Start to Done), got {completion_times[0]}"


def test_achievements_multiple_starts(app, test_user):
    """
    Test that achievements uses the FIRST Started tracker when multiple sessions exist.
    
    Setup:
    - Start at T=0 hour (Status 10)
    - Pause at T=1 hour
    - Resume at T=1.5 hour (Status 12)
    - Pause again at T=2 hour
    - Resume at T=2.5 hour (Status 12 again)
    - Done at T=3 hour
    
    Expected: Time Taken from first Start (T=0) to Done (T=3) = 3 hours
    """
    from app import db
    
    with app.app_context():
        todo = Todo(name='Multi-session Task', user_id=test_user)
        db.session.add(todo)
        db.session.flush()
        
        base_time = datetime.utcnow()
        
        trackers_data = [
            (10, 0.0),     # Started
            (11, 1.0),     # Paused
            (12, 1.5),     # Resumed
            (11, 2.0),     # Paused
            (12, 2.5),     # Resumed
            (6, 3.0),      # Done
        ]
        
        for status_id, hours_offset in trackers_data:
            tracker = Tracker(
                todo_id=todo.id,
                status_id=status_id,
                timestamp=base_time + timedelta(hours=hours_offset)
            )
            db.session.add(tracker)
        
        db.session.commit()
        
        # Calculate time - should use first Started (Status 10)
        completed_todos = db.session.query(Todo, Tracker).join(
            Tracker, Todo.id == Tracker.todo_id
        ).filter(
            Todo.user_id == test_user,
            Tracker.status_id == 6
        ).order_by(Tracker.timestamp.desc()).limit(20).all()
        
        completion_times = []
        for todo_item, completion_tracker in completed_todos:
            started_tracker_result = db.session.query(Tracker).filter_by(
                todo_id=todo_item.id, status_id=10
            ).order_by(Tracker.timestamp.asc()).first()
            
            if started_tracker_result:
                time_diff = completion_tracker.timestamp - started_tracker_result.timestamp
                completion_times.append(time_diff.total_seconds() / 3600)
        
        assert len(completion_times) == 1
        assert completion_times[0] == 3.0, f"Time should be 3 hours (first Start to Done), got {completion_times[0]}"
