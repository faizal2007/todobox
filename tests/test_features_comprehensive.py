#!/usr/bin/env python
"""
Comprehensive manual test of all registration and terms features
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import User, TermsAndDisclaimer
from app.verification import VerificationToken
import markdown

def test_terms_model():
    """Test TermsAndDisclaimer model"""
    print("\n=== Testing TermsAndDisclaimer Model ===")
    with app.app_context():
        # Test get_active
        active = TermsAndDisclaimer.get_active()
        print(f"✓ get_active() returned: {active}")
        
        # Test get_or_create_default
        default = TermsAndDisclaimer.get_or_create_default()
        print(f"✓ get_or_create_default() version: {default.version}")
        
        # Check if it has terms and disclaimer
        assert default.terms_of_use, "Terms of Use missing"
        assert default.disclaimer, "Disclaimer missing"
        print(f"✓ Default terms created with {len(default.terms_of_use)} chars")
        print(f"✓ Default disclaimer created with {len(default.disclaimer)} chars")

def test_user_model():
    """Test User model with new fields"""
    print("\n=== Testing User Model ===")
    with app.app_context():
        # Test created_at field
        user = User(email='test@example.com')
        assert hasattr(user, 'created_at'), "User missing created_at field"
        print(f"✓ User has created_at field")
        
        # Test terms_accepted_version field
        assert hasattr(user, 'terms_accepted_version'), "User missing terms_accepted_version field"
        print(f"✓ User has terms_accepted_version field")
        
        # Test email_verified field
        assert hasattr(user, 'email_verified'), "User missing email_verified field"
        print(f"✓ User has email_verified field")

def test_markdown_rendering():
    """Test markdown to HTML rendering"""
    print("\n=== Testing Markdown Rendering ===")
    with app.app_context():
        from bleach import clean
        
        # Get the markdown filter from the app
        test_md = """# Terms of Use

This is **bold** text.

- Item 1
- Item 2

~~Strikethrough~~ text."""
        
        # Test rendering
        html = markdown.markdown(test_md, extensions=['fenced_code', 'tables', 'pymdownx.tilde'])
        print(f"✓ Markdown rendered to HTML: {len(html)} chars")
        
        # Check for key elements
        assert '<h1>' in html, "Header not rendered"
        assert '<strong>' in html, "Bold not rendered"
        assert '<li>' in html, "List not rendered"
        assert '<del>' in html or '<s>' in html, "Strikethrough not rendered"
        print(f"✓ All markdown elements rendered correctly")

def test_verification_tokens():
    """Test email verification token system"""
    print("\n=== Testing Email Verification ===")
    with app.app_context():
        email = 'testuser@example.com'
        
        # Create a test user first
        user = User(email=email)
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Create verification token
        token, expires_at = VerificationToken.create_verification_token(user)
        print(f"✓ Verification token created: {token[:20]}...")
        
        # Verify the token
        is_valid = VerificationToken.verify_email_token(token, email)
        assert is_valid, "Token verification failed"
        print(f"✓ Token verification successful")
        
        # Test with wrong email
        is_valid = VerificationToken.verify_email_token(token, 'wrong@example.com')
        assert not is_valid, "Token should not verify for different email"
        print(f"✓ Token correctly rejects wrong email")
        
        # Clean up
        db.session.delete(user)
        db.session.commit()

def test_database_migration():
    """Test that all new columns exist"""
    print("\n=== Testing Database Columns ===")
    with app.app_context():
        # Check User table columns
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        user_columns = [c['name'] for c in inspector.get_columns('user')]
        
        assert 'created_at' in user_columns, "created_at column missing from user table"
        print(f"✓ created_at column exists in user table")
        
        assert 'terms_accepted_version' in user_columns, "terms_accepted_version column missing"
        print(f"✓ terms_accepted_version column exists in user table")
        
        assert 'email_verified' in user_columns, "email_verified column missing"
        print(f"✓ email_verified column exists in user table")
        
        # Check TermsAndDisclaimer table
        terms_columns = [c['name'] for c in inspector.get_columns('terms_and_disclaimer')]
        assert 'version' in terms_columns, "version column missing from terms table"
        assert 'terms_of_use' in terms_columns, "terms_of_use column missing"
        assert 'disclaimer' in terms_columns, "disclaimer column missing"
        assert 'is_active' in terms_columns, "is_active column missing"
        print(f"✓ All TermsAndDisclaimer columns exist")

def test_routes_exist():
    """Test that all new routes are registered"""
    print("\n=== Testing Routes Registration ===")
    
    routes_to_check = [
        '/register',
        '/verify-email/<token>',
        '/resend-verification',
        '/admin/terms',
        '/accept-terms-oauth'
    ]
    
    registered_routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    for route in routes_to_check:
        # For parameterized routes, just check the base
        base_route = route.split('<')[0].rstrip('/')
        found = any(base_route in r for r in registered_routes)
        assert found, f"Route {route} not registered"
        print(f"✓ Route {route} is registered")

def test_templates_exist():
    """Test that all templates exist"""
    print("\n=== Testing Templates ===")
    import os
    template_dir = 'app/templates'
    
    templates_to_check = [
        'register.html',
        'verification_sent.html',
        'resend_verification.html',
        'admin/manage_terms.html',
        'accept_terms_oauth.html'
    ]
    
    for template in templates_to_check:
        path = os.path.join(template_dir, template)
        assert os.path.exists(path), f"Template {template} not found"
        print(f"✓ Template {template} exists")

def test_markdown_filter():
    """Test the render_markdown template filter"""
    print("\n=== Testing Markdown Filter ===")
    
    # Check if filter is registered
    assert 'render_markdown' in app.jinja_env.filters, "render_markdown filter not registered"
    print(f"✓ render_markdown filter is registered")
    
    with app.app_context():
        filter_func = app.jinja_env.filters['render_markdown']
        
        # Test basic rendering
        result = filter_func("**bold** and *italic*")
        assert '<strong>' in result, "Bold not rendered"
        assert '<em>' in result, "Italic not rendered"
        print(f"✓ Filter renders markdown correctly")

def main():
    """Run all tests"""
    print("=" * 60)
    print("COMPREHENSIVE FEATURE TEST")
    print("=" * 60)
    
    try:
        test_terms_model()
        test_user_model()
        test_markdown_rendering()
        test_verification_tokens()
        test_database_migration()
        test_routes_exist()
        test_templates_exist()
        test_markdown_filter()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
