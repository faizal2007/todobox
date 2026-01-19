"""Add database indexes for performance optimization

Revision ID: p7_001_performance_indexes
Revises: None
Create Date: 2026-01-17

This migration adds critical database indexes to resolve N+1 query problems
and improve query performance for common access patterns.

Indexes Added:
1. idx_todo_user_target_date - For /today /tomorrow /later views
2. idx_tracker_todo_status - For tracker lookups by todo and status
3. idx_tracker_todo_timestamp - For latest tracker queries
4. idx_user_email - For email-based lookups
5. idx_user_oauth_id - For OAuth lookups
6. idx_tracker_status - For status joins
7. idx_status_name - For status by name lookups
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'p7_001_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for performance optimization"""
    
    # 1. Index for /today, /tomorrow, /later views
    # Filters by user_id and target_date - most common query pattern
    op.create_index(
        'idx_todo_user_target_date',
        'todo',
        ['user_id', 'target_date'],
        unique=False
    )
    
    # 2. Index for tracker lookups by todo and status
    # Used when querying tracker for specific status
    op.create_index(
        'idx_tracker_todo_status',
        'tracker',
        ['todo_id', 'status_id'],
        unique=False
    )
    
    # 3. Index for getting latest tracker of a todo
    # Used in lines 778, 863 - order by timestamp desc
    op.create_index(
        'idx_tracker_todo_timestamp',
        'tracker',
        ['todo_id', 'timestamp'],
        unique=False
    )
    
    # 4. Index for user email lookups
    # Used in login, registration, OAuth matching
    op.create_index(
        'idx_user_email',
        'user',
        ['email'],
        unique=True
    )
    
    # 5. Index for user OAuth lookups
    # Used in OAuth flow
    op.create_index(
        'idx_user_oauth_id',
        'user',
        ['oauth_id'],
        unique=False
    )
    
    # 6. Index for tracker status joins
    # Used in status queries with joins
    op.create_index(
        'idx_tracker_status',
        'tracker',
        ['status_id'],
        unique=False
    )
    
    # 7. Index for status name lookups
    # Used in status.query.filter_by(name=...) queries
    op.create_index(
        'idx_status_name',
        'status',
        ['name'],
        unique=False
    )


def downgrade():
    """Remove indexes"""
    
    op.drop_index('idx_todo_user_target_date', table_name='todo')
    op.drop_index('idx_tracker_todo_status', table_name='tracker')
    op.drop_index('idx_tracker_todo_timestamp', table_name='tracker')
    op.drop_index('idx_user_email', table_name='user')
    op.drop_index('idx_user_oauth_id', table_name='user')
    op.drop_index('idx_tracker_status', table_name='tracker')
    op.drop_index('idx_status_name', table_name='status')
