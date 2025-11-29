"""
Encryption utilities for protecting sensitive todo data from database administrators.
Uses Fernet symmetric encryption with a key derived from the application's secret key.
Encryption can be enabled/disabled via TODO_ENCRYPTION_ENABLED in .flaskenv
"""
import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def is_encryption_enabled():
    """Check if todo encryption is enabled in the configuration.
    
    Returns False if called outside of an application context to ensure
    graceful degradation when the app context is not available.
    """
    try:
        from flask import current_app, has_app_context
        if not has_app_context():
            return False
        return current_app.config.get('TODO_ENCRYPTION_ENABLED', False)
    except RuntimeError:
        # Return False if called outside of application context
        return False


def _get_encryption_key():
    """
    Derive a Fernet-compatible encryption key from the app's SECRET_KEY and SALT.
    The key is derived using PBKDF2 to ensure it's cryptographically strong.
    
    Raises RuntimeError if called outside of an application context.
    """
    from flask import current_app, has_app_context
    
    if not has_app_context():
        raise RuntimeError("Cannot derive encryption key outside of application context")
    
    secret_key = current_app.config.get('SECRET_KEY', 'change-me-in-production')
    salt = current_app.config.get('SALT', 'default-salt-change-in-production')
    
    # Convert to bytes if they're strings
    if isinstance(secret_key, str):
        secret_key = secret_key.encode('utf-8')
    if isinstance(salt, str):
        salt = salt.encode('utf-8')
    
    # Use PBKDF2 to derive a key from the secret key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key))
    return key


def get_fernet():
    """Get a Fernet instance for encryption/decryption."""
    key = _get_encryption_key()
    return Fernet(key)


def encrypt_text(plaintext):
    """
    Encrypt plaintext string and return base64-encoded ciphertext.
    Returns the plaintext unchanged if encryption is disabled or if an error occurs.
    Returns None if plaintext is None or empty.
    """
    if not plaintext:
        return plaintext
    
    # If encryption is disabled, return plaintext as-is
    if not is_encryption_enabled():
        return plaintext
    
    try:
        fernet = get_fernet()
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        encrypted = fernet.encrypt(plaintext)
        return encrypted.decode('utf-8')
    except RuntimeError:
        # Return plaintext if called outside of application context
        # This ensures graceful degradation
        if isinstance(plaintext, bytes):
            return plaintext.decode('utf-8')
        return plaintext


def decrypt_text(ciphertext):
    """
    Decrypt base64-encoded ciphertext and return plaintext string.
    Returns the ciphertext unchanged if encryption is disabled.
    Returns None if ciphertext is None or empty.
    Returns the original text if decryption fails (for backward compatibility with unencrypted data).
    """
    if not ciphertext:
        return ciphertext
    
    # If encryption is disabled, return ciphertext as-is (it's actually plaintext)
    if not is_encryption_enabled():
        return ciphertext
    
    # Store original value before any modifications because ciphertext may be
    # converted to bytes during decryption attempt, and we need the original
    # value to return in case of decryption failure (backward compatibility)
    original_ciphertext = ciphertext
    
    try:
        fernet = get_fernet()
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode('utf-8')
        
        decrypted = fernet.decrypt(ciphertext)
        return decrypted.decode('utf-8')
    except (InvalidToken, ValueError, TypeError, UnicodeDecodeError, UnicodeEncodeError, RuntimeError):
        # Return original text if decryption fails due to:
        # - InvalidToken: invalid encrypted data
        # - ValueError/TypeError: data format issues
        # - UnicodeDecodeError/UnicodeEncodeError: encoding issues
        # - RuntimeError: no app context available
        # This handles backward compatibility with existing unencrypted data
        # Use original_ciphertext to avoid returning modified bytes
        if isinstance(original_ciphertext, bytes):
            return original_ciphertext.decode('utf-8')
        return original_ciphertext
