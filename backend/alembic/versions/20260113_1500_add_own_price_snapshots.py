"""Add own_price_snapshots table

Revision ID: add_own_price_snapshots
Revises: 3830de192d80
Create Date: 2026-01-13 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_own_price_snapshots'
down_revision: Union[str, None] = '3830de192d80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 創建 own_price_snapshots 表
    op.create_table(
        'own_price_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True, comment='原價（劃線價）'),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('stock_status', sa.String(50), nullable=True, comment='in_stock, out_of_stock, low_stock'),
        sa.Column('promotion_text', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # 創建索引
    op.create_index('idx_own_price_snapshots_product_id', 'own_price_snapshots', ['product_id'])
    op.create_index('idx_own_price_snapshots_recorded_at', 'own_price_snapshots', ['recorded_at'])


def downgrade() -> None:
    # 刪除索引
    op.drop_index('idx_own_price_snapshots_recorded_at', table_name='own_price_snapshots')
    op.drop_index('idx_own_price_snapshots_product_id', table_name='own_price_snapshots')

    # 刪除表
    op.drop_table('own_price_snapshots')
