"""Add SEO and GEO tables

Revision ID: add_seo_geo_tables
Revises: add_own_price_snapshots
Create Date: 2026-01-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_seo_geo_tables'
down_revision: Union[str, None] = 'add_own_price_snapshots'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =============================================
    # 1. SEO Contents 表
    # =============================================
    op.create_table(
        'seo_contents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # SEO 核心欄位
        sa.Column('meta_title', sa.String(70), nullable=False, comment='SEO 標題 (max 70 chars)'),
        sa.Column('meta_description', sa.String(160), nullable=False, comment='SEO 描述 (max 160 chars)'),

        # 關鍵詞
        sa.Column('primary_keyword', sa.String(100), nullable=True, comment='主關鍵詞'),
        sa.Column('secondary_keywords', postgresql.JSONB(), nullable=True, server_default='[]',
                  comment='次要關鍵詞列表'),
        sa.Column('long_tail_keywords', postgresql.JSONB(), nullable=True, server_default='[]',
                  comment='長尾關鍵詞'),

        # SEO 評分
        sa.Column('seo_score', sa.Integer(), nullable=True, comment='SEO 總評分 0-100'),
        sa.Column('score_breakdown', postgresql.JSONB(), nullable=True,
                  comment='評分詳情'),
        sa.Column('improvement_suggestions', postgresql.JSONB(), nullable=True, server_default='[]',
                  comment='改進建議列表'),

        # 多語言
        sa.Column('language', sa.String(10), nullable=False, server_default='zh-HK'),
        sa.Column('localized_seo', postgresql.JSONB(), nullable=True,
                  comment='多語言SEO'),

        # Open Graph
        sa.Column('og_title', sa.String(100), nullable=True),
        sa.Column('og_description', sa.String(200), nullable=True),
        sa.Column('og_image_url', sa.Text(), nullable=True),

        # 版本控制
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),

        # 元數據
        sa.Column('generation_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('input_data', postgresql.JSONB(), nullable=True),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.String(255), nullable=True),
    )

    # SEO Contents 索引
    op.create_index('idx_seo_contents_product_id', 'seo_contents', ['product_id'])
    op.create_index('idx_seo_contents_primary_keyword', 'seo_contents', ['primary_keyword'])
    op.create_index('idx_seo_contents_status', 'seo_contents', ['status'])
    op.create_index('idx_seo_contents_language', 'seo_contents', ['language'])
    op.create_index('idx_seo_contents_seo_score', 'seo_contents', ['seo_score'])

    # =============================================
    # 2. Structured Data 表 (Schema.org JSON-LD)
    # =============================================
    op.create_table(
        'structured_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # Schema.org 類型
        sa.Column('schema_type', sa.String(50), nullable=False,
                  comment='Product, FAQPage, BreadcrumbList, etc.'),

        # JSON-LD 數據
        sa.Column('json_ld', postgresql.JSONB(), nullable=False, comment='完整 JSON-LD 結構'),

        # AI 搜索引擎優化
        sa.Column('ai_summary', sa.Text(), nullable=True, comment='AI 搜索引擎友好摘要'),
        sa.Column('ai_facts', postgresql.JSONB(), nullable=True, server_default='[]',
                  comment='結構化事實列表'),
        sa.Column('ai_entities', postgresql.JSONB(), nullable=True, comment='實體關聯'),

        # 驗證狀態
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('validation_errors', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('last_validated_at', sa.DateTime(), nullable=True),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Structured Data 索引
    op.create_index('idx_structured_data_product_id', 'structured_data', ['product_id'])
    op.create_index('idx_structured_data_schema_type', 'structured_data', ['schema_type'])
    op.create_index('idx_structured_data_is_valid', 'structured_data', ['is_valid'])

    # =============================================
    # 3. Brand Knowledge 表 (品牌知識圖譜)
    # =============================================
    op.create_table(
        'brand_knowledge',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # 知識類型
        sa.Column('knowledge_type', sa.String(50), nullable=False,
                  comment='brand_info, product_fact, faq, expert_claim, testimonial'),

        # 內容
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.String(500), nullable=True),

        # 關聯實體
        sa.Column('related_products', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('related_categories', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 可信度與來源
        sa.Column('credibility_score', sa.Integer(), nullable=True, comment='可信度評分 0-100'),
        sa.Column('source_type', sa.String(50), nullable=False, server_default='internal'),
        sa.Column('source_reference', sa.Text(), nullable=True),
        sa.Column('author', sa.String(255), nullable=True),

        # 標籤與搜索
        sa.Column('tags', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('search_keywords', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 狀態
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('display_order', sa.Integer(), nullable=True),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Brand Knowledge 索引
    op.create_index('idx_brand_knowledge_type', 'brand_knowledge', ['knowledge_type'])
    op.create_index('idx_brand_knowledge_is_active', 'brand_knowledge', ['is_active'])
    op.create_index('idx_brand_knowledge_is_featured', 'brand_knowledge', ['is_featured'])
    op.create_index('idx_brand_knowledge_tags', 'brand_knowledge', ['tags'],
                    postgresql_using='gin')

    # =============================================
    # 4. Keyword Research 表 (關鍵詞研究)
    # =============================================
    op.create_table(
        'keyword_research',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # 關鍵詞
        sa.Column('keyword', sa.String(255), nullable=False, unique=True),
        sa.Column('keyword_normalized', sa.String(255), nullable=True),

        # 搜索數據
        sa.Column('search_volume', sa.Integer(), nullable=True, comment='月搜索量'),
        sa.Column('difficulty', sa.Integer(), nullable=True, comment='競爭難度 0-100'),
        sa.Column('cpc', sa.Numeric(10, 2), nullable=True, comment='每次點擊成本'),
        sa.Column('competition_level', sa.String(20), nullable=True),

        # 趨勢數據
        sa.Column('trend_data', postgresql.JSONB(), nullable=True),
        sa.Column('trend_direction', sa.String(20), nullable=True),
        sa.Column('seasonality', sa.String(50), nullable=True),

        # 相關詞
        sa.Column('related_keywords', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('long_tail_variants', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 分類與意圖
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('intent', sa.String(50), nullable=True),

        # 數據來源
        sa.Column('data_source', sa.String(50), nullable=False, server_default='ai_generated'),
        sa.Column('source_confidence', sa.Integer(), nullable=True),

        # 時間戳
        sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Keyword Research 索引
    op.create_index('idx_keyword_research_keyword', 'keyword_research', ['keyword'])
    op.create_index('idx_keyword_research_category', 'keyword_research', ['category'])
    op.create_index('idx_keyword_research_volume', 'keyword_research', ['search_volume'])
    op.create_index('idx_keyword_research_intent', 'keyword_research', ['intent'])
    op.create_index('idx_keyword_research_difficulty', 'keyword_research', ['difficulty'])

    # =============================================
    # 5. Content Audits 表 (內容審計)
    # =============================================
    op.create_table(
        'content_audits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # 審計結果
        sa.Column('audit_type', sa.String(50), nullable=False,
                  comment='full, title_only, description_only, keywords'),
        sa.Column('overall_score', sa.Integer(), nullable=False, comment='總評分 0-100'),

        # 分項評分
        sa.Column('scores', postgresql.JSONB(), nullable=False),

        # 問題與建議
        sa.Column('issues', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('recommendations', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 對比數據
        sa.Column('competitor_comparison', postgresql.JSONB(), nullable=True),
        sa.Column('industry_benchmark', postgresql.JSONB(), nullable=True),

        # 時間戳
        sa.Column('audited_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Content Audits 索引
    op.create_index('idx_content_audits_product_id', 'content_audits', ['product_id'])
    op.create_index('idx_content_audits_overall_score', 'content_audits', ['overall_score'])
    op.create_index('idx_content_audits_audited_at', 'content_audits', ['audited_at'])


def downgrade() -> None:
    # 按照創建順序的相反順序刪除

    # 5. Content Audits
    op.drop_index('idx_content_audits_audited_at', table_name='content_audits')
    op.drop_index('idx_content_audits_overall_score', table_name='content_audits')
    op.drop_index('idx_content_audits_product_id', table_name='content_audits')
    op.drop_table('content_audits')

    # 4. Keyword Research
    op.drop_index('idx_keyword_research_difficulty', table_name='keyword_research')
    op.drop_index('idx_keyword_research_intent', table_name='keyword_research')
    op.drop_index('idx_keyword_research_volume', table_name='keyword_research')
    op.drop_index('idx_keyword_research_category', table_name='keyword_research')
    op.drop_index('idx_keyword_research_keyword', table_name='keyword_research')
    op.drop_table('keyword_research')

    # 3. Brand Knowledge
    op.drop_index('idx_brand_knowledge_tags', table_name='brand_knowledge')
    op.drop_index('idx_brand_knowledge_is_featured', table_name='brand_knowledge')
    op.drop_index('idx_brand_knowledge_is_active', table_name='brand_knowledge')
    op.drop_index('idx_brand_knowledge_type', table_name='brand_knowledge')
    op.drop_table('brand_knowledge')

    # 2. Structured Data
    op.drop_index('idx_structured_data_is_valid', table_name='structured_data')
    op.drop_index('idx_structured_data_schema_type', table_name='structured_data')
    op.drop_index('idx_structured_data_product_id', table_name='structured_data')
    op.drop_table('structured_data')

    # 1. SEO Contents
    op.drop_index('idx_seo_contents_seo_score', table_name='seo_contents')
    op.drop_index('idx_seo_contents_language', table_name='seo_contents')
    op.drop_index('idx_seo_contents_status', table_name='seo_contents')
    op.drop_index('idx_seo_contents_primary_keyword', table_name='seo_contents')
    op.drop_index('idx_seo_contents_product_id', table_name='seo_contents')
    op.drop_table('seo_contents')
