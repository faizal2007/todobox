"""
Timezone utility functions for converting between UTC and user timezones.
"""

from datetime import datetime
import pytz
import logging

def convert_to_user_timezone(dt, user_timezone='UTC'):
    """
    Convert a datetime from UTC to user's timezone.
    
    Args:
        dt: datetime object (assumed to be in UTC)
        user_timezone: User's timezone string (e.g., 'America/New_York')
        
    Returns:
        datetime object in user's timezone
    """
    if dt is None:
        return None
    
    try:
        # If datetime is naive, assume it's UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            # Convert to UTC first if it has timezone info
            dt = dt.astimezone(pytz.UTC)
        
        # Convert to user's timezone
        user_tz = pytz.timezone(user_timezone)
        return dt.astimezone(user_tz)
    except Exception as e:
        logging.error(f"Timezone conversion error: {e}")
        return dt

def convert_from_user_timezone(dt, user_timezone='UTC'):
    """
    Convert a datetime from user's timezone to UTC.
    
    Args:
        dt: datetime object (in user's timezone)
        user_timezone: User's timezone string (e.g., 'America/New_York')
        
    Returns:
        datetime object in UTC
    """
    if dt is None:
        return None
    
    try:
        # If datetime is naive, assume it's in user's timezone
        if dt.tzinfo is None:
            user_tz = pytz.timezone(user_timezone)
            dt = user_tz.localize(dt)
        
        # Convert to UTC
        return dt.astimezone(pytz.UTC).replace(tzinfo=None)
    except Exception as e:
        logging.error(f"Timezone conversion error: {e}")
        return dt

def get_user_local_time(user):
    """
    Get current time in user's timezone.
    
    Args:
        user: User object
        
    Returns:
        datetime object in user's local timezone
    """
    user_tz = pytz.timezone(user.timezone or 'UTC')
    return datetime.now(user_tz)
