"""add age column to submissions

Revision ID: 004
Revises: 003
Create Date: 2024-09-21 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the age column to submissions table
    op.add_column('submissions', sa.Column('age', sa.Integer(), nullable=True))

    # Calculate and populate age for existing submissions
    # This uses a SQL function to calculate age based on date_of_birth and submitted_at
    op.execute("""
        UPDATE submissions
        SET age = EXTRACT(YEAR FROM AGE(submitted_at::date, TO_DATE(date_of_birth, 'YYYY-MM-DD')))::integer
        WHERE date_of_birth IS NOT NULL
        AND submitted_at IS NOT NULL
        AND date_of_birth ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
    """)


def downgrade() -> None:
    # Remove the age column
    op.drop_column('submissions', 'age')