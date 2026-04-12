"""comments table for simple communication notes

Revision ID: 20260411_07
Revises: 20260411_06
Create Date: 2026-04-11 22:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260411_07"
down_revision = "20260411_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=120), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_comments_created_by_user_id_users",
        ),
    )
    op.create_index("ix_comments_entity", "comments", ["entity_type", "entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comments_entity", table_name="comments")
    op.drop_table("comments")
