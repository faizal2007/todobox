# Email Deliverability Guide

## Current Implementation Status
✅ **Email Headers Optimized** (v1.1)

The verification email function has been updated with proper headers to maximize deliverability and minimize spam folder placement.

## Email Headers Added

### Critical Headers
- **Reply-To**: Set to SMTP_FROM_EMAIL for proper reply routing
- **X-Priority**: Set to "3" (Normal) to indicate standard importance
- **X-Mailer**: "TodoBox/1.0" - identifies the application sending the email
- **Importance**: Set to "high" for consistent priority across clients
- **X-MSMail-Priority**: "Normal" - for Outlook compatibility
- **List-Unsubscribe-Post**: Indicates one-click unsubscribe support
- **MIME-Version**: "1.0" - proper MIME compliance
- **Content-Type**: "multipart/alternative" - supports both plain text and HTML

### Email Structure
- Plain text version (fallback for old clients)
- HTML version (rich formatting with styling)
- Both versions are equivalent in content, formatted appropriately for their type

### Email Content Improvements
- Professional HTML template with gradient header
- Better visual hierarchy and formatting
- Clear call-to-action button
- Fallback plain text link
- Footer with unsubscribe notice
- Proper character encoding (UTF-8)

## Configuration Requirements

### Environment Variables
Ensure these are set in your `.env` file:

```
SMTP_SERVER=smtp.gmail.com           # Gmail SMTP server
SMTP_PORT=587                         # TLS port
SMTP_USERNAME=your-email@gmail.com   # Your Gmail address
SMTP_PASSWORD=your-app-password      # Gmail app-specific password (NOT your regular password)
SMTP_FROM_EMAIL=noreply@yourdomain   # Sender email address
```

### Gmail Setup for App-Specific Password
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" if not already enabled
3. Go to "App passwords" section
4. Select "Mail" and "Windows Computer" (or your OS)
5. Google will generate a 16-character password
6. Use this password in `SMTP_PASSWORD` (NOT your regular Gmail password)

## Best Practices

### 1. **Sender Reputation**
- Use a consistent sender email address
- Ensure SMTP_FROM_EMAIL matches an authorized sender in your domain
- Monitor bounce rates and unsubscribe rates

### 2. **Content Guidelines**
- Keep subject lines clear and descriptive
- Avoid spam trigger words:
  - "URGENT", "LIMITED TIME", "ACT NOW"
  - Multiple exclamation marks!!!
  - ALL CAPS text
  - Too many links
- Include plain text and HTML versions
- Keep HTML simple and clean
- Avoid large images or attachments

### 3. **Technical Requirements**
- Use TLS encryption (port 587) - ✅ Implemented
- Enable STARTTLS - ✅ Implemented
- Set proper timeouts - ✅ Implemented (10 seconds)
- Use authenticated SMTP - ✅ Implemented

### 4. **Server-Level Configuration** (Advanced)
For production environments, also implement:

#### SPF (Sender Policy Framework)
Add to your domain's DNS:
```
v=spf1 include:gmail.com ~all
```
This tells email providers that Gmail is authorized to send emails on your behalf.

#### DKIM (DomainKeys Identified Mail)
Gmail automatically signs emails with DKIM. Verify it's enabled in your Gmail settings.

#### DMARC (Domain-based Message Authentication, Reporting and Conformance)
Add to your domain's DNS:
```
v=DMARC1; p=quarantine; rua=mailto:admin@yourdomain.com
```
This policy tells providers what to do with emails that fail SPF/DKIM checks.

## Testing Email Delivery

### Local Testing
1. Register with a Gmail account
2. Check the Inbox
3. If email doesn't appear:
   - Check Spam folder
   - Check Promotions tab (for Gmail)
   - Check email headers in the raw message

### Gmail Spam Folder Debugging
1. Open the email in Spam folder
2. Click "Not spam" to train Gmail's filter
3. Check the email headers:
   - Look for "Authentication-Results" header
   - Check if SPF/DKIM/DMARC passed

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Emails going to spam | Ensure SPF/DKIM/DMARC are properly configured at domain level |
| "Authentication failed" | Verify SMTP credentials and app-specific password |
| "Connection timeout" | Check firewall allows port 587, verify SMTP_SERVER setting |
| Bounces/undeliverable | Verify recipient email addresses are valid |
| HTML not rendering | Check email client compatibility, simplify CSS |

## Email Function Reference

**Location**: `app/routes.py` (lines 1016-1120)
**Function**: `send_verification_email(user: User, token: str) -> None`

**Usage**:
```python
from app.routes import send_verification_email
from app.models import User

user = User.query.get(1)
token = generate_verification_token(user)
send_verification_email(user, token)
```

## Monitoring

### Log Messages
The function logs:
- ✅ Success: "Verification email sent successfully to {email}"
- ❌ SMTP Error: "SMTP Error sending verification email to {email}"
- ❌ General Error: "Error sending verification email to {email}"

Check application logs to verify emails are being sent.

## Future Enhancements

- [ ] Add email queue system (Celery/RQ) for async sending
- [ ] Implement email bounce handling
- [ ] Add unsubscribe link tracking
- [ ] Create email templates in database
- [ ] Add email sending statistics dashboard
- [ ] Implement rate limiting to prevent abuse
- [ ] Add email preview functionality in admin

## References

- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SPF Record Guide](https://support.google.com/a/answer/33786)
- [DKIM Configuration](https://support.google.com/a/answer/174124)
- [DMARC Best Practices](https://support.google.com/a/answer/2466563)
- [Email Deliverability Best Practices](https://www.rfc-editor.org/rfc/rfc5321)
