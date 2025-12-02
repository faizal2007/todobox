"""
Reminder service to handle scheduled reminders for todos.
Checks for pending reminders and sends notifications.
"""

from datetime import datetime
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
            List of Todo objects with pending reminders
        """
        query = Todo.query.filter(
            Todo.reminder_enabled == True,
            Todo.reminder_sent == False,
            Todo.reminder_time.isnot(None),
            Todo.reminder_time <= datetime.now()
        )
        
        if user_id:
            query = query.filter(Todo.user_id == user_id)
        
        return query.all()
    
    @staticmethod
    def mark_reminder_sent(todo_id):
        """Mark a reminder as sent
        
        Args:
            todo_id: ID of the todo
        """
        todo = Todo.query.get(todo_id)
        if todo:
            todo.reminder_sent = True
            db.session.commit()
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
                    
                    print(f"Reminder sent for todo {todo.id}: {todo.name}")
            except Exception as e:
                result['errors'].append({
                    'todo_id': todo.id,
                    'error': str(e)
                })
                print(f"Error processing reminder for todo {todo.id}: {str(e)}")
        
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
            Todo.reminder_time.isnot(None)
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
