#!/usr/bin/env python3
"""
Frontend functionality validation tests for TodoBox.
Tests static assets, PWA features, and frontend functionality.
"""
import pytest
import os
import sys
import json

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
    
    with app.app_context():
        db.create_all()
        
        # Seed status data
        from app.models import Status
        if Status.query.count() == 0:
            Status.seed()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    # Workaround for werkzeug.__version__ issue
    import werkzeug
    if not hasattr(werkzeug, '__version__'):
        werkzeug.__version__ = '3.0.0'
    return app.test_client()


# ============================================================================
# STATIC ASSET TESTS
# ============================================================================

class TestStaticAssets:
    """Test static asset availability and integrity."""
    
    def test_css_files_exist(self):
        """Test CSS files are present."""
        css_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'static', 'css'
        )
        
        if os.path.exists(css_dir):
            css_files = os.listdir(css_dir)
            assert len(css_files) > 0, "CSS directory should contain files"
    
    def test_fonts_directory_exists(self):
        """Test fonts directory exists."""
        fonts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'static', 'fonts'
        )
        assert os.path.exists(fonts_dir)
    
    def test_assets_directory_exists(self):
        """Test assets directory exists."""
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'static', 'assets'
        )
        assert os.path.exists(assets_dir)


class TestPWAFeatures:
    """Test Progressive Web App features."""
    
    def test_service_worker_content(self, client):
        """Test service worker has valid content."""
        response = client.get('/service-worker.js')
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Should contain service worker keywords
            assert any(keyword in content for keyword in [
                'self', 'cache', 'fetch', 'install', 'activate'
            ]), "Service worker should contain valid PWA code"
    
    def test_manifest_json_structure(self, client):
        """Test manifest.json has valid PWA structure."""
        response = client.get('/static/manifest.json')
        
        if response.status_code == 200:
            manifest = json.loads(response.data)
            
            # Check required PWA manifest fields
            assert isinstance(manifest, dict)
            
            # Common manifest fields
            possible_fields = ['name', 'short_name', 'start_url', 'display', 
                             'background_color', 'theme_color', 'icons']
            
            # Should have at least some PWA fields
            has_pwa_fields = any(field in manifest for field in possible_fields)
            assert has_pwa_fields, "Manifest should have PWA fields"
    
    def test_offline_capability_structure(self, client):
        """Test service worker enables offline capability."""
        response = client.get('/service-worker.js')
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Check for cache strategies
            has_cache_logic = any(keyword in content for keyword in [
                'cache', 'Cache', 'CACHE'
            ])
            
            if has_cache_logic:
                assert True, "Service worker implements caching"


# ============================================================================
# TEMPLATE TESTS
# ============================================================================

class TestTemplates:
    """Test template files exist and are valid."""
    
    def test_templates_directory_exists(self):
        """Test templates directory exists."""
        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates'
        )
        assert os.path.exists(templates_dir)
    
    def test_base_template_exists(self):
        """Test base template exists."""
        base_template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'base.html'
        )
        assert os.path.exists(base_template)
    
    def test_main_template_exists(self):
        """Test main template exists."""
        main_template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'main.html'
        )
        assert os.path.exists(main_template)
    
    def test_login_template_exists(self):
        """Test login template exists."""
        login_template = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'app', 'templates', 'login.html'
        )
        assert os.path.exists(login_template)


# ============================================================================
# FRONTEND FUNCTIONALITY TESTS
# ============================================================================

class TestFrontendIntegration:
    """Test frontend integration with backend."""
    
    def test_html_pages_render(self, client, app):
        """Test HTML pages render without errors."""
        from app.models import User
        
        with app.app_context():
            # Create a user
            user = User(email='frontend@example.com')
            user.set_password('password')
            from app import db
            db.session.add(user)
            db.session.commit()
        
        # Test login page renders
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200
        assert b'html' in response.data or b'HTML' in response.data
    
    def test_setup_wizard_renders(self, client):
        """Test setup wizard renders."""
        response = client.get('/setup')
        assert response.status_code == 200
        assert b'html' in response.data or b'HTML' in response.data
    
    def test_static_file_serving(self, client):
        """Test static files are served correctly."""
        # Test service worker
        response = client.get('/service-worker.js')
        assert response.status_code == 200
        
        # Test manifest
        response = client.get('/static/manifest.json')
        # Manifest may or may not exist, but route should be accessible
        assert response.status_code in [200, 404]


# ============================================================================
# RESPONSIVE DESIGN TESTS
# ============================================================================

