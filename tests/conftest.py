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
@pytest.fixture(autouse=True)
def purge_example_test_users():
    """Autouse fixture to remove test users and their data before each test.

    Deletes rows for emails under known test domains to avoid UNIQUE
    constraint violations when tests re-create the same users repeatedly.
    Does NOT drop tables.
    """
    from app import app, db
    from app.models import User, Todo, Tracker, KIV, TodoShare, ShareInvitation, DeletedAccount
    # Use a temporary app context for cleanup only; do not keep it active
    with app.app_context():
        # Allow disabling via env if needed
        import os as _os
        if _os.environ.get('DISABLE_PURGE_TEST_EMAILS') == '1':
            return

        # Purge emails under test domains
        test_domains = ['@example.com', '@test.com']

        # Collect users to purge
        users = User.query.filter(
            (User.email.like('%@example.com')) | (User.email.like('%@test.com'))
        ).all()

        for u in users:
            try:
                # Delete trackers and KIV entries for user's todos
                todos = Todo.query.filter_by(user_id=u.id).all()
                todo_ids = [t.id for t in todos]
                if todo_ids:
                    Tracker.query.filter(Tracker.todo_id.in_(todo_ids)).delete(synchronize_session=False)
                    KIV.query.filter(KIV.todo_id.in_(todo_ids)).delete(synchronize_session=False)
                    Todo.query.filter(Todo.id.in_(todo_ids)).delete(synchronize_session=False)

                # Delete sharing relationships and invitations
                TodoShare.query.filter((TodoShare.owner_id == u.id) | (TodoShare.shared_with_id == u.id)).delete(synchronize_session=False)
                ShareInvitation.query.filter((ShareInvitation.from_user_id == u.id) | (ShareInvitation.to_email == u.email)).delete(synchronize_session=False)
                DeletedAccount.query.filter(DeletedAccount.email == u.email).delete(synchronize_session=False)

                # Finally delete the user
                db.session.delete(u)
                db.session.commit()
            except Exception:
                db.session.rollback()
                # Continue purging other users even if one fails
                continue


@pytest.fixture(autouse=True)
def ensure_status_new_id5():
    """Autouse fixture to ensure `Status(id=5, name='new')` exists.

    Some tests insert `Tracker` rows referencing `status_id=5` without using
    the `app` fixture. To avoid foreign key violations across all databases,
    ensure this status row is present and normalized before each test.
    """
    from app import app, db
    from app.models import Status
    with app.app_context():
        try:
            existing_id5 = db.session.get(Status, 5)
        except Exception:
            existing_id5 = Status.query.filter_by(id=5).first()
        if existing_id5 is None:
            s = Status(name='new')
            s.id = 5
            db.session.add(s)
            db.session.commit()
        elif getattr(existing_id5, 'name', None) != 'new':
            existing_id5.name = 'new'
            db.session.commit()


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
    # Allow adding routes in tests even if app handled prior requests
    try:
        app._got_first_request = False  # type: ignore[attr-defined]
    except Exception:
        pass
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
    
    # Perform setup within an application context and keep it active during tests
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

        # Ensure status with id=5 exists and represents 'new' to prevent FK violations
        # Some tests insert tracker rows with status_id=5 expecting the 'new' status.
        try:
            existing_id5 = db.session.get(Status, 5)
        except Exception:
            existing_id5 = Status.query.filter_by(id=5).first()
        if existing_id5 is None:
            s = Status(name='new')
            s.id = 5
            db.session.add(s)
            db.session.commit()
        elif getattr(existing_id5, 'name', None) != 'new':
            existing_id5.name = 'new'
            db.session.commit()

        # Seed/normalize terms: ensure exactly one active version and it's '1.0'
        from sqlalchemy import or_
        existing_terms = TermsAndDisclaimer.query.all()
        for term in existing_terms:
            term.is_active = False
        db.session.commit()

        default = TermsAndDisclaimer.query.filter_by(version='1.0').first()
        if not default:
            default = TermsAndDisclaimer(
                terms_of_use='These are the terms of use.',
                disclaimer='This is the disclaimer.',
                version='1.0',
                is_active=True
            )
            db.session.add(default)
        else:
            default.is_active = True
        db.session.commit()

        # Yield app while context is active
        # Clean any test endpoints that might conflict when redefined in tests
        try:
            for ep in ['test_route']:
                app.view_functions.pop(ep, None)
        except Exception:
            pass
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
