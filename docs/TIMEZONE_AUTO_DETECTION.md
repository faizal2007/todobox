# Automatic Timezone Detection Feature

## Overview

TodoBox now automatically detects the user's timezone based on their internet location (IP geolocation) when they first register or log in. This ensures that reminders and todo times are displayed correctly without requiring manual timezone configuration.

## How It Works

### User Registration (Direct Login)
1. User creates an account via `/setup/account`
2. System detects user's IP address
3. Queries ip-api.com for timezone information
4. Sets user's timezone automatically
5. User is logged in with correct timezone

### Google OAuth Login
1. User logs in via Google OAuth
2. New user account is created
3. System detects user's IP address  
4. Queries ip-api.com for timezone information
5. Sets user's timezone automatically
6. User is logged in with correct timezone

### Existing Users
- Timezone is only auto-detected on first account creation/login
- Existing users can change their timezone anytime in settings
- The settings page now shows a hint about automatic detection

## Technical Details

### Geolocation Service
- **Service**: ip-api.com (free, no API key required)
- **Rate Limit**: 45 requests per minute per IP
- **Response Time**: ~200ms average
- **Privacy**: No IP logging by default (check their privacy policy)

### Fallback Behavior

1. **If timezone is detected**: Use detected timezone
2. **If IP detection fails**: 
   - Use user's explicit timezone if provided
   - Default to UTC
3. **Localhost/Private IPs**: Skipped (won't attempt geolocation)
   - 127.0.0.1, localhost, 192.168.x.x, 10.x.x.x

### Country to Timezone Mapping
If ip-api.com returns timezone info but it's not in pytz's database, the system has a fallback mapping of countries to default timezones:

```python
COUNTRY_TO_TIMEZONE = {
    'US': 'America/New_York',
    'GB': 'Europe/London',
    'AU': 'Australia/Sydney',
    'MY': 'Asia/Kuala_Lumpur',
    # ... 20+ more countries
}
```

## File Structure

### New Files
```bash
app/geolocation.py          # Core geolocation and timezone detection module
```

### Updated Files
```bash
app/routes.py               # setup_account() - added timezone detection
app/oauth.py                # process_google_callback() - added timezone detection
app/templates/settings.html # Added user notification about auto-detection
```

## Available Timezones

The system supports **433 different timezone options** including:
- All major cities and regions
- DST-aware timezones
- Historical timezone data

Examples:
- Americas: `America/New_York`, `America/Chicago`, `America/Los_Angeles`, etc.
- Europe: `Europe/London`, `Europe/Paris`, `Europe/Berlin`, etc.
- Asia: `Asia/Tokyo`, `Asia/Hong_Kong`, `Asia/Bangkok`, `Asia/Kuala_Lumpur`, etc.
- Africa: `Africa/Cairo`, `Africa/Johannesburg`, etc.
- Australia: `Australia/Sydney`, `Australia/Melbourne`, etc.

## User Experience

### First Login
```bash
[User registers from Malaysia]
    ↓
[System detects IP: 8.8.8.8]
    ↓
[Queries timezone API]
    ↓
[Auto-sets timezone to Asia/Kuala_Lumpur]
    ↓
[User sees notification: "Your timezone is automatically detected..."]
```

### Changing Timezone
Users can always change their timezone in Settings:
1. Go to Settings
2. Find "Timezone Settings" section
3. Select desired timezone
4. Changes take effect immediately

## Reminder Behavior

With automatic timezone detection:
- Reminders are stored in UTC in the database
- When checked, they're converted to user's timezone
- Users see times in their local timezone in the UI
- Example: `2025-12-02T16:20` (user's local) → `2025-12-02 08:20:00` (UTC storage)

## Error Handling

The system gracefully handles various error scenarios:

| Scenario | Behavior |
|----------|----------|
| IP detection API unavailable | Defaults to UTC |
| Localhost/private IP | Skips geolocation (UTC) |
| Invalid timezone returned | Uses country fallback |
| Invalid user timezone | Corrects to detected or UTC |
| Network timeout | Defaults to UTC (3s timeout) |

## Privacy Considerations

- IP addresses are NOT stored or logged
- Only used for timezone detection
- No tracking or analytics
- Users can manually set timezone to override detection
- Works behind proxies (checks `X-Forwarded-For` headers)

## Configuration

No special configuration needed! The feature works out of the box.

Optional: To use a different geolocation service, modify `app/geolocation.py`:
```python
# Replace ip-api.com with your preferred service
response = requests.get(
    'https://your-api.com/json/{ip}',
    # ... configure parameters
)
```

## Testing

Test timezone detection in development:

```python
from app import app
from app.geolocation import detect_timezone_from_ip, get_timezone_for_user

# Test with specific IP
with app.test_request_context(environ_base={'REMOTE_ADDR': '8.8.8.8'}):
    tz = detect_timezone_from_ip()
    print(f"Detected: {tz}")  # Output: America/New_York

# Test timezone correction
tz = get_timezone_for_user('Invalid/Zone')
print(f"Corrected: {tz}")  # Output: UTC or detected timezone
```

## Future Enhancements

Possible improvements:
- Add browser-side timezone detection as fallback
- Cache timezone detections for performance
- Allow admin to disable auto-detection
- Add timezone offset detection (summer time handling)
- Integration with Maxmind GeoLite2 for higher accuracy

## Troubleshooting

**Issue**: Reminders showing wrong time
- **Solution**: Check timezone in Settings - manually correct if needed

**Issue**: Timezone not detected on registration
- **Solution**: Manually set in Settings. Usually only happens if API is down.

**Issue**: Seeing UTC instead of local timezone
- **Possible causes**:
  - API service unavailable
  - Behind a proxy (check X-Forwarded-For header)
  - Localhost/private IP during testing
- **Solution**: Manually set timezone in Settings

## References

- [pytz Documentation](https://pypi.org/project/pytz/)
- [ip-api.com Documentation](https://ip-api.com/docs)
- [IANA Timezone Database](https://www.iana.org/time-zones)
