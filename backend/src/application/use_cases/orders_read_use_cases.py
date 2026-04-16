"""Read-oriented use cases for dashboard and orders views."""

from __future__ import annotations

import copy
from collections import defaultdict
from dataclasses import dataclass

from application.errors import NotFoundError
from domain.entities import AppOrder
from domain.services import evaluate_orders_sequentially
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshotPort


@dataclass(frozen=True)
class DashboardOverviewResult:
    open_orders: list[AppOrder]
    open_orders_count: int
    critical_orders_count: int


class ListOrdersDetailedUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
    ) -> None:
        self._order_repository = order_repository
        self._stock_snapshot_port = stock_snapshot_port

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
        sorted_orders = sorted(
            orders,
            key=lambda order: order.priority_order if order.priority_order is not None else 10**9,
        )
        return _enrich_orders_with_disposition(sorted_orders, self._stock_snapshot_port)


class GetOrderDetailUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
    ) -> None:
        self._order_repository = order_repository
        self._stock_snapshot_port = stock_snapshot_port

    def execute(self, order_id: str) -> AppOrder:
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Auftrag nicht gefunden: {order_id}")
        material = order.material_article_number
        group = self._order_repository.list_by_material(material)
        copies = [copy.deepcopy(o) for o in group]
        snapshot = self._stock_snapshot_port.get_snapshot(material)
        evaluated = evaluate_orders_sequentially(
            copies,
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        for ev in evaluated:
            if ev.order_id == order_id:
                return ev
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


def _enrich_orders_with_disposition(
    orders: list[AppOrder],
    stock_snapshot_port: StockSnapshotPort,
) -> list[AppOrder]:
    """Pro Materialgruppe sequentielle Disposition (Ampel + Verfügbarkeit vor Auftrag), ohne Persistenz."""
    if not orders:
        return []
    by_material: dict[str, list[AppOrder]] = defaultdict(list)
    for o in orders:
        by_material[o.material_article_number].append(o)
    enriched: dict[str, AppOrder] = {}
    for material, group in by_material.items():
        snapshot = stock_snapshot_port.get_snapshot(material)
        copies = [copy.deepcopy(o) for o in group]
        evaluated = evaluate_orders_sequentially(
            copies,
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        for ev in evaluated:
            if ev.order_id:
                enriched[ev.order_id] = ev
    out: list[AppOrder] = []
    for o in orders:
        if o.order_id and o.order_id in enriched:
            out.append(enriched[o.order_id])
        else:
            out.append(o)
    return out
