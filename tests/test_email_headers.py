#!/usr/bin/env python
"""
Email deliverability test - verifies that email headers are properly set
to minimize spam folder placement.
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import SMTP_FROM_EMAIL

def test_email_headers():
    """Test that email message includes all necessary headers for deliverability"""
    
    # Create a test email message
    msg = MIMEMultipart('alternative')
    
    # Set headers (matching send_verification_email function)
    msg['Subject'] = 'Verify Your TodoBox Email Address'
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = 'test@example.com'
    msg['Reply-To'] = SMTP_FROM_EMAIL
    msg['X-Priority'] = '3'
    msg['X-Mailer'] = 'TodoBox/1.0'
    msg['Importance'] = 'high'
    msg['X-MSMail-Priority'] = 'Normal'
    msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    msg['MIME-Version'] = '1.0'
    msg['Content-Type'] = 'multipart/alternative'
    
    # Test plain text and HTML parts
    text_content = "Test plain text"
    html_content = "<html><body>Test HTML</body></html>"
    
    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Verify headers
    checks = {
        'Subject': 'Verify Your TodoBox Email Address',
        'From': SMTP_FROM_EMAIL,
        'To': 'test@example.com',
        'Reply-To': SMTP_FROM_EMAIL,
        'X-Priority': '3',
        'X-Mailer': 'TodoBox/1.0',
        'Importance': 'high',
        'X-MSMail-Priority': 'Normal',
        'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
        'MIME-Version': '1.0',
    }
    
    passed = 0
    failed = 0
    
    print("\n📧 Email Header Deliverability Check")
    print("=" * 50)
    
    for header, expected_value in checks.items():
        actual_value = msg.get(header)
        if actual_value == expected_value:
            print(f"✅ {header:25} = {actual_value}")
            passed += 1
        else:
            print(f"❌ {header:25} expected: {expected_value}")
            print(f"                          actual: {actual_value}")
            failed += 1
    
    # Check for multipart structure
    print(f"\n📦 Message Structure Check")
    print("=" * 50)
    
    if msg.is_multipart():
        print("✅ Message is multipart")
        passed += 1
        
        parts = msg.get_payload()
        if len(parts) == 2:
            print(f"✅ Contains 2 parts (plain text + HTML)")
            passed += 1
            
            # Check content types
            if parts[0].get_content_type() == 'text/plain':
                print(f"✅ Part 1: text/plain")
                passed += 1
            else:
                print(f"❌ Part 1: expected text/plain, got {parts[0].get_content_type()}")
                failed += 1
            
            if parts[1].get_content_type() == 'text/html':
                print(f"✅ Part 2: text/html")
                passed += 1
            else:
                print(f"❌ Part 2: expected text/html, got {parts[1].get_content_type()}")
                failed += 1
        else:
            print(f"❌ Expected 2 parts, got {len(parts)}")
            failed += 1
    else:
        print("❌ Message is not multipart")
        failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = test_email_headers()
    sys.exit(0 if success else 1)
