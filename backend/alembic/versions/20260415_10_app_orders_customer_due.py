"""Optional Kunde und Faelligkeitsdatum fuer App-Auftraege."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260415_10_app_cust_due"
down_revision = "20260415_08_ext_oid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("app_orders", sa.Column("customer_name", sa.String(length=255), nullable=True))
    op.add_column("app_orders", sa.Column("due_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("app_orders", "due_date")
    op.drop_column("app_orders", "customer_name")
