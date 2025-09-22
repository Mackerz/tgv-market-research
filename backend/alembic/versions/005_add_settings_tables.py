"""add settings tables

Revision ID: 005
Revises: 004
Create Date: 2024-09-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_settings table
    op.create_table('report_settings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('survey_id', sa.BigInteger(), nullable=False),
        sa.Column('age_ranges', JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('survey_id')
    )
    op.create_index(op.f('ix_report_settings_id'), 'report_settings', ['id'], unique=False)

    # Create question_display_names table
    op.create_table('question_display_names',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('report_settings_id', sa.BigInteger(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=True),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['report_settings_id'], ['report_settings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_display_names_id'), 'question_display_names', ['id'], unique=False)

    # Set default age ranges for report_settings
    default_age_ranges = [
        {"min": 0, "max": 18, "label": "0-18"},
        {"min": 18, "max": 25, "label": "18-25"},
        {"min": 25, "max": 40, "label": "25-40"},
        {"min": 40, "max": 60, "label": "40-60"},
        {"min": 60, "max": None, "label": "60+"}
    ]

    # Set the default value for age_ranges column
    import json
    default_json = json.dumps(default_age_ranges)
    op.alter_column('report_settings', 'age_ranges',
                   server_default=sa.text(f"'{default_json}'::json"))


def downgrade() -> None:
    # Drop question_display_names table
    op.drop_index(op.f('ix_question_display_names_id'), table_name='question_display_names')
    op.drop_table('question_display_names')

    # Drop report_settings table
    op.drop_index(op.f('ix_report_settings_id'), table_name='report_settings')
    op.drop_table('report_settings')