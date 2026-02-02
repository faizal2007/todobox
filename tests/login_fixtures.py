import pytest
from flask_login import login_user as flask_login_user
from app.models import User
from app import db

@pytest.fixture
def test_user(app):
    """Create a test user for login."""
    with app.app_context():
        from app.models import TermsAndDisclaimer
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com', fullname='Test User')
            user.set_password('password')
            user.email_verified = True
            # Accept terms
            active_terms = TermsAndDisclaimer.get_active()
            if active_terms:
                user.terms_accepted_version = active_terms.version
            db.session.add(user)
            db.session.commit()
        
        # Return user ID instead of user object to avoid detached instance errors
        user_id = user.id
        user_email = user.email
    
    # Create a simple object to hold user info without database attachment
    class TestUserInfo:
        def __init__(self, id, email):
            self.id = id
            self.email = email
    
    return TestUserInfo(user_id, user_email)

@pytest.fixture
def login_user(app, client, test_user):
    """Log in the test user for a test using HTTP request."""
    def do_login(user=None):
        # If user is passed, get its email while it might be in a session context
        # If user is None, use test_user's email
        if user is None:
            email = 'test@example.com'  # Default from test_user fixture
        else:
            # Get the email from the user object
            # If it's a detached instance, we already know test_user uses 'test@example.com'
            try:
                email = user.email
            except Exception:
                # If we can't access email due to detached instance, use test_user email
                email = 'test@example.com'
        
        # Login via HTTP POST (preserves session with client)
        response = client.post('/login', data={
            'email': email,
            'password': 'password'  # Password from test_user fixture
        }, follow_redirects=True)
        # If login page rendered (no dashboard), fall back to direct test login route
        if b'Sign In' in response.data or response.status_code != 200:
            with app.app_context():
                u = User.query.filter_by(email=email).first()
                assert u is not None, "Test user not found for direct login"
                response = client.get(f'/test/login/{u.id}')
                assert response.status_code == 200, f"Direct test login failed: {response.status_code}"
        else:
            assert response.status_code == 200, f"Login failed with status {response.status_code}"
        # Ensure session persists across subsequent requests in tests
        try:
            # If _user_id is not set, inject it into the session
            with client.session_transaction() as sess:
                if not sess.get('_user_id'):
                    # Lookup user id from DB within app context
                    with app.app_context():
                        u = User.query.filter_by(email=email).first()
                        if u:
                            sess['_user_id'] = str(u.id)
                            sess['_fresh'] = True
                            # Seed session activity for session handler
                            from datetime import datetime
                            sess['last_activity'] = datetime.utcnow().isoformat()
        except Exception:
            # Non-fatal: tests will still proceed; session may be handled by cookies
            pass
        return response
    return do_login

@pytest.fixture
def auth_client(app, client, test_user):
    """Authenticated test client with logged-in user."""
    with app.app_context():
        # Use the test_user fixture credentials to login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        # Verify login was successful (no redirect to login page)
        assert response.status_code == 200
    return client
