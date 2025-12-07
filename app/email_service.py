"""
Email Service for sending sharing invitation links via Gmail API
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for, render_template_string

# Setup logging
logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # App-specific password for Gmail
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')

# HTML email template for sharing invitation
INVITATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #4a90d9; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }
        .content { background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }
        .button { display: inline-block; padding: 12px 24px; margin: 10px 5px; text-decoration: none; border-radius: 5px; font-weight: bold; }
        .accept { background-color: #28a745; color: white; }
        .decline { background-color: #dc3545; color: white; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TodoBox Sharing Invitation</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p><strong>{{ from_user_name }}</strong> ({{ from_user_email }}) would like to share their todos with you on TodoBox.</p>
            <p>If you accept this invitation, you will be able to view their todos in your TodoBox dashboard.</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ accept_url }}" class="button accept">Accept Invitation</a>
                <a href="{{ decline_url }}" class="button decline">Decline</a>
            </p>
            <p><small>This invitation will expire in 7 days.</small></p>
            <p><small>If you don't have a TodoBox account, you'll need to sign in first.</small></p>
        </div>
        <div class="footer">
            <p>This email was sent from TodoBox. If you didn't expect this invitation, you can safely ignore it.</p>
        </div>
    </div>
</body>
</html>
"""

# Plain text email template (fallback)
INVITATION_TEMPLATE_TEXT = """
TodoBox Sharing Invitation

Hello,

{{ from_user_name }} ({{ from_user_email }}) would like to share their todos with you on TodoBox.

If you accept this invitation, you will be able to view their todos in your TodoBox dashboard.

Accept Invitation: {{ accept_url }}
Decline: {{ decline_url }}

This invitation will expire in 7 days.

If you don't have a TodoBox account, you'll need to sign in first.

---
This email was sent from TodoBox. If you didn't expect this invitation, you can safely ignore it.
"""


def is_email_configured():
    """Check if email sending is properly configured"""
    # SMTP_SERVER and SMTP_PORT are required, but USERNAME/PASSWORD are optional (for MailHog)
    # SMTP_FROM_EMAIL is required to send from
    configured = all([SMTP_SERVER, SMTP_PORT, SMTP_FROM_EMAIL])
    logger.debug(f"Email configured check: {configured} (server={SMTP_SERVER}, port={SMTP_PORT}, from={SMTP_FROM_EMAIL})")
    return configured


def send_sharing_invitation(invitation, from_user):
    """
    Send a sharing invitation email
    
    Args:
        invitation: ShareInvitation model instance
        from_user: User model instance (sender)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    logger.info(f"Attempting to send email to {invitation.to_email} from {from_user.email}")
    
    if not is_email_configured():
        msg = "Email service is not configured. Please configure SMTP settings."
        logger.error(msg)
        return False, msg
    
    try:
        logger.debug(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
        
        # Generate URLs for accept/decline actions
        accept_url = url_for('accept_share_invitation', token=invitation.token, _external=True)
        decline_url = url_for('decline_share_invitation', token=invitation.token, _external=True)
        
        # Get sender's display name and escape for safety
        from html import escape
        from markupsafe import Markup
        
        from_user_name = escape(from_user.fullname or from_user.email)
        from_user_email = escape(from_user.email)
        
        # Create safe context for template rendering
        template_context = {
            'from_user_name': from_user_name,
            'from_user_email': from_user_email,
            'accept_url': accept_url,  # URLs are already safe from url_for
            'decline_url': decline_url
        }
        
        # Render email templates with escaped data
        html_content = render_template_string(
            INVITATION_TEMPLATE,
            **template_context
        )
        
        text_content = render_template_string(
            INVITATION_TEMPLATE_TEXT,
            **template_context
        )
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{from_user_name} wants to share their todos with you"
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = invitation.to_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logger.debug(f"Connected to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
            
            # Only use TLS and login if credentials are provided (not needed for MailHog)
            if SMTP_USERNAME and SMTP_PASSWORD:
                logger.debug("Using TLS and authentication")
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            else:
                logger.debug("No credentials provided, sending without authentication (MailHog mode)")
            
            logger.info(f"Sending email from {SMTP_FROM_EMAIL} to {invitation.to_email}")
            server.sendmail(SMTP_FROM_EMAIL, invitation.to_email, msg.as_string())
            logger.info(f"Email sent successfully to {invitation.to_email}")
        
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        msg = "Failed to authenticate with email server. Please check SMTP credentials."
        logger.error(f"SMTP Auth Error: {str(e)}")
        return False, msg
    except smtplib.SMTPRecipientsRefused as e:
        msg = f"The email address {invitation.to_email} was rejected by the server."
        logger.error(f"SMTP Recipients Refused: {str(e)}")
        return False, msg
    except smtplib.SMTPException as e:
        msg = f"Failed to send email: {str(e)}"
        logger.error(f"SMTP Exception: {str(e)}")
        return False, msg
    except Exception as e:
        msg = f"An unexpected error occurred: {str(e)}"
        logger.exception(f"Unexpected error sending email: {str(e)}")
        return False, msg


def get_invitation_link(invitation):
    """
    Generate a sharing invitation link that can be manually shared
    
    Args:
        invitation: ShareInvitation model instance
    
    Returns:
        str: The accept invitation URL
    """
    return url_for('accept_share_invitation', token=invitation.token, _external=True)
