"""Add image generation tables

Revision ID: 3830de192d80
Revises: add_mrc_fields_001
Create Date: 2026-01-12 13:36:44.704283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3830de192d80'
down_revision: Union[str, None] = 'add_mrc_fields_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 創建 GenerationMode 和 TaskStatus Enum 類型（如果不存在）
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE generationmode AS ENUM ('white_bg_topview', 'professional_photo');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE taskstatus AS ENUM ('pending', 'processing', 'completed', 'failed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # 創建 Enum 對象引用（不創建新類型）
    generation_mode_enum = postgresql.ENUM('white_bg_topview', 'professional_photo', name='generationmode', create_type=False)
    task_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='taskstatus', create_type=False)

    # 創建 image_generation_tasks 表
    op.create_table(
        'image_generation_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('mode', generation_mode_enum, nullable=False),
        sa.Column('style_description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, nullable=False, server_default='pending'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 創建 input_images 表
    op.create_table(
        'input_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('image_generation_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(50), nullable=False),
        sa.Column('upload_order', sa.Integer(), nullable=False),
        sa.Column('analysis_result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # 創建 output_images 表
    op.create_table(
        'output_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('image_generation_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(50), nullable=False, server_default='image/png'),
        sa.Column('prompt_used', sa.Text(), nullable=True),
        sa.Column('generation_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )


def downgrade() -> None:
    # 刪除表
    op.drop_table('output_images')
    op.drop_table('input_images')
    op.drop_table('image_generation_tasks')

    # 刪除 Enum 類型
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS generationmode')
