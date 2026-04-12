"""initial schema

Revision ID: 20260411_01
Revises:
Create Date: 2026-04-11 14:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260411_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("code", name="uq_roles_code"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("erp_user_reference", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name="fk_users_role_id_roles"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "material_types",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("article_number", sa.String(length=100), nullable=False),
        sa.Column("erp_material_id", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("profile", sa.String(length=100), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("min_rest_length_mm", sa.Integer(), nullable=True),
        sa.Column("erp_stock_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("rest_stock_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("main_storage_location", sa.String(length=100), nullable=True),
        sa.Column("rest_storage_location", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("article_number", name="uq_material_types_article_number"),
    )

    op.create_table(
        "rest_stock_accounts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("material_type_id", sa.BigInteger(), nullable=False),
        sa.Column("rest_stock_id", sa.String(length=100), nullable=False),
        sa.Column("total_rest_stock_m", sa.Numeric(14, 3), nullable=False),
        sa.Column("storage_location", sa.String(length=100), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["material_type_id"],
            ["material_types.id"],
            name="fk_rest_stock_accounts_material_type_id_material_types",
        ),
        sa.UniqueConstraint("material_type_id", name="uq_rest_stock_accounts_material_type_id"),
        sa.UniqueConstraint("rest_stock_id", name="uq_rest_stock_accounts_rest_stock_id"),
    )

    op.create_table(
        "cutting_machines",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("machine_code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("kerf_mm", sa.Numeric(8, 3), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "erp_profiles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("erp_type", sa.String(length=50), nullable=True),
        sa.Column("connection_type", sa.String(length=50), nullable=True),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("tenant_code", sa.String(length=100), nullable=True),
    )

    op.create_table(
        "erp_auth_configs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("auth_type", sa.String(length=50), nullable=True),
        sa.Column("client_id", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("token_url", sa.Text(), nullable=True),
    )

    op.create_table(
        "erp_function_endpoints",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("erp_profile_id", sa.BigInteger(), nullable=False),
        sa.Column("functional_key", sa.String(length=100), nullable=False),
        sa.Column("http_method", sa.String(length=10), nullable=False),
        sa.Column("path_template", sa.Text(), nullable=False),
        sa.Column("query_template_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("request_template_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["erp_profile_id"],
            ["erp_profiles.id"],
            name="fk_erp_function_endpoints_erp_profile_id_erp_profiles",
        ),
    )

    op.create_table(
        "erp_field_mappings",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("endpoint_id", sa.BigInteger(), nullable=False),
        sa.Column("app_field", sa.String(length=100), nullable=False),
        sa.Column("erp_field", sa.String(length=255), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["endpoint_id"],
            ["erp_function_endpoints.id"],
            name="fk_erp_field_mappings_endpoint_id_erp_function_endpoints",
        ),
    )

    op.create_table(
        "app_orders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("material_type_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("part_length_mm", sa.Integer(), nullable=False),
        sa.Column("cutting_machine_id", sa.BigInteger(), nullable=True),
        sa.Column("kerf_mm_snapshot", sa.Numeric(14, 3), nullable=True),
        sa.Column("include_rest_stock", sa.Boolean(), nullable=True),
        sa.Column("calculated_total_demand_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("demand_from_full_stock_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("demand_from_rest_stock_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("shortage_m", sa.Numeric(14, 3), nullable=True),
        sa.Column("traffic_light", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority_order", sa.Integer(), nullable=True),
        sa.Column("erp_order_number", sa.String(length=100), nullable=True),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_app_orders_status",
        ),
        sa.ForeignKeyConstraint(
            ["material_type_id"],
            ["material_types.id"],
            name="fk_app_orders_material_type_id_material_types",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_app_orders_created_by_user_id_users",
        ),
        sa.ForeignKeyConstraint(
            ["cutting_machine_id"],
            ["cutting_machines.id"],
            name="fk_app_orders_cutting_machine_id_cutting_machines",
        ),
    )

    op.create_table(
        "order_status_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("app_order_id", sa.BigInteger(), nullable=False),
        sa.Column("old_status", sa.String(length=30), nullable=False),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("changed_by_user_id", sa.BigInteger(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "old_status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_order_status_history_old_status",
        ),
        sa.CheckConstraint(
            "new_status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_order_status_history_new_status",
        ),
        sa.ForeignKeyConstraint(
            ["app_order_id"],
            ["app_orders.id"],
            name="fk_order_status_history_app_order_id_app_orders",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["users.id"],
            name="fk_order_status_history_changed_by_user_id_users",
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.create_index("ix_material_types_article_number", "material_types", ["article_number"])
    op.create_index("ix_app_orders_material_type_id", "app_orders", ["material_type_id"])
    op.create_index("ix_app_orders_status", "app_orders", ["status"])
    op.create_index("ix_app_orders_priority_order", "app_orders", ["priority_order"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity_type", table_name="audit_logs")
    op.drop_index("ix_app_orders_priority_order", table_name="app_orders")
    op.drop_index("ix_app_orders_status", table_name="app_orders")
    op.drop_index("ix_app_orders_material_type_id", table_name="app_orders")
    op.drop_index("ix_material_types_article_number", table_name="material_types")

    op.drop_table("audit_logs")
    op.drop_table("order_status_history")
    op.drop_table("app_orders")
    op.drop_table("erp_field_mappings")
    op.drop_table("erp_function_endpoints")
    op.drop_table("erp_auth_configs")
    op.drop_table("erp_profiles")
    op.drop_table("cutting_machines")
    op.drop_table("rest_stock_accounts")
    op.drop_table("material_types")
    op.drop_table("users")
    op.drop_table("roles")
