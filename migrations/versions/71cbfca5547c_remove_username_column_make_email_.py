"""Remove username column, make email required

Revision ID: 71cbfca5547c
Revises: f8802884f95e
Create Date: 2025-11-30 12:44:45.572534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71cbfca5547c'
down_revision = 'f8802884f95e'
branch_labels = None
depends_on = None


def upgrade():
    # Make email column NOT NULL
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.String(length=120),
               nullable=False)
        batch_op.drop_column('username')


def downgrade():
    # Add back username column and make email nullable again
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=64), nullable=True))
        batch_op.create_index('ix_user_username', ['username'], unique=True)
        batch_op.alter_column('email',
               existing_type=sa.String(length=120),
               nullable=True)
    
    # Note: This downgrade will leave username NULL for existing users
    # You may need to manually populate usernames if rolling back
