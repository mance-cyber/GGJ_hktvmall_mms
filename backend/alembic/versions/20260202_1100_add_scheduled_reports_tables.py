"""add scheduled_reports and report_executions tables

Revision ID: 20260202_1100
Revises: 20260202_1000
Create Date: 2026-02-02 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260202_1100'
down_revision = '20260202_1000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =============================================
    # scheduled_reports 表
    # =============================================
    op.create_table(
        'scheduled_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        # 基本信息
        sa.Column('name', sa.String(200), nullable=False, comment='排程名稱'),
        sa.Column('description', sa.Text(), nullable=True, comment='排程描述'),
        # 報告配置
        sa.Column('report_type', sa.String(50), nullable=False, server_default='price_analysis', comment='報告類型'),
        sa.Column('report_config', postgresql.JSONB(), nullable=True, comment='報告配置'),
        # 排程配置
        sa.Column('frequency', sa.String(20), nullable=False, server_default='daily', comment='頻率'),
        sa.Column('cron_expression', sa.String(100), nullable=True, comment='Cron 表達式'),
        sa.Column('schedule_time', sa.String(10), nullable=True, comment='執行時間 HH:MM'),
        sa.Column('schedule_day', sa.Integer(), nullable=True, comment='執行日期'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Asia/Hong_Kong', comment='時區'),
        # 交付配置
        sa.Column('delivery_channels', postgresql.JSONB(), nullable=True, comment='交付渠道配置'),
        # 狀態
        sa.Column('status', sa.String(20), nullable=False, server_default='active', comment='狀態'),
        # 執行統計
        sa.Column('last_run_at', sa.DateTime(), nullable=True, comment='上次執行時間'),
        sa.Column('next_run_at', sa.DateTime(), nullable=True, comment='下次執行時間'),
        sa.Column('run_count', sa.Integer(), nullable=False, server_default='0', comment='總執行次數'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0', comment='成功次數'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0', comment='失敗次數'),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0', comment='連續失敗次數'),
        # 來源追溯
        sa.Column('source_conversation_id', sa.String(100), nullable=True, comment='來源對話 ID'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, comment='創建者'),
        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 索引
    op.create_index('idx_scheduled_reports_status', 'scheduled_reports', ['status'])
    op.create_index('idx_scheduled_reports_next_run', 'scheduled_reports', ['next_run_at'])
    op.create_index('idx_scheduled_reports_conversation', 'scheduled_reports', ['source_conversation_id'])

    # =============================================
    # report_executions 表
    # =============================================
    op.create_table(
        'report_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        # 關聯排程
        sa.Column('schedule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scheduled_reports.id', ondelete='CASCADE'), nullable=False),
        # 執行狀態
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', comment='執行狀態'),
        # 執行時間
        sa.Column('scheduled_at', sa.DateTime(), nullable=False, comment='計劃執行時間'),
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='實際開始時間'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='完成時間'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='執行耗時'),
        # 報告內容
        sa.Column('report_content', sa.Text(), nullable=True, comment='報告內容'),
        sa.Column('report_data', postgresql.JSONB(), nullable=True, comment='報告數據'),
        # 交付狀態
        sa.Column('delivery_status', postgresql.JSONB(), nullable=True, comment='交付狀態'),
        # 錯誤信息
        sa.Column('error_message', sa.Text(), nullable=True, comment='錯誤信息'),
        sa.Column('error_details', postgresql.JSONB(), nullable=True, comment='錯誤詳情'),
        # 重試
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0', comment='重試次數'),
        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # 索引
    op.create_index('idx_report_executions_schedule', 'report_executions', ['schedule_id'])
    op.create_index('idx_report_executions_status', 'report_executions', ['status'])
    op.create_index('idx_report_executions_scheduled_at', 'report_executions', ['scheduled_at'])

    # =============================================
    # alert_workflow_configs 表 (Phase 3 預備)
    # =============================================
    op.create_table(
        'alert_workflow_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        # 基本信息
        sa.Column('name', sa.String(200), nullable=False, comment='配置名稱'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否啟用'),
        # 觸發條件
        sa.Column('trigger_conditions', postgresql.JSONB(), nullable=True, comment='觸發條件'),
        # 動作配置
        sa.Column('auto_analyze', sa.Boolean(), nullable=False, server_default='true', comment='自動 AI 分析'),
        sa.Column('auto_create_proposal', sa.Boolean(), nullable=False, server_default='false', comment='自動創建提案'),
        sa.Column('notify_channels', postgresql.JSONB(), nullable=True, comment='通知渠道'),
        # 靜默時段
        sa.Column('quiet_hours_start', sa.String(10), nullable=True, comment='靜默開始'),
        sa.Column('quiet_hours_end', sa.String(10), nullable=True, comment='靜默結束'),
        # 時間戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('idx_alert_workflow_configs_active', 'alert_workflow_configs', ['is_active'])


def downgrade() -> None:
    op.drop_index('idx_alert_workflow_configs_active', table_name='alert_workflow_configs')
    op.drop_table('alert_workflow_configs')

    op.drop_index('idx_report_executions_scheduled_at', table_name='report_executions')
    op.drop_index('idx_report_executions_status', table_name='report_executions')
    op.drop_index('idx_report_executions_schedule', table_name='report_executions')
    op.drop_table('report_executions')

    op.drop_index('idx_scheduled_reports_conversation', table_name='scheduled_reports')
    op.drop_index('idx_scheduled_reports_next_run', table_name='scheduled_reports')
    op.drop_index('idx_scheduled_reports_status', table_name='scheduled_reports')
    op.drop_table('scheduled_reports')
