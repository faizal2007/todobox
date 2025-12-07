#!/usr/bin/env python
"""Test email sending through Flask app context"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app and initialize config
from app import app

print("=" * 70)
print("TESTING EMAIL SENDING THROUGH FLASK APP")
print("=" * 70)

with app.app_context():
    print("\n✓ Flask app context created")
    
    # Check Flask config
    print("\nFlask Config:")
    print(f"  SMTP_SERVER: {app.config.get('SMTP_SERVER')!r}")
    print(f"  SMTP_PORT: {app.config.get('SMTP_PORT')!r}")
    print(f"  SMTP_USERNAME: {app.config.get('SMTP_USERNAME')!r}")
    print(f"  SMTP_PASSWORD: {app.config.get('SMTP_PASSWORD')!r}")
    print(f"  SMTP_FROM_EMAIL: {app.config.get('SMTP_FROM_EMAIL')!r}")
    
    # Test email service
    from app.email_service import is_email_configured, _get_smtp_config, send_sharing_invitation
    
    print("\n" + "=" * 70)
    print("EMAIL SERVICE CONFIG CHECK")
    print("=" * 70)
    
    config = _get_smtp_config()
    print(f"\nDynamic config from _get_smtp_config():")
    print(f"  server: {config['server']!r}")
    print(f"  port: {config['port']!r}")
    print(f"  username: {config['username']!r}")
    print(f"  password: {config['password']!r}")
    print(f"  from_email: {config['from_email']!r}")
    
    is_configured = is_email_configured()
    print(f"\nis_email_configured(): {is_configured}")
    
    if not is_configured:
        print("\n✗ EMAIL NOT CONFIGURED!")
        print("Check your .flaskenv file - SMTP settings might be missing")
        sys.exit(1)
    
    print("\n✓ Email is configured")
    
    # Now test actual SMTP connection
    print("\n" + "=" * 70)
    print("TESTING SMTP CONNECTION")
    print("=" * 70)
    
    import smtplib
    
    try:
        print(f"\nConnecting to {config['server']}:{config['port']}...")
        with smtplib.SMTP(config['server'], config['port'], timeout=5) as server:
            print(f"✓ Connected to SMTP server")
            
            if config['username'] and config['password']:
                print(f"Attempting login with credentials...")
                server.starttls()
                server.login(config['username'], config['password'])
                print(f"✓ Authentication successful")
            else:
                print(f"✓ No credentials - using MailHog mode")
            
            print(f"✓ SMTP connection successful!")
    except ConnectionRefusedError as e:
        print(f"✗ Connection refused: {e}")
        print(f"\nMailHog might not be running!")
        print(f"Start MailHog with: mailhog")
        sys.exit(1)
    except Exception as e:
        print(f"✗ SMTP Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test sending a real email
    print("\n" + "=" * 70)
    print("TESTING ACTUAL EMAIL SEND")
    print("=" * 70)
    
    try:
        from app.models import User
        
        # Get or create a test user
        test_user = User.query.filter_by(email='admin@example.com').first()
        if not test_user:
            print("\nNo test user found, creating mock user for testing...")
            test_user = User(email='admin@example.com', fullname='Test User')
            test_user.id = 999  # Mock ID
        
        print(f"Test user: {test_user.email}")
        
        # Create a mock ShareInvitation
        from app.models import ShareInvitation
        import uuid
        
        mock_invitation = ShareInvitation(
            from_user_id=test_user.id,
            to_email='recipient@example.com',
            token=str(uuid.uuid4())
        )
        print(f"Mock invitation created (token: {mock_invitation.token[:8]}...)")
        
        print(f"\nAttempting to send email...")
        success, error = send_sharing_invitation(mock_invitation, test_user)
        
        if success:
            print(f"✓ EMAIL SENT SUCCESSFULLY!")
            print(f"\nCheck MailHog at: http://127.0.0.1:8025")
        else:
            print(f"✗ EMAIL SEND FAILED: {error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error during send test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED!")
print("=" * 70)
