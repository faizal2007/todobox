"""
Test utilities and shared fixtures for TodoBox tests.
"""


def apply_werkzeug_version_workaround():
    """
    Apply werkzeug version compatibility workaround.
    
    Some versions of Flask-Login expect werkzeug to have a __version__ attribute,
    but newer versions of werkzeug don't include it. This workaround adds it.
    
    Should be called in test client fixtures before creating the test client.
    """
    import werkzeug
    if not hasattr(werkzeug, '__version__'):
        werkzeug.__version__ = '3.0.0'


def seed_status_data(db):
    """
    Seed database with status data.
    
    Args:
        db: SQLAlchemy database instance
        
    Status IDs start at 5 for historical compatibility
    with existing database records.
    """
    from app.models import Status
    
    if Status.query.count() == 0:
        statuses = [
            Status(name='new'),
            Status(name='done'),
            Status(name='failed'),
            Status(name='re-assign')
        ]
        for i, status in enumerate(statuses, start=5):
            status.id = i
        db.session.add_all(statuses)
        db.session.commit()
