#!/usr/bin/env python
"""
Test script to verify auto-close reminder functionality.

This script tests:
1. Reminder notification counter increments correctly
2. Auto-close triggers after 3 notifications within 30 minutes
3. Reminders close properly when auto-close condition is met
4. Edge cases like 30-minute timeout
"""

import sys
from datetime import datetime, timedelta
import pytz

# Add the app to path
sys.path.insert(0, '/workspaces/todobox')

from app import app, db
from app.models import Todo, User
from app.reminder_service import ReminderService

def test_reminder_auto_close():
    """Test auto-close reminder functionality"""
    
    print("\n" + "="*60)
    print("Testing Auto-Close Reminder Feature")
    print("="*60)
    
    with app.app_context():
        # Create or get test user
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com')
            user.set_password('test123')
            db.session.add(user)  # type: ignore[attr-defined]
            db.session.commit()  # type: ignore[attr-defined]
            print("✓ Created test user")
        else:
            print("✓ Using existing test user")
        
        # Create a test todo with reminder
        todo = Todo(
            name="Test Auto-Close Reminder",
            details="Testing the auto-close feature",
            user_id=user.id,
            reminder_enabled=True,
            reminder_time=datetime.now(pytz.UTC).replace(tzinfo=None) - timedelta(seconds=10),  # Time already passed
            reminder_sent=False,
            reminder_notification_count=0
        )
        db.session.add(todo)  # type: ignore[attr-defined]
        db.session.commit()  # type: ignore[attr-defined]
        print(f"✓ Created test todo (ID: {todo.id})")
        
        # Test 1: Check if todo appears in pending reminders
        print("\n--- Test 1: Check Pending Reminders ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert len(pending) > 0, "No pending reminders found"
        assert todo.id in [t.id for t in pending], "Test todo not in pending reminders"
        print(f"✓ Found {len(pending)} pending reminder(s)")
        print(f"✓ Test todo is pending (notification_count: {todo.reminder_notification_count})")
        
        # Test 2: Send first notification
        print("\n--- Test 2: Send First Notification ---")
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        assert todo.reminder_notification_count == 1, f"Expected count 1, got {todo.reminder_notification_count}"
        assert todo.reminder_first_notification_time is not None, "First notification time not set"
        assert not todo.should_auto_close_reminder(), "Should not auto-close after 1st notification"
        print(f"✓ First notification sent (count: {todo.reminder_notification_count})")
        print(f"✓ First notification time recorded: {todo.reminder_first_notification_time}")
        print(f"✓ Auto-close condition NOT met (count: {todo.reminder_notification_count} < 3)")
        
        # Test 3: Send second notification
        print("\n--- Test 3: Send Second Notification ---")
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        assert todo.reminder_notification_count == 2, f"Expected count 2, got {todo.reminder_notification_count}"
        assert not todo.should_auto_close_reminder(), "Should not auto-close after 2nd notification"
        print(f"✓ Second notification sent (count: {todo.reminder_notification_count})")
        print(f"✓ Auto-close condition NOT met (count: {todo.reminder_notification_count} < 3)")
        
        # Test 4: Send third notification - should trigger auto-close
        print("\n--- Test 4: Send Third Notification (AUTO-CLOSE) ---")
        ReminderService.mark_reminder_sent(todo.id)
        todo = Todo.query.get(todo.id)
        assert todo.reminder_notification_count == 3, f"Expected count 3, got {todo.reminder_notification_count}"
        assert todo.should_auto_close_reminder(), "Auto-close condition should be met"
        assert not todo.reminder_enabled, "Reminder should be disabled"
        assert todo.reminder_sent, "Reminder should be marked as sent"
        print(f"✓ Third notification sent (count: {todo.reminder_notification_count})")
        print(f"✓ Auto-close condition MET (count: 3, within 30 minutes)")
        print(f"✓ Reminder automatically disabled (reminder_enabled: {todo.reminder_enabled})")
        print(f"✓ Reminder marked as sent (reminder_sent: {todo.reminder_sent})")
        
        # Test 5: Verify it doesn't appear in pending reminders anymore
        print("\n--- Test 5: Verify Auto-Closed Reminder Not Pending ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert todo.id not in [t.id for t in pending], "Auto-closed todo should not be pending"
        print(f"✓ Auto-closed reminder removed from pending queue")
        print(f"✓ Remaining pending reminders: {len(pending)}")
        
        # Test 6: Reset and test 30-minute timeout
        print("\n--- Test 6: Test 30-Minute Timeout ---")
        todo.reminder_enabled = True
        todo.reminder_sent = False
        todo.reminder_notification_count = 3
        # Set first notification time to 31 minutes ago
        todo.reminder_first_notification_time = datetime.now() - timedelta(minutes=31)
        db.session.commit()  # type: ignore[attr-defined]
        
        # Should NOT auto-close because 30+ minutes have passed
        should_close = todo.should_auto_close_reminder()
        assert not should_close, "Should not auto-close after 30 minute window"
        print(f"✓ 3 notifications but > 30 minutes elapsed: NO auto-close")
        print(f"✓ First notification time: {todo.reminder_first_notification_time}")
        print(f"✓ Elapsed time: > 30 minutes")
        
        # Test 7: Test edge case - exactly 30 minutes
        print("\n--- Test 7: Test Exactly 30-Minute Boundary ---")
        # Set first notification time to exactly 30 minutes ago + 1 second buffer for execution time
        todo.reminder_first_notification_time = datetime.now() - timedelta(seconds=1799)  # Just under 30 min
        db.session.commit()  # type: ignore[attr-defined]
        
        # Should still auto-close (1799 seconds < 1800 seconds)
        should_close = todo.should_auto_close_reminder()
        assert should_close, "Should auto-close when within 30 minute window"
        print(f"✓ 3 notifications within 30 minute window: SHOULD auto-close")
        
        # Test 8: Test just over 30 minutes (should NOT auto-close)
        print("\n--- Test 8: Test Just Over 30-Minute Boundary ---")
        todo.reminder_first_notification_time = datetime.now() - timedelta(seconds=1801)  # Just over 30 min
        db.session.commit()  # type: ignore[attr-defined]
        
        should_close = todo.should_auto_close_reminder()
        assert not should_close, "Should NOT auto-close after 30 minute window"
        print(f"✓ 3 notifications but > 30 minutes elapsed: NO auto-close")
        
        # Cleanup
        print("\n--- Cleanup ---")
        db.session.delete(todo)  # type: ignore[attr-defined]
        db.session.commit()  # type: ignore[attr-defined]
        print("✓ Test todo deleted")
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")

if __name__ == '__main__':
    try:
        test_reminder_auto_close()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
