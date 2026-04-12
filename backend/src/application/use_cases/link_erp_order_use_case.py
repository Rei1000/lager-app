"""Use case for linking one app order to ERP reference."""

from __future__ import annotations

from application.dtos import LinkErpOrderCommand
from application.errors import NotFoundError
from domain.entities import AppOrder
from ports.audit_log_port import AuditLogPort
from ports.erp_order_link_port import ErpOrderLinkPort
from ports.order_repository_port import OrderRepositoryPort


class LinkErpOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        erp_order_link_port: ErpOrderLinkPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._order_repository = order_repository
        self._erp_order_link_port = erp_order_link_port
        self._audit_log_port = audit_log_port

    def execute(self, command: LinkErpOrderCommand) -> AppOrder:
        order = self._order_repository.get_by_id(command.order_id)
        if order is None:
            raise NotFoundError(f"Auftrag nicht gefunden: {command.order_id}")
        if not command.erp_order_number.strip():
            raise ValueError("erp_order_number darf nicht leer sein")
        if not self._erp_order_link_port.exists_order_reference(command.erp_order_number):
            raise NotFoundError(f"ERP-Auftrag nicht gefunden: {command.erp_order_number}")

        order.erp_order_number = command.erp_order_number
        order.transition_to("linked")
        self._order_repository.save(order)
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="order",
                entity_id=order.order_id,
                action="erp_linked",
                user_id=command.acting_user_id,
                payload={"erp_order_number": order.erp_order_number},
            )
        return order
