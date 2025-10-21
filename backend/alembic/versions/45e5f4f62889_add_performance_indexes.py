"""add_performance_indexes

Revision ID: 45e5f4f62889
Revises: 007
Create Date: 2025-10-21 11:32:05.293405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45e5f4f62889'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes to frequently queried columns"""

    # Surveys table indexes
    op.create_index('ix_surveys_name', 'surveys', ['name'])
    op.create_index('ix_surveys_client', 'surveys', ['client'])
    op.create_index('ix_surveys_is_active', 'surveys', ['is_active'])
    op.create_index('ix_surveys_created_at', 'surveys', ['created_at'])
    # Composite index for common query pattern (active surveys sorted by date)
    op.create_index('ix_surveys_active_created', 'surveys', ['is_active', 'created_at'])

    # Submissions table indexes
    op.create_index('ix_submissions_survey_id', 'submissions', ['survey_id'])
    op.create_index('ix_submissions_email', 'submissions', ['email'])
    op.create_index('ix_submissions_region', 'submissions', ['region'])
    op.create_index('ix_submissions_is_approved', 'submissions', ['is_approved'])
    op.create_index('ix_submissions_is_completed', 'submissions', ['is_completed'])
    op.create_index('ix_submissions_submitted_at', 'submissions', ['submitted_at'])
    # Composite indexes for common query patterns
    op.create_index('ix_submissions_survey_completed', 'submissions', ['survey_id', 'is_completed'])
    op.create_index('ix_submissions_survey_submitted', 'submissions', ['survey_id', 'submitted_at'])
    op.create_index('ix_submissions_survey_approved', 'submissions', ['survey_id', 'is_approved'])

    # Responses table indexes
    op.create_index('ix_responses_submission_id', 'responses', ['submission_id'])
    op.create_index('ix_responses_question_type', 'responses', ['question_type'])
    op.create_index('ix_responses_responded_at', 'responses', ['responded_at'])

    # Media table indexes (if not already present)
    op.create_index('ix_media_response_id', 'media', ['response_id'])


def downgrade() -> None:
    """Remove performance indexes"""

    # Drop surveys table indexes
    op.drop_index('ix_surveys_name', table_name='surveys')
    op.drop_index('ix_surveys_client', table_name='surveys')
    op.drop_index('ix_surveys_is_active', table_name='surveys')
    op.drop_index('ix_surveys_created_at', table_name='surveys')
    op.drop_index('ix_surveys_active_created', table_name='surveys')

    # Drop submissions table indexes
    op.drop_index('ix_submissions_survey_id', table_name='submissions')
    op.drop_index('ix_submissions_email', table_name='submissions')
    op.drop_index('ix_submissions_region', table_name='submissions')
    op.drop_index('ix_submissions_is_approved', table_name='submissions')
    op.drop_index('ix_submissions_is_completed', table_name='submissions')
    op.drop_index('ix_submissions_submitted_at', table_name='submissions')
    op.drop_index('ix_submissions_survey_completed', table_name='submissions')
    op.drop_index('ix_submissions_survey_submitted', table_name='submissions')
    op.drop_index('ix_submissions_survey_approved', table_name='submissions')

    # Drop responses table indexes
    op.drop_index('ix_responses_submission_id', table_name='responses')
    op.drop_index('ix_responses_question_type', table_name='responses')
    op.drop_index('ix_responses_responded_at', table_name='responses')

    # Drop media table indexes
    op.drop_index('ix_media_response_id', table_name='media')