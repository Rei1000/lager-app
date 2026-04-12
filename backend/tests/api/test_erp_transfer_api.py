from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_approve_erp_transfer_use_case,
    get_create_erp_transfer_request_use_case,
    get_list_erp_transfer_requests_use_case,
    get_mark_erp_transfer_failed_use_case,
    get_mark_erp_transfer_ready_use_case,
    get_mark_erp_transfer_sent_use_case,
)
from ports.erp_transfer_repository_port import ErpTransferRequestRecord


def _record(status: str, transfer_id: int = 1) -> ErpTransferRequestRecord:
    now = datetime.now(timezone.utc)
    return ErpTransferRequestRecord(
        id=transfer_id,
        order_id="ORD-1",
        material_article_number="ART-001",
        status=status,
        requested_by_user_id=1,
        payload={"amount_mm": 1000},
        created_at=now,
    )


def test_erp_transfer_list_and_create_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="leitung",
        role_code="leitung",
        role_name="Leitung",
    )

    class FakeListUseCase:
        def execute(self) -> list[ErpTransferRequestRecord]:
            return [_record("draft", transfer_id=1)]

    class FakeCreateUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            return _record("draft", transfer_id=2)

    app.dependency_overrides[get_list_erp_transfer_requests_use_case] = lambda: FakeListUseCase()
    app.dependency_overrides[get_create_erp_transfer_request_use_case] = lambda: FakeCreateUseCase()
    client = TestClient(app)

    list_response = client.get("/erp/transfers")
    create_response = client.post(
        "/erp/transfers",
        json={
            "order_id": "ORD-2",
            "material_article_number": "ART-002",
            "requested_by_user_id": 5,
            "payload": {"amount_mm": 2500},
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["status"] == "draft"
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 2
    app.dependency_overrides.clear()


def test_erp_transfer_status_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=3,
        username="admin",
        role_code="admin",
        role_name="Admin",
    )

    class FakeReadyUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            return _record("ready", transfer_id=10)

    class FakeSentUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            return _record("sent", transfer_id=10)

    class FakeApproveUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            return _record("approved", transfer_id=10)

    class FakeFailUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            return ErpTransferRequestRecord(
                id=11,
                order_id="ORD-1",
                material_article_number="ART-001",
                status="failed",
                requested_by_user_id=1,
                payload={"amount_mm": 1000},
                created_at=datetime.now(timezone.utc),
                failure_reason="ERP nicht erreichbar",
            )

    app.dependency_overrides[get_mark_erp_transfer_ready_use_case] = lambda: FakeReadyUseCase()
    app.dependency_overrides[get_approve_erp_transfer_use_case] = lambda: FakeApproveUseCase()
    app.dependency_overrides[get_mark_erp_transfer_sent_use_case] = lambda: FakeSentUseCase()
    app.dependency_overrides[get_mark_erp_transfer_failed_use_case] = lambda: FakeFailUseCase()
    client = TestClient(app)

    ready_response = client.post("/erp/transfers/10/ready", json={"acting_user_id": 2})
    approve_response = client.post("/erp/transfers/10/approve", json={"acting_user_id": 2})
    sent_response = client.post("/erp/transfers/10/send", json={"acting_user_id": 3})
    fail_response = client.post(
        "/erp/transfers/11/fail",
        json={"acting_user_id": 4, "failure_reason": "ERP nicht erreichbar"},
    )

    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"
    assert sent_response.status_code == 200
    assert sent_response.json()["status"] == "sent"
    assert fail_response.status_code == 200
    assert fail_response.json()["failure_reason"] == "ERP nicht erreichbar"
    app.dependency_overrides.clear()


def test_erp_transfer_send_requires_admin() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="leitung",
        role_code="leitung",
        role_name="Leitung",
    )
    client = TestClient(app)

    response = client.post("/erp/transfers/10/send", json={"acting_user_id": 3})

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_erp_transfer_approve_requires_leitung_or_admin() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    client = TestClient(app)

    response = client.post("/erp/transfers/10/approve", json={"acting_user_id": 3})

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_erp_transfer_send_without_approve_returns_400() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=3,
        username="admin",
        role_code="admin",
        role_name="Admin",
    )

    class FakeSentUseCase:
        def execute(self, _command: object) -> ErpTransferRequestRecord:
            raise ValueError("ERP-Transferstatus nicht erlaubt: ready -> sent")

    app.dependency_overrides[get_mark_erp_transfer_sent_use_case] = lambda: FakeSentUseCase()
    client = TestClient(app)

    response = client.post("/erp/transfers/10/send", json={"acting_user_id": 3})

    assert response.status_code == 400
    app.dependency_overrides.clear()
