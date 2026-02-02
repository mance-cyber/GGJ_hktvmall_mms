"""add workflow fields to price_proposals

Revision ID: 20260202_1000
Revises: 20260117_1000_add_seo_ranking_tables
Create Date: 2026-02-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260202_1000'
down_revision = '20260117_1000_add_seo_ranking_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to price_proposals for workflow integration
    op.add_column('price_proposals', sa.Column(
        'source_conversation_id',
        sa.String(100),
        nullable=True,
        comment='來自邊個 AI 對話'
    ))
    op.add_column('price_proposals', sa.Column(
        'source_type',
        sa.String(50),
        nullable=False,
        server_default='manual',
        comment='manual | ai_suggestion | auto_alert'
    ))
    op.add_column('price_proposals', sa.Column(
        'assigned_to',
        postgresql.UUID(as_uuid=True),
        nullable=True,
        comment='指定審批人'
    ))
    op.add_column('price_proposals', sa.Column(
        'due_date',
        sa.DateTime(),
        nullable=True,
        comment='審批期限'
    ))
    op.add_column('price_proposals', sa.Column(
        'reminder_sent',
        sa.Boolean(),
        nullable=False,
        server_default='false',
        comment='已發提醒'
    ))

    # Create index for source_type queries
    op.create_index(
        'idx_price_proposals_source_type',
        'price_proposals',
        ['source_type']
    )

    # Create index for conversation lookups
    op.create_index(
        'idx_price_proposals_conversation_id',
        'price_proposals',
        ['source_conversation_id']
    )


def downgrade() -> None:
    op.drop_index('idx_price_proposals_conversation_id', table_name='price_proposals')
    op.drop_index('idx_price_proposals_source_type', table_name='price_proposals')
    op.drop_column('price_proposals', 'reminder_sent')
    op.drop_column('price_proposals', 'due_date')
    op.drop_column('price_proposals', 'assigned_to')
    op.drop_column('price_proposals', 'source_type')
    op.drop_column('price_proposals', 'source_conversation_id')
