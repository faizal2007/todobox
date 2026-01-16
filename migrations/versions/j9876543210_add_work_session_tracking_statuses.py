"""Add work session tracking statuses (Started, Paused, Resumed)

Revision ID: j9876543210
Revises: add_todo_type_001
Create Date: 2026-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j9876543210'
down_revision = 'add_todo_type_001'
branch_labels = None
depends_on = None


def upgrade():
    """Add new status records for work session tracking"""
    connection = op.get_bind()
    
    # Insert new status records for work session tracking
    # Status 10: Started - marks when user begins working on a todo
    # Status 11: Paused - marks when user pauses work on a todo
    # Status 12: Resumed - marks when user resumes work on a paused todo
    
    insert_sql = """
    INSERT IGNORE INTO status (id, name) VALUES
    (10, 'started'),
    (11, 'paused'),
    (12, 'resumed');
    """
    
    try:
        connection.execute(sa.text(insert_sql))
    except Exception as e:
        print(f"Warning: Could not insert status records: {str(e)}")


def downgrade():
    """Remove work session tracking statuses"""
    connection = op.get_bind()
    
    # Remove the work session statuses
    delete_sql = """
    DELETE FROM status WHERE id IN (10, 11, 12);
    """
    
    try:
        connection.execute(sa.text(delete_sql))
    except Exception as e:
        print(f"Warning: Could not delete status records: {str(e)}")
