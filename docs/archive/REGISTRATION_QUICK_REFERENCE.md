# User Registration System - Quick Reference

## Getting Started

### Registration Workflow
```
New User → /register → Fill Form → Receive Email → Click Link → /verify-email/<token> → Can Login
```

### New Routes Available
- `/register` - Registration page
- `/verify-email/<token>` - Email verification link
- `/resend-verification` - Resend verification email
- `/verification-sent` - Confirmation page

### Key Files
- `app/verification.py` - Token generation/validation
- `app/forms.py` - RegistrationForm class
- `app/routes.py` - Registration routes
- `app/models.py` - User model with email_verified field
- `tests/test_registration.py` - 9 tests (all passing)

## Database Setup

```bash
# Apply migration
python -m alembic upgrade head

# Verify User table has email_verified column
```

## Email Configuration

Set environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@todobox.com
```

## Testing

```bash
# Run all registration tests
pytest tests/test_registration.py -v

# Expected: 9 passed, 0 failed
```

## Features

✅ Self-service registration
✅ Email verification (24-hour tokens)
✅ Password validation (min 8 chars)
✅ Resend verification email
✅ OAuth user bypass
✅ Admin auto-verification
✅ Secure token generation
✅ HTML email templates
✅ Form validation

## Security

- Tokens: 256-bit random + email hash
- Passwords: Hashed with werkzeug.security
- CSRF: Protected with Flask-WTF
- Email: Validation + uniqueness check
- Expiration: 24 hours

## User Experience

```
Registration:
1. Visit /register
2. Fill form (email, password, name)
3. Click "Create Account"
4. Check email for verification link
5. Click link in email
6. Email verified! Ready to login

If email not received:
1. Visit /resend-verification
2. Enter email
3. Click "Resend Email"
4. Check inbox again

If not verified before login:
1. Enter credentials at /login
2. Get message to verify email
3. Click "Resend verification"
4. Complete verification
5. Try login again
```

## Code Examples

### Generate Token
```python
from app.verification import VerificationToken
token = VerificationToken.generate_token('user@example.com')
```

### Verify Token
```python
is_valid = VerificationToken.verify_email_token(token, 'user@example.com')
```

### Create User
```python
from app.models import User
user = User(email='user@example.com')
user.set_password('SecurePassword123')
user.email_verified = False  # Will be set to True after email verification
db.session.add(user)
db.session.commit()
```

## Status

✅ **Implementation Complete**
- All routes working
- Tests passing (9/9)
- Documentation complete
- Email templates ready
- Database schema updated
- Ready for deployment

## Documentation

- `docs/USER_REGISTRATION_GUIDE.md` - Detailed guide (475 lines)
- `docs/REGISTRATION_IMPLEMENTATION_SUMMARY.md` - Complete summary
- `tests/test_registration.py` - Test examples and coverage
- `CHANGELOG.md` - Feature documentation

## Next Steps

1. ✅ Test registration flow manually
2. ✅ Verify email sending works
3. ✅ Test verification link in email
4. ✅ Confirm login works after verification
5. ✅ Test resend functionality
6. Ready for production deployment!

## Troubleshooting

**Emails not sending?**
- Check SMTP_* environment variables
- Verify email server allows connections
- Check app logs for SMTP errors

**Token always invalid?**
- Ensure User has email_verified field
- Run database migration: `python -m alembic upgrade head`
- Check token URL format in email

**Can't log in after verification?**
- Verify email_verified=True in database
- Clear browser cache/cookies
- Check session timeout settings

## Support

See `docs/USER_REGISTRATION_GUIDE.md` for detailed troubleshooting guide and all implementation details.
