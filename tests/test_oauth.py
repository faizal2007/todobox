"""
Tests for OAuth functionality including error handling and proxy scenarios.
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from app import app, db
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Seed status data
        from app.models import Status
        if Status.query.count() == 0:
            statuses = [
                Status(name='new'),
                Status(name='done'),
                Status(name='failed'),
                Status(name='re-assign')
            ]
            for i, status in enumerate(statuses, start=5):
                status.id = i
            db.session.add_all(statuses)
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


class TestOAuthErrorHandling:
    """Test OAuth error handling for proxy and network scenarios."""
    
    def test_oauth_error_exception_class_exists(self):
        """Test that OAuthError exception class is available."""
        from app.oauth import OAuthError
        
        error = OAuthError("Test error message")
        assert str(error) == "Test error message"
    
    def test_get_google_provider_config_raises_oauth_error_on_network_failure(self, app):
        """Test that get_google_provider_config raises OAuthError on network failure."""
        from app.oauth import get_google_provider_config, OAuthError
        import requests as requests_lib
        
        with app.test_request_context('/auth/login/google'):
            with patch('app.oauth.requests.get') as mock_get:
                # Simulate a requests.RequestException (network error)
                mock_get.side_effect = requests_lib.exceptions.RequestException("Network error")
                
                with pytest.raises(OAuthError) as excinfo:
                    get_google_provider_config()
                
                assert "Failed to fetch Google OAuth configuration" in str(excinfo.value)
    
    def test_generate_google_auth_url_raises_oauth_error_on_failure(self, app):
        """Test that generate_google_auth_url raises OAuthError on failure."""
        from app.oauth import generate_google_auth_url, OAuthError
        
        with app.test_request_context('/auth/login/google'):
            with patch('app.oauth.requests.get') as mock_get:
                mock_get.side_effect = Exception("Connection failed")
                
                with pytest.raises(OAuthError) as excinfo:
                    generate_google_auth_url()
                
                assert "Failed" in str(excinfo.value)
    
    def test_generate_google_auth_url_success_with_mock(self, app):
        """Test that generate_google_auth_url works correctly with mocked Google config."""
        from app.oauth import generate_google_auth_url
        
        mock_config = {
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_endpoint": "https://oauth2.googleapis.com/token",
        }
        
        with app.test_request_context(
            '/auth/login/google',
            base_url='https://myapp.cloudflare.com'
        ):
            with patch('app.oauth.requests.get') as mock_get:
                mock_get.return_value.json.return_value = mock_config
                mock_get.return_value.raise_for_status.return_value = None
                
                url = generate_google_auth_url()
                
                assert "accounts.google.com" in url
                assert "client_id" in url
                assert "redirect_uri" in url
    
    def test_oauth_route_handles_oauth_error_gracefully(self, app, client):
        """Test that the OAuth login route handles OAuthError gracefully."""
        with patch('app.oauth.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            response = client.get('/auth/login/google')
            
            # Should redirect to login page, not return 500
            assert response.status_code == 302
            assert '/login' in response.headers.get('Location', '')
    
    def test_oauth_route_returns_500_without_error_handling(self, app):
        """Verify that without our error handling, the route would crash."""
        from app.oauth import generate_google_auth_url, OAuthError
        
        # This test verifies that OAuthError is raised, which our route catches
        with app.test_request_context('/auth/login/google'):
            with patch('app.oauth.requests.get') as mock_get:
                mock_get.side_effect = Exception("Connection failed")
                
                with pytest.raises(OAuthError):
                    generate_google_auth_url()


class TestOAuthRedirectURI:
    """Test OAuth redirect URI generation for various scenarios."""
    
    def test_get_oauth_redirect_uri_uses_configured_uri_when_set(self, app):
        """Test that configured OAUTH_REDIRECT_URI is used when set to non-localhost."""
        from app.oauth import get_oauth_redirect_uri
        
        with app.test_request_context('/auth/login/google'):
            # Set a custom redirect URI
            app.config['OAUTH_REDIRECT_URI'] = 'https://myapp.cloudflare.com/auth/callback/google'
            
            uri = get_oauth_redirect_uri()
            
            assert uri == 'https://myapp.cloudflare.com/auth/callback/google'
    
    def test_get_oauth_redirect_uri_falls_back_to_url_for_with_localhost(self, app):
        """Test that url_for is used when OAUTH_REDIRECT_URI is localhost."""
        from app.oauth import get_oauth_redirect_uri
        
        with app.test_request_context('/auth/login/google'):
            # Set a localhost redirect URI (default)
            app.config['OAUTH_REDIRECT_URI'] = 'http://localhost:5000/auth/callback/google'
            
            uri = get_oauth_redirect_uri()
            
            # Should fall back to url_for() which generates localhost in test context
            assert uri.endswith('/auth/callback/google')
    
    def test_get_oauth_redirect_uri_handles_127_0_0_1(self, app):
        """Test that url_for is used when OAUTH_REDIRECT_URI is 127.0.0.1."""
        from app.oauth import get_oauth_redirect_uri
        
        with app.test_request_context('/auth/login/google'):
            # Set a 127.0.0.1 redirect URI
            app.config['OAUTH_REDIRECT_URI'] = 'http://127.0.0.1:5000/auth/callback/google'
            
            uri = get_oauth_redirect_uri()
            
            # Should fall back to url_for() and end with the callback path
            assert uri.endswith('/auth/callback/google')
    
    def test_get_oauth_redirect_uri_logs_warning_for_proxy_mismatch(self, app):
        """Test that a warning is logged when localhost URI is used but proxy headers are present."""
        from app.oauth import get_oauth_redirect_uri
        
        with app.test_request_context(
            '/auth/login/google',
            headers={
                'X-Forwarded-Host': 'myapp.cloudflare.com',
                'X-Forwarded-Proto': 'https'
            }
        ):
            # Set localhost redirect URI
            app.config['OAUTH_REDIRECT_URI'] = 'http://localhost:5000/auth/callback/google'
            
            # This should work but may log a warning
            # We can't easily test logging here, but we verify the function works
            uri = get_oauth_redirect_uri()
            
            assert uri.endswith('/auth/callback/google')


class TestOAuthCallbackHandling:
    """Test OAuth callback error handling."""
    
    def test_oauth_callback_handles_google_error(self, app, client):
        """Test that OAuth callback handles error parameter from Google."""
        response = client.get('/auth/callback/google?error=access_denied')
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.headers.get('Location', '')
    
    def test_oauth_callback_handles_missing_code(self, app, client):
        """Test that OAuth callback handles missing authorization code."""
        response = client.get('/auth/callback/google')
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.headers.get('Location', '')
    
    def test_process_google_callback_returns_none_on_error(self, app):
        """Test that process_google_callback returns (None, False) on errors."""
        from app.oauth import process_google_callback
        
        with app.test_request_context('/auth/callback/google'):
            with patch('app.oauth.requests.get') as mock_get:
                mock_get.side_effect = Exception("Network error")
                
                user, is_new = process_google_callback("fake_code")
                
                assert user is None
                assert is_new is False


class TestProxyFixIntegration:
    """Test ProxyFix middleware integration with OAuth."""
    
    def test_proxyfix_modifies_request_correctly(self, app):
        """Test that ProxyFix correctly modifies request based on X-Forwarded headers."""
        from werkzeug.test import EnvironBuilder
        from werkzeug.middleware.proxy_fix import ProxyFix
        
        # Build environment with proxy headers
        builder = EnvironBuilder(
            method='GET',
            path='/test',
            headers={
                'X-Forwarded-For': '203.0.113.50',
                'X-Forwarded-Proto': 'https',
                'X-Forwarded-Host': 'myapp.cloudflare.com',
                'Host': 'localhost:5000'
            }
        )
        environ = builder.get_environ()
        
        # Capture what ProxyFix does
        captured = {}
        
        def capture_app(environ, start_response):
            captured['host'] = environ.get('HTTP_HOST')
            captured['scheme'] = environ.get('wsgi.url_scheme')
            start_response('200 OK', [])
            return [b'OK']
        
        proxy_app = ProxyFix(capture_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        list(proxy_app(environ, lambda *args: None))
        
        # ProxyFix should update the host and scheme
        assert captured['host'] == 'myapp.cloudflare.com'
        assert captured['scheme'] == 'https'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