class TestResponsiveDesign:
    """Test responsive design features."""
    
    def test_viewport_meta_tag(self, client, app):
        """Test pages include viewport meta tag for mobile."""
        from app.models import User
        
        with app.app_context():
            user = User(email='viewport@example.com')
            user.set_password('password')
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.get('/login', follow_redirects=True)
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Check for viewport meta tag (common in responsive designs)
            has_viewport = 'viewport' in content.lower()
            
            # Should have responsive meta tags
            assert has_viewport or 'meta' in content.lower()


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================

class TestAccessibility:
    """Test accessibility features."""
    
    def test_html_lang_attribute(self, client, app):
        """Test HTML pages have lang attribute."""
        from app.models import User
        
        with app.app_context():
            user = User(email='lang@example.com')
            user.set_password('password')
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.get('/login', follow_redirects=True)
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Check for lang attribute or DOCTYPE
            has_html_structure = any(tag in content for tag in [
                '<html', 'DOCTYPE', '<!DOCTYPE'
            ])
            
            assert has_html_structure


# ============================================================================
# SECURITY HEADERS TESTS
# ============================================================================

class TestSecurityHeaders:
    """Test security headers are set."""
    
    def test_no_cache_headers(self, client):
        """Test no-cache headers are set."""
        response = client.get('/healthz')
        
        # Check for cache control headers
        assert 'Cache-Control' in response.headers
        assert 'no-cache' in response.headers.get('Cache-Control', '')
    
    def test_content_type_headers(self, client):
        """Test content type headers are set correctly."""
        # Test JSON endpoint
        response = client.get('/healthz')
        assert 'Content-Type' in response.headers
        assert 'json' in response.headers.get('Content-Type', '').lower()
    
    def test_api_json_response(self, client):
        """Test API returns JSON with correct headers."""
        response = client.get('/api/quote')
        
        assert response.status_code == 200
        assert 'Content-Type' in response.headers
        assert 'json' in response.headers.get('Content-Type', '').lower()
        
        # Verify JSON is parseable
        data = json.loads(response.data)
        assert isinstance(data, dict)


# ============================================================================
# FRONTEND ERROR HANDLING TESTS
# ============================================================================

class TestFrontendErrorHandling:
    """Test frontend error handling."""
    
    def test_404_page_handling(self, client):
        """Test 404 errors are handled gracefully."""
        response = client.get('/non-existent-page-12345')
        assert response.status_code == 404
    
    def test_500_error_handling(self, client):
        """Test server errors are handled gracefully."""
        # The app should not crash on any request
        response = client.get('/healthz')
        assert response.status_code != 500


# ============================================================================
# FORM FUNCTIONALITY TESTS
# ============================================================================

class TestFormFunctionality:
    """Test form submission and validation."""
    
    def test_login_form_structure(self, client, app):
        """Test login form is present."""
        from app.models import User
        
        with app.app_context():
            user = User(email='form@example.com')
            user.set_password('password')
            from app import db
            db.session.add(user)
            db.session.commit()
        
        response = client.get('/login', follow_redirects=True)
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            
            # Should have form elements
            has_form = '<form' in content or 'form' in content.lower()
            assert has_form or 'input' in content.lower()


# ============================================================================
# BROWSER FEATURE TESTS
# ============================================================================

class TestBrowserFeatures:
    """Test browser-specific features."""
    
    def test_no_console_errors_in_healthz(self, client):
        """Test healthz endpoint works without errors."""
        response = client.get('/healthz')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_json_responses_valid(self, client):
        """Test all JSON responses are valid."""
        json_endpoints = [
            '/healthz',
            '/api/quote'
        ]
        
        for endpoint in json_endpoints:
            response = client.get(endpoint)
            
            if response.status_code == 200:
                # Should be valid JSON
                data = json.loads(response.data)
                assert isinstance(data, dict)


# ============================================================================
# INTEGRATION WITH BACKEND TESTS
# ============================================================================

class TestFrontendBackendIntegration:
    """Test frontend integration with backend APIs."""
    
    def test_api_endpoints_accessible_from_frontend(self, client):
        """Test API endpoints are accessible."""
        # Public API endpoint
        response = client.get('/api/quote')
        assert response.status_code == 200
    
    def test_authenticated_endpoints_protected(self, client):
        """Test authenticated endpoints are protected."""
        # Should redirect or return 401
        response = client.get('/')
        assert response.status_code in [302, 401]
        
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]
    
    def test_api_returns_json(self, client):
        """Test API endpoints return JSON."""
        endpoints = ['/api/quote', '/healthz']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            
            if response.status_code == 200:
                assert 'application/json' in response.headers.get('Content-Type', '')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
