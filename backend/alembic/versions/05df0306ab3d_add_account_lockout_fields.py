"""add_account_lockout_fields

Revision ID: 05df0306ab3d
Revises: f3fcb7ec435e
Create Date: 2025-10-23 10:53:01.819824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05df0306ab3d'
down_revision = 'f3fcb7ec435e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add account lockout fields
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')