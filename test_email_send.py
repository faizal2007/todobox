#!/usr/bin/env python
"""Test actually sending an email through MailHog"""

import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s'
)

# Load environment
from dotenv import load_dotenv
load_dotenv('.flaskenv')

# Get config
SMTP_SERVER = os.environ.get('SMTP_SERVER', '127.0.0.1')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '1025'))
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', 'noreply@todobox.local')

print("=" * 60)
print("SENDING TEST EMAIL TO MAILHOG")
print("=" * 60)
print(f"\nUsing: {SMTP_FROM_EMAIL} → test@example.com")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")

try:
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'MailHog Test Email'
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = 'test@example.com'
    
    text_content = "This is a test email from TodoBox"
    html_content = "<html><body><p>This is a test email from TodoBox</p></body></html>"
    
    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))
    
    print(f"\n✓ Email message created")
    
    # Send via MailHog
    print(f"\nConnecting to MailHog at {SMTP_SERVER}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5) as server:
        print(f"✓ Connected")
        
        print(f"Sending email...")
        result = server.sendmail(SMTP_FROM_EMAIL, 'test@example.com', msg.as_string())
        print(f"✓ Email sent successfully!")
        print(f"Server result: {result}")
        
    print(f"\n✓ SUCCESS! Check MailHog Web UI at http://127.0.0.1:8025")
        
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
