from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_erp_material_stock_use_case,
    get_erp_material_use_case,
    get_validate_erp_order_reference_use_case,
)


def test_get_erp_material_endpoint_returns_payload() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None

    class FakeUseCase:
        def execute(self, _reference: str) -> dict[str, object]:
            return {"material_reference": "MAT-1", "name": "Steel"}

    app.dependency_overrides[get_erp_material_use_case] = lambda: FakeUseCase()
    client = TestClient(app)

    response = client.get("/erp/materials/MAT-1")

    assert response.status_code == 200
    assert response.json()["payload"]["material_reference"] == "MAT-1"
    app.dependency_overrides.clear()


def test_get_erp_material_stock_endpoint_returns_payload() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None

    class FakeUseCase:
        def execute(self, _reference: str) -> dict[str, object]:
            return {"material_reference": "MAT-1", "stock_m": 55.0}

    app.dependency_overrides[get_erp_material_stock_use_case] = lambda: FakeUseCase()
    client = TestClient(app)

    response = client.get("/erp/materials/MAT-1/stock")

    assert response.status_code == 200
    assert response.json()["payload"]["stock_m"] == 55.0
    app.dependency_overrides.clear()


def test_validate_erp_order_reference_endpoint_returns_boolean() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None

    class FakeUseCase:
        def execute(self, _reference: str) -> bool:
            return True

    app.dependency_overrides[get_validate_erp_order_reference_use_case] = lambda: FakeUseCase()
    client = TestClient(app)

    response = client.get("/erp/orders/ERP-42/validate")

    assert response.status_code == 200
    assert response.json()["is_valid"] is True
    app.dependency_overrides.clear()
