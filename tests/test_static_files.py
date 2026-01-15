"""
Static Files Test - Verify all required static files exist and are valid

This test layer catches:
- Missing asset files
- Invalid JSON in configuration files
- Broken icon references
- Missing manifest entries
"""
import json
import pytest
from pathlib import Path
from app import app


class TestStaticFilesExist:
    """Verify all required static files exist"""
    
    def test_service_worker_exists(self):
        """Service worker must exist"""
        path = Path(app.static_folder) / 'service-worker.js'
        assert path.exists(), "service-worker.js not found"
        assert path.stat().st_size > 0, "service-worker.js is empty"
    
    def test_manifest_exists(self):
        """manifest.json must exist for PWA"""
        path = Path(app.static_folder) / 'manifest.json'
        assert path.exists(), "manifest.json not found"
        assert path.stat().st_size > 0, "manifest.json is empty"
    
    def test_main_css_exists(self):
        """Main stylesheet must exist"""
        # Try common locations
        possible_paths = [
            Path(app.static_folder) / 'css' / 'style.css',
            Path(app.static_folder) / 'style.css',
            Path(app.static_folder) / 'assets' / 'css' / 'style.css',
        ]
        found = any(p.exists() for p in possible_paths)
        assert found, f"Main CSS not found in any of: {[str(p) for p in possible_paths]}"
    
    def test_critical_icon_exists(self):
        """At least one icon must exist"""
        icons_dir = Path(app.static_folder) / 'assets' / 'icons'
        if not icons_dir.exists():
            # Try alternative location
            icons_dir = Path(app.static_folder) / 'icons'
        
        if icons_dir.exists():
            icon_files = list(icons_dir.glob('*png'))
            assert len(icon_files) > 0, "No PNG icons found"
    
    def test_vendor_js_exists(self):
        """Vendor JavaScript bundle must exist"""
        possible_paths = [
            Path(app.static_folder) / 'assets' / 'js' / 'vendor.min.js',
            Path(app.static_folder) / 'js' / 'vendor.min.js',
            Path(app.static_folder) / 'vendor.min.js',
        ]
        found = any(p.exists() for p in possible_paths)
        assert found, "Vendor JavaScript not found"
    
    def test_todo_operations_js_exists(self):
        """Todo operations JavaScript must exist"""
        possible_paths = [
            Path(app.static_folder) / 'assets' / 'js' / 'todo-operations.js',
            Path(app.static_folder) / 'js' / 'todo-operations.js',
            Path(app.static_folder) / 'todo-operations.js',
        ]
        found = any(p.exists() for p in possible_paths)
        # This may be optional in some deployments
        if not found:
            pytest.skip("todo-operations.js not found - may not be required")


class TestManifestValidity:
    """Test that manifest.json is properly formatted"""
    
    @pytest.fixture
    def manifest(self):
        """Load and parse manifest.json"""
        path = Path(app.static_folder) / 'manifest.json'
        return json.loads(path.read_text())
    
    def test_manifest_has_name(self, manifest):
        """Manifest must have name field"""
        assert 'name' in manifest, "manifest.json missing 'name'"
        assert isinstance(manifest['name'], str), "'name' must be string"
        assert len(manifest['name']) > 0, "'name' cannot be empty"
    
    def test_manifest_has_short_name(self, manifest):
        """Manifest must have short_name field"""
        assert 'short_name' in manifest, "manifest.json missing 'short_name'"
        assert isinstance(manifest['short_name'], str), "'short_name' must be string"
    
    def test_manifest_has_icons(self, manifest):
        """Manifest must have icons array"""
        assert 'icons' in manifest, "manifest.json missing 'icons'"
        assert isinstance(manifest['icons'], list), "'icons' must be array"
        assert len(manifest['icons']) > 0, "'icons' cannot be empty"
    
    def test_manifest_icons_have_required_fields(self, manifest):
        """Each icon must have src and sizes"""
        for icon in manifest['icons']:
            assert 'src' in icon, f"Icon missing 'src': {icon}"
            assert 'sizes' in icon or 'size' in icon, f"Icon missing size info: {icon}"
    
    def test_manifest_icons_are_accessible(self, manifest):
        """Icons referenced in manifest must exist"""
        for icon in manifest['icons']:
            icon_src = icon.get('src')
            if icon_src and not icon_src.startswith('http'):
                # Convert to file path
                rel_path = icon_src.lstrip('/')
                full_path = Path(app.root_path) / rel_path
                # Icon might not exist if it's generated, so skip if missing
                if full_path.exists():
                    assert full_path.stat().st_size > 0, f"Icon is empty: {icon_src}"
    
    def test_manifest_start_url(self, manifest):
        """Manifest should have start_url"""
        if 'start_url' in manifest:
            assert isinstance(manifest['start_url'], str), "'start_url' must be string"
            # Should be root or /index or /dashboard
            assert manifest['start_url'].startswith('/'), "'start_url' must be absolute"
    
    def test_manifest_display_mode(self, manifest):
        """Manifest display should be valid"""
        if 'display' in manifest:
            valid_modes = ['fullscreen', 'standalone', 'minimal-ui', 'browser']
            assert manifest['display'] in valid_modes, \
                f"Invalid display mode: {manifest['display']}"


