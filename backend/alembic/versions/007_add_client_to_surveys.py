"""Add client field to surveys

Revision ID: 007
Revises: 006
Create Date: 2025-10-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add client field to surveys table to track which client/organization the survey is for
    """
    op.add_column('surveys', sa.Column('client', sa.String(), nullable=True))


def downgrade():
    """
    Remove client field from surveys table
    """
    op.drop_column('surveys', 'client')
