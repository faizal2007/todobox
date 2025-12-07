# Timezone Integration for Reminders

## Overview

The TodoBox application now has complete timezone support for reminders. Users can set their local timezone in settings, and all reminders will be correctly converted between their local time and UTC storage, with proper display in notifications and edit forms.

## Features Implemented

### 1. User Timezone Setting
- **Location**: Settings page (`/settings`)
- **Timezone Options**: 43 different timezones across 7 regions
  - UTC
  - Americas (10 zones: EST, CST, MST, PST, AKT, HST, Canada, Mexico, South America)
  - Europe (12 zones: UK, France, Germany, Spain, Italy, Netherlands, Austria, Czech, Hungary, Turkey, Russia)
  - Asia (9 zones: UAE, India, Thailand, Singapore, Hong Kong, China, Japan, Korea, Malaysia)
  - Africa (3 zones: Egypt, South Africa, Nigeria)
  - Oceania (2 zones: New Zealand, Fiji)
- **Storage**: User.timezone field (String(50), defaults to 'UTC')
- **Validation**: Backend whitelist of 41 valid timezone strings

### 2. Reminder Time Conversion Flow

#### When Creating/Editing a Reminder

1. User sets reminder time in their local timezone via form
2. Backend converts local time to UTC using `convert_from_user_timezone()`
3. UTC time is stored in database (todo.reminder_time)

```python
# Example flow for America/New_York timezone:
User sets reminder: 2:00 PM EST (local)
Convert to UTC: 7:00 PM UTC
Store in DB: 2025-01-15 19:00:00
```

#### When Displaying Reminder

1. UTC time retrieved from database
2. Backend converts UTC to user's timezone using `convert_to_user_timezone()`
3. Converted time displayed in form, notifications, and API responses

```python
# Example display flow:
Stored in DB: 2025-01-15 19:00:00 UTC
User timezone: America/New_York
Convert to user: 2:00 PM EST
Display in form: Shows as 2:00 PM local time
```

#### When Checking Pending Reminders

1. Get current time in user's timezone
2. Compare against reminder_time in UTC
3. Notification shows time in user's local timezone

### 3. Core Components

#### Timezone Utilities (`app/timezone_utils.py`)
- `convert_to_user_timezone(dt, user_timezone)` - UTC → User Local
- `convert_from_user_timezone(dt, user_timezone)` - User Local → UTC
- `get_user_local_time(user)` - Get current time in user's timezone
- All functions include error handling and return None gracefully on errors

#### Reminder Service (`app/reminder_service.py`)
- Updated `get_pending_reminders()` to check in user's local timezone
- Compares reminder times against current time in user's timezone
- Handles multiple users with different timezone settings

#### API Endpoints

##### `/api/reminders/check` (GET)
- Returns pending reminders with times converted to user's timezone
- Used by frontend to check for reminders every 30 seconds
- Response includes reminder_time in user's local timezone

##### `/api/reminders/process` (POST)
- Marks reminders as sent
- Returns notifications with times displayed in user's local timezone
- Used to trigger browser and in-app notifications

#### Route Handlers

##### `/add` (POST)
- Handles both creating new reminders and editing existing ones
- Converts reminder_datetime from user's local timezone to UTC
- Stores converted UTC time in database

##### `/getTodo` (POST)
- Retrieves todo for editing
- Converts reminder_time from UTC back to user's timezone
- Form displays reminder time in user's local timezone

##### `/settings` (POST)
- Accepts timezone parameter
- Validates against whitelist of valid timezones
- Stores in user.timezone field

### 4. Database Schema

#### User Model
```python
timezone = db.Column(db.String(50), default='UTC')
```

#### Todo Model
```python
reminder_enabled = db.Column(db.Boolean, default=False)
reminder_time = db.Column(db.DateTime)  # Always stored in UTC
reminder_sent = db.Column(db.Boolean, default=False)
```

### 5. UI Components

#### Settings Form (`templates/settings.html`)
- Timezone selector with 43 options
- Current timezone pre-selected
- Form POSTs to `/settings`
- Success/error messages on save

#### Todo Add Form (`templates/todo_add.html`)
- Reminder checkbox to enable/disable
- Reminder type selector: "Custom Time" or "Before Target"
- Custom Time: datetime-local input (user's local timezone)
- Before Target: offset selector (minutes/hours/days)
- Dynamic visibility based on selected type

#### Notification System (`templates/main.html`)
- 30-second polling interval to check for reminders
- In-app toast notifications showing reminder in user's timezone
- Desktop browser notifications (with permission)
- Toast auto-dismisses after 8 seconds

## Testing Checklist

- [x] Timezone utilities convert times correctly
- [x] User can set timezone in settings
- [x] Timezone is stored in database
- [x] Reminder creation uses timezone conversion
- [x] Reminder editing uses timezone conversion
- [x] getTodo response converts reminder times for display
- [x] Reminder API endpoints use timezone conversion
- [x] Notification system displays times correctly
- [x] Multiple users with different timezones work independently

## Edge Cases Handled

1. **Invalid timezone strings**: Gracefully falls back to 'UTC'
2. **Daylight saving time**: pytz handles automatically
3. **User changing timezone**: Existing reminders stored as UTC, will show in new timezone
4. **Missing reminder time**: Null checks throughout to prevent errors
5. **Shared todos**: Timezone is still user-specific (each user sees in their timezone)

## Files Modified

- `app/models.py` - Added timezone field to User model
- `app/routes.py` - Updated /add, getTodo, /settings, /api/reminders/* endpoints
- `app/reminder_service.py` - Added timezone awareness to reminder checking
- `app/templates/settings.html` - Added timezone selector form
- `app/templates/todo_add.html` - Reminder form uses timezone input (existing)
- `app/templates/main.html` - Notification system (existing)
- `app/timezone_utils.py` - NEW: Core timezone conversion utilities
- `migrations/versions/h1234567890_add_timezone_field_to_user.py` - NEW: Database migration

## Future Enhancements

1. Auto-detect user timezone from browser geolocation
2. Show timezone abbreviation in UI (e.g., "EST", "JST")
3. Batch convert multiple reminders for performance
4. Add timezone to shared todo view (show both owner and viewer timezone)
5. Timezone history for reminders (track timezone at time of creation)

## Deployment Notes

1. Run migration: `python -m flask db upgrade`
2. Existing users get default timezone 'UTC'
3. All existing reminder times will be treated as UTC
4. New reminders will be created with proper timezone conversion

## Support

For timezone issues:
1. Check user's timezone setting in `/settings`
2. Verify server timezone (should not affect functionality)
3. Check browser console for any errors
4. Verify reminder is enabled (reminder_enabled = True)
5. Test with `/api/reminders/check` to see pending reminders
