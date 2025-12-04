#!/usr/bin/env python3
"""
Test script to verify deleted account blocking functionality
"""
from app import app, db
from app.models import User, DeletedAccount
from datetime import datetime, timedelta

def test_deleted_account_blocking():
    """Test that deleted accounts are properly blocked from re-registration"""
    with app.app_context():
        print("Testing DeletedAccount blocking functionality...\n")
        
        # Test 1: Create a deleted account record
        test_email = "test_deleted@example.com"
        test_oauth_id = "google_123456"
        
        # Clean up any existing test records
        DeletedAccount.query.filter_by(email=test_email).delete()
        db.session.commit()
        
        print(f"Test 1: Creating deleted account record for {test_email}")
        deleted = DeletedAccount(
            email=test_email,
            oauth_id=test_oauth_id,
            cooldown_days=7
        )
        db.session.add(deleted)
        db.session.commit()
        print("✓ Deleted account record created")
        print(f"  - Email: {deleted.email}")
        print(f"  - OAuth ID: {deleted.oauth_id}")
        print(f"  - Deleted at: {deleted.deleted_at}")
        print(f"  - Cooldown until: {deleted.cooldown_until}\n")
        
        # Test 2: Check if email is blocked
        print(f"Test 2: Checking if {test_email} is blocked...")
        is_blocked = DeletedAccount.is_blocked(test_email)
        if is_blocked:
            print(f"✓ Email {test_email} is correctly blocked")
        else:
            print(f"✗ ERROR: Email {test_email} should be blocked but isn't!")
            return False
        
        # Test 3: Check if OAuth ID is blocked
        print(f"\nTest 3: Checking if OAuth ID {test_oauth_id} is blocked...")
        is_blocked_oauth = DeletedAccount.is_blocked("different_email@example.com", test_oauth_id)
        if is_blocked_oauth:
            print(f"✓ OAuth ID {test_oauth_id} is correctly blocked")
        else:
            print(f"✗ ERROR: OAuth ID {test_oauth_id} should be blocked but isn't!")
            return False
        
        # Test 4: Check that non-deleted email is not blocked
        print(f"\nTest 4: Checking that non-deleted email is not blocked...")
        not_deleted = "not_deleted@example.com"
        is_not_blocked = DeletedAccount.is_blocked(not_deleted)
        if not is_not_blocked:
            print(f"✓ Email {not_deleted} is correctly not blocked")
        else:
            print(f"✗ ERROR: Email {not_deleted} should not be blocked!")
            return False
        
        # Test 5: Test expired cooldown
        print(f"\nTest 5: Testing expired cooldown period...")
        expired_email = "expired@example.com"
        expired = DeletedAccount(
            email=expired_email,
            oauth_id="expired_oauth",
            cooldown_days=0  # Already expired
        )
        expired.cooldown_until = datetime.utcnow() - timedelta(days=1)  # Set to past
        db.session.add(expired)
        db.session.commit()
        
        is_expired_blocked = DeletedAccount.is_blocked(expired_email)
        if not is_expired_blocked:
            print(f"✓ Expired cooldown for {expired_email} correctly not blocking")
        else:
            print(f"✗ ERROR: Expired cooldown should not block!")
            return False
        
        # Clean up test data
        print("\n\nCleaning up test data...")
        DeletedAccount.query.filter_by(email=test_email).delete()
        DeletedAccount.query.filter_by(email=expired_email).delete()
        db.session.commit()
        print("✓ Test data cleaned up")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nDeleted account blocking is working correctly:")
        print("- Deleted emails are blocked during cooldown period")
        print("- Deleted OAuth IDs are blocked during cooldown period")
        print("- Non-deleted accounts are not affected")
        print("- Expired cooldowns correctly allow re-registration")
        
        return True

if __name__ == '__main__':
    success = test_deleted_account_blocking()
    exit(0 if success else 1)
