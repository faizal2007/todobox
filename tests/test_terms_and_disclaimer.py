"""
Tests for Terms and Disclaimer feature
Tests for admin functionality to manage terms
Tests for registration with terms acceptance
"""
import pytest
from app.models import User, TermsAndDisclaimer


class TestTermsAndDisclaimerModel:
    """Test the TermsAndDisclaimer model"""
    
    def test_terms_model_creation(self, app, db_session):
        """Test creating a TermsAndDisclaimer record"""
        with app.app_context():
            terms = TermsAndDisclaimer(
                terms_of_use="<p>Test Terms</p>",
                disclaimer="<p>Test Disclaimer</p>",
                version="1.0",
                is_active=True
            )
            db_session.session.add(terms)
            db_session.session.commit()
            
            assert terms.id is not None
            assert terms.version == "1.0"
            assert terms.is_active is True
    
    def test_get_active_terms(self, app, db_session):
        """Test getting active terms"""
        with app.app_context():
            # Create inactive terms
            inactive_terms = TermsAndDisclaimer(
                terms_of_use="<p>Old Terms</p>",
                disclaimer="<p>Old Disclaimer</p>",
                version="0.9",
                is_active=False
            )
            db_session.session.add(inactive_terms)
            db_session.session.commit()
            
            # Create active terms
            active_terms = TermsAndDisclaimer(
                terms_of_use="<p>Current Terms</p>",
                disclaimer="<p>Current Disclaimer</p>",
                version="1.0",
                is_active=True
            )
            db_session.session.add(active_terms)
            db_session.session.commit()
            
            result = TermsAndDisclaimer.get_active()
            assert result.id == active_terms.id
            assert result.version == "1.0"
    
    def test_get_or_create_default(self, app, db_session):
        """Test getting or creating default terms"""
        with app.app_context():
            # Should create default if none exist
            terms = TermsAndDisclaimer.get_or_create_default()
            
            assert terms is not None
            assert terms.version == "1.0"
            assert terms.is_active is True
            assert len(terms.terms_of_use) > 0
            assert len(terms.disclaimer) > 0


