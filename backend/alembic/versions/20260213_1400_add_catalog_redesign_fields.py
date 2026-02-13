"""add_catalog_redesign_fields

競品監測系統重設計：新增標籤、匹配層級、監測狀態字段

Revision ID: catalog_redesign_v1
Revises: 2a0ebbab370c
Create Date: 2026-02-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'catalog_redesign_v1'
down_revision: Union[str, None] = '2a0ebbab370c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =============================================
    # competitor_products: 標籤 + 監測狀態
    # =============================================
    op.add_column(
        'competitor_products',
        sa.Column('category_tag', sa.String(50), nullable=True,
                  comment='大類標籤：牛/豬/羊/雞鴨/魚/蝦/蟹/貝')
    )
    op.add_column(
        'competitor_products',
        sa.Column('sub_tag', sa.String(50), nullable=True,
                  comment='細分標籤：西冷/肉眼/牛柳/牛仔骨/三文魚/刺身...')
    )
    op.add_column(
        'competitor_products',
        sa.Column('needs_matching', sa.Boolean(), nullable=False,
                  server_default='true',
                  comment='是否需要重新匹配')
    )
    op.add_column(
        'competitor_products',
        sa.Column('last_seen_at', sa.DateTime(), nullable=True,
                  comment='最後一次在分類頁出現的時間')
    )
    op.add_column(
        'competitor_products',
        sa.Column('tag_source', sa.String(20), nullable=True,
                  comment='標籤來源：rule/ai')
    )

    # 標籤索引（預篩查詢用）
    op.create_index('idx_cp_category_tag', 'competitor_products', ['category_tag'])
    op.create_index('idx_cp_sub_tag', 'competitor_products', ['sub_tag'])
    op.create_index('idx_cp_needs_matching', 'competitor_products', ['needs_matching'])

    # =============================================
    # product_competitor_mapping: 匹配層級
    # =============================================
    op.add_column(
        'product_competitor_mapping',
        sa.Column('match_level', sa.Integer(), nullable=True,
                  comment='匹配層級：1=直接替代 2=近似競品 3=品類競品')
    )
    op.add_column(
        'product_competitor_mapping',
        sa.Column('match_reason', sa.Text(), nullable=True,
                  comment='AI 匹配理由')
    )

    op.create_index('idx_pcm_match_level', 'product_competitor_mapping', ['match_level'])

    # =============================================
    # products: 自家商品也打標籤
    # =============================================
    op.add_column(
        'products',
        sa.Column('category_tag', sa.String(50), nullable=True,
                  comment='大類標籤：牛/豬/羊/雞鴨/魚/蝦/蟹/貝')
    )
    op.add_column(
        'products',
        sa.Column('sub_tag', sa.String(50), nullable=True,
                  comment='細分標籤：西冷/肉眼/牛柳/牛仔骨/三文魚/刺身...')
    )

    op.create_index('idx_products_category_tag', 'products', ['category_tag'])


def downgrade() -> None:
    # products
    op.drop_index('idx_products_category_tag', table_name='products')
    op.drop_column('products', 'sub_tag')
    op.drop_column('products', 'category_tag')

    # product_competitor_mapping
    op.drop_index('idx_pcm_match_level', table_name='product_competitor_mapping')
    op.drop_column('product_competitor_mapping', 'match_reason')
    op.drop_column('product_competitor_mapping', 'match_level')

    # competitor_products
    op.drop_index('idx_cp_needs_matching', table_name='competitor_products')
    op.drop_index('idx_cp_sub_tag', table_name='competitor_products')
    op.drop_index('idx_cp_category_tag', table_name='competitor_products')
    op.drop_column('competitor_products', 'tag_source')
    op.drop_column('competitor_products', 'last_seen_at')
    op.drop_column('competitor_products', 'needs_matching')
    op.drop_column('competitor_products', 'sub_tag')
    op.drop_column('competitor_products', 'category_tag')
