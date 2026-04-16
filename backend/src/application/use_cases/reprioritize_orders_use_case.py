"""Use case for reordering one material order sequence."""

from __future__ import annotations

import logging

from application.dtos import ReprioritizeOrdersCommand
from domain.entities import AppOrder
from domain.services import evaluate_orders_sequentially
from ports.audit_log_port import AuditLogPort
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshotPort

logger = logging.getLogger(__name__)


class ReprioritizeOrdersUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._order_repository = order_repository
        self._stock_snapshot_port = stock_snapshot_port
        self._audit_log_port = audit_log_port

    def execute(self, command: ReprioritizeOrdersCommand) -> list[AppOrder]:
        orders = self._order_repository.list_by_material(command.material_article_number)
        order_by_id = {order.order_id: order for order in orders}

        current_ids = {order.order_id for order in orders}
        target_ids = set(command.ordered_ids)
        if current_ids != target_ids:
            raise ValueError("Repriorisierung erfordert vollstaendige ID-Liste je Material")

        for index, order_id in enumerate(command.ordered_ids, start=1):
            order = order_by_id[order_id]
            order.priority_order = index

        snapshot = self._stock_snapshot_port.get_snapshot(command.material_article_number)
        evaluated = evaluate_orders_sequentially(
            orders=orders,
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        for order in evaluated:
            self._order_repository.save(order)
        if self._audit_log_port is not None:
            try:
                self._audit_log_port.log_event(
                    entity_type="order",
                    entity_id=command.material_article_number,
                    action="reprioritized",
                    user_id=command.acting_user_id,
                    payload={"ordered_ids": command.ordered_ids},
                )
            except Exception:
                logger.warning(
                    "Audit-Event fuer order reprioritized konnte nicht gespeichert werden "
                    "(Reihung wurde bereits persistiert).",
                    exc_info=True,
                )
        return evaluated
