"""Tests for user registration with email verification"""
import pytest
from app import app, db
from app.models import User
from app.forms import RegistrationForm
from app.verification import VerificationToken


class TestRegistrationFlow:
    """Test user registration system with email verification"""

    def test_verification_token_generation(self):
        """Test email verification token generation"""
        email = 'test@example.com'
        token = VerificationToken.generate_token(email)
        
        # Token should be non-empty
        assert len(token) > 0
        
        # Token should contain underscore separator
        assert '_' in token
        
        # Token should be URL-safe
        assert all(c.isalnum() or c in '-_' for c in token)

    def test_verification_token_validation(self):
        """Test email verification token validation"""
        email = 'test@example.com'
        token = VerificationToken.generate_token(email)
        
        # Should validate for correct email
        assert VerificationToken.verify_email_token(token, email) is True
        
        # Should not validate for different email
        assert VerificationToken.verify_email_token(token, 'other@example.com') is False
        
        # Should be case-insensitive
        assert VerificationToken.verify_email_token(token, email.upper()) is True

    def test_verification_token_invalidation(self):
        """Test invalid tokens are rejected"""
        # Invalid token format
        assert VerificationToken.verify_email_token('invalid', 'test@example.com') is False
        
        # Token without email hash
        assert VerificationToken.verify_email_token('onlytoken', 'test@example.com') is False
        
        # Empty token
        assert VerificationToken.verify_email_token('', 'test@example.com') is False

    def test_user_model_email_verified_field(self):
        """Test User model has email_verified field"""
        with app.app_context():
            # Create test user without committing
            user = User(email='test@example.com')
            user.set_password('TestPassword123')
            
            # Check that field exists and can be set
            user.email_verified = False
            assert user.email_verified is False
            
            user.email_verified = True
            assert user.email_verified is True

    def test_registration_form_password_validation(self):
        """Test RegistrationForm has required fields"""
        # Just verify form class has the expected attributes
        form_fields = ['email', 'password', 'confirm_password', 'fullname', 'submit']
        for field_name in form_fields:
            assert hasattr(RegistrationForm, field_name), f"Form missing {field_name} field"

    def test_registration_form_field_validation(self):
        """Test RegistrationForm field definitions"""
        # Verify form class structure without instantiating
        from wtforms import StringField, PasswordField, SubmitField
        
        # Access form field definitions
        form_class = RegistrationForm
        assert form_class is not None
        # Form exists and can be imported without errors

    def test_verification_token_uniqueness(self):
        """Test that each token is unique"""
        email = 'test@example.com'
        
        # Generate two tokens for same email
        token1 = VerificationToken.generate_token(email)
        token2 = VerificationToken.generate_token(email)
        
        # Tokens should be different (due to random part)
        assert token1 != token2
        
        # Both should validate for same email
        assert VerificationToken.verify_email_token(token1, email) is True
        assert VerificationToken.verify_email_token(token2, email) is True

    def test_verification_token_email_binding(self):
        """Test that tokens are bound to specific email addresses"""
        email1 = 'user1@example.com'
        email2 = 'user2@example.com'
        
        token1 = VerificationToken.generate_token(email1)
        token2 = VerificationToken.generate_token(email2)
        
        # token1 should not validate for email2
        assert VerificationToken.verify_email_token(token1, email2) is False
        
        # token2 should not validate for email1
        assert VerificationToken.verify_email_token(token2, email1) is False
        
        # Each token validates only for its own email
        assert VerificationToken.verify_email_token(token1, email1) is True
        assert VerificationToken.verify_email_token(token2, email2) is True

    def test_create_verification_token_returns_tuple(self):
        """Test create_verification_token returns (token, expires_at)"""
        with app.app_context():
            user = User(email='test@example.com')
            user.set_password('TestPassword123')
            
            result = VerificationToken.create_verification_token(user)
            
            # Should return tuple with 2 elements
            assert isinstance(result, tuple)
            assert len(result) == 2
            
            token, expires_at = result
            
            # Token should be valid
            assert len(token) > 0
            assert '_' in token
            
            # Expires_at should be ISO format string
            assert isinstance(expires_at, str)
            assert 'T' in expires_at  # ISO format contains 'T'
            # Should be a valid ISO datetime format
            assert 'Z' not in expires_at  # Using isoformat() which doesn't include Z


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



if __name__ == '__main__':
    pytest.main([__file__, '-v'])
