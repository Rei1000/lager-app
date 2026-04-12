from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import get_list_audit_logs_use_case
from ports.audit_log_port import AuditLogRecord


def test_list_audit_logs_endpoint_returns_records() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="leitung",
        role_code="leitung",
        role_name="Leitung",
    )

    class FakeUseCase:
        def execute(self, **_kwargs: object) -> list[AuditLogRecord]:
            return [
                AuditLogRecord(
                    id=1,
                    entity_type="erp_transfer",
                    entity_id="5",
                    action="approved",
                    user_id=2,
                    occurred_at=datetime.now(timezone.utc),
                    payload={"order_id": "ORD-1"},
                    comment=None,
                )
            ]

    app.dependency_overrides[get_list_audit_logs_use_case] = lambda: FakeUseCase()
    client = TestClient(app)

    response = client.get("/audit-logs?entity_type=erp_transfer&entity_id=5")

    assert response.status_code == 200
    assert response.json()[0]["action"] == "approved"
    app.dependency_overrides.clear()


def test_list_audit_logs_requires_leitung_or_admin() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    client = TestClient(app)

    response = client.get("/audit-logs")

    assert response.status_code == 403
    app.dependency_overrides.clear()
