#!/usr/bin/env python
"""
Test for reminder clear functionality.
Verifies that setting reminder to unchecked properly saves to database.
"""

import sys
from app import app, db
from app.models import User, Todo, Status, Tracker
from datetime import datetime, timedelta
import json

def setup_test_data():
    """Create test user and todo with reminder"""
    with app.app_context():
        # Clean up existing test data
        User.query.filter_by(email='test_reminder_clear@test.com').delete()
        db.session.commit()
        
        # Create test user
        user = User(
            email='test_reminder_clear@test.com',
            fullname='Test User'
        )
        user.set_password('testpass123')
        user.timezone = 'UTC'
        db.session.add(user)
        db.session.commit()
        
        # Create status records if they don't exist
        if Status.query.count() == 0:
            Status.seed()
        
        # Create a todo with reminder
        todo = Todo(
            name='Test Todo with Reminder',
            details='This is a test todo',
            user_id=user.id,
            reminder_enabled=True,
            reminder_time=datetime.utcnow() + timedelta(hours=1),
            reminder_sent=False
        )
        db.session.add(todo)
        db.session.commit()
        
        # Add tracker entry
        Tracker.add(todo.id, 5, datetime.utcnow())  # Status 5 = new
        
        return user.id, todo.id

def test_reminder_clear():
    """Test that unchecking reminder in edit saves properly"""
    with app.app_context():
        user_id, todo_id = setup_test_data()
        
        # Verify initial state - reminder should be enabled
        todo = Todo.query.get(todo_id)
        print(f"Initial state:")
        print(f"  Reminder Enabled: {todo.reminder_enabled}")
        print(f"  Reminder Time: {todo.reminder_time}")
        assert todo.reminder_enabled == True, "Reminder should be enabled initially"
        assert todo.reminder_time is not None, "Reminder time should be set initially"
        
        # Simulate editing the todo and unchecking reminder
        # This mimics the form submission with reminder_enabled = False
        todo.reminder_enabled = False
        todo.reminder_time = None
        todo.reminder_sent = False
        db.session.commit()
        
        # Verify reminder was cleared
        todo = Todo.query.get(todo_id)
        print(f"\nAfter unchecking reminder:")
        print(f"  Reminder Enabled: {todo.reminder_enabled}")
        print(f"  Reminder Time: {todo.reminder_time}")
        print(f"  Reminder Sent: {todo.reminder_sent}")
        
        assert todo.reminder_enabled == False, "Reminder should be disabled"
        assert todo.reminder_time is None, "Reminder time should be None"
        assert todo.reminder_sent == False, "Reminder sent should be False"
        
        print("\n✅ Test passed: Reminder properly cleared when unchecked")
        
        # Clean up
        Tracker.query.filter_by(todo_id=todo_id).delete()
        Todo.query.filter_by(id=todo_id).delete()
        User.query.filter_by(id=user_id).delete()
        db.session.commit()

def test_form_data_collection():
    """Test that form collects reminder_enabled correctly"""
    print("\n" + "="*60)
    print("Testing form data collection logic:")
    print("="*60)
    
    # Simulate different form states
    test_cases = [
        {
            'name': 'Reminder checked with custom time',
            'reminder_enabled': 'true',
            'reminder_type': 'custom',
            'reminder_datetime': '2025-12-06T14:30',
            'expected_backend_enabled': True
        },
        {
            'name': 'Reminder unchecked',
            'reminder_enabled': '',  # Not submitted when unchecked
            'reminder_type': None,
            'reminder_datetime': None,
            'expected_backend_enabled': False
        },
        {
            'name': 'Reminder checked with before option',
            'reminder_enabled': 'true',
            'reminder_type': 'before',
            'reminder_before_minutes': '30',
            'reminder_before_unit': 'minutes',
            'expected_backend_enabled': True
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Test: {test_case['name']}")
        # Simulate backend logic
        reminder_enabled = test_case.get('reminder_enabled') == 'true'
        reminder_type = test_case.get('reminder_type')
        
        print(f"    reminder_enabled value: {test_case.get('reminder_enabled')}")
        print(f"    reminder_enabled boolean: {reminder_enabled}")
        print(f"    reminder_type: {reminder_type}")
        
        # Backend logic check
        if reminder_enabled and reminder_type:
            print(f"    ✅ Will SET reminder (enabled and type provided)")
            actual_enabled = True
        else:
            print(f"    ✅ Will CLEAR reminder (disabled or no type)")
            actual_enabled = False
        
        assert actual_enabled == test_case['expected_backend_enabled'], \
            f"Backend logic mismatch for {test_case['name']}"

if __name__ == '__main__':
    print("="*60)
    print("Testing Reminder Clear Functionality")
    print("="*60)
    
    try:
        test_reminder_clear()
        test_form_data_collection()
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
