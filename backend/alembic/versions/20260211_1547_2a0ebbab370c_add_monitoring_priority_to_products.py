"""add_monitoring_priority_to_products

Revision ID: 2a0ebbab370c
Revises: add_outputs_per_image
Create Date: 2026-02-11 15:47:51.823760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a0ebbab370c'
down_revision: Union[str, None] = 'add_outputs_per_image'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 monitoring_priority 欄位
    op.add_column(
        'products',
        sa.Column(
            'monitoring_priority',
            sa.String(length=10),
            nullable=False,
            server_default='B',
            comment='監測優先級: A=核心商品(3次/天), B=一般商品(2次/天), C=低優先(1次/天)'
        )
    )


def downgrade() -> None:
    # 移除 monitoring_priority 欄位
    op.drop_column('products', 'monitoring_priority')
