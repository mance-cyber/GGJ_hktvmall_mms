"""add name_en to competitor_products

Revision ID: add_name_en_cp
Revises: None
Create Date: 2026-03-12 00:24:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_name_en_cp'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('competitor_products', sa.Column('name_en', sa.String(500), nullable=True, comment='English product name'))


def downgrade() -> None:
    op.drop_column('competitor_products', 'name_en')
