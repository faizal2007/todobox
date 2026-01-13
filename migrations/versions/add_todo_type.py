"""Add todo_type column to support simple and advanced todo types

Revision ID: add_todo_type_001
Revises: 0e7e1c5570bc
Create Date: 2026-01-13 11:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_todo_type_001'
down_revision = '0e7e1c5570bc'
branch_labels = None
depends_on = None


def upgrade():
    # Add todo_type column with default value 'advanced'
    op.add_column('todo', sa.Column('todo_type', sa.String(20), nullable=False, server_default='advanced'))


def downgrade():
    # Remove todo_type column
    op.drop_column('todo', 'todo_type')
