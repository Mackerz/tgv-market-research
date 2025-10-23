"""add_taxonomy_tables

Revision ID: f3fcb7ec435e
Revises: 04bb2e4a7922
Create Date: 2025-10-23 09:24:46.042661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3fcb7ec435e'
down_revision = '04bb2e4a7922'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reporting_labels table
    op.create_table(
        'reporting_labels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('survey_id', sa.BigInteger(), nullable=False),
        sa.Column('label_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_ai_generated', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reporting_labels_id'), 'reporting_labels', ['id'], unique=False)

    # Create label_mappings table
    op.create_table(
        'label_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporting_label_id', sa.Integer(), nullable=False),
        sa.Column('system_label', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reporting_label_id'], ['reporting_labels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_label_mappings_id'), 'label_mappings', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_label_mappings_id'), table_name='label_mappings')
    op.drop_table('label_mappings')
    op.drop_index(op.f('ix_reporting_labels_id'), table_name='reporting_labels')
    op.drop_table('reporting_labels')