#!/usr/bin/env python
"""
Test script to verify the reminder notification fix.

This script tests:
1. Reminders are only sent 3 times maximum
2. After 3rd notification, reminder is auto-closed
3. When todo is deleted, reminder stops appearing
4. When reminder is cancelled, it stops appearing
5. Cancelled reminder clears all tracking fields
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add the app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models import Todo, User, Tracker
from app.reminder_service import ReminderService

def test_reminder_three_notification_limit():
    """Test that reminders only send 3 notifications maximum"""
    
    print("\n" + "="*70)
    print("Test 1: 3 Notification Limit")
    print("="*70)
    
    with app.app_context():
        # Create or get test user
        user = User.query.filter_by(email='test_reminder_fix@example.com').first()
        if not user:
            user = User(email='test_reminder_fix@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
        
        # Create test todo with reminder that's already due
        todo = Todo(
            name='Test 3 Notification Limit',
            details='Testing max 3 notifications',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=5),
            reminder_notification_count=0
        )
        db.session.add(todo)
        db.session.commit()
        print(f"✓ Created test todo (ID: {todo.id})")
        
        # 1st notification
        print("\n--- Sending 1st notification ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id in [t.id for t in pending], "1st notification should be pending"
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        print(f"✓ 1st notification sent (count: {todo.reminder_notification_count})")
        assert todo.reminder_notification_count == 1
        assert todo.reminder_enabled == True, "Reminder should still be enabled"
        assert todo.reminder_sent == False, "Reminder should not be marked as sent yet"
        
        # 2nd notification (simulate 30 minutes later)
        print("\n--- Sending 2nd notification (30 min later) ---")
        todo.reminder_first_notification_time = datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=30)
        db.session.commit()
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id in [t.id for t in pending], "2nd notification should be pending"
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        print(f"✓ 2nd notification sent (count: {todo.reminder_notification_count})")
        assert todo.reminder_notification_count == 2
        assert todo.reminder_enabled == True, "Reminder should still be enabled"
        assert todo.reminder_sent == False, "Reminder should not be marked as sent yet"
        
        # 3rd notification (simulate 60 minutes later)
        print("\n--- Sending 3rd notification (60 min later) ---")
        todo.reminder_first_notification_time = datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=60)
        db.session.commit()
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id in [t.id for t in pending], "3rd notification should be pending"
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        print(f"✓ 3rd notification sent (count: {todo.reminder_notification_count})")
        assert todo.reminder_notification_count == 3
        assert todo.reminder_enabled == False, "Reminder should be disabled after 3rd notification"
        assert todo.reminder_sent == True, "Reminder should be marked as sent"
        
        # Try to get pending again - should NOT appear
        print("\n--- Checking for 4th notification ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id not in [t.id for t in pending], "4th notification should NOT be pending"
        print(f"✓ No 4th notification (reminder auto-closed)")
        
        # Cleanup
        db.session.delete(todo)
        db.session.commit()
        print("\n✅ Test 1 passed: Reminders limited to 3 notifications\n")


def test_reminder_auto_close_on_pending_check():
    """Test that reminder auto-closes when count >= 3 during pending check"""
    
    print("\n" + "="*70)
    print("Test 2: Auto-close on Pending Check")
    print("="*70)
    
    with app.app_context():
        user = User.query.filter_by(email='test_reminder_fix@example.com').first()
        
        # Create a todo with notification count already at 3
        todo = Todo(
            name='Test Auto-Close',
            details='Testing auto-close logic',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=5),
            reminder_notification_count=3,
            reminder_first_notification_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=90)
        )
        db.session.add(todo)
        db.session.commit()
        print(f"✓ Created todo with notification_count=3")
        
        # Check pending reminders - should auto-close
        print("\n--- Checking pending reminders ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id not in [t.id for t in pending], "Todo should not be in pending"
        
        # Verify auto-close happened
        todo = Todo.query.get(todo.id)
        print(f"✓ Auto-close triggered (enabled: {todo.reminder_enabled}, sent: {todo.reminder_sent})")
        assert todo.reminder_enabled == False, "Reminder should be disabled"
        assert todo.reminder_sent == True, "Reminder should be marked as sent"
        
        # Cleanup
        db.session.delete(todo)
        db.session.commit()
        print("\n✅ Test 2 passed: Auto-close works during pending check\n")


def test_cancel_reminder():
    """Test that cancel_reminder properly disables reminders"""
    
    print("\n" + "="*70)
    print("Test 3: Cancel Reminder")
    print("="*70)
    
    with app.app_context():
        user = User.query.filter_by(email='test_reminder_fix@example.com').first()
        
        # Create test todo with active reminder
        todo = Todo(
            name='Test Cancel Reminder',
            details='Testing cancel functionality',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=5),
            reminder_notification_count=1,
            reminder_first_notification_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=10)
        )
        db.session.add(todo)
        db.session.commit()
        print(f"✓ Created todo with active reminder (count: {todo.reminder_notification_count})")
        
        # Cancel the reminder
        print("\n--- Cancelling reminder ---")
        result = ReminderService.cancel_reminder(todo.id)
        assert result == True, "Cancel should return True"
        
        # Verify reminder is cancelled
        todo = Todo.query.get(todo.id)
        print(f"✓ Reminder cancelled")
        print(f"  - enabled: {todo.reminder_enabled}")
        print(f"  - sent: {todo.reminder_sent}")
        print(f"  - count: {todo.reminder_notification_count}")
        print(f"  - first_time: {todo.reminder_first_notification_time}")
        
        assert todo.reminder_enabled == False, "Reminder should be disabled"
        assert todo.reminder_sent == True, "Reminder should be marked as sent"
        assert todo.reminder_notification_count == 0, "Count should be reset"
        assert todo.reminder_first_notification_time is None, "First time should be cleared"
        
        # Verify it doesn't appear in pending
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id not in [t.id for t in pending], "Cancelled reminder should not be pending"
        print(f"✓ Cancelled reminder not in pending queue")
        
        # Cleanup
        db.session.delete(todo)
        db.session.commit()
        print("\n✅ Test 3 passed: Cancel reminder works correctly\n")


def test_delete_todo_cancels_reminder():
    """Test that deleting a todo cancels its reminder"""
    
    print("\n" + "="*70)
    print("Test 4: Delete Todo Cancels Reminder")
    print("="*70)
    
    with app.app_context():
        user = User.query.filter_by(email='test_reminder_fix@example.com').first()
        
        # Create test todo with active reminder (first notification, count=0)
        todo = Todo(
            name='Test Delete Todo',
            details='Testing delete cancels reminder',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(minutes=5),
            reminder_notification_count=0  # First notification should be pending
        )
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
        print(f"✓ Created todo with active reminder (ID: {todo_id})")
        
        # Verify it's in pending
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo_id in [t.id for t in pending], "Todo should be in pending"
        print(f"✓ Todo is in pending queue")
        
        # Cancel reminder before deleting (simulating what happens in delete route)
        if todo.reminder_enabled:
            ReminderService.cancel_reminder(todo.id)
            print(f"✓ Reminder cancelled before deletion")
        
        # Delete the todo
        from app.models import Tracker
        Tracker.query.filter_by(todo_id=todo_id).delete()
        db.session.delete(todo)
        db.session.commit()
        print(f"✓ Todo deleted")
        
        # Verify todo is gone
        todo = Todo.query.get(todo_id)
        assert todo is None, "Todo should be deleted"
        
        # Verify it doesn't appear in pending
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo_id not in [t.id for t in pending], "Deleted todo should not be pending"
        print(f"✓ Deleted todo not in pending queue")
        
        print("\n✅ Test 4 passed: Deleting todo cancels reminder\n")


def cleanup_test_data():
    """Clean up any test data"""
    with app.app_context():
        user = User.query.filter_by(email='test_reminder_fix@example.com').first()
        if user:
            # Delete all todos for test user
            todos = Todo.query.filter_by(user_id=user.id).all()
            for todo in todos:
                Tracker.query.filter_by(todo_id=todo.id).delete()
                db.session.delete(todo)
            # Delete test user
            db.session.delete(user)
            db.session.commit()
            print("✓ Cleaned up test data")


if __name__ == '__main__':
    try:
        test_reminder_three_notification_limit()
        test_reminder_auto_close_on_pending_check()
        test_cancel_reminder()
        test_delete_todo_cancels_reminder()
        
        cleanup_test_data()
        
        print("\n" + "="*70)
        print("✅ All reminder fix tests passed!")
        print("="*70 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
