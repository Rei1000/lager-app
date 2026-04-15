"""Use case for creating one order."""

from __future__ import annotations

import logging

from application.dtos import CreateOrderCommand
from domain.entities import AppOrder
from domain.services import evaluate_orders_sequentially
from ports.audit_log_port import AuditLogPort
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshotPort

logger = logging.getLogger(__name__)


class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._order_repository = order_repository
        self._stock_snapshot_port = stock_snapshot_port
        self._audit_log_port = audit_log_port

    def execute(self, command: CreateOrderCommand) -> AppOrder:
        existing_orders = self._order_repository.list_by_material(command.material_article_number)
        next_priority = max((o.priority_order or 0 for o in existing_orders), default=0) + 1

        cust = (command.customer_name or "").strip() or None
        new_order = AppOrder(
            order_id=command.order_id,
            material_article_number=command.material_article_number,
            quantity=command.quantity,
            part_length_mm=command.part_length_mm,
            kerf_mm=command.kerf_mm,
            include_rest_stock=command.include_rest_stock,
            priority_order=next_priority,
            created_by_user_id=command.acting_user_id,
            customer_name=cust,
            due_date=command.due_date,
        )

        snapshot = self._stock_snapshot_port.get_snapshot(command.material_article_number)
        evaluated_orders = evaluate_orders_sequentially(
            orders=[*existing_orders, new_order],
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            app_reservations_mm=snapshot.app_reservations_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        for order in evaluated_orders:
            self._order_repository.save(order)

        for order in evaluated_orders:
            if order.order_id == command.order_id:
                if self._audit_log_port is not None:
                    try:
                        self._audit_log_port.log_event(
                            entity_type="order",
                            entity_id=order.order_id,
                            action="created",
                            user_id=command.acting_user_id,
                            payload={
                                "material_article_number": order.material_article_number,
                                "quantity": order.quantity,
                                "priority_order": order.priority_order,
                            },
                        )
                    except Exception:
                        logger.warning(
                            "Audit-Event fuer order created konnte nicht gespeichert werden "
                            "(Auftrag wurde bereits persistiert).",
                            exc_info=True,
                        )
                return order
        raise ValueError("Neuer Auftrag konnte nicht gespeichert werden")
