"""erp transfer request preparation table

Revision ID: 20260411_03
Revises: 20260411_02
Create Date: 2026-04-11 21:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260411_03"
down_revision = "20260411_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "erp_transfer_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.String(length=100), nullable=False),
        sa.Column("material_article_number", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("requested_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("ready_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("sent_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("failed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft','ready','sent','failed')",
            name="ck_erp_transfer_requests_status",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name="fk_erp_transfer_requests_requested_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["ready_by_user_id"],
            ["users.id"],
            name="fk_erp_transfer_requests_ready_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["sent_by_user_id"],
            ["users.id"],
            name="fk_erp_transfer_requests_sent_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["failed_by_user_id"],
            ["users.id"],
            name="fk_erp_transfer_requests_failed_by_user_id_users",
        ),
    )


def downgrade() -> None:
    op.drop_table("erp_transfer_requests")
