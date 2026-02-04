"""Add outputs_per_image column and analyzing status

Revision ID: add_outputs_per_image
Revises: 20260202_scheduled_reports
Create Date: 2026-02-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_outputs_per_image'
down_revision: Union[str, None] = '20260202_1100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 outputs_per_image 欄位
    op.add_column(
        'image_generation_tasks',
        sa.Column('outputs_per_image', sa.Integer(), nullable=True, server_default='1')
    )

    # 添加 'analyzing' 狀態到 taskstatus enum
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'analyzing' AFTER 'pending'")


def downgrade() -> None:
    # 刪除 outputs_per_image 欄位
    op.drop_column('image_generation_tasks', 'outputs_per_image')

    # 注意：PostgreSQL 不支持從 enum 中刪除值，需要重建 enum
    # 這裡跳過 enum 的回滾
