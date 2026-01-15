import pytest
from flask_login import login_user as flask_login_user
from app.models import User
from app import db

@pytest.fixture
def test_user(app):
    """Create a test user for login."""
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(email='test@example.com', fullname='Test User')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        return user

@pytest.fixture
def login_user(app, client, test_user):
    """Log in the test user for a test."""
    def do_login(user=None):
        with app.app_context():
            flask_login_user(user or test_user)
    return do_login
