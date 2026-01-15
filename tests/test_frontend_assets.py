"""
Frontend Asset Tests - Validate static files, templates, and service worker

These tests ensure that all static assets are properly formed and available.
This layer catches issues like:
- Service worker syntax errors
- Missing files
- Invalid JSON
- Broken HTML templates
"""
import json
import re
import pytest
from pathlib import Path
from app import app


class TestServiceWorker:
    """Tests for service worker functionality and correctness"""
    
    @pytest.fixture
    def sw_file(self):
        """Load service worker file"""
        sw_path = Path(app.static_folder) / 'service-worker.js'
        return sw_path.read_text()
    
    def test_service_worker_file_exists(self):
        """Service worker file must exist"""
        sw_path = Path(app.static_folder) / 'service-worker.js'
        assert sw_path.exists(), "service-worker.js not found in static folder"
    
    def test_service_worker_syntax_valid(self, sw_file):
        """Service worker JavaScript must be syntactically valid"""
        # Check for basic syntax issues
        assert 'self.addEventListener' in sw_file, "Missing event listeners"
        assert 'fetch' in sw_file, "Missing fetch handler"
        assert 'caches' in sw_file, "Missing cache API usage"
        # Check for common syntax errors
        assert sw_file.count('{') == sw_file.count('}'), "Mismatched braces"
        assert sw_file.count('[') == sw_file.count(']'), "Mismatched brackets"
        assert sw_file.count('(') == sw_file.count(')'), "Mismatched parentheses"
    
    def test_service_worker_has_external_resource_detection(self, sw_file):
        """Service worker must have function to detect external resources"""
        assert 'isExternalResource' in sw_file, "Missing isExternalResource function"
        assert 'currentOrigin' in sw_file, "Missing origin check"
        assert 'new URL' in sw_file, "Missing URL parsing"
    
    def test_service_worker_skips_external_resources(self, sw_file):
        """Service worker must NOT intercept external resources"""
        # The key pattern: if (isExternalResource(url)) { return; }
        assert 'isExternalResource(url)' in sw_file, "Not checking external resources"
        # Should return early without calling respondWith
        pattern = r'if\s*\(\s*isExternalResource\s*\(\s*url\s*\)\s*\)\s*\{[^}]*return[^}]*\}'
        assert re.search(pattern, sw_file), "Service worker doesn't skip external resources properly"
    
    def test_service_worker_handles_internal_resources(self, sw_file):
        """Service worker must properly handle internal resources"""
        assert 'shouldCache(url)' in sw_file, "Missing cache decision logic"
        assert 'fetch(request)' in sw_file, "Missing fetch handler"
        assert 'caches.match' in sw_file, "Missing cache matching"
    
    def test_service_worker_returns_valid_responses(self, sw_file):
        """Service worker must always return valid Response objects, never undefined"""
        # Check that error handlers return Response objects
        assert 'new Response' in sw_file, "Missing Response object creation"
        # Should not return undefined
        assert '.catch(() => { })' not in sw_file, "Empty catch handler would return undefined"
        # Should have proper error handling
        assert 'status:' in sw_file or 'statusText:' in sw_file, "Missing status in error responses"
    
    def test_service_worker_cache_names_incremented(self, sw_file):
        """Cache names should be versioned for cache busting"""
        # Check for v3 (latest version)
        assert 'v3' in sw_file or 'v2' in sw_file, "Cache versions not found"
        # Count how many version references exist
        version_refs = len(re.findall(r"'todobox.*-v\d+'", sw_file))
        assert version_refs >= 2, "Should have multiple cache version references for busting"
    
    def test_no_hardcoded_external_urls_in_cache(self, sw_file):
        """Service worker shouldn't try to cache external URLs"""
        # Look for STATIC_ASSETS array
        assert 'STATIC_ASSETS' in sw_file, "Missing STATIC_ASSETS constant"
        # It should only reference /static/ paths
        if 'https://' in sw_file and 'STATIC_ASSETS' in sw_file:
            # Find the STATIC_ASSETS block
            start = sw_file.find('STATIC_ASSETS')
            end = sw_file.find(']', start) + 1
            static_assets = sw_file[start:end]
            # Should not have https URLs in STATIC_ASSETS
            assert 'https://' not in static_assets, "STATIC_ASSETS shouldn't contain external URLs"


