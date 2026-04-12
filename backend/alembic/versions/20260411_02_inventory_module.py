"""inventory and stock correction module

Revision ID: 20260411_02
Revises: 20260411_01
Create Date: 2026-04-11 19:05:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260411_02"
down_revision = "20260411_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_counts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("material_article_number", sa.String(length=100), nullable=False),
        sa.Column("counted_stock_mm", sa.Integer(), nullable=False),
        sa.Column("reference_stock_mm", sa.Integer(), nullable=False),
        sa.Column("difference_mm", sa.Integer(), nullable=False),
        sa.Column("difference_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="recorded"),
        sa.Column("counted_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "difference_type IN ('surplus','deficit','equal')",
            name="ck_inventory_counts_difference_type",
        ),
        sa.CheckConstraint(
            "status IN ('recorded','compared','correction_requested','closed')",
            name="ck_inventory_counts_status",
        ),
        sa.ForeignKeyConstraint(
            ["counted_by_user_id"],
            ["users.id"],
            name="fk_inventory_counts_counted_by_user_id_users",
        ),
    )

    op.create_table(
        "stock_corrections",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("inventory_count_id", sa.BigInteger(), nullable=False),
        sa.Column("material_article_number", sa.String(length=100), nullable=False),
        sa.Column("correction_mm", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="requested"),
        sa.Column("requested_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("confirmed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("canceled_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('requested','confirmed','canceled')",
            name="ck_stock_corrections_status",
        ),
        sa.ForeignKeyConstraint(
            ["inventory_count_id"],
            ["inventory_counts.id"],
            name="fk_stock_corrections_inventory_count_id_inventory_counts",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name="fk_stock_corrections_requested_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by_user_id"],
            ["users.id"],
            name="fk_stock_corrections_confirmed_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["canceled_by_user_id"],
            ["users.id"],
            name="fk_stock_corrections_canceled_by_user_id_users",
        ),
    )


def downgrade() -> None:
    op.drop_table("stock_corrections")
    op.drop_table("inventory_counts")
