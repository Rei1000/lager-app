"""Use case for reserving one order in app status model."""

from __future__ import annotations

from application.dtos import ReserveOrderCommand
from application.errors import NotFoundError
from domain.entities import AppOrder
from ports.audit_log_port import AuditLogPort
from ports.order_repository_port import OrderRepositoryPort


class ReserveOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._order_repository = order_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ReserveOrderCommand) -> AppOrder:
        order = self._order_repository.get_by_id(command.order_id)
        if order is None:
            raise NotFoundError(f"Auftrag nicht gefunden: {command.order_id}")

        order.transition_to("reserved")
        self._order_repository.save(order)
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="order",
                entity_id=order.order_id,
                action="reserved",
                user_id=command.acting_user_id,
                payload={"status": order.status},
            )
        return order
