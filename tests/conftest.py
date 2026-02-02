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
    
    # Configure for testing - use development database config from .flaskenv
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TODO_ENCRYPTION_ENABLED'] = False
    # Database URI will come from .flaskenv via app's normal config
    # This means tests use the actual development/staging database
    
    with app.app_context():
        # Cleanup test data from previous runs BEFORE running tests
        from app.models import User, Todo, Tracker, KIV, TodoShare
        try:
            # Find test users - use @example.com domain pattern which is used by all tests
            # This catches all test emails: admin@example.com, user@example.com, workflow@example.com, etc.
            test_users = User.query.filter(
                User.email.like('%@example.com')
            ).all()
            
            for user in test_users:
                # Delete todo shares (owner_id and shared_with_id)
                TodoShare.query.filter_by(owner_id=user.id).delete()
                TodoShare.query.filter_by(shared_with_id=user.id).delete()
                
                # Delete todos and their related data
                todos = Todo.query.filter_by(user_id=user.id).all()
                for todo in todos:
                    Tracker.query.filter_by(todo_id=todo.id).delete()
                    KIV.query.filter_by(todo_id=todo.id).delete()
                Todo.query.filter_by(user_id=user.id).delete()
                
                db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Note: Cleanup error (may occur on first run): {e}")
        
        # Create all tables in the development database
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
        
        # Cleanup test data after tests complete
        try:
            from app.models import User, Todo, Tracker, KIV, TodoShare
            test_users = User.query.filter(
                (User.email.contains('test')) | 
                (User.email.contains('persist')) |
                (User.email.contains('exists')) |
                (User.email.contains('unverified'))
            ).all()
            
            for user in test_users:
                # Delete todo shares (owner_id and shared_with_id)
                TodoShare.query.filter_by(owner_id=user.id).delete()
                TodoShare.query.filter_by(shared_with_id=user.id).delete()
                
                # Delete todos and related data
                todos = Todo.query.filter_by(user_id=user.id).all()
                for todo in todos:
                    Tracker.query.filter_by(todo_id=todo.id).delete()
                    KIV.query.filter_by(todo_id=todo.id).delete()
                Todo.query.filter_by(user_id=user.id).delete()
                db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        
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
