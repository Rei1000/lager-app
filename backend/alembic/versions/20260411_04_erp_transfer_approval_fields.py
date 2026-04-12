"""erp transfer approval fields

Revision ID: 20260411_04
Revises: 20260411_03
Create Date: 2026-04-11 22:15:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260411_04"
down_revision = "20260411_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "erp_transfer_requests",
        sa.Column("approved_by_user_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "erp_transfer_requests",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_erp_transfer_requests_approved_by_user_id_users",
        "erp_transfer_requests",
        "users",
        ["approved_by_user_id"],
        ["id"],
    )
    op.drop_constraint("ck_erp_transfer_requests_status", "erp_transfer_requests", type_="check")
    op.create_check_constraint(
        "ck_erp_transfer_requests_status",
        "erp_transfer_requests",
        "status IN ('draft','ready','approved','sent','failed')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_erp_transfer_requests_status", "erp_transfer_requests", type_="check")
    op.create_check_constraint(
        "ck_erp_transfer_requests_status",
        "erp_transfer_requests",
        "status IN ('draft','ready','sent','failed')",
    )
    op.drop_constraint(
        "fk_erp_transfer_requests_approved_by_user_id_users",
        "erp_transfer_requests",
        type_="foreignkey",
    )
    op.drop_column("erp_transfer_requests", "approved_at")
    op.drop_column("erp_transfer_requests", "approved_by_user_id")
