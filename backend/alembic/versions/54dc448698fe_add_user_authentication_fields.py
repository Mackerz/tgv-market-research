"""add_user_authentication_fields

Revision ID: 54dc448698fe
Revises: 45e5f4f62889
Create Date: 2025-10-21 17:55:47.715916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54dc448698fe'
down_revision = '45e5f4f62889'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))

    # Create indexes for new columns
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_users_google_id', table_name='users')

    # Remove columns
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'hashed_password')