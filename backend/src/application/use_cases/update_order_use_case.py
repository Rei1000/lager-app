"""Use case for updating editable fields on an existing app order."""

from __future__ import annotations

import logging

from application.dtos import RecalculateOrdersCommand, UpdateOrderCommand
from application.errors import NotFoundError
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from domain.entities import AppOrder
from ports.audit_log_port import AuditLogPort
from ports.order_repository_port import OrderRepositoryPort

logger = logging.getLogger(__name__)


class UpdateOrderUseCase:
    """Persistiert geaenderte Schnitt-/Stueckdaten und loest Recalculate fuer das Material aus."""

    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        recalculate_orders_use_case: RecalculateOrdersUseCase,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._order_repository = order_repository
        self._recalculate_orders_use_case = recalculate_orders_use_case
        self._audit_log_port = audit_log_port

    def execute(self, command: UpdateOrderCommand) -> AppOrder:
        order = self._order_repository.get_by_id(command.order_id)
        if order is None:
            raise NotFoundError(f"Auftrag nicht gefunden: {command.order_id}")

        if order.status in {"done", "canceled"}:
            raise ValueError("Abgeschlossene oder stornierte Auftraege koennen nicht bearbeitet werden")

        if command.quantity <= 0:
            raise ValueError("quantity muss groesser als 0 sein")
        if command.part_length_mm <= 0:
            raise ValueError("part_length_mm muss groesser als 0 sein")
        if command.kerf_mm < 0:
            raise ValueError("kerf_mm darf nicht negativ sein")

        cust = (command.customer_name or "").strip() or None
        if cust is not None and len(cust) > 255:
            raise ValueError("customer_name ist zu lang")

        order.quantity = command.quantity
        order.part_length_mm = command.part_length_mm
        order.kerf_mm = command.kerf_mm
        order.customer_name = cust
        order.due_date = command.due_date

        self._order_repository.save(order)

        evaluated = self._recalculate_orders_use_case.execute(
            RecalculateOrdersCommand(material_article_number=order.material_article_number)
        )
        for ev in evaluated:
            if ev.order_id == command.order_id:
                if self._audit_log_port is not None:
                    try:
                        self._audit_log_port.log_event(
                            entity_type="order",
                            entity_id=command.order_id,
                            action="updated",
                            user_id=command.acting_user_id,
                            payload={
                                "quantity": command.quantity,
                                "part_length_mm": command.part_length_mm,
                                "kerf_mm": command.kerf_mm,
                            },
                        )
                    except Exception:
                        logger.warning(
                            "Audit-Event fuer order updated konnte nicht gespeichert werden "
                            "(Auftrag wurde bereits aktualisiert).",
                            exc_info=True,
                        )
                return ev

        raise ValueError("Aktualisierter Auftrag konnte nach Neuberechnung nicht ermittelt werden")
