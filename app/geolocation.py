"""Geolocation utility for detecting user timezone from IP address"""

import requests
from flask import request
import pytz
from typing import Optional, Tuple

# Timezone mapping for country codes to default timezones
COUNTRY_TO_TIMEZONE = {
    'US': 'America/New_York',
    'GB': 'Europe/London',
    'CA': 'America/Toronto',
    'AU': 'Australia/Sydney',
    'DE': 'Europe/Berlin',
    'FR': 'Europe/Paris',
    'IN': 'Asia/Kolkata',
    'JP': 'Asia/Tokyo',
    'SG': 'Asia/Singapore',
    'MY': 'Asia/Kuala_Lumpur',
    'TH': 'Asia/Bangkok',
    'PH': 'Asia/Manila',
    'CN': 'Asia/Shanghai',
    'BR': 'America/Sao_Paulo',
    'MX': 'America/Mexico_City',
    'NZ': 'Pacific/Auckland',
    'ZA': 'Africa/Johannesburg',
    'AE': 'Asia/Dubai',
    'HK': 'Asia/Hong_Kong',
    'KR': 'Asia/Seoul',
    'RU': 'Europe/Moscow',
    'ES': 'Europe/Madrid',
    'IT': 'Europe/Rome',
    'NL': 'Europe/Amsterdam',
    'SE': 'Europe/Stockholm',
    'CH': 'Europe/Zurich',
}


def get_client_ip() -> str:
    """Get the client's IP address from the request, accounting for proxies"""
    # Check for IP from proxy headers first (for use behind reverse proxy)
    x_forwarded = request.headers.get('X-Forwarded-For')
    if x_forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return x_forwarded.split(',')[0].strip()
    
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        return x_real_ip
    
    return request.remote_addr or '127.0.0.1'


def detect_timezone_from_ip() -> Optional[str]:
    """
    Detect user's timezone from their IP address using ip-api.com (free, no API key needed)
    
    Returns:
        Timezone string (e.g., 'America/New_York') or None if detection fails
    """
    try:
        client_ip = get_client_ip()
        
        # Don't try to geolocate localhost/private IPs
        if client_ip in ['127.0.0.1', 'localhost'] or client_ip.startswith('192.168.') or client_ip.startswith('10.'):
            return None
        
        # Use ip-api.com (free, no key needed, allows 45 requests per minute)
        response = requests.get(
            f'http://ip-api.com/json/{client_ip}',
            params={'fields': 'status,timezone,countryCode'},
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                timezone = data.get('timezone')
                
                # Validate timezone against pytz available timezones
                if timezone and timezone in pytz.all_timezones:
                    return timezone
                
                # Fallback to country-based timezone
                country_code = data.get('countryCode')
                if country_code in COUNTRY_TO_TIMEZONE:
                    return COUNTRY_TO_TIMEZONE[country_code]
        
        return None
        
    except requests.RequestException as e:
        # If the API call fails, silently return None
        # This ensures the app doesn't break if the service is unavailable
        print(f"DEBUG: Timezone detection failed: {str(e)}")
        return None
    except Exception as e:
        print(f"DEBUG: Unexpected error in timezone detection: {str(e)}")
        return None


def get_timezone_for_user(user_timezone: Optional[str] = None) -> str:
    """
    Get the appropriate timezone for a user.
    
    If user_timezone is provided and valid, use it.
    Otherwise, detect from IP address.
    If detection fails, default to UTC.
    
    Args:
        user_timezone: Optional timezone string from user settings
        
    Returns:
        Valid timezone string
    """
    # If user has already set a timezone, use it
    if user_timezone and user_timezone in pytz.all_timezones:
        return user_timezone
    
    # Try to detect from IP
    detected = detect_timezone_from_ip()
    if detected:
        return detected
    
    # Default to UTC
    return 'UTC'


def get_timezone_options() -> list:
    """
    Get list of available timezone options for timezone selector.
    
    Returns:
        List of (timezone, display_name) tuples
    """
    timezones = []
    for tz in pytz.common_timezones:
        timezones.append((tz, tz))
    return timezones
