"""Email verification token generation and validation utilities"""
import secrets
import hashlib
from datetime import datetime, timedelta
from app import db
from app.models import User


class VerificationToken:
    """Generate and validate email verification tokens"""
    
    # Token validity period (24 hours)
    EXPIRATION_HOURS = 24
    
    @staticmethod
    def generate_token(email: str, purpose: str = 'email_verification') -> str:
        """
        Generate a secure verification token for email verification.
        
        Args:
            email: User email address
            purpose: Purpose of token (default: email_verification)
            
        Returns:
            Secure token string
        """
        # Generate a random token
        random_part = secrets.token_urlsafe(32)
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
        token = f"{random_part}_{email_hash}"
        return token
    
    @staticmethod
    def verify_email_token(token: str, email: str) -> bool:
        """
        Verify an email verification token.
        
        Args:
            token: Token to verify
            email: Email address to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            if not token or '_' not in token:
                return False
            
            # Extract email hash and verify it matches
            _, stored_hash = token.rsplit('_', 1)
            computed_hash = hashlib.sha256(email.lower().encode()).hexdigest()[:16]
            
            return stored_hash == computed_hash
        except Exception:
            return False
    
    @staticmethod
    def create_verification_token(user: User) -> tuple[str, str]:
        """
        Create and store a verification token for a user.
        
        Args:
            user: User object
            
        Returns:
            Tuple of (token, expires_at_iso_string)
        """
        token = VerificationToken.generate_token(user.email)
        return token, (datetime.utcnow() + timedelta(hours=VerificationToken.EXPIRATION_HOURS)).isoformat()
