from __future__ import annotations

from dataclasses import dataclass

from application.use_cases.orders_read_use_cases import (
    GetDashboardOverviewUseCase,
    GetOrderDetailUseCase,
    ListOrdersDetailedUseCase,
)
from domain.entities import AppOrder
from domain.value_objects import TrafficLight
from ports.order_repository_port import OrderRepositoryPort


@dataclass
class FakeOrderRepository(OrderRepositoryPort):
    orders: list[AppOrder]

    def list_all(self) -> list[AppOrder]:
        return list(self.orders)

    def get_by_id(self, order_id: str) -> AppOrder | None:
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def list_by_material(self, material_article_number: str) -> list[AppOrder]:
        return [order for order in self.orders if order.material_article_number == material_article_number]

    def save(self, order: AppOrder) -> None:
        for idx, existing in enumerate(self.orders):
            if existing.order_id == order.order_id:
                self.orders[idx] = order
                return
        self.orders.append(order)


def _make_order(order_id: str, material: str, status: str, priority: int, light: TrafficLight) -> AppOrder:
    order = AppOrder(
        order_id=order_id,
        material_article_number=material,
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status=status,
        priority_order=priority,
    )
    order.traffic_light = light
    return order


def test_list_orders_detailed_use_case_filters_and_sorts() -> None:
    repo = FakeOrderRepository(
        orders=[
            _make_order("A2", "ART-001", "checked", 2, TrafficLight.YELLOW),
            _make_order("A1", "ART-001", "checked", 1, TrafficLight.GREEN),
            _make_order("B1", "ART-002", "draft", 1, TrafficLight.GREEN),
        ]
    )
    use_case = ListOrdersDetailedUseCase(order_repository=repo)

    result = use_case.execute(status="checked", material_article_number="ART-001")

    assert [order.order_id for order in result] == ["A1", "A2"]


def test_get_order_detail_use_case_returns_one_order() -> None:
    repo = FakeOrderRepository(
        orders=[_make_order("A1", "ART-001", "reserved", 1, TrafficLight.GREEN)]
    )
    use_case = GetOrderDetailUseCase(order_repository=repo)

    result = use_case.execute("A1")

    assert result.status == "reserved"


def test_dashboard_overview_use_case_counts_open_and_critical_orders() -> None:
    repo = FakeOrderRepository(
        orders=[
            _make_order("A1", "ART-001", "checked", 1, TrafficLight.GREEN),
            _make_order("A2", "ART-001", "reserved", 2, TrafficLight.RED),
            _make_order("A3", "ART-001", "done", 3, TrafficLight.RED),
        ]
    )
    use_case = GetDashboardOverviewUseCase(order_repository=repo)

    overview = use_case.execute()

    assert overview.open_orders_count == 2
    assert overview.critical_orders_count == 1
