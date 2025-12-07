# Auto-Close Reminder Feature

## Overview

This feature automatically closes reminders after 3 notifications are sent within a 30-minute period. This prevents reminder fatigue and ensures users aren't continuously bothered by the same reminder if they choose not to manually close it.

## How It Works

### Reminder Lifecycle

1. **First Notification** (Notification Count: 1)
   - Reminder triggers when scheduled time is reached
   - User sees standard yellow notification: `(1st reminder)`
   - Bell icon pulses at normal speed (1.5s interval)
   - Standard notification sound plays

2. **Second Notification** (Notification Count: 2)
   - 30-minute timer continues from first notification
   - User sees orange notification: `(2nd reminder)`
   - If 30 minutes haven't elapsed, reminder still shows as pending

3. **Third Notification** (Notification Count: 3)
   - This is the FINAL reminder before auto-close
   - User sees RED critical notification: `(Final reminder - will auto-close after this)`
   - Bell icon pulses FASTER (0.8s interval) to draw attention
   - HIGHER PITCH notification sound plays to indicate urgency
   - Different background color (#fff3cd) with red border

4. **Auto-Close**
   - After 3rd notification is sent, reminder automatically closes
   - User can still manually close notification at any time
   - If 30 minutes pass without reaching 3 notifications, reminder closes anyway

### User Control

Despite auto-close, users have full control:

- **Close Manually**: Click the × button on any notification to immediately close the reminder
- **Disable Reminder**: Users can disable reminders in todo settings before creation
- **Set New Reminder**: After a reminder closes, users can set a new one

## Technical Implementation

### Database Changes

New fields added to `Todo` model:

```python
reminder_notification_count = db.Column(db.Integer, default=0)
reminder_first_notification_time = db.Column(db.DateTime, nullable=True)
```python

**Migration**: `i1234567890_add_reminder_notification_tracking.py`

### Backend Logic

#### `app/models.py` - Todo Model

**New Method**: `should_auto_close_reminder()`
```python
def should_auto_close_reminder(self):
    """Check if reminder should be automatically closed (3 notifications in 30 minutes)"""
    if self.reminder_notification_count >= 3 and self.reminder_first_notification_time:
        elapsed_time = datetime.now() - self.reminder_first_notification_time
        # If 3 notifications sent within 30 minutes, auto-close
        if elapsed_time.total_seconds() <= 30 * 60:  # 30 minutes = 1800 seconds
            return True
    return False
```python

#### `app/reminder_service.py` - ReminderService

**Updated `mark_reminder_sent()` Method**:
- Increments `reminder_notification_count`
- Records `reminder_first_notification_time` on first notification
- Calls `should_auto_close_reminder()` to check if limit reached
- Automatically disables and closes reminder if 3 notifications sent within 30 minutes

**Updated `get_pending_reminders()` Method**:
- Checks each reminder with `should_auto_close_reminder()`
- Auto-closes any that have exceeded the limit
- Filters them out from pending list to prevent infinite notifications

### API Endpoints

#### `/api/reminders/check` (GET)

Response now includes:
```json
{
  "count": 1,
  "reminders": [
    {
      "todo_id": 1,
      "title": "Complete project",
      "details": "Finish the quarterly report",
      "reminder_time": "2025-12-03T14:30:00",
      "notification_count": 2,
      "is_last_notification": true
    }
  ]
}
```yaml

**New Fields**:
- `notification_count`: How many times user has been notified (0, 1, 2, or 3)
- `is_last_notification`: Boolean indicating if this is the 3rd/final notification

#### `/api/reminders/process` (POST)

Response includes notification count and auto-close info:
```json
{
  "count": 1,
  "notifications": [
    {
      "todo_id": 1,
      "title": "Reminder: Complete project",
      "message": "Your task 'Complete project' is due! (Final reminder - will auto-close after this)",
      "reminder_time": "2025-12-03T14:30:00",
      "notification_count": 3,
      "is_last_notification": true
    }
  ]
}
```yaml

**Enhanced Message**: Message now includes:
- `(1st reminder)` for first notification
- `(2nd reminder)` for second notification
- `(Final reminder - will auto-close after this)` for third notification

### Frontend Changes

#### `app/templates/main.html` - `showReminderNotification()` Function

**Visual Enhancements**:

1. **Color Coding**:
   - 1st & 2nd reminders: Orange (#ff9800) - warning level
   - 3rd reminder: Red (#ff5555) - critical level

2. **Animation**:
   - Standard reminders: Bell pulses every 1.5 seconds
   - Final reminder: Bell pulses every 0.8 seconds (faster)

3. **Sound**:
   - Standard reminders: 800Hz tone for 0.5 seconds
   - Final reminder: 1000Hz tone (higher pitch) for 0.7 seconds

4. **Notification Display**:
   - Shows count like `(1st reminder)`, `(2nd reminder)`, `(Final reminder - will auto-close after this)`
   - Changes box-shadow color based on urgency
   - Browser notification title shows `(Final Reminder)` for last notification

## Testing the Feature

### Manual Testing Steps

1. **Create a reminder** that triggers in 1-2 minutes
2. **Wait for first notification** - verify it says "(1st reminder)"
3. **Click elsewhere** (don't close the notification)
4. **Wait ~2 seconds** and check if another reminder is pending
5. **Second notification shows** - verify it says "(2nd reminder)"
6. **Repeat step 3-4** 
7. **Third notification shows** - verify it says "(Final reminder...)"
8. **Note the styling**:
   - Red border instead of orange
   - Faster bell pulse
   - Different sound (higher pitch)
9. **Wait 10 seconds** - notification auto-dismisses
10. **Check reminder status** - should be closed (no more pending reminders)

### Edge Cases

- **Manually close before 3rd**: Click × button - reminder closes immediately
- **30-minute timeout**: If less than 3 notifications in 30 minutes, reminder auto-closes anyway
- **Multiple reminders**: Each todo has independent notification count
- **Browser offline**: Sound/notification might not play, but counter still tracks

## Database Schema

```sql
ALTER TABLE todo ADD COLUMN reminder_notification_count INT DEFAULT 0;
ALTER TABLE todo ADD COLUMN reminder_first_notification_time DATETIME;
```sql

## Configuration

The auto-close behavior is hardcoded with these constants:

- **Maximum notifications**: 3
- **Time window**: 30 minutes (1800 seconds)

To modify these values in the future, update:

1. **Backend**: `app/models.py` - `should_auto_close_reminder()` method (line with "30 * 60")
2. **Frontend**: `app/templates/main.html` - `showReminderNotification()` function (notification_count >= 3 check)

## Backward Compatibility

- Existing reminders will have `reminder_notification_count = 0` and `reminder_first_notification_time = NULL`
- These reminders will behave normally (no auto-close) until first notification is sent
- After first notification, counter starts tracking

## Future Enhancements

Potential improvements:

1. **User-configurable limits**:
   - Allow users to set max notifications (1, 2, 3, 5, etc.)
   - Allow users to set time window (15, 30, 60 minutes)

2. **Reminder persistence**:
   - Option to "snooze" reminder instead of closing it
   - Reschedule reminder for later

3. **Statistics**:
   - Track how many reminders users typically dismiss before auto-close
   - Use data to optimize default limits

4. **Smart timing**:
   - Increase interval between notifications (1st at time, 2nd after 5min, 3rd after 15min)
   - Detect if user is active or inactive

## Troubleshooting

### Reminder not auto-closing
- Check browser console for JavaScript errors
- Verify database migration was applied: `python -m flask db current`
- Check that `reminder_notification_count` field exists: `DESCRIBE todo;`

### Wrong notification count
- Clear browser cache
- Verify backend restarted after code deploy
- Check that correct version is running

### Sound not playing
- Check browser audio settings
- Verify notification permissions granted
- Some browsers require user interaction before audio context works

## References

- Database schema changes: `/workspaces/todobox/migrations/versions/i1234567890_add_reminder_notification_tracking.py`
- Model implementation: `/workspaces/todobox/app/models.py` (lines 225-310)
- Reminder service: `/workspaces/todobox/app/reminder_service.py`
- API endpoints: `/workspaces/todobox/app/routes.py` (lines 92-165)
- Frontend implementation: `/workspaces/todobox/app/templates/main.html` (lines 80-280)
