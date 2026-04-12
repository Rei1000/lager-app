from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import get_dashboard_overview_use_case
from application.use_cases.orders_read_use_cases import DashboardOverviewResult
from domain.entities import AppOrder
from domain.value_objects import TrafficLight


def _make_order(order_id: str, status: str, priority: int, light: TrafficLight) -> AppOrder:
    order = AppOrder(
        order_id=order_id,
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status=status,
        priority_order=priority,
    )
    order.traffic_light = light
    return order


def test_dashboard_overview_endpoint_returns_open_orders_and_metrics() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: None

    class FakeDashboardUseCase:
        def execute(self) -> DashboardOverviewResult:
            orders = [
                _make_order("A1", "checked", 1, TrafficLight.GREEN),
                _make_order("A2", "reserved", 2, TrafficLight.RED),
            ]
            return DashboardOverviewResult(
                open_orders=orders,
                open_orders_count=2,
                critical_orders_count=1,
            )

    app.dependency_overrides[get_dashboard_overview_use_case] = lambda: FakeDashboardUseCase()
    client = TestClient(app)

    response = client.get("/dashboard/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["open_orders_count"] == 2
    assert payload["critical_orders_count"] == 1
    assert payload["open_orders"][1]["traffic_light"] == "red"
    app.dependency_overrides.clear()
