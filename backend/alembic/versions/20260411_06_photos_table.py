"""photos table for material and inventory documentation

Revision ID: 20260411_06
Revises: 20260411_05
Create Date: 2026-04-11 23:40:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260411_06"
down_revision = "20260411_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "photos",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=120), nullable=False),
        sa.Column("file_key", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("uploaded_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["uploaded_by_user_id"],
            ["users.id"],
            name="fk_photos_uploaded_by_user_id_users",
        ),
    )
    op.create_index("ix_photos_entity", "photos", ["entity_type", "entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_photos_entity", table_name="photos")
    op.drop_table("photos")
