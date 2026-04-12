"""audit log event fields

Revision ID: 20260411_05
Revises: 20260411_04
Create Date: 2026-04-11 22:45:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260411_05"
down_revision = "20260411_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("audit_logs", "event_type", new_column_name="action")
    op.add_column("audit_logs", sa.Column("entity_id", sa.String(length=120), nullable=True))
    op.add_column("audit_logs", sa.Column("user_id", sa.BigInteger(), nullable=True))
    op.add_column("audit_logs", sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("audit_logs", sa.Column("comment", sa.Text(), nullable=True))
    op.execute("UPDATE audit_logs SET occurred_at = NOW() WHERE occurred_at IS NULL")
    op.alter_column("audit_logs", "occurred_at", nullable=False)


def downgrade() -> None:
    op.drop_column("audit_logs", "comment")
    op.drop_column("audit_logs", "occurred_at")
    op.drop_column("audit_logs", "user_id")
    op.drop_column("audit_logs", "entity_id")
    op.alter_column("audit_logs", "action", new_column_name="event_type")
