"""add_performance_indexes

Revision ID: 1e3c7b4af839
Revises: f3fcb7ec435e
Create Date: 2025-10-23 10:52:08.052356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e3c7b4af839'
down_revision = 'f3fcb7ec435e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes to foreign keys for better join performance
    op.create_index('ix_submissions_survey_id', 'submissions', ['survey_id'])
    op.create_index('ix_responses_submission_id', 'responses', ['submission_id'])

    # Add index to frequently filtered column
    op.create_index('ix_responses_question_type', 'responses', ['question_type'])

    # Add composite index for common query pattern (survey + status filters)
    op.create_index(
        'ix_submissions_survey_status',
        'submissions',
        ['survey_id', 'is_completed', 'is_approved']
    )

    # Add index for media lookups by response
    op.create_index('ix_media_response_id', 'media', ['response_id'])


def downgrade() -> None:
    op.drop_index('ix_media_response_id', table_name='media')
    op.drop_index('ix_submissions_survey_status', table_name='submissions')
    op.drop_index('ix_responses_question_type', table_name='responses')
    op.drop_index('ix_responses_submission_id', table_name='responses')
    op.drop_index('ix_submissions_survey_id', table_name='submissions')