"""
Comprehensive test for reminder persistence after editing todos.
Tests the complete flow from frontend format to backend storage and retrieval.
"""

import sys
import json
from datetime import datetime, timedelta
from app import app, db
from app.models import User, Todo, Status, Tracker
from app.timezone_utils import convert_from_user_timezone, convert_to_user_timezone


def test_reminder_persistence_flow():
    """
    Test the complete reminder persistence flow:
    1. Frontend sends ISO format (from Flatpickr)
    2. Backend receives and parses ISO format
    3. Backend converts to UTC and saves
    4. Backend retrieves and converts back to user timezone
    5. Frontend receives ISO format and displays correctly
    """
    with app.app_context():
        # Setup
        db.create_all()
        
        # Clean up - delete todos first, then user (due to foreign key)
        user = User.query.filter_by(email='test@example.com').first()
        if user:
            Todo.query.filter_by(user_id=user.id).delete()
            User.query.filter_by(email='test@example.com').delete()
        db.session.commit()
        
        # Create test user
        user = User(email='test@example.com', fullname='Test User')
        user.timezone = 'US/Eastern'
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create todo with reminder
        todo = Todo(
            name='Test todo with reminder',
            details='Test details',
            user_id=user.id,
            reminder_enabled=False,
            reminder_sent=False
        )
        db.session.add(todo)
        db.session.commit()
        
        # Simulate frontend sending ISO format datetime
        # User selects 2025-12-06 14:30 (2:30 PM ET) via Flatpickr
        frontend_iso_format = '2025-12-06T14:30'
        
        # Backend parses ISO format
        try:
            reminder_dt = datetime.fromisoformat(frontend_iso_format)
            print(f"✅ Backend parsed ISO format successfully: {reminder_dt}")
        except ValueError as e:
            print(f"❌ Backend failed to parse ISO format: {e}")
            return False
        
        # Backend converts from user timezone to UTC
        reminder_dt_utc = convert_from_user_timezone(reminder_dt, user.timezone)
        print(f"✅ Converted to UTC: {reminder_dt_utc}")
        
        # Backend saves to database
        todo.reminder_time = reminder_dt_utc
        todo.reminder_enabled = True
        todo.reminder_sent = False
        db.session.commit()
        print(f"✅ Saved to database - reminder_time: {todo.reminder_time}")
        
        # Simulate retrieving from database for display
        retrieved_todo = Todo.query.filter_by(id=todo.id).first()
        assert retrieved_todo.reminder_enabled == True, "Reminder should be enabled"
        assert retrieved_todo.reminder_time is not None, "Reminder time should be saved"
        print(f"✅ Retrieved from database - reminder_time: {retrieved_todo.reminder_time}")
        
        # Backend converts UTC back to user timezone for display
        reminder_time_user_tz = convert_to_user_timezone(
            retrieved_todo.reminder_time,
            user.timezone
        )
        print(f"✅ Converted back to user timezone: {reminder_time_user_tz}")
        
        # Backend sends ISO format to frontend
        reminder_time_iso = reminder_time_user_tz.isoformat()
        print(f"✅ Converted to ISO format for frontend: {reminder_time_iso}")
        
        # Frontend extracts first 16 characters for Flatpickr
        frontend_extracted = reminder_time_iso[:16]
        print(f"✅ Frontend extracted for Flatpickr: {frontend_extracted}")
        
        # Verify the extracted format is what Flatpickr expects
        assert frontend_extracted == frontend_iso_format, \
            f"Format mismatch: {frontend_extracted} != {frontend_iso_format}"
        
        print("\n" + "="*60)
        print("✅ COMPLETE REMINDER PERSISTENCE FLOW VALIDATED")
        print("="*60)
        print(f"Frontend input (ISO):        {frontend_iso_format}")
        print(f"Parsed datetime:             {reminder_dt}")
        print(f"Converted to UTC:            {reminder_dt_utc}")
        print(f"Stored in DB:                {todo.reminder_time}")
        print(f"Retrieved from DB:           {retrieved_todo.reminder_time}")
        print(f"Converted to user TZ:        {reminder_time_user_tz}")
        print(f"Sent to frontend (ISO):      {reminder_time_iso}")
        print(f"Frontend extracts (first 16):{frontend_extracted}")
        print("="*60)
        
        return True


def test_reminder_clearing():
    """Test that reminder can be cleared (unchecked) and persisted"""
    with app.app_context():
        # Setup
        db.create_all()
        
        # Clean up - delete todos first, then user (due to foreign key)
        user = User.query.filter_by(email='test2@example.com').first()
        if user:
            Todo.query.filter_by(user_id=user.id).delete()
            User.query.filter_by(email='test2@example.com').delete()
        db.session.commit()
        
        # Create test user
        user = User(email='test2@example.com', fullname='Test User 2')
        user.timezone = 'US/Pacific'
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Create todo with existing reminder
        future_time = convert_from_user_timezone(
            datetime.fromisoformat('2025-12-06T14:30'),
            user.timezone
        )
        
        todo = Todo(
            name='Todo with existing reminder',
            details='Test details',
            user_id=user.id,
            reminder_enabled=True,
            reminder_time=future_time,
            reminder_sent=False
        )
        db.session.add(todo)
        db.session.commit()
        
        assert todo.reminder_enabled == True
        print(f"✅ Created todo with reminder: {todo.reminder_time}")
        
        # Simulate user unchecking reminder (setting reminder_enabled=False)
        todo.reminder_enabled = False
        todo.reminder_time = None
        db.session.commit()
        
        # Verify it was cleared
        retrieved = Todo.query.filter_by(id=todo.id).first()
        assert retrieved.reminder_enabled == False, "Reminder should be disabled"
        assert retrieved.reminder_time is None, "Reminder time should be cleared"
        
        print(f"✅ Successfully cleared reminder")
        print(f"   reminder_enabled: {retrieved.reminder_enabled}")
        print(f"   reminder_time: {retrieved.reminder_time}")
        
        return True


def test_format_compatibility():
    """Test that various datetime formats work correctly"""
    with app.app_context():
        test_cases = [
            '2025-12-06T14:30',      # Standard ISO
            '2025-01-01T00:00',      # New Year
            '2025-12-31T23:59',      # End of year
            '2025-06-15T12:00',      # Noon
        ]
        
        print("\nTesting format compatibility:")
        print("-" * 50)
        
        for test_input in test_cases:
            try:
                dt = datetime.fromisoformat(test_input)
                print(f"✅ {test_input} -> {dt}")
            except ValueError as e:
                print(f"❌ {test_input} -> ERROR: {e}")
                return False
        
        return True


if __name__ == '__main__':
    print("Testing Reminder Persistence Flow")
    print("=" * 60)
    
    success = True
    
    # Run tests
    if not test_reminder_persistence_flow():
        success = False
    
    print("\n")
    
    if not test_reminder_clearing():
        success = False
    
    print("\n")
    
    if not test_format_compatibility():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
