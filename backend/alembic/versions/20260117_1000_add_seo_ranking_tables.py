"""Add SEO ranking tracking tables

Revision ID: add_seo_ranking_tables
Revises: add_seo_geo_tables
Create Date: 2026-01-17 10:00:00.000000

新增表：
- keyword_configs: 關鍵詞追蹤配置
- keyword_rankings: 關鍵詞排名歷史記錄
- seo_reports: SEO 優化報告
- ranking_alerts: 排名變化警報
- ranking_scrape_jobs: 抓取任務記錄
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_seo_ranking_tables'
down_revision: Union[str, None] = 'add_seo_geo_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =============================================
    # 1. Keyword Configs 表（關鍵詞追蹤配置）
    # =============================================
    op.create_table(
        'keyword_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # 關鍵詞基本資訊
        sa.Column('keyword', sa.String(255), nullable=False, comment='追蹤的關鍵詞'),
        sa.Column('keyword_normalized', sa.String(255), nullable=False, comment='標準化關鍵詞'),
        sa.Column('keyword_type', sa.String(20), nullable=False, server_default='secondary',
                  comment='primary, secondary, long_tail, brand, competitor'),

        # 追蹤設定
        sa.Column('track_google', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('track_hktvmall', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # 目標與基準
        sa.Column('target_google_rank', sa.Integer(), nullable=True, comment='Google 目標排名'),
        sa.Column('target_hktvmall_rank', sa.Integer(), nullable=True, comment='HKTVmall 目標排名'),
        sa.Column('baseline_google_rank', sa.Integer(), nullable=True, comment='Google 基準排名'),
        sa.Column('baseline_hktvmall_rank', sa.Integer(), nullable=True, comment='HKTVmall 基準排名'),

        # 最新排名快照
        sa.Column('latest_google_rank', sa.Integer(), nullable=True, comment='最新 Google 排名'),
        sa.Column('latest_hktvmall_rank', sa.Integer(), nullable=True, comment='最新 HKTVmall 排名'),
        sa.Column('latest_tracked_at', sa.DateTime(), nullable=True, comment='最後追蹤時間'),

        # 競品追蹤
        sa.Column('track_competitors', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('competitor_product_ids', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 元數據
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Keyword Configs 索引
    op.create_index('idx_keyword_configs_product_id', 'keyword_configs', ['product_id'])
    op.create_index('idx_keyword_configs_keyword', 'keyword_configs', ['keyword'])
    op.create_index('idx_keyword_configs_keyword_normalized', 'keyword_configs', ['keyword_normalized'])
    op.create_index('idx_keyword_configs_keyword_type', 'keyword_configs', ['keyword_type'])
    op.create_index('idx_keyword_configs_is_active', 'keyword_configs', ['is_active'])
    op.create_index('idx_keyword_configs_latest_google_rank', 'keyword_configs', ['latest_google_rank'])
    op.create_index('idx_keyword_configs_latest_hktvmall_rank', 'keyword_configs', ['latest_hktvmall_rank'])

    # =============================================
    # 2. Keyword Rankings 表（排名歷史記錄）
    # =============================================
    op.create_table(
        'keyword_rankings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('keyword_config_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('keyword_configs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # 關鍵詞（冗餘存儲）
        sa.Column('keyword', sa.String(255), nullable=False),

        # Google 排名數據
        sa.Column('google_rank', sa.Integer(), nullable=True, comment='Google 排名 1-100'),
        sa.Column('google_page', sa.Integer(), nullable=True, comment='Google 結果頁碼'),
        sa.Column('google_url', sa.Text(), nullable=True, comment='排名 URL'),
        sa.Column('google_snippet', sa.Text(), nullable=True, comment='搜尋結果摘要'),
        sa.Column('google_total_results', sa.Integer(), nullable=True, comment='總結果數'),

        # HKTVmall 排名數據
        sa.Column('hktvmall_rank', sa.Integer(), nullable=True, comment='HKTVmall 站內排名'),
        sa.Column('hktvmall_page', sa.Integer(), nullable=True, comment='HKTVmall 結果頁碼'),
        sa.Column('hktvmall_total_results', sa.Integer(), nullable=True, comment='HKTVmall 總結果數'),
        sa.Column('hktvmall_product_url', sa.Text(), nullable=True, comment='產品頁 URL'),

        # 排名變化
        sa.Column('google_rank_change', sa.Integer(), nullable=True, comment='Google 排名變化'),
        sa.Column('hktvmall_rank_change', sa.Integer(), nullable=True, comment='HKTVmall 排名變化'),

        # 競品排名
        sa.Column('competitor_rankings', postgresql.JSONB(), nullable=True, comment='競品排名數據'),

        # SERP 特徵
        sa.Column('serp_features', postgresql.JSONB(), nullable=True, comment='SERP 特徵'),

        # 抓取元數據
        sa.Column('source', sa.String(30), nullable=False, server_default='google_hk',
                  comment='google_hk, hktvmall, google_organic, google_local'),
        sa.Column('tracked_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('scrape_duration_ms', sa.Integer(), nullable=True),
        sa.Column('scrape_success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('scrape_error', sa.Text(), nullable=True),
    )

    # Keyword Rankings 索引
    op.create_index('idx_keyword_rankings_keyword_config_id', 'keyword_rankings', ['keyword_config_id'])
    op.create_index('idx_keyword_rankings_product_id', 'keyword_rankings', ['product_id'])
    op.create_index('idx_keyword_rankings_keyword', 'keyword_rankings', ['keyword'])
    op.create_index('idx_keyword_rankings_tracked_at', 'keyword_rankings', ['tracked_at'])
    op.create_index('idx_keyword_rankings_google_rank', 'keyword_rankings', ['google_rank'])
    op.create_index('idx_keyword_rankings_hktvmall_rank', 'keyword_rankings', ['hktvmall_rank'])
    op.create_index('idx_keyword_rankings_keyword_tracked', 'keyword_rankings',
                    ['keyword_config_id', 'tracked_at'])

    # =============================================
    # 3. SEO Reports 表（優化報告）
    # =============================================
    op.create_table(
        'seo_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # 報告基本資訊
        sa.Column('report_type', sa.String(20), nullable=False, server_default='weekly',
                  comment='daily, weekly, monthly, manual'),
        sa.Column('report_title', sa.String(255), nullable=False),
        sa.Column('report_period_start', sa.DateTime(), nullable=False),
        sa.Column('report_period_end', sa.DateTime(), nullable=False),

        # Google SEO 摘要
        sa.Column('google_summary', postgresql.JSONB(), nullable=True,
                  comment='Google SEO 統計摘要'),

        # HKTVmall SEO 摘要
        sa.Column('hktvmall_summary', postgresql.JSONB(), nullable=True,
                  comment='HKTVmall SEO 統計摘要'),

        # 關鍵詞排名詳情
        sa.Column('keyword_details', postgresql.JSONB(), nullable=True,
                  comment='關鍵詞排名詳情列表'),

        # 競品對比
        sa.Column('competitor_comparison', postgresql.JSONB(), nullable=True,
                  comment='競品對比數據'),

        # AI 優化建議
        sa.Column('recommendations', postgresql.JSONB(), nullable=True,
                  comment='AI 優化建議列表'),

        # 效果追蹤
        sa.Column('previous_report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('improvement_score', sa.Integer(), nullable=True, comment='改進分數 -100 到 100'),

        # 報告狀態
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),

        # 生成元數據
        sa.Column('generation_metadata', postgresql.JSONB(), nullable=True),

        # 時間戳
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(), nullable=True),
    )

    # SEO Reports 索引
    op.create_index('idx_seo_reports_product_id', 'seo_reports', ['product_id'])
    op.create_index('idx_seo_reports_report_type', 'seo_reports', ['report_type'])
    op.create_index('idx_seo_reports_generated_at', 'seo_reports', ['generated_at'])
    op.create_index('idx_seo_reports_status', 'seo_reports', ['status'])

    # =============================================
    # 4. Ranking Alerts 表（排名警報）
    # =============================================
    op.create_table(
        'ranking_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('keyword_config_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('keyword_configs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),

        # 警報資訊
        sa.Column('alert_type', sa.String(50), nullable=False,
                  comment='rank_drop, rank_improve, competitor_overtake, target_achieved'),
        sa.Column('severity', sa.String(20), nullable=False, server_default='info',
                  comment='info, warning, critical'),

        # 警報內容
        sa.Column('keyword', sa.String(255), nullable=False),
        sa.Column('source', sa.String(30), nullable=False, comment='google_hk, hktvmall'),
        sa.Column('previous_rank', sa.Integer(), nullable=True),
        sa.Column('current_rank', sa.Integer(), nullable=True),
        sa.Column('rank_change', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),

        # 狀態
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(255), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Ranking Alerts 索引
    op.create_index('idx_ranking_alerts_keyword_config_id', 'ranking_alerts', ['keyword_config_id'])
    op.create_index('idx_ranking_alerts_product_id', 'ranking_alerts', ['product_id'])
    op.create_index('idx_ranking_alerts_alert_type', 'ranking_alerts', ['alert_type'])
    op.create_index('idx_ranking_alerts_severity', 'ranking_alerts', ['severity'])
    op.create_index('idx_ranking_alerts_is_read', 'ranking_alerts', ['is_read'])
    op.create_index('idx_ranking_alerts_created_at', 'ranking_alerts', ['created_at'])

    # =============================================
    # 5. Ranking Scrape Jobs 表（抓取任務記錄）
    # =============================================
    op.create_table(
        'ranking_scrape_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # 任務資訊
        sa.Column('job_type', sa.String(50), nullable=False,
                  comment='full, google_only, hktvmall_only, single_keyword'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending',
                  comment='pending, running, completed, failed, cancelled'),

        # 任務範圍
        sa.Column('total_keywords', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_keywords', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_keywords', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_keywords', sa.Integer(), nullable=False, server_default='0'),

        # 執行詳情
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),

        # 錯誤記錄
        sa.Column('errors', postgresql.JSONB(), nullable=True, server_default='[]'),

        # 觸發資訊
        sa.Column('triggered_by', sa.String(50), nullable=False, server_default='scheduler'),
        sa.Column('triggered_by_user', sa.String(255), nullable=True),

        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Ranking Scrape Jobs 索引
    op.create_index('idx_ranking_scrape_jobs_status', 'ranking_scrape_jobs', ['status'])
    op.create_index('idx_ranking_scrape_jobs_job_type', 'ranking_scrape_jobs', ['job_type'])
    op.create_index('idx_ranking_scrape_jobs_created_at', 'ranking_scrape_jobs', ['created_at'])


def downgrade() -> None:
    # 5. Ranking Scrape Jobs
    op.drop_index('idx_ranking_scrape_jobs_created_at', table_name='ranking_scrape_jobs')
    op.drop_index('idx_ranking_scrape_jobs_job_type', table_name='ranking_scrape_jobs')
    op.drop_index('idx_ranking_scrape_jobs_status', table_name='ranking_scrape_jobs')
    op.drop_table('ranking_scrape_jobs')

    # 4. Ranking Alerts
    op.drop_index('idx_ranking_alerts_created_at', table_name='ranking_alerts')
    op.drop_index('idx_ranking_alerts_is_read', table_name='ranking_alerts')
    op.drop_index('idx_ranking_alerts_severity', table_name='ranking_alerts')
    op.drop_index('idx_ranking_alerts_alert_type', table_name='ranking_alerts')
    op.drop_index('idx_ranking_alerts_product_id', table_name='ranking_alerts')
    op.drop_index('idx_ranking_alerts_keyword_config_id', table_name='ranking_alerts')
    op.drop_table('ranking_alerts')

    # 3. SEO Reports
    op.drop_index('idx_seo_reports_status', table_name='seo_reports')
    op.drop_index('idx_seo_reports_generated_at', table_name='seo_reports')
    op.drop_index('idx_seo_reports_report_type', table_name='seo_reports')
    op.drop_index('idx_seo_reports_product_id', table_name='seo_reports')
    op.drop_table('seo_reports')

    # 2. Keyword Rankings
    op.drop_index('idx_keyword_rankings_keyword_tracked', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_hktvmall_rank', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_google_rank', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_tracked_at', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_keyword', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_product_id', table_name='keyword_rankings')
    op.drop_index('idx_keyword_rankings_keyword_config_id', table_name='keyword_rankings')
    op.drop_table('keyword_rankings')

    # 1. Keyword Configs
    op.drop_index('idx_keyword_configs_latest_hktvmall_rank', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_latest_google_rank', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_is_active', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_keyword_type', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_keyword_normalized', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_keyword', table_name='keyword_configs')
    op.drop_index('idx_keyword_configs_product_id', table_name='keyword_configs')
    op.drop_table('keyword_configs')