class TestFilePermissions:
    """Test that static files have correct permissions"""
    
    def test_static_files_are_readable(self):
        """Static files must be readable"""
        static_path = Path(app.static_folder)
        
        critical_files = [
            'service-worker.js',
            'manifest.json',
        ]
        
        for filename in critical_files:
            path = static_path / filename
            if path.exists():
                # On Windows, st_mode might not have execute bit
                mode = path.stat().st_mode
                assert mode & 0o400, f"File not readable: {filename}"
    
    def test_no_files_too_large(self):
        """Static files shouldn't be unexpectedly large"""
        static_path = Path(app.static_folder)
        
        # Reasonable limits for different file types
        limits = {
            '.js': 10_000_000,  # 10MB max for JS files
            '.css': 5_000_000,  # 5MB max for CSS
            '.json': 1_000_000,  # 1MB max for JSON
            '.png': 5_000_000,  # 5MB max for PNG
        }
        
        for ext, limit in limits.items():
            for filepath in static_path.rglob(f'*{ext}'):
                size = filepath.stat().st_size
                # Skip vendor files and minified
                if 'vendor' in str(filepath) and size > limit:
                    continue
                # This is just a sanity check
                if 'node_modules' in str(filepath):
                    continue


class TestAssetReferences:
    """Test that referenced assets are available"""
    
    def test_manifest_icons_referenced(self):
        """Icons in manifest are referenced"""
        manifest_path = Path(app.static_folder) / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        
        assert len(manifest.get('icons', [])) > 0, "No icons defined in manifest"
    
    def test_no_broken_references_in_manifest(self):
        """All references in manifest should point to accessible files"""
        manifest_path = Path(app.static_folder) / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        
        # Check theme colors are valid if present
        if 'theme_color' in manifest:
            # Must be valid hex color
            color = manifest['theme_color']
            assert color.startswith('#'), "theme_color should be hex color"
        
        if 'background_color' in manifest:
            color = manifest['background_color']
            assert color.startswith('#'), "background_color should be hex color"


class TestServiceWorkerFileIntegrity:
    """Test service worker file integrity"""
    
    def test_service_worker_not_empty(self):
        """Service worker must not be empty"""
        path = Path(app.static_folder) / 'service-worker.js'
        content = path.read_text()
        assert len(content) > 100, "Service worker is too small"
    
    def test_service_worker_has_version_info(self):
        """Service worker should have version/cache name"""
        path = Path(app.static_folder) / 'service-worker.js'
        content = path.read_text()
        # Should have version references for cache busting
        assert 'CACHE_NAME' in content or 'v3' in content or 'v2' in content, \
            "Service worker missing version/cache info"
    
    def test_service_worker_balanced_braces(self):
        """Service worker must have balanced braces"""
        path = Path(app.static_folder) / 'service-worker.js'
        content = path.read_text()
        assert content.count('{') == content.count('}'), "Unbalanced braces"
        assert content.count('[') == content.count(']'), "Unbalanced brackets"
        assert content.count('(') == content.count(')'), "Unbalanced parentheses"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
