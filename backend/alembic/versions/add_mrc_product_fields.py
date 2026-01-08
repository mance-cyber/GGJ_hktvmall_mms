"""Add Market Response Center (MRC) fields to products table

Revision ID: add_mrc_fields_001
Revises: add_category_001
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_mrc_fields_001'
down_revision = 'add_category_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =============================================
    # Market Response Center (MRC) 擴展欄位
    # 用於 GogoJap SKU 智能營運系統
    # =============================================

    # 多語言商品名稱 (用於智能搜索匹配)
    op.add_column('products', sa.Column('name_zh', sa.String(500), nullable=True, comment='中文品名'))
    op.add_column('products', sa.Column('name_ja', sa.String(500), nullable=True, comment='日文品名 - 核心搜索鍵'))
    op.add_column('products', sa.Column('name_en', sa.String(500), nullable=True, comment='英文品名/規格'))

    # 分類層級
    op.add_column('products', sa.Column('category_main', sa.String(100), nullable=True, comment='大分類: 飛機貨、乾貨、急凍...'))
    op.add_column('products', sa.Column('category_sub', sa.String(100), nullable=True, comment='小分類: 鮮魚、貝類、蝦蟹...'))

    # 商品屬性
    op.add_column('products', sa.Column('unit', sa.String(50), nullable=True, comment='單位: KG, PK, PC, BTL...'))
    op.add_column('products', sa.Column('season_tag', sa.String(100), nullable=True, comment='季節標籤: ALL, WINTER, SPRING-SUMMER...'))

    # 數據來源追蹤
    op.add_column('products', sa.Column('source', sa.String(50), nullable=True, server_default='manual', comment='數據來源: gogojap_csv, hktv_api, manual'))

    # MRC 搜索優化索引
    op.create_index('idx_products_name_ja', 'products', ['name_ja'])
    op.create_index('idx_products_season_tag', 'products', ['season_tag'])
    op.create_index('idx_products_category_main', 'products', ['category_main'])
    op.create_index('idx_products_source', 'products', ['source'])


def downgrade() -> None:
    # 移除索引
    op.drop_index('idx_products_source', table_name='products')
    op.drop_index('idx_products_category_main', table_name='products')
    op.drop_index('idx_products_season_tag', table_name='products')
    op.drop_index('idx_products_name_ja', table_name='products')

    # 移除欄位
    op.drop_column('products', 'source')
    op.drop_column('products', 'season_tag')
    op.drop_column('products', 'unit')
    op.drop_column('products', 'category_sub')
    op.drop_column('products', 'category_main')
    op.drop_column('products', 'name_en')
    op.drop_column('products', 'name_ja')
    op.drop_column('products', 'name_zh')
