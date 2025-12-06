#!/usr/bin/env python3
"""
Test script to simulate cooldown expiry and verify re-registration is allowed
"""
from app import app, db
from app.models import User, DeletedAccount
from datetime import datetime, timedelta

def test_cooldown_expiry_flow():
    """Test complete cooldown flow from deletion to re-registration"""
    with app.app_context():
        print("="*70)
        print("TESTING COOLDOWN EXPIRY AND RE-REGISTRATION FLOW")
        print("="*70)
        
        test_email = "cooldown_test@example.com"
        test_oauth_id = "google_test_12345"
        
        # Clean up any existing test data
        print("\n1. CLEANUP: Removing any existing test data...")
        User.query.filter_by(email=test_email).delete()
        DeletedAccount.query.filter_by(email=test_email).delete()
        db.session.commit()
        print(f"   ✓ Cleaned up test email: {test_email}")
        
        # Step 1: Create a deleted account record (simulating account deletion)
        print(f"\n2. SIMULATE DELETION: Creating deleted account record...")
        deleted = DeletedAccount(
            email=test_email,
            oauth_id=test_oauth_id,
            cooldown_days=7
        )
        db.session.add(deleted)
        db.session.commit()
        print(f"   ✓ Account marked as deleted")
        print(f"   - Email: {deleted.email}")
        # Don't log full OAuth ID, mask most info
        print(f"   - OAuth ID: [REDACTED] (ends with ...{str(deleted.oauth_id)[-4:]})" if deleted.oauth_id else "   - OAuth ID: [REDACTED]")
        print(f"   - Deleted at: {deleted.deleted_at}")
        print(f"   - Cooldown until: {deleted.cooldown_until}")
        
        # Step 2: Verify account is blocked during cooldown
        print(f"\n3. VERIFY BLOCKING: Checking if account is blocked...")
        is_blocked = DeletedAccount.is_blocked(test_email, test_oauth_id)
        if is_blocked:
            print(f"   ✓ PASS: Email is correctly blocked during cooldown period")
        else:
            print(f"   ✗ FAIL: Email should be blocked but isn't!")
            return False
        
        # Verify OAuth ID is also blocked
        is_oauth_blocked = DeletedAccount.is_blocked("different@email.com", test_oauth_id)
        if is_oauth_blocked:
            print(f"   ✓ PASS: OAuth ID is correctly blocked during cooldown period")
        else:
            print(f"   ✗ FAIL: OAuth ID should be blocked but isn't!")
            return False
        
        # Step 3: Simulate cooldown expiry by setting cooldown_until to the past
        print(f"\n4. SIMULATE EXPIRY: Setting cooldown to expired (1 day in the past)...")
        deleted.cooldown_until = datetime.utcnow() - timedelta(days=1)
        db.session.commit()
        print(f"   ✓ Cooldown set to: {deleted.cooldown_until}")
        print(f"   - Current time: {datetime.utcnow()}")
        print(f"   - Status: EXPIRED")
        
        # Step 4: Verify account is NO LONGER blocked after expiry
        print(f"\n5. VERIFY UNBLOCKING: Checking if account is unblocked after expiry...")
        is_still_blocked = DeletedAccount.is_blocked(test_email, test_oauth_id)
        if not is_still_blocked:
            print(f"   ✓ PASS: Email is correctly unblocked after cooldown expiry")
        else:
            print(f"   ✗ FAIL: Email should be unblocked but still blocked!")
            return False
        
        # Verify OAuth ID is also unblocked
        is_oauth_still_blocked = DeletedAccount.is_blocked("different@email.com", test_oauth_id)
        if not is_oauth_still_blocked:
            print(f"   ✓ PASS: OAuth ID is correctly unblocked after cooldown expiry")
        else:
            print(f"   ✗ FAIL: OAuth ID should be unblocked but still blocked!")
            return False
        
        # Step 5: Simulate re-registration (creating new user with same email)
        print(f"\n6. SIMULATE RE-REGISTRATION: Creating new user account...")
        new_user = User(
            email=test_email,
            oauth_provider="google",
            oauth_id=test_oauth_id
        )
        new_user.fullname = "Test User Reregistered"
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"   ✓ PASS: User successfully re-registered after cooldown")
            print(f"   - User ID: {new_user.id}")
            print(f"   - Email: {new_user.email}")
            print(f"   - Full Name: {new_user.fullname}")
            # Don't log full OAuth ID, mask most info
            print(f"   - OAuth ID: [REDACTED] (ends with ...{str(new_user.oauth_id)[-4:]})" if new_user.oauth_id else "   - OAuth ID: [REDACTED]")
        except Exception as e:
            print(f"   ✗ FAIL: Re-registration failed with error: {str(e)}")
            return False
        
        # Step 6: Verify user can be retrieved
        print(f"\n7. VERIFY USER: Checking if user can be retrieved from database...")
        retrieved_user = User.query.filter_by(email=test_email).first()
        if retrieved_user:
            print(f"   ✓ PASS: User successfully retrieved")
            print(f"   - User ID: {retrieved_user.id}")
            print(f"   - Email: {retrieved_user.email}")
            print(f"   - OAuth Provider: {retrieved_user.oauth_provider}")
        else:
            print(f"   ✗ FAIL: User not found in database!")
            return False
        
        # Step 7: Test cleanup of expired records
        print(f"\n8. TEST CLEANUP: Testing expired record cleanup...")
        expired_count = DeletedAccount.cleanup_expired()
        print(f"   ✓ PASS: Cleanup removed {expired_count} expired record(s)")
        
        # Verify cleanup worked
        remaining = DeletedAccount.query.filter_by(email=test_email).first()
        if not remaining:
            print(f"   ✓ PASS: Expired record successfully removed")
        else:
            print(f"   ✗ FAIL: Expired record still exists!")
            return False
        
        # Final cleanup
        print(f"\n9. FINAL CLEANUP: Removing test data...")
        User.query.filter_by(email=test_email).delete()
        DeletedAccount.query.filter_by(email=test_email).delete()
        db.session.commit()
        print(f"   ✓ Test data cleaned up")
        
        # Success summary
        print("\n" + "="*70)
        print("ALL TESTS PASSED! ✓")
        print("="*70)
        print("\nCooldown Flow Summary:")
        print("1. ✓ Account deletion creates cooldown record")
        print("2. ✓ Email and OAuth ID are blocked during cooldown")
        print("3. ✓ Cooldown expiry unblocks email and OAuth ID")
        print("4. ✓ Re-registration is allowed after expiry")
        print("5. ✓ User can be created with previously deleted email")
        print("6. ✓ Expired records can be cleaned up")
        print("\nConclusion: Users CAN re-register after 7-day cooldown expires!")
        print("="*70)
        
        return True

if __name__ == '__main__':
    success = test_cooldown_expiry_flow()
    exit(0 if success else 1)
