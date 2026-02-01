"""
Pytest configuration and shared fixtures for all tests

CRITICAL FIX: Prevents tests from dropping production MariaDB tables by:
1. Using in-memory SQLite for all tests
2. Disposing old connections and creating fresh test database
3. Ensuring db.drop_all() only affects test database, never production
"""
import pytest
import os
import sys


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import login fixtures for pytest discovery
from tests.login_fixtures import *


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance with ISOLATED database.
    
    CRITICAL FIX: Reconfigures the global app to use in-memory SQLite instead of
    production MariaDB. This ensures db.drop_all() during teardown only affects
    the test database, never the production database.
    """
    
    from app import app, db
    
    # Save original config to restore later
    original_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # CRITICAL: Override database configuration BEFORE app context
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    
    with app.app_context():
        # Dispose of any existing connections to MariaDB
        db.engine.dispose()
        
        # Create all tables in the in-memory test database
        db.create_all()
        
        # Seed status data
        from app.models import Status, TermsAndDisclaimer
        if Status.query.count() == 0:
            statuses = [
                Status(name='new'),
                Status(name='done'),
                Status(name='failed'),
                Status(name='re-assign'),
                Status(name='kiv'),
                Status(name='started'),
                Status(name='paused'),
                Status(name='resumed')
            ]
            for i, status in enumerate(statuses, start=5):
                status.id = i
            db.session.add_all(statuses)
            db.session.commit()
        
        # Seed terms and disclaimer
        if TermsAndDisclaimer.query.count() == 0:
            terms = TermsAndDisclaimer(
                terms_of_use='These are the terms of use.',
                disclaimer='This is the disclaimer.',
                version='1.0',
                is_active=True
            )
            db.session.add(terms)
            db.session.commit()
        else:
            # Ensure only one active terms record
            active_terms = TermsAndDisclaimer.query.filter_by(is_active=True).all()
            if len(active_terms) > 1:
                for term in active_terms[1:]:
                    term.is_active = False
                db.session.commit()
        
        yield app
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()  # Only drops in-memory test database, NOT production MariaDB
        
        # Restore original database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri
        db.engine.dispose()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for tests."""
    from app import db
    
    class DBSession:
        def __init__(self, session):
            self.session = session
    
    return DBSession(db.session)
