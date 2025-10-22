"""add_question_id_to_responses

Revision ID: 04bb2e4a7922
Revises: 54dc448698fe
Create Date: 2025-10-22 21:34:44.053625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04bb2e4a7922'
down_revision = '54dc448698fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add question_id column to responses table
    op.add_column('responses', sa.Column('question_id', sa.String(), nullable=True))

    # Add index for better query performance
    op.create_index('ix_responses_question_id', 'responses', ['question_id'])


def downgrade() -> None:
    # Remove index
    op.drop_index('ix_responses_question_id', table_name='responses')

    # Remove column
    op.drop_column('responses', 'question_id')