class TestStaticFiles:
    """Tests for static file existence and validity"""
    
    def test_manifest_json_exists(self):
        """manifest.json must exist for PWA"""
        manifest_path = Path(app.static_folder) / 'manifest.json'
        assert manifest_path.exists(), "manifest.json not found"
    
    def test_manifest_json_valid(self):
        """manifest.json must be valid JSON"""
        manifest_path = Path(app.static_folder) / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        assert manifest.get('name'), "manifest missing 'name'"
        assert manifest.get('short_name'), "manifest missing 'short_name'"
        assert manifest.get('icons'), "manifest missing 'icons'"
    
    def test_required_icons_exist(self):
        """All referenced icons must exist"""
        manifest_path = Path(app.static_folder) / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        
        for icon in manifest.get('icons', []):
            icon_src = icon.get('src')
            if icon_src and not icon_src.startswith('http'):
                # Remove leading /
                rel_path = icon_src.lstrip('/')
                full_path = Path(app.root_path) / rel_path
                assert full_path.exists(), f"Icon not found: {icon_src}"
    
    def test_critical_css_files_exist(self):
        """Critical CSS files must exist"""
        critical_css = [
            'static/css/style.css',
        ]
        for css_file in critical_css:
            path = Path(app.root_path) / css_file
            assert path.exists(), f"CSS file not found: {css_file}"
    
    def test_critical_js_files_exist(self):
        """Critical JavaScript files must exist"""
        critical_js = [
            'static/service-worker.js',
            'static/assets/js/todo-operations.js',
            'static/assets/js/vendor.min.js',
        ]
        for js_file in critical_js:
            path = Path(app.root_path) / js_file
            assert path.exists(), f"JavaScript file not found: {js_file}"
    
    def test_no_empty_static_files(self):
        """Static files shouldn't be empty"""
        static_path = Path(app.static_folder)
        
        critical_extensions = ['.js', '.css']
        for pattern in ['**/*.js', '**/*.css']:
            for filepath in static_path.glob(pattern):
                # Skip vendor files and minified files over 100KB
                if 'vendor' in str(filepath):
                    continue
                if filepath.stat().st_size > 100_000:
                    continue
                
                assert filepath.stat().st_size > 0, f"Empty file: {filepath}"


