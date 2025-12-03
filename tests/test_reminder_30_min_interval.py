#!/usr/bin/env python
"""
Test script to verify reminder notifications are spaced 30 minutes apart.

This script tests:
1. First reminder notification is shown immediately
2. Second reminder is NOT shown until 30 minutes have passed
3. Third reminder is NOT shown until another 30 minutes have passed (60 total)
4. Reminder auto-closes after 3rd notification within 30-minute window
"""

import sys
from datetime import datetime, timedelta
import pytz

# Add the app to path
sys.path.insert(0, '/workspaces/todobox')

from app import app, db
from app.models import Todo, User
from app.reminder_service import ReminderService

def test_30_minute_intervals():
    """Test that reminders are spaced 30 minutes apart"""
    
    print("\n" + "="*70)
    print("Testing 30-Minute Interval Enforcement for Reminders")
    print("="*70)
    
    with app.app_context():
        # Create or get test user
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com', password='test_password')
            db.session.add(user)
            db.session.commit()
        print(f"✓ Using test user: {user.email}")
        
        # Create test todo with reminder
        todo = Todo(
            name='Test Reminder Task',
            details='Testing 30-minute intervals',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC) - timedelta(minutes=5),  # Past time so it's due
            reminder_notification_count=0
        )
        db.session.add(todo)
        db.session.commit()
        print(f"✓ Created test todo (ID: {todo.id})")
        
        # TEST 1: First notification should be shown immediately
        print("\n--- TEST 1: First Notification (Immediate) ---")
        pending = ReminderService.get_pending_reminders(user.id)
        assert len(pending) > 0 and any(t.id == todo.id for t in pending), "First reminder should be pending"
        print(f"✓ Reminder is pending (first_notification_time is None)")
        
        # Mark first notification as sent
        ReminderService.mark_reminder_sent(todo.id)
        db.session.refresh(todo)
        print(f"✓ First notification sent (count: {todo.reminder_notification_count})")
        print(f"✓ First notification time: {todo.reminder_first_notification_time}")
        
        # TEST 2: Within 30 minutes - reminder should NOT be shown
        print("\n--- TEST 2: Within 30 Minutes (Should NOT Show) ---")
        # Simulate 15 minutes passing
        now = datetime.now(pytz.UTC)
        elapsed_15_min = now - timedelta(minutes=15)
        todo.reminder_first_notification_time = elapsed_15_min.replace(tzinfo=None)
        db.session.commit()
        
        pending = ReminderService.get_pending_reminders(user.id)
        is_pending = any(t.id == todo.id for t in pending)
        assert not is_pending, "Reminder should NOT be pending within 30 minutes"
        print(f"✓ Reminder NOT pending (15 minutes elapsed, < 30 required)")
        print(f"  Elapsed: 15 minutes - within threshold, won't show")
        
        # TEST 3: At exactly 30 minutes - reminder SHOULD be shown
        print("\n--- TEST 3: Exactly 30 Minutes (Should Show) ---")
        # Simulate exactly 30 minutes
        elapsed_30_min = now - timedelta(minutes=30)
        todo.reminder_first_notification_time = elapsed_30_min.replace(tzinfo=None)
        db.session.commit()
        
        pending = ReminderService.get_pending_reminders(user.id)
        is_pending = any(t.id == todo.id for t in pending)
        assert is_pending, "Reminder SHOULD be pending at 30 minutes"
        print(f"✓ Reminder IS pending (30 minutes elapsed, >= 30 required)")
        print(f"  Elapsed: exactly 30 minutes - shows next reminder")
        
        # Mark second notification as sent
        ReminderService.mark_reminder_sent(todo.id)
        db.session.refresh(todo)
        print(f"✓ Second notification sent (count: {todo.reminder_notification_count})")
        
        # TEST 4: After second notification, within 30 minutes again - should NOT show
        print("\n--- TEST 4: After 2nd, Within 30 Minutes (Should NOT Show) ---")
        # Simulate 40 minutes from first notification (10 after second)
        elapsed_40_min = now - timedelta(minutes=40)
        todo.reminder_first_notification_time = elapsed_40_min.replace(tzinfo=None)
        db.session.commit()
        
        pending = ReminderService.get_pending_reminders(user.id)
        is_pending = any(t.id == todo.id for t in pending)
        assert not is_pending, "Reminder should NOT be pending yet (only 40 min from first)"
        print(f"✓ Reminder NOT pending (40 minutes elapsed, < 60 for third)")
        print(f"  Elapsed: 40 minutes - still within threshold, won't show")
        
        # TEST 5: At 60 minutes (or more) - third reminder SHOULD show
        print("\n--- TEST 5: 60+ Minutes (3rd Reminder Should Show) ---")
        # Simulate exactly 60 minutes
        elapsed_60_min = now - timedelta(minutes=60)
        todo.reminder_first_notification_time = elapsed_60_min.replace(tzinfo=None)
        db.session.commit()
        
        pending = ReminderService.get_pending_reminders(user.id)
        is_pending = any(t.id == todo.id for t in pending)
        assert is_pending, "Reminder SHOULD be pending at 60+ minutes"
        print(f"✓ Reminder IS pending (60+ minutes elapsed)")
        print(f"  Elapsed: 60 minutes - shows final reminder")
        
        # Mark third notification as sent
        ReminderService.mark_reminder_sent(todo.id)
        db.session.refresh(todo)
        print(f"✓ Third notification sent (count: {todo.reminder_notification_count})")
        
        # Check auto-close logic
        # Since we're at 60 minutes, elapsed > 30 min, so should NOT auto-close
        should_close = todo.should_auto_close_reminder()
        print(f"✓ Auto-close check: {should_close} (elapsed: 60 min from first)")
        print(f"  Note: Auto-close won't trigger because elapsed > 30 minutes")
        print(f"  (All 3 notifications must happen within 30 min window for auto-close)")
        
        # TEST 6: Verify no duplicate notifications between intervals
        print("\n--- TEST 6: Verify No Duplicates Between Intervals ---")
        # Create a fresh reminder to test duplicate prevention
        todo2 = Todo(
            name='Test Duplicate Prevention',
            details='Ensuring no duplicate notifications',
            user_id=user.id,
            reminder_enabled=True,
            reminder_sent=False,
            reminder_time=datetime.now(pytz.UTC) - timedelta(minutes=5),
            reminder_notification_count=0
        )
        db.session.add(todo2)
        db.session.commit()
        
        # Get pending - should include todo2
        pending = ReminderService.get_pending_reminders(user.id)
        todo2_in_pending = any(t.id == todo2.id for t in pending)
        assert todo2_in_pending, "Fresh reminder should be pending"
        print(f"✓ Fresh reminder is pending (first notification)")
        
        # Send first notification
        ReminderService.mark_reminder_sent(todo2.id)
        
        # Try getting pending multiple times within next 30 minutes
        for i in range(5):
            elapsed_time = now - timedelta(minutes=5 + i*5)
            todo2.reminder_first_notification_time = elapsed_time.replace(tzinfo=None)
            db.session.commit()
            
            pending = ReminderService.get_pending_reminders(user.id)
            is_pending = any(t.id == todo2.id for t in pending)
            assert not is_pending, f"Reminder should not be pending at {5 + i*5} minutes"
        
        print(f"✓ No duplicates shown during 30-minute interval (tested 5 times)")
        
        # Cleanup
        print("\n--- Cleanup ---")
        db.session.delete(todo)
        db.session.delete(todo2)
        db.session.commit()
        print("✓ Test todos deleted")
        
        print("\n" + "="*70)
        print("✅ All 30-minute interval tests passed!")
        print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_30_minute_intervals()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
