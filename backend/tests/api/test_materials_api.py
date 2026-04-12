from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_material_by_article_number_use_case,
    get_search_materials_use_case,
)
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
