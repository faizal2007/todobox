"""
Comprehensive tests for utility functions in TodoBox application.
Tests encryption, geolocation, timezone utilities, and email services.
"""

import pytest
from datetime import datetime, timedelta
import pytz
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    from app import app, db
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key-for-encryption'
    app.config['SALT'] = 'test-salt-for-encryption'
    app.config['TODO_ENCRYPTION_ENABLED'] = True
    app.config['SERVER_NAME'] = 'localhost'
    
    with app.app_context():
        db.create_all()
        from tests.test_utils import seed_status_data
        seed_status_data(db)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    # Workaround for werkzeug.__version__ issue
    import werkzeug
    if not hasattr(werkzeug, '__version__'):
        werkzeug.__version__ = '3.0.0'
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context for testing"""
    with app.app_context():
        yield app


class TestEncryptionUtilities:
    """Tests for encryption.py utility functions"""
    
    def test_is_encryption_enabled_with_context(self, app_context):
        """Test encryption status check with app context"""
        from app.encryption import is_encryption_enabled
        assert is_encryption_enabled() is True
    
    def test_is_encryption_enabled_without_context(self):
        """Test encryption status check without app context"""
        from app.encryption import is_encryption_enabled
        # Should return False gracefully without app context
        assert is_encryption_enabled() is False
    
    def test_encrypt_text_basic(self, app_context):
        """Test basic text encryption"""
        from app.encryption import encrypt_text, decrypt_text
        plaintext = "This is a secret todo"
        encrypted = encrypt_text(plaintext)
        
        assert encrypted is not None
        assert encrypted != plaintext
        assert isinstance(encrypted, str)
        
        # Verify decryption
        decrypted = decrypt_text(encrypted)
        assert decrypted == plaintext
    
    def test_encrypt_text_empty(self, app_context):
        """Test encrypting empty string"""
        from app.encryption import encrypt_text
        assert encrypt_text("") == ""
        assert encrypt_text(None) is None
    
    def test_encrypt_text_unicode(self, app_context):
        """Test encrypting unicode characters"""
        from app.encryption import encrypt_text, decrypt_text
        plaintext = "Hello 世界 🌍 émojis"
        encrypted = encrypt_text(plaintext)
        decrypted = decrypt_text(encrypted)
        assert decrypted == plaintext
    
    def test_decrypt_text_invalid_data(self, app_context):
        """Test decrypting invalid encrypted data returns original"""
        from app.encryption import decrypt_text
        invalid_ciphertext = "not-valid-encrypted-data"
        result = decrypt_text(invalid_ciphertext)
        # Should return original text for backward compatibility
        assert result == invalid_ciphertext
    
    def test_decrypt_text_empty(self, app_context):
        """Test decrypting empty string"""
        from app.encryption import decrypt_text
        assert decrypt_text("") == ""
        assert decrypt_text(None) is None
    
    def test_encryption_without_app_context(self):
        """Test encryption gracefully degrades without app context"""
        from app.encryption import encrypt_text, decrypt_text
        plaintext = "test text"
        # Should return plaintext when no context
        assert encrypt_text(plaintext) == plaintext
        assert decrypt_text(plaintext) == plaintext
    
    def test_get_fernet_creates_valid_instance(self, app_context):
        """Test Fernet instance creation"""
        from app.encryption import get_fernet
        from cryptography.fernet import Fernet
        
        fernet = get_fernet()
        assert isinstance(fernet, Fernet)
    
    def test_encryption_key_derivation_consistency(self, app_context):
        """Test that encryption key derivation is consistent"""
        from app.encryption import _get_encryption_key
        key1 = _get_encryption_key()
        key2 = _get_encryption_key()
        assert key1 == key2


class TestTimezoneUtilities:
    """Tests for timezone_utils.py utility functions"""
    
    def test_convert_to_user_timezone(self):
        """Test converting UTC datetime to user timezone"""
        from app.timezone_utils import convert_to_user_timezone
        
        utc_dt = datetime(2024, 12, 4, 12, 0, 0)  # Noon UTC
        est_dt = convert_to_user_timezone(utc_dt, 'America/New_York')
        
        assert est_dt is not None
        # EST is UTC-5, so noon UTC = 7am EST
        assert est_dt.hour == 7
    
    def test_convert_to_user_timezone_none(self):
        """Test converting None datetime"""
        from app.timezone_utils import convert_to_user_timezone
        assert convert_to_user_timezone(None) is None
    
    def test_convert_to_user_timezone_with_tzinfo(self):
        """Test converting datetime that already has timezone info"""
        from app.timezone_utils import convert_to_user_timezone
        
        # Create datetime in PST
        pst = pytz.timezone('America/Los_Angeles')
        pst_dt = pst.localize(datetime(2024, 12, 4, 9, 0, 0))
        
        # Convert to EST
        est_dt = convert_to_user_timezone(pst_dt, 'America/New_York')
        assert est_dt.hour == 12  # 9am PST = 12pm EST
    
    def test_convert_from_user_timezone(self):
        """Test converting user timezone datetime to UTC"""
        from app.timezone_utils import convert_from_user_timezone
        
        # 7am EST
        local_dt = datetime(2024, 12, 4, 7, 0, 0)
        utc_dt = convert_from_user_timezone(local_dt, 'America/New_York')
        
        assert utc_dt is not None
        # 7am EST = 12pm UTC
        assert utc_dt.hour == 12
    
    def test_convert_from_user_timezone_none(self):
        """Test converting None datetime from user timezone"""
        from app.timezone_utils import convert_from_user_timezone
        assert convert_from_user_timezone(None) is None
    
    def test_get_user_local_time(self, app_context):
        """Test getting current time in user timezone"""
        from app.timezone_utils import get_user_local_time
        from app.models import User
        
        user = User(email='test@example.com')
        user.timezone = 'America/New_York'
        
        local_time = get_user_local_time(user)
        
        assert local_time is not None
        assert local_time.tzinfo is not None
    
    def test_timezone_conversion_error_handling(self):
        """Test error handling with invalid timezone"""
        from app.timezone_utils import convert_to_user_timezone
        
        utc_dt = datetime(2024, 12, 4, 12, 0, 0)
        # Should handle invalid timezone gracefully
        result = convert_to_user_timezone(utc_dt, 'Invalid/Timezone')
        assert result is not None


class TestGeolocationUtilities:
    """Tests for geolocation.py utility functions"""
    
    def test_get_client_ip_direct(self, client, app):
        """Test getting client IP directly"""
        with app.test_request_context(environ_base={'REMOTE_ADDR': '1.2.3.4'}):
            from app.geolocation import get_client_ip
            ip = get_client_ip()
            assert ip == '1.2.3.4'
    
    def test_get_client_ip_from_x_forwarded_for(self, client, app):
        """Test getting client IP from X-Forwarded-For header"""
        with app.test_request_context(headers={'X-Forwarded-For': '5.6.7.8, 1.2.3.4'}):
            from app.geolocation import get_client_ip
            ip = get_client_ip()
            assert ip == '5.6.7.8'
    
    def test_get_client_ip_from_x_real_ip(self, client, app):
        """Test getting client IP from X-Real-IP header"""
        with app.test_request_context(headers={'X-Real-IP': '9.10.11.12'}):
            from app.geolocation import get_client_ip
            ip = get_client_ip()
            assert ip == '9.10.11.12'
    
    @patch('app.geolocation.requests.get')
    @patch('app.geolocation.get_client_ip')
    def test_detect_timezone_from_ip_success(self, mock_get_ip, mock_requests_get):
        """Test successful timezone detection from IP"""
        from app.geolocation import detect_timezone_from_ip
        
        mock_get_ip.return_value = '8.8.8.8'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'timezone': 'America/New_York',
            'countryCode': 'US'
        }
        mock_requests_get.return_value = mock_response
        
        tz = detect_timezone_from_ip()
        assert tz == 'America/New_York'
    
    @patch('app.geolocation.requests.get')
    @patch('app.geolocation.get_client_ip')
    def test_detect_timezone_from_ip_localhost(self, mock_get_ip, mock_requests_get):
        """Test timezone detection skips localhost"""
        from app.geolocation import detect_timezone_from_ip
        
        mock_get_ip.return_value = '127.0.0.1'
        
        tz = detect_timezone_from_ip()
        assert tz is None
        # Should not make API call for localhost
        mock_requests_get.assert_not_called()
    
    @patch('app.geolocation.requests.get')
    @patch('app.geolocation.get_client_ip')
    def test_detect_timezone_from_ip_private_network(self, mock_get_ip, mock_requests_get):
        """Test timezone detection skips private IP ranges"""
        from app.geolocation import detect_timezone_from_ip
        
        mock_get_ip.return_value = '192.168.1.1'
        
        tz = detect_timezone_from_ip()
        assert tz is None
        mock_requests_get.assert_not_called()
    
    @patch('app.geolocation.requests.get')
    @patch('app.geolocation.get_client_ip')
    def test_detect_timezone_from_ip_api_failure(self, mock_get_ip, mock_requests_get):
        """Test timezone detection handles API failures gracefully"""
        from app.geolocation import detect_timezone_from_ip
        import requests
        
        mock_get_ip.return_value = '8.8.8.8'
        mock_requests_get.side_effect = requests.RequestException("API unavailable")
        
        tz = detect_timezone_from_ip()
        assert tz is None
    
    @patch('app.geolocation.requests.get')
    @patch('app.geolocation.get_client_ip')
    def test_detect_timezone_from_ip_fallback_to_country(self, mock_get_ip, mock_requests_get):
        """Test timezone detection falls back to country code"""
        from app.geolocation import detect_timezone_from_ip
        
        mock_get_ip.return_value = '8.8.8.8'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'timezone': 'Invalid/Timezone',
            'countryCode': 'US'
        }
        mock_requests_get.return_value = mock_response
        
        tz = detect_timezone_from_ip()
        assert tz == 'America/New_York'  # Default US timezone
    
    def test_get_timezone_for_user_with_valid_timezone(self):
        """Test getting timezone when user has valid timezone set"""
        from app.geolocation import get_timezone_for_user
        
        tz = get_timezone_for_user('America/Los_Angeles')
        assert tz == 'America/Los_Angeles'
    
    def test_get_timezone_for_user_with_invalid_timezone(self):
        """Test getting timezone with invalid user timezone"""
        from app.geolocation import get_timezone_for_user
        
        with patch('app.geolocation.detect_timezone_from_ip') as mock_detect:
            mock_detect.return_value = None
            tz = get_timezone_for_user('Invalid/Timezone')
            assert tz == 'UTC'
    
    @patch('app.geolocation.detect_timezone_from_ip')
    def test_get_timezone_for_user_detects_from_ip(self, mock_detect):
        """Test timezone detection from IP when user has no timezone"""
        from app.geolocation import get_timezone_for_user
        
        mock_detect.return_value = 'Asia/Tokyo'
        tz = get_timezone_for_user(None)
        assert tz == 'Asia/Tokyo'
    
    def test_get_timezone_options(self):
        """Test getting list of timezone options"""
        from app.geolocation import get_timezone_options
        
        options = get_timezone_options()
        assert isinstance(options, list)
        assert len(options) > 0
        # Each option should be a tuple
        assert all(isinstance(opt, tuple) and len(opt) == 2 for opt in options)


class TestEmailService:
    """Tests for email_service.py functions"""
    
    def test_is_email_configured_with_settings(self, app_context):
        """Test email configuration check with settings"""
        from app import email_service
        
        # Mock environment variables
        with patch.dict('os.environ', {
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'test@example.com',
            'SMTP_PASSWORD': 'password',
            'SMTP_FROM_EMAIL': 'test@example.com'
        }):
            # Reload module to pick up env vars
            import importlib
            importlib.reload(email_service)
            result = email_service.is_email_configured()
            assert isinstance(result, bool)


class TestUtilityFunctions:
    """Tests for utils.py functions"""
    
    def test_momentjs_format(self):
        """Test momentjs utility format method"""
        from app.utils import momentjs
        
        timestamp = "2024-12-04T12:00:00"
        m = momentjs(timestamp)
        
        result = m.format("YYYY-MM-DD")
        assert isinstance(result.striptags(), str)
    
    def test_momentjs_calendar(self):
        """Test momentjs calendar method"""
        from app.utils import momentjs
        
        timestamp = "2024-12-04T12:00:00"
        m = momentjs(timestamp)
        
        result = m.calendar()
        assert isinstance(result.striptags(), str)
    
    def test_momentjs_fromNow(self):
        """Test momentjs fromNow method"""
        from app.utils import momentjs
        
        timestamp = "2024-12-04T12:00:00"
        m = momentjs(timestamp)
        
        result = m.fromNow()
        assert isinstance(result.striptags(), str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
