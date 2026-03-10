"""add report_subscribers table

Revision ID: 20260310_1440
Revises: 20260308_2200_add_stock_level
Create Date: 2026-03-10 14:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260310_1440"
down_revision = "20260308_2200_add_stock_level"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_subscribers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chat_id", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("subscribed_at", sa.DateTime(), nullable=True),
        sa.Column("last_delivered_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("report_subscribers")
