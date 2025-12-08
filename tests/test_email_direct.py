#!/usr/bin/env python
"""Direct test of email configuration and sending"""

import os
import sys
import logging

# Setup logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv('.flaskenv')

# Now test email config
from app.email_service import (
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, 
    SMTP_FROM_EMAIL, is_email_configured
)

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print(f"\nSMTP_SERVER: {SMTP_SERVER!r}")
print(f"SMTP_PORT: {SMTP_PORT!r}")
print(f"SMTP_USERNAME: {SMTP_USERNAME!r}")
print(f"SMTP_PASSWORD: {'[REDACTED]' if SMTP_PASSWORD else ''}")
print(f"SMTP_FROM_EMAIL: {SMTP_FROM_EMAIL!r}")
print(f"\nis_email_configured(): {is_email_configured()}")

print("\n" + "=" * 60)
print("TESTING SMTP CONNECTION")
print("=" * 60)

import smtplib

try:
    print(f"\nConnecting to {SMTP_SERVER}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        print(f"✓ Connected to SMTP server")
        print(f"Server response: {server.helo()}")
        
        if SMTP_USERNAME and SMTP_PASSWORD:
            print(f"\nAuthentication credentials found, attempting login...")
            server.starttls()
            print(f"✓ TLS enabled")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print(f"✓ Authenticated")
        else:
            print(f"\nNo credentials, connecting without authentication (MailHog mode)")
        
        print(f"\n✓ SMTP connection successful!")
        
except ConnectionRefusedError as e:
    print(f"✗ Connection refused: {e}")
    print(f"  Make sure MailHog is running: mailhog")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
