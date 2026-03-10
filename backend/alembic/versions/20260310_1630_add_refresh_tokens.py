"""add refresh_tokens table and products columns previously in run_migrations

Revision ID: 4f8a2b1c9d0e
Revises: 20260310_1440_add_report_subscribers
Create Date: 2026-03-10 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = '4f8a2b1c9d0e'
down_revision: Union[str, None] = None  # Will be auto-resolved by Alembic
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # RefreshToken table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('token', sa.String(128), unique=True, index=True, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('revoked', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime),
    )

    # Products columns (migrated from run_migrations)
    for col, col_type in [
        ('min_price', 'NUMERIC(10, 2)'),
        ('max_price', 'NUMERIC(10, 2)'),
        ('auto_pricing_enabled', 'BOOLEAN DEFAULT FALSE'),
        ('cost', 'NUMERIC(10, 2)'),
        ('monitoring_priority', "VARCHAR(10) DEFAULT 'B'"),
    ]:
        op.execute(f'ALTER TABLE products ADD COLUMN IF NOT EXISTS {col} {col_type}')

    op.execute("UPDATE products SET monitoring_priority = 'B' WHERE monitoring_priority IS NULL")

    # Pipeline tasks columns
    op.execute('ALTER TABLE pipeline_tasks ADD COLUMN IF NOT EXISTS progress JSONB')
    op.execute('ALTER TABLE pipeline_tasks ADD COLUMN IF NOT EXISTS step_started_at TIMESTAMP')


def downgrade() -> None:
    op.drop_table('refresh_tokens')
