"""
Pytest configuration and shared fixtures for all tests

Goal: Run tests against the configured database (from .flaskenv) without
ever dropping tables. Tests may insert/update/delete rows, but schema
changes are prohibited.
"""
import pytest
import os
import sys

# Respect the configured database. To force SQLite, set FORCE_SQLITE_FOR_TESTS=1


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import login fixtures for pytest discovery
from tests.login_fixtures import *


@pytest.fixture(scope="function")
def app(request):
    """Create and configure a test application instance.
    
    IMPORTANT: Tests use the DEVELOPMENT database from .flaskenv, not in-memory SQLite.
    This ensures tests run against the same database setup as production.
    Database configuration comes from .flaskenv:
    - DB_URL: 192.168.1.112
    - DB_USER: freakie
    - DB_NAME: shimasu_db
    
    NOTE: Test data cleanup happens between tests to avoid conflicts.
    """
    
    from app import app, db
    
    # Configure for testing - isolate using SQLite to avoid impacting dev DB
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Default encryption disabled; selectively enable for specific test modules
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    # Ensure cookies persist in test client (HTTP, not HTTPS)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['SERVER_NAME'] = 'localhost'
    # If explicitly forced, use in-memory SQLite for isolation; otherwise
    # use the configured DB from .flaskenv (mysql/postgres/sqlite file)
    if os.environ.get('FORCE_SQLITE_FOR_TESTS') == '1':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Enable encryption for utility tests that expect it
    try:
        fspath = str(request.node.fspath)
        if fspath.endswith('test_utility_functions.py'):
            app.config['TODO_ENCRYPTION_ENABLED'] = True
    except Exception:
        pass
    
    with app.app_context():
        # Initialize schema only for in-memory SQLite; never drop tables.
        try:
            uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
        except Exception:
            uri = ''
        if uri.startswith('sqlite:///:memory:'):
            db.create_all()
        
        # Seed status data if needed
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
        
        # Seed terms and disclaimer if needed
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
        
        # Ensure session removal after each test
        db.session.remove()


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
