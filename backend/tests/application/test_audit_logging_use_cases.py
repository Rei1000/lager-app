from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from application.dtos import (
    ChangeErpTransferStatusCommand,
    ChangeStockCorrectionStatusCommand,
    ReserveOrderCommand,
)
from application.use_cases.erp_transfer_use_cases import ApproveErpTransferUseCase
from application.use_cases.inventory_use_cases import ConfirmStockCorrectionUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase
from domain.entities import AppOrder
from ports.audit_log_port import AuditLogPort, AuditLogRecord
from ports.erp_transfer_repository_port import ErpTransferRepositoryPort, ErpTransferRequestRecord
from ports.inventory_repository_port import InventoryRepositoryPort, StockCorrectionRecord
from ports.order_repository_port import OrderRepositoryPort


@dataclass
class FakeAuditLogPort(AuditLogPort):
    events: list[AuditLogRecord] = field(default_factory=list)

    def log_event(
        self,
        *,
        entity_type: str,
        entity_id: str | None,
        action: str,
        user_id: int | None,
        payload: dict[str, object] | None = None,
        comment: str | None = None,
    ) -> AuditLogRecord:
        record = AuditLogRecord(
            id=len(self.events) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            occurred_at=datetime.now(timezone.utc),
            payload=payload,
            comment=comment,
        )
        self.events.append(record)
        return record

    def list_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        return self.events[:limit]


@dataclass
class FakeOrderRepository(OrderRepositoryPort):
    order: AppOrder

    def list_all(self) -> list[AppOrder]:
        return [self.order]

    def get_by_id(self, order_id: str) -> AppOrder | None:
        return self.order if self.order.order_id == order_id else None

    def list_by_material(self, material_article_number: str) -> list[AppOrder]:
        return [self.order]

    def save(self, order: AppOrder) -> None:
        self.order = order


@dataclass
class FakeInventoryRepository(InventoryRepositoryPort):
    correction: StockCorrectionRecord

    def create_inventory_count(self, **kwargs):  # pragma: no cover - unused in this test
        raise NotImplementedError

    def list_inventory_counts(self):  # pragma: no cover - unused in this test
        raise NotImplementedError

    def get_inventory_count(self, inventory_count_id: int):  # pragma: no cover - unused
        raise NotImplementedError

    def create_stock_correction(self, **kwargs):  # pragma: no cover - unused
        raise NotImplementedError

    def get_stock_correction(self, correction_id: int) -> StockCorrectionRecord:
        return self.correction

    def update_stock_correction_status(
        self,
        *,
        correction_id: int,
        status: str,
        acting_user_id: int,
    ) -> StockCorrectionRecord:
        self.correction = StockCorrectionRecord(
            id=self.correction.id,
            inventory_count_id=self.correction.inventory_count_id,
            material_article_number=self.correction.material_article_number,
            correction_mm=self.correction.correction_mm,
            status=status,
            requested_by_user_id=self.correction.requested_by_user_id,
            comment=self.correction.comment,
            created_at=self.correction.created_at,
            confirmed_by_user_id=acting_user_id if status == "confirmed" else None,
            confirmed_at=datetime.now(timezone.utc) if status == "confirmed" else None,
            canceled_by_user_id=acting_user_id if status == "canceled" else None,
            canceled_at=datetime.now(timezone.utc) if status == "canceled" else None,
        )
        return self.correction


@dataclass
class FakeErpTransferRepository(ErpTransferRepositoryPort):
    transfer: ErpTransferRequestRecord

    def create_transfer_request(self, **kwargs):  # pragma: no cover - unused
        raise NotImplementedError

    def list_transfer_requests(self):  # pragma: no cover - unused
        raise NotImplementedError

    def get_transfer_request(self, transfer_id: int) -> ErpTransferRequestRecord:
        return self.transfer

    def update_transfer_status(
        self,
        *,
        transfer_id: int,
        status: str,
        acting_user_id: int,
        failure_reason: str | None = None,
    ) -> ErpTransferRequestRecord:
        self.transfer = ErpTransferRequestRecord(
            id=self.transfer.id,
            order_id=self.transfer.order_id,
            material_article_number=self.transfer.material_article_number,
            status=status,
            requested_by_user_id=self.transfer.requested_by_user_id,
            payload=self.transfer.payload,
            created_at=self.transfer.created_at,
            ready_by_user_id=self.transfer.ready_by_user_id,
            approved_by_user_id=acting_user_id if status == "approved" else self.transfer.approved_by_user_id,
            sent_by_user_id=self.transfer.sent_by_user_id,
            failed_by_user_id=self.transfer.failed_by_user_id,
            ready_at=self.transfer.ready_at,
            approved_at=datetime.now(timezone.utc) if status == "approved" else self.transfer.approved_at,
            sent_at=self.transfer.sent_at,
            failed_at=self.transfer.failed_at,
            failure_reason=failure_reason,
        )
        return self.transfer


def test_reserve_order_writes_audit_event() -> None:
    order = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status="checked",
        priority_order=1,
    )
    audit = FakeAuditLogPort()
    use_case = ReserveOrderUseCase(
        order_repository=FakeOrderRepository(order=order),
        audit_log_port=audit,
    )

    use_case.execute(ReserveOrderCommand(order_id="A1", acting_user_id=7))

    assert audit.events[0].entity_type == "order"
    assert audit.events[0].action == "reserved"
    assert audit.events[0].user_id == 7


def test_confirm_stock_correction_writes_audit_event() -> None:
    now = datetime.now(timezone.utc)
    correction = StockCorrectionRecord(
        id=10,
        inventory_count_id=1,
        material_article_number="ART-001",
        correction_mm=-200,
        status="requested",
        requested_by_user_id=2,
        comment=None,
        created_at=now,
    )
    audit = FakeAuditLogPort()
    use_case = ConfirmStockCorrectionUseCase(
        inventory_repository=FakeInventoryRepository(correction=correction),
        audit_log_port=audit,
    )

    use_case.execute(ChangeStockCorrectionStatusCommand(correction_id=10, acting_user_id=5))

    assert audit.events[0].entity_type == "stock_correction"
    assert audit.events[0].action == "confirmed"
    assert audit.events[0].user_id == 5


def test_approve_erp_transfer_writes_audit_event() -> None:
    now = datetime.now(timezone.utc)
    transfer = ErpTransferRequestRecord(
        id=3,
        order_id="ORD-9",
        material_article_number="ART-009",
        status="ready",
        requested_by_user_id=2,
        payload={"amount_mm": 500},
        created_at=now,
    )
    audit = FakeAuditLogPort()
    use_case = ApproveErpTransferUseCase(
        transfer_repository=FakeErpTransferRepository(transfer=transfer),
        audit_log_port=audit,
    )

    use_case.execute(ChangeErpTransferStatusCommand(transfer_id=3, acting_user_id=4))

    assert audit.events[0].entity_type == "erp_transfer"
    assert audit.events[0].entity_id == "3"
    assert audit.events[0].action == "approved"
