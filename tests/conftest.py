"""
Pytest configuration and shared fixtures for all tests

CRITICAL FIX: Prevents tests from dropping production MariaDB tables by:
1. Using in-memory SQLite for all tests
2. Monkeypatching the global db to use test database
3. Ensuring db.drop_all() only affects test database, never production
"""
import pytest
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import login fixtures for pytest discovery
from tests.login_fixtures import *


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance with ISOLATED database.
    
    CRITICAL: This creates a completely separate Flask app with in-memory SQLite
    database to prevent tests from accidentally dropping production MariaDB tables.
    
    The global 'app' and 'db' from app/__init__.py are monkeypatched to use this
    test app and test_db, ensuring NO database operations touch production.
    """
    
    # Create a FRESH Flask app instance for testing
    test_app = Flask(__name__, instance_relative_config=True)
    
    # Configure for testing ONLY - never connect to production database
    test_app.config['TESTING'] = True
    test_app.config['WTF_CSRF_ENABLED'] = False
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    test_app.config['TODO_ENCRYPTION_ENABLED'] = False
    
    # Create isolated database instance for this test
    test_db = SQLAlchemy(test_app)
    
    # Monkeypatch the global app and db to prevent tests from using production database
    import app as app_module
    original_app = app_module.app
    original_db = app_module.db
    app_module.app = test_app
    app_module.db = test_db
    
    with test_app.app_context():
        # Import models inside app context to use test_db
        from app.models import User, Todo, Status, TermsAndDisclaimer, Tracker, KIV, DeletedAccount, TodoShare, ShareInvitation
        
        # Create all tables in the test database
        test_db.create_all()
        
        # Seed status data
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
            test_db.session.add_all(statuses)
            test_db.session.commit()
        
        # Seed terms and disclaimer
        if TermsAndDisclaimer.query.count() == 0:
            terms = TermsAndDisclaimer(
                terms_of_use='These are the terms of use.',
                disclaimer='This is the disclaimer.',
                version='1.0',
                is_active=True
            )
            test_db.session.add(terms)
            test_db.session.commit()
        else:
            # Ensure only one active terms record
            active_terms = TermsAndDisclaimer.query.filter_by(is_active=True).all()
            if len(active_terms) > 1:
                for term in active_terms[1:]:
                    term.is_active = False
                test_db.session.commit()
        
        # Store references for other fixtures
        test_app.test_db = test_db
        test_app.original_app = original_app
        test_app.original_db = original_db
        
        yield test_app
        
        # Cleanup after test
        test_db.session.remove()
        test_db.drop_all()  # Only drops in-memory test database, NOT production MariaDB
        
        # Restore original app and db
        app_module.app = original_app
        app_module.db = original_db


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for tests using the isolated test database."""
    
    class DBSession:
        def __init__(self, session):
            self.session = session
    
    return DBSession(app.test_db.session)
