"""
Encryption utilities for protecting sensitive todo data from database administrators.
Uses Fernet symmetric encryption with a key derived from the application's secret key.
"""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_encryption_key():
    """
    Derive a Fernet-compatible encryption key from the app's SECRET_KEY and SALT.
    The key is derived using PBKDF2 to ensure it's cryptographically strong.
    """
    from flask import current_app
    
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
    Returns None if plaintext is None or empty.
    """
    if not plaintext:
        return plaintext
    
    fernet = get_fernet()
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    encrypted = fernet.encrypt(plaintext)
    return encrypted.decode('utf-8')


def decrypt_text(ciphertext):
    """
    Decrypt base64-encoded ciphertext and return plaintext string.
    Returns None if ciphertext is None or empty.
    Returns the original text if decryption fails (for backward compatibility with unencrypted data).
    """
    if not ciphertext:
        return ciphertext
    
    try:
        fernet = get_fernet()
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode('utf-8')
        
        decrypted = fernet.decrypt(ciphertext)
        return decrypted.decode('utf-8')
    except Exception:
        # Return original text if decryption fails
        # This handles backward compatibility with existing unencrypted data
        if isinstance(ciphertext, bytes):
            return ciphertext.decode('utf-8')
        return ciphertext
