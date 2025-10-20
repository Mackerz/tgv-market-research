"""Make is_approved nullable for pending status

Revision ID: 006
Revises: 005
Create Date: 2025-10-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """
    Make is_approved nullable to support three states:
    - None (null): Pending approval (newly completed submissions)
    - True: Approved
    - False: Rejected
    """
    # Alter the column to be nullable
    op.alter_column('submissions', 'is_approved',
                    existing_type=sa.Boolean(),
                    nullable=True,
                    existing_server_default=sa.false())

    # Update existing records: False -> None (pending), True stays True
    # This sets all currently unapproved submissions to pending status
    op.execute("UPDATE submissions SET is_approved = NULL WHERE is_approved = FALSE")


def downgrade():
    """
    Revert to non-nullable boolean with default False
    """
    # Convert NULL back to False
    op.execute("UPDATE submissions SET is_approved = FALSE WHERE is_approved IS NULL")

    # Make column non-nullable again
    op.alter_column('submissions', 'is_approved',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.false())
