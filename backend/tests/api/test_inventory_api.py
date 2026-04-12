from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_cancel_stock_correction_use_case,
    get_compare_inventory_to_reference_use_case,
    get_confirm_stock_correction_use_case,
    get_create_inventory_count_use_case,
    get_create_stock_correction_use_case,
    get_list_inventory_counts_use_case,
)
from domain.entities import InventoryDifference
from ports.inventory_repository_port import InventoryCountRecord, StockCorrectionRecord


def test_inventory_count_list_and_create_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    now = datetime.now(timezone.utc)

    class FakeListInventoryCountsUseCase:
        def execute(self) -> list[InventoryCountRecord]:
            return [
                InventoryCountRecord(
                    id=1,
                    material_article_number="ART-001",
                    counted_stock_mm=9_000,
                    reference_stock_mm=10_000,
                    difference_mm=-1_000,
                    difference_type="deficit",
                    status="recorded",
                    counted_by_user_id=1,
                    comment="nachtzaehlung",
                    created_at=now,
                )
            ]

    class FakeCreateInventoryCountUseCase:
        def execute(self, _command: object) -> InventoryCountRecord:
            return InventoryCountRecord(
                id=2,
                material_article_number="ART-001",
                counted_stock_mm=9_500,
                reference_stock_mm=10_000,
                difference_mm=-500,
                difference_type="deficit",
                status="recorded",
                counted_by_user_id=2,
                comment=None,
                created_at=now,
            )

    app.dependency_overrides[get_list_inventory_counts_use_case] = lambda: FakeListInventoryCountsUseCase()
    app.dependency_overrides[get_create_inventory_count_use_case] = lambda: FakeCreateInventoryCountUseCase()
    client = TestClient(app)

    list_response = client.get("/inventory/counts")
    create_response = client.post(
        "/inventory/counts",
        json={
            "material_article_number": "ART-001",
            "counted_stock_mm": 9500,
            "counted_by_user_id": 2,
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["difference_type"] == "deficit"
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 2
    app.dependency_overrides.clear()


def test_inventory_compare_endpoint() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    class FakeCompareUseCase:
        def execute(self, _command: object) -> InventoryDifference:
            return InventoryDifference(
                material_article_number="ART-001",
                counted_stock_mm=8_500,
                reference_stock_mm=10_000,
            )

    app.dependency_overrides[get_compare_inventory_to_reference_use_case] = lambda: FakeCompareUseCase()
    client = TestClient(app)

    response = client.post(
        "/inventory/compare",
        json={"material_article_number": "ART-001", "counted_stock_mm": 8500},
    )

    assert response.status_code == 200
    assert response.json()["difference_mm"] == -1500
    app.dependency_overrides.clear()


def test_inventory_correction_create_confirm_cancel_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="leitung",
        role_code="leitung",
        role_name="Leitung",
    )
    now = datetime.now(timezone.utc)

    class FakeCreateCorrectionUseCase:
        def execute(self, _command: object) -> StockCorrectionRecord:
            return StockCorrectionRecord(
                id=10,
                inventory_count_id=1,
                material_article_number="ART-001",
                correction_mm=-1500,
                status="requested",
                requested_by_user_id=2,
                comment="abweichung pruefen",
                created_at=now,
            )

    class FakeConfirmCorrectionUseCase:
        def execute(self, _command: object) -> StockCorrectionRecord:
            return StockCorrectionRecord(
                id=10,
                inventory_count_id=1,
                material_article_number="ART-001",
                correction_mm=-1500,
                status="confirmed",
                requested_by_user_id=2,
                comment="ok",
                created_at=now,
                confirmed_by_user_id=5,
                confirmed_at=now,
            )

    class FakeCancelCorrectionUseCase:
        def execute(self, _command: object) -> StockCorrectionRecord:
            return StockCorrectionRecord(
                id=11,
                inventory_count_id=2,
                material_article_number="ART-002",
                correction_mm=500,
                status="canceled",
                requested_by_user_id=2,
                comment="falsche zaehlung",
                created_at=now,
                canceled_by_user_id=6,
                canceled_at=now,
            )

    app.dependency_overrides[get_create_stock_correction_use_case] = lambda: FakeCreateCorrectionUseCase()
    app.dependency_overrides[get_confirm_stock_correction_use_case] = lambda: FakeConfirmCorrectionUseCase()
    app.dependency_overrides[get_cancel_stock_correction_use_case] = lambda: FakeCancelCorrectionUseCase()
    client = TestClient(app)

    create_response = client.post(
        "/inventory/corrections",
        json={"inventory_count_id": 1, "requested_by_user_id": 2, "comment": "abweichung pruefen"},
    )
    confirm_response = client.post("/inventory/corrections/10/confirm", json={"acting_user_id": 5})
    cancel_response = client.post("/inventory/corrections/11/cancel", json={"acting_user_id": 6})

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "requested"
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "confirmed"
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"
    app.dependency_overrides.clear()


def test_inventory_confirm_requires_leitung_or_admin() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeConfirmCorrectionUseCase:
        def execute(self, _command: object) -> StockCorrectionRecord:
            now = datetime.now(timezone.utc)
            return StockCorrectionRecord(
                id=10,
                inventory_count_id=1,
                material_article_number="ART-001",
                correction_mm=-1000,
                status="confirmed",
                requested_by_user_id=2,
                comment=None,
                created_at=now,
                confirmed_by_user_id=5,
                confirmed_at=now,
            )

    app.dependency_overrides[get_confirm_stock_correction_use_case] = lambda: FakeConfirmCorrectionUseCase()
    client = TestClient(app)

    response = client.post("/inventory/corrections/10/confirm", json={"acting_user_id": 5})

    assert response.status_code == 403
    app.dependency_overrides.clear()
