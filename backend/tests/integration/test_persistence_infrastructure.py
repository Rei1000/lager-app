from __future__ import annotations

from pathlib import Path

from adapters.persistence.base import Base
from adapters.persistence.models import *  # noqa: F401,F403
from config.settings import settings


def test_sqlalchemy_base_importable() -> None:
    assert Base.metadata is not None


def test_model_metadata_contains_expected_tables() -> None:
    expected_tables = {
        "roles",
        "users",
        "material_types",
        "rest_stock_accounts",
        "cutting_machines",
        "app_orders",
        "order_status_history",
        "erp_profiles",
        "erp_auth_configs",
        "erp_function_endpoints",
        "erp_field_mappings",
        "erp_transfer_requests",
        "inventory_counts",
        "stock_corrections",
        "photos",
        "comments",
        "audit_logs",
    }
    assert expected_tables.issubset(set(Base.metadata.tables.keys()))


def test_alembic_configuration_files_exist() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    assert (backend_root / "alembic.ini").is_file()
    assert (backend_root / "alembic" / "env.py").is_file()
    assert (backend_root / "alembic" / "versions").is_dir()


def test_engine_has_configured_url() -> None:
    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")