class TestAdminManageTerms:
    """Test admin management of terms and disclaimer"""
    
    @pytest.fixture
    def admin_user(self, app, db_session):
        """Create an admin user"""
        with app.app_context():
            user = User(email='admin@example.com')
            user.set_password('AdminPass123!')
            user.is_admin = True
            db_session.session.add(user)
            db_session.session.commit()
            return user
    
    @pytest.fixture
    def admin_client(self, client, admin_user, app):
        """Admin authenticated client"""
        with app.app_context():
            client.post('/login', data={
                'email': 'admin@example.com',
                'password': 'AdminPass123!'
            }, follow_redirects=True)
        return client
    
    def test_admin_access_manage_terms_page(self, admin_client):
        """Test admin can access terms management page"""
        response = admin_client.get('/admin/terms')
        assert response.status_code == 200
        assert b'Edit Terms and Disclaimer' in response.data
    
    def test_non_admin_cannot_access_manage_terms(self, app, client, db_session):
        """Test non-admin users cannot access terms management"""
        with app.app_context():
            user = User(email='user@example.com')
            user.set_password('Pass123!')
            db_session.session.add(user)
            db_session.session.commit()
            
            client.post('/login', data={
                'email': 'user@example.com',
                'password': 'Pass123!'
            }, follow_redirects=True)
            
            response = client.get('/admin/terms')
            assert response.status_code in [302, 403]
    
    def test_admin_update_terms(self, app, admin_client, db_session):
        """Test admin can update terms and disclaimer"""
        new_terms_html = "<h4>New Terms</h4><p>Updated terms content</p>"
        new_disclaimer_html = "<h4>New Disclaimer</h4><p>Updated disclaimer content</p>"
        
        response = admin_client.post('/admin/terms', data={
            'version': '1.1',
            'terms_of_use': new_terms_html,
            'disclaimer': new_disclaimer_html
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Terms and Disclaimer updated successfully' in response.data
        
        with app.app_context():
            # Verify new version is created and active
            active_terms = TermsAndDisclaimer.get_active()
            assert active_terms.version == "1.1"
            assert active_terms.is_active is True
            assert new_terms_html in active_terms.terms_of_use
            assert new_disclaimer_html in active_terms.disclaimer
    
    def test_admin_cannot_update_with_empty_terms(self, admin_client):
        """Test admin cannot submit empty terms"""
        response = admin_client.post('/admin/terms', data={
            'version': '1.1',
            'terms_of_use': '',
            'disclaimer': '<p>Test</p>'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Both Terms of Use and Disclaimer are required' in response.data


class TestRegistrationWithTerms:
    """Test registration form with terms acceptance"""
    
    def test_registration_page_displays_terms(self, client):
        """Test that registration page displays terms"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Terms of Use' in response.data
        assert b'Disclaimer' in response.data
        assert b'accept_terms' in response.data
    
    def test_registration_without_accepting_terms_fails(self, client):
        """Test registration fails if terms not accepted"""
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123',
            'fullname': 'Test User',
            'accept_terms': False
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'must accept' in response.data.lower()
    
    def test_registration_with_accepted_terms_succeeds(self, app, client):
        """Test registration succeeds when terms are accepted"""
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123',
            'fullname': 'Test User',
            'accept_terms': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show verification email message
        assert b'verification' in response.data.lower() or b'email' in response.data.lower()
        
        with app.app_context():
            # Verify user was created
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.fullname == 'Test User'
    
    def test_registration_form_has_terms_checkbox(self, client):
        """Test that registration form includes terms checkbox"""
        response = client.get('/register')
        assert b'accept_terms' in response.data
        assert b'I agree to the Terms of Use and Disclaimer' in response.data


class TestTermsVersioning:
    """Test terms versioning system"""
    
    def test_multiple_versions_can_exist(self, app, db_session):
        """Test that multiple versions can coexist"""
        with app.app_context():
            v1 = TermsAndDisclaimer(
                version="1.0",
                terms_of_use="<p>v1</p>",
                disclaimer="<p>v1 disclaimer</p>",
                is_active=False
            )
            v2 = TermsAndDisclaimer(
                version="2.0",
                terms_of_use="<p>v2</p>",
                disclaimer="<p>v2 disclaimer</p>",
                is_active=True
            )
            db_session.session.add(v1)
            db_session.session.add(v2)
            db_session.session.commit()
            
            all_versions = TermsAndDisclaimer.query.all()
            assert len(all_versions) >= 2
            assert len([v for v in all_versions if v.is_active]) == 1
    
    def test_version_timestamps(self, app, db_session):
        """Test that created_at and updated_at are set"""
        with app.app_context():
            terms = TermsAndDisclaimer(
                version="1.0",
                terms_of_use="<p>Test</p>",
                disclaimer="<p>Test</p>",
                is_active=True
            )
            db_session.session.add(terms)
            db_session.session.commit()
            
            assert terms.created_at is not None
            assert terms.updated_at is not None


class TestTermsIntegration:
    """Integration tests for terms system"""
    
    def test_new_registration_sees_latest_terms(self, app, client, db_session):
        """Test that new users see the latest terms during registration"""
        with app.app_context():
            # Create v1 terms
            v1 = TermsAndDisclaimer(
                version="1.0",
                terms_of_use="<p>Version 1</p>",
                disclaimer="<p>Version 1 disclaimer</p>",
                is_active=False
            )
            db_session.session.add(v1)
            db_session.session.commit()
            
            # Create v2 terms
            v2 = TermsAndDisclaimer(
                version="2.0",
                terms_of_use="<p>Version 2</p>",
                disclaimer="<p>Version 2 disclaimer</p>",
                is_active=True
            )
            db_session.session.add(v2)
            db_session.session.commit()
        
        # Visit registration page
        response = client.get('/register')
        assert response.status_code == 200
        # Should see version 2
        assert b'Version 2' in response.data
    
    def test_admin_dashboard_link_to_terms_management(self, app, client, db_session):
        """Test that admin panel has link to terms management"""
        with app.app_context():
            admin = User(email='admin@example.com')
            admin.set_password('AdminPass123!')
            admin.is_admin = True
            db_session.session.add(admin)
            db_session.session.commit()
            
            client.post('/login', data={
                'email': 'admin@example.com',
                'password': 'AdminPass123!'
            }, follow_redirects=True)
            
            response = client.get('/admin')
            assert response.status_code == 200
            assert b'Manage Terms' in response.data
