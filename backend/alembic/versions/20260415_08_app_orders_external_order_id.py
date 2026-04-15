"""Add external_order_id to app_orders for stable API keys."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260415_08_app_orders_external_order_id"
down_revision = "20260411_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "app_orders",
        sa.Column("external_order_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_app_orders_external_order_id_unique",
        "app_orders",
        ["external_order_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_app_orders_external_order_id_unique", table_name="app_orders")
    op.drop_column("app_orders", "external_order_id")
