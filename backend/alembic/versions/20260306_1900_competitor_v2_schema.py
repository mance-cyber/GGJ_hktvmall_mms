"""competitor_v2_schema

競品監測系統 v2 重構：
- 清空舊競品數據
- Competitor: 加 tier, store_code，移除 scrape_config_id
- CompetitorProduct: 移除舊標籤欄位，加 product_type, unit_weight_g
- PriceSnapshot: 加 unit_price_per_100g
- ProductCompetitorMapping: 加 match_type

Revision ID: competitor_v2
Revises: catalog_redesign_v1
Create Date: 2026-03-06 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'competitor_v2'
down_revision: Union[str, None] = 'catalog_redesign_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # =============================================
    # Step 1: 清空舊競品數據（CASCADE 處理 FK）
    # =============================================
    conn.execute(sa.text("TRUNCATE TABLE price_alerts CASCADE"))
    conn.execute(sa.text("TRUNCATE TABLE price_snapshots CASCADE"))
    conn.execute(sa.text("TRUNCATE TABLE product_competitor_mapping CASCADE"))
    conn.execute(sa.text("TRUNCATE TABLE competitor_products CASCADE"))
    conn.execute(sa.text("TRUNCATE TABLE competitors CASCADE"))

    # =============================================
    # Step 2: competitors 表
    # =============================================
    conn.execute(sa.text("""
        ALTER TABLE competitors
        ADD COLUMN IF NOT EXISTS tier INTEGER NOT NULL DEFAULT 2,
        ADD COLUMN IF NOT EXISTS store_code VARCHAR(50)
    """))

    # 移除 scrape_config_id FK（如存在）
    conn.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='competitors' AND column_name='scrape_config_id'
            ) THEN
                ALTER TABLE competitors DROP COLUMN scrape_config_id;
            END IF;
        END $$
    """))

    # =============================================
    # Step 3: competitor_products 表 — 移除舊欄位
    # =============================================
    old_columns = ['category_tag', 'sub_tag', 'needs_matching', 'tag_source',
                   'scrape_config_override', 'scrape_error']
    for col in old_columns:
        conn.execute(sa.text(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='competitor_products' AND column_name='{col}'
                ) THEN
                    ALTER TABLE competitor_products DROP COLUMN {col};
                END IF;
            END $$
        """))

    # 移除舊索引（IF EXISTS）
    old_indexes = ['idx_cp_category_tag', 'idx_cp_sub_tag', 'idx_cp_needs_matching']
    for idx in old_indexes:
        conn.execute(sa.text(f"DROP INDEX IF EXISTS {idx}"))

    # 加新欄位
    conn.execute(sa.text("""
        ALTER TABLE competitor_products
        ADD COLUMN IF NOT EXISTS product_type VARCHAR(20) DEFAULT 'unknown',
        ADD COLUMN IF NOT EXISTS unit_weight_g INTEGER
    """))

    # 加新索引
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cp_product_type ON competitor_products(product_type)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cp_last_seen_at ON competitor_products(last_seen_at)"
    ))

    # =============================================
    # Step 4: price_snapshots 表
    # =============================================
    conn.execute(sa.text("""
        ALTER TABLE price_snapshots
        ADD COLUMN IF NOT EXISTS unit_price_per_100g NUMERIC(10, 2)
    """))

    # =============================================
    # Step 5: product_competitor_mapping 表
    # =============================================
    conn.execute(sa.text("""
        ALTER TABLE product_competitor_mapping
        ADD COLUMN IF NOT EXISTS match_type VARCHAR(20) NOT NULL DEFAULT 'ai_matched'
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE product_competitor_mapping DROP COLUMN IF EXISTS match_type"
    ))
    conn.execute(sa.text(
        "ALTER TABLE price_snapshots DROP COLUMN IF EXISTS unit_price_per_100g"
    ))
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_cp_product_type"))
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_cp_last_seen_at"))
    conn.execute(sa.text("""
        ALTER TABLE competitor_products
        DROP COLUMN IF EXISTS unit_weight_g,
        DROP COLUMN IF EXISTS product_type
    """))
    conn.execute(sa.text("""
        ALTER TABLE competitors
        DROP COLUMN IF EXISTS store_code,
        DROP COLUMN IF EXISTS tier
    """))