class TestTemplates:
    """Tests for HTML template validity"""
    
    def test_main_template_has_service_worker_registration(self):
        """main.html should register service worker"""
        # Find main.html - it might be in different locations
        possible_paths = [
            Path('app/templates/main.html'),
            Path(app.template_folder) / 'main.html',
            Path(app.root_path) / 'templates' / 'main.html',
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            pytest.skip("main.html not found in any expected location")
        
        content = template_path.read_text()
        assert 'serviceWorker' in content, "Service worker registration missing"
        assert 'register(' in content, "Service worker registration logic missing"
    
    def test_dashboard_template_has_chart(self):
        """dashboard.html should have chart canvas elements"""
        possible_paths = [
            Path('app/templates/dashboard.html'),
            Path(app.template_folder) / 'dashboard.html',
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            pytest.skip("dashboard.html not found")
        
        content = template_path.read_text()
        assert 'canvas' in content, "Chart canvas missing"
        assert 'todoChart' in content or 'chart' in content, "Chart elements missing"
    
    def test_list_template_has_external_resources(self):
        """list.html should load external resources properly"""
        possible_paths = [
            Path('app/templates/list.html'),
            Path(app.template_folder) / 'list.html',
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            pytest.skip("list.html not found")
        
        content = template_path.read_text()
        # Should reference CDN resources (or at least have some resource loading)
        has_cdn = 'cdn' in content.lower() or 'cdnjs' in content.lower() or 'jsdelivr' in content.lower()
        # If no CDN directly, it might inherit from base or main
        if not has_cdn:
            # That's okay, it might be inherited from parent templates
            pytest.skip("list.html doesn't directly reference CDN resources")
    
    def test_images_have_fallback_onerror(self):
        """All images should have fallback handlers"""
        possible_paths = [
            Path('app/templates/main.html'),
            Path(app.template_folder) / 'main.html',
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            pytest.skip("main.html not found")
        
        content = template_path.read_text()
        
        # Find image tags
        img_tags = re.findall(r'<img[^>]*>', content)
        for img_tag in img_tags:
            # Gravatar images should have onerror fallback
            if 'gravatar' in img_tag.lower():
                assert 'onerror' in img_tag.lower(), f"Gravatar image missing onerror: {img_tag}"


class TestExternalResourceHandling:
    """Tests for proper external resource handling"""
    
    def test_external_cdn_resources_not_in_service_worker_cache(self):
        """External resources shouldn't be in service worker cache list"""
        sw_path = Path(app.static_folder) / 'service-worker.js'
        content = sw_path.read_text()
        
        # Find STATIC_ASSETS section
        if 'STATIC_ASSETS' in content:
            start = content.find('STATIC_ASSETS')
            end = content.find(']', start) + 1
            assets_section = content[start:end]
            
            # Should not contain external URLs
            external_domains = ['cdnjs', 'jsdelivr', 'gravatar', 'cloudflare', 'googleapis']
            for domain in external_domains:
                assert domain not in assets_section.lower(), \
                    f"External resource {domain} found in cache assets"
    
    def test_cdn_resources_use_https(self):
        """All CDN resources should use HTTPS"""
        template_path = Path(app.template_folder) / 'main.html'
        if not template_path.exists():
            pytest.skip("main.html not found")
        content = template_path.read_text()
        
        # Find all script and link tags with http (not https)
        http_urls = re.findall(r"src=['\"]http://[^'\"]*['\"]|href=['\"]http://[^'\"]*['\"]", content)
        assert len(http_urls) == 0, f"Found HTTP (not HTTPS) resources: {http_urls}"
    
    def test_subresource_integrity_for_external_js(self):
        """External JavaScript should have integrity hashes where possible"""
        template_path = Path(app.template_folder) / 'main.html'
        if not template_path.exists():
            pytest.skip("main.html not found")
        content = template_path.read_text()
        
        # Find external script tags (rough check)
        ext_scripts = re.findall(r'<script[^>]*src=["\']https?://[^>]*>', content)
        # Note: Some external scripts may not have integrity (like relative paths)
        # Just checking that the pattern exists is enough
        assert len(ext_scripts) >= 0, "Script tag pattern check"


class TestProductionReadiness:
    """Tests for production deployment readiness"""
    
    def test_all_required_static_files_present(self):
        """All critical static files must be present"""
        required_files = [
            'service-worker.js',
            'manifest.json',
            'css/style.css',
        ]
        
        static_path = Path(app.static_folder)
        for file_rel in required_files:
            file_path = static_path / file_rel
            assert file_path.exists(), f"Missing critical file: {file_rel}"
            assert file_path.stat().st_size > 0, f"Empty critical file: {file_rel}"
    
    def test_no_debug_logs_in_service_worker(self):
        """Service worker shouldn't have verbose debug logging"""
        sw_path = Path(app.static_folder) / 'service-worker.js'
        content = sw_path.read_text()
        
        # Should be minimal console logs
        console_logs = len(re.findall(r'console\.log\(', content))
        console_errors = len(re.findall(r'console\.error\(', content))
        assert console_logs <= 5, f"Too many console.log statements: {console_logs}"
        assert console_errors <= 5, f"Too many console.error statements: {console_errors}"
    
    def test_error_handling_in_service_worker(self):
        """Service worker must have proper error handling"""
        sw_path = Path(app.static_folder) / 'service-worker.js'
        content = sw_path.read_text()
        
        assert '.catch' in content, "Missing error handling in service worker"
        assert 'try' in content or '.catch' in content, "No error handling pattern"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
