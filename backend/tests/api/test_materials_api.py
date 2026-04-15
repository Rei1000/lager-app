from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_material_by_article_number_use_case,
    get_preview_order_plan_use_case,
    get_search_materials_use_case,
)
from application.dtos import OrderPlanOpenOrderLine, OrderPlanPreviewResult
from ports.material_lookup_port import MaterialLookupRecord


def test_search_materials_endpoint_returns_matches() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None
    class FakeSearchMaterialsUseCase:
        def execute(self, _command: object) -> list[MaterialLookupRecord]:
            return [
                MaterialLookupRecord(
                    article_number="ART-001",
                    name="Stahlprofil 40x40",
                    profile="40x40",
                    erp_stock_m=120.0,
                    rest_stock_m=12.0,
                )
            ]

    app.dependency_overrides[get_search_materials_use_case] = lambda: FakeSearchMaterialsUseCase()
    client = TestClient(app)

    response = client.get("/materials/search", params={"query": "ART-001"})

    assert response.status_code == 200
    assert response.json()[0]["article_number"] == "ART-001"
    app.dependency_overrides.clear()


def test_get_material_by_article_number_endpoint_returns_detail() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None
    class FakeGetMaterialUseCase:
        def execute(self, _article_number: str) -> MaterialLookupRecord:
            return MaterialLookupRecord(
                article_number="ART-001",
                name="Stahlprofil 40x40",
                profile="40x40",
                erp_stock_m=120.0,
                rest_stock_m=12.0,
            )

    app.dependency_overrides[get_material_by_article_number_use_case] = lambda: FakeGetMaterialUseCase()
    client = TestClient(app)

    response = client.get("/materials/ART-001")

    assert response.status_code == 200
    assert response.json()["name"] == "Stahlprofil 40x40"
    app.dependency_overrides.clear()


def test_search_materials_endpoint_rejects_empty_query() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None
    client = TestClient(app)
    response = client.get("/materials/search", params={"query": ""})
    assert response.status_code == 422


def test_plan_preview_endpoint_returns_computed_preview() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None

    class FakePreviewOrderPlanUseCase:
        def execute(self, _command: object) -> OrderPlanPreviewResult:
            return OrderPlanPreviewResult(
                article_number="ART-1",
                material_name="Test",
                stock_m=100.0,
                in_pipeline_m=5.0,
                available_m=95.0,
                open_orders=(
                    OrderPlanOpenOrderLine(order_reference="O-1", required_m=5.0, status="open"),
                ),
                net_required_mm=2000,
                kerf_total_mm=2,
                gross_required_mm=2002,
                net_required_m=2.0,
                kerf_total_m=0.002,
                gross_required_m=2.002,
                feasible=True,
            )

    app.dependency_overrides[get_preview_order_plan_use_case] = lambda: FakePreviewOrderPlanUseCase()
    client = TestClient(app)

    response = client.post(
        "/materials/plan-preview",
        json={
            "article_number": "ART-1",
            "quantity": 2,
            "part_length_mm": 1000,
            "kerf_mm": 2,
            "rest_piece_consideration_requested": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["article_number"] == "ART-1"
    assert body["feasible"] is True
    assert body["gross_required_m"] == 2.002
    assert body["open_orders"][0]["order_reference"] == "O-1"
    app.dependency_overrides.clear()
