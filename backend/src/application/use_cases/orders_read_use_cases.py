"""Read-oriented use cases for dashboard and orders views."""

from __future__ import annotations

from dataclasses import dataclass

from application.errors import NotFoundError
from domain.entities import AppOrder
from ports.order_repository_port import OrderRepositoryPort


@dataclass(frozen=True)
class DashboardOverviewResult:
    open_orders: list[AppOrder]
    open_orders_count: int
    critical_orders_count: int


class ListOrdersDetailedUseCase:
    def __init__(self, order_repository: OrderRepositoryPort) -> None:
        self._order_repository = order_repository

    def execute(
        self,
        *,
        status: str | None = None,
        material_article_number: str | None = None,
    ) -> list[AppOrder]:
        orders = self._order_repository.list_all()
        if status:
            orders = [order for order in orders if order.status == status]
        if material_article_number:
            orders = [
                order
                for order in orders
                if order.material_article_number == material_article_number
            ]
        return sorted(
            orders,
            key=lambda order: order.priority_order if order.priority_order is not None else 10**9,
        )


class GetOrderDetailUseCase:
    def __init__(self, order_repository: OrderRepositoryPort) -> None:
        self._order_repository = order_repository

    def execute(self, order_id: str) -> AppOrder:
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Auftrag nicht gefunden: {order_id}")
        return order


class GetDashboardOverviewUseCase:
    def __init__(self, order_repository: OrderRepositoryPort) -> None:
        self._order_repository = order_repository

    def execute(self) -> DashboardOverviewResult:
        orders = self._order_repository.list_all()
        open_orders = [order for order in orders if order.status not in {"done", "canceled"}]
        critical_orders_count = sum(1 for order in open_orders if order.traffic_light and order.traffic_light.value == "red")
        return DashboardOverviewResult(
            open_orders=open_orders,
            open_orders_count=len(open_orders),
            critical_orders_count=critical_orders_count,
        )
