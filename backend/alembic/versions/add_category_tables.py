"""add category database tables

Revision ID: add_category_001
Revises:
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_category_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== 創建類別數據庫表 =====
    op.create_table(
        'category_databases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('hktv_category_url', sa.Text(), nullable=True),
        sa.Column('total_products', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=True),
        sa.Column('scrape_frequency', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # ===== 創建類別商品表 =====
    op.create_table(
        'category_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_databases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('sku', sa.String(255), nullable=True),
        sa.Column('brand', sa.String(255), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('attributes', postgresql.JSONB(), nullable=True),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('unit_type', sa.String(50), nullable=False, server_default='per_100g'),
        sa.Column('stock_status', sa.String(50), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # 創建索引
    op.create_index('idx_category_products_category', 'category_products', ['category_id'])
    op.create_index('idx_category_products_url', 'category_products', ['url'])
    op.create_index('idx_category_products_brand', 'category_products', ['brand'])
    op.create_index('idx_category_products_unit_price', 'category_products', ['unit_price'])

    # ===== 創建價格快照表 =====
    op.create_table(
        'category_price_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('stock_status', sa.String(50), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # 創建索引
    op.create_index('idx_price_snapshots_product', 'category_price_snapshots', ['category_product_id'])
    op.create_index('idx_price_snapshots_scraped_at', 'category_price_snapshots', ['scraped_at'])

    # ===== 創建 AI 分析報告表 =====
    op.create_table(
        'category_analysis_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_databases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=True),
        sa.Column('report_title', sa.String(255), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_findings', postgresql.JSONB(), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(), nullable=True),
        sa.Column('data_snapshot', postgresql.JSONB(), nullable=True),
        sa.Column('generated_by', sa.String(50), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # 創建索引
    op.create_index('idx_analysis_reports_category', 'category_analysis_reports', ['category_id'])
    op.create_index('idx_analysis_reports_type', 'category_analysis_reports', ['report_type'])
    op.create_index('idx_analysis_reports_generated_at', 'category_analysis_reports', ['generated_at'])


def downgrade() -> None:
    op.drop_table('category_analysis_reports')
    op.drop_table('category_price_snapshots')
    op.drop_table('category_products')
    op.drop_table('category_databases')
