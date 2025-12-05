"""
Reminder service to handle scheduled reminders for todos.
Checks for pending reminders and sends notifications.
"""

from datetime import datetime
import pytz
import logging
from sqlalchemy import and_, not_
from app import db
from app.models import Todo, User
from flask import current_app

class ReminderService:
    """Service to manage todo reminders"""
    
    @staticmethod
    def get_pending_reminders(user_id=None):
        """Get all pending reminders for a user or all users
        
        Args:
            user_id: Optional user ID to filter reminders
            
        Returns:
            List of Todo objects with pending reminders (excluding auto-closed ones)
        """
        query = Todo.query.filter(
            and_(
                Todo.reminder_enabled == True,
                Todo.reminder_sent == False,
                Todo.reminder_time != None
            )
        )
        
        if user_id:
            query = query.filter(Todo.user_id == user_id)
        
        # Get current time in UTC for comparison (reminder_time is stored in UTC)
        now = datetime.now(pytz.UTC).replace(tzinfo=None)
        
        # Filter by reminder time - only include reminders where time has passed
        # reminder_time is stored as UTC, so we compare against UTC now
        results = []
        for todo in query.all():
            if todo.reminder_time and todo.reminder_time < now:
                notification_count = todo.reminder_notification_count or 0
                
                # Auto-close if already sent 3 notifications
                if notification_count >= 3:
                    # Auto-close the reminder
                    todo.reminder_enabled = False
                    todo.reminder_sent = True
                    db.session.commit()  # type: ignore[attr-defined]
                    logging.info(f"Auto-closed reminder for todo {todo.id} after 3 notifications")
                elif notification_count == 0:
                    # First notification - always show
                    results.append(todo)
                elif todo.reminder_first_notification_time:
                    # For subsequent notifications, check if appropriate time has passed
                    # 2nd reminder: needs 30 min elapsed
                    # 3rd reminder: needs 60 min elapsed
                    elapsed_time = now - todo.reminder_first_notification_time
                    required_elapsed_seconds = notification_count * 30 * 60  # 1st=0, 2nd=1800, 3rd=3600, etc
                    
                    if elapsed_time.total_seconds() >= required_elapsed_seconds:
                        # Only show up to 3 reminders total
                        if notification_count < 3:
                            results.append(todo)
        
        return results
    
    @staticmethod
    def mark_reminder_sent(todo_id):
        """Mark a reminder as sent and track notification count
        
        Args:
            todo_id: ID of the todo
        """
        todo = Todo.query.get(todo_id)
        if todo:
            # Increment notification count
            if todo.reminder_notification_count is None:
                todo.reminder_notification_count = 0
            todo.reminder_notification_count += 1
            
            # Track first notification time
            if todo.reminder_first_notification_time is None:
                todo.reminder_first_notification_time = datetime.now(pytz.UTC).replace(tzinfo=None)
            
            # Auto-close after 3rd notification
            if todo.reminder_notification_count >= 3:
                todo.reminder_enabled = False
                todo.reminder_sent = True
                logging.info(f"Auto-closed reminder for todo {todo_id} after 3 notifications")
            
            db.session.add(todo)  # type: ignore[attr-defined]
            db.session.flush()  # type: ignore[attr-defined]
            db.session.commit()  # type: ignore[attr-defined]
            return True
        return False
    
    @staticmethod
    def cancel_reminder(todo_id):
        """Cancel a reminder (disable it and clear all tracking)
        
        Args:
            todo_id: ID of the todo
            
        Returns:
            bool: True if reminder was cancelled successfully, False otherwise
        """
        todo = Todo.query.get(todo_id)
        if todo and todo.reminder_enabled:
            # Disable the reminder and clear all tracking
            todo.reminder_enabled = False
            todo.reminder_sent = True  # Mark as sent to prevent further notifications
            todo.reminder_notification_count = 0
            todo.reminder_first_notification_time = None
            db.session.commit()  # type: ignore[attr-defined]
            logging.info(f"Reminder cancelled for todo {todo_id}")
            return True
        return False
    
    @staticmethod
    def process_reminders():
        """Process all pending reminders and send notifications
        
        Returns:
            Dict with notification details
        """
        pending_reminders = ReminderService.get_pending_reminders()
        
        result = {
            'total': len(pending_reminders),
            'processed': 0,
            'errors': []
        }
        
        for todo in pending_reminders:
            try:
                # Create notification
                notification = ReminderService.create_notification(todo)
                
                if notification:
                    # Mark reminder as sent
                    ReminderService.mark_reminder_sent(todo.id)
                    result['processed'] += 1
                    
                    logging.info(f"Reminder sent for todo {todo.id}: {todo.name}")
            except Exception as e:
                result['errors'].append({
                    'todo_id': todo.id,
                    'error': str(e)
                })
                logging.error(f"Error processing reminder for todo {todo.id}: {str(e)}")
        
        return result
    
    @staticmethod
    def create_notification(todo):
        """Create a notification for a reminder
        
        Args:
            todo: Todo object with pending reminder
            
        Returns:
            Notification dict or None
        """
        notification = {
            'todo_id': todo.id,
            'user_id': todo.user_id,
            'title': f"Reminder: {todo.name}",
            'message': f"Your task '{todo.name}' is due soon",
            'timestamp': datetime.now(),
            'read': False
        }
        
        return notification
    
    @staticmethod
    def get_user_reminders(user_id):
        """Get all reminders for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            List of reminder dicts
        """
        todos = Todo.query.filter(
            Todo.user_id == user_id,
            Todo.reminder_enabled == True,
            Todo.reminder_time != None  # type: ignore[comparison-overlap]
        ).all()
        
        reminders = []
        for todo in todos:
            reminder = {
                'todo_id': todo.id,
                'todo_title': todo.name,
                'reminder_time': todo.reminder_time.isoformat() if todo.reminder_time else None,
                'is_pending': todo.has_pending_reminder(),
                'is_sent': todo.reminder_sent
            }
            reminders.append(reminder)
        
        return reminders
