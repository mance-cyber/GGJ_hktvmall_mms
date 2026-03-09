"""add_stock_level_to_price_snapshots

Add numeric stock_level column to price_snapshots for precise inventory tracking.
Algolia only provides hasStock (boolean), but the stock probe script reads
exact stockLevel from product page SSR HTML.

Revision ID: add_stock_level
Revises: competitor_v2
Create Date: 2026-03-08 22:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'add_stock_level'
down_revision: Union[str, None] = 'competitor_v2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('price_snapshots', sa.Column(
        'stock_level', sa.Integer(), nullable=True,
        comment='Exact stock quantity from product page SSR (NULL = not probed)',
    ))


def downgrade() -> None:
    op.drop_column('price_snapshots', 'stock_level')
