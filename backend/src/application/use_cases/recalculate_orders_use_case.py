"""Use case for recalculating one material order sequence."""

from __future__ import annotations

from application.dtos import RecalculateOrdersCommand
from domain.entities import AppOrder
from domain.services import evaluate_orders_sequentially
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshotPort


class RecalculateOrdersUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
    ) -> None:
        self._order_repository = order_repository
        self._stock_snapshot_port = stock_snapshot_port

    def execute(self, command: RecalculateOrdersCommand) -> list[AppOrder]:
        orders = self._order_repository.list_by_material(command.material_article_number)
        snapshot = self._stock_snapshot_port.get_snapshot(command.material_article_number)
        evaluated = evaluate_orders_sequentially(
            orders=orders,
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            app_reservations_mm=snapshot.app_reservations_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        for order in evaluated:
            self._order_repository.save(order)
        return evaluated
