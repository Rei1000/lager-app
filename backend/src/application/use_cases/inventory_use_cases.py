"""Use cases for inventory counts and stock corrections."""

from __future__ import annotations

from application.dtos import (
    ChangeStockCorrectionStatusCommand,
    CompareInventoryToReferenceCommand,
    CreateInventoryCountCommand,
    CreateStockCorrectionCommand,
)
from domain.entities import InventoryCount, InventoryDifference, StockCorrectionRequest
from ports.audit_log_port import AuditLogPort
from ports.inventory_repository_port import (
    InventoryCountRecord,
    InventoryRepositoryPort,
    StockCorrectionRecord,
)
from ports.stock_snapshot_port import StockSnapshotPort


def _reference_stock_mm_from_snapshot(
    *,
    erp_stock_mm: int,
    open_erp_orders_mm: int,
    app_reservations_mm: int,
    rest_stock_mm: int,
) -> int:
    reference = erp_stock_mm - open_erp_orders_mm - app_reservations_mm + rest_stock_mm
    return max(reference, 0)


class CompareInventoryToReferenceUseCase:
    def __init__(self, stock_snapshot_port: StockSnapshotPort) -> None:
        self._stock_snapshot_port = stock_snapshot_port

    def execute(self, command: CompareInventoryToReferenceCommand) -> InventoryDifference:
        snapshot = self._stock_snapshot_port.get_snapshot(command.material_article_number)
        reference_stock_mm = _reference_stock_mm_from_snapshot(
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            app_reservations_mm=snapshot.app_reservations_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        return InventoryDifference(
            material_article_number=command.material_article_number,
            counted_stock_mm=command.counted_stock_mm,
            reference_stock_mm=reference_stock_mm,
        )


class CreateInventoryCountUseCase:
    def __init__(
        self,
        inventory_repository: InventoryRepositoryPort,
        stock_snapshot_port: StockSnapshotPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._inventory_repository = inventory_repository
        self._stock_snapshot_port = stock_snapshot_port
        self._audit_log_port = audit_log_port

    def execute(self, command: CreateInventoryCountCommand) -> InventoryCountRecord:
        snapshot = self._stock_snapshot_port.get_snapshot(command.material_article_number)
        reference_stock_mm = _reference_stock_mm_from_snapshot(
            erp_stock_mm=snapshot.erp_stock_mm,
            open_erp_orders_mm=snapshot.open_erp_orders_mm,
            app_reservations_mm=snapshot.app_reservations_mm,
            rest_stock_mm=snapshot.rest_stock_mm,
        )
        count = InventoryCount(
            material_article_number=command.material_article_number,
            counted_stock_mm=command.counted_stock_mm,
            reference_stock_mm=reference_stock_mm,
            counted_by_user_id=command.counted_by_user_id,
            comment=command.comment,
        )
        created = self._inventory_repository.create_inventory_count(
            material_article_number=count.material_article_number,
            counted_stock_mm=count.counted_stock_mm,
            reference_stock_mm=count.reference_stock_mm,
            difference_mm=count.difference_mm,
            difference_type=count.difference_type,
            counted_by_user_id=count.counted_by_user_id,
            comment=count.comment,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="inventory_count",
                entity_id=str(created.id),
                action="created",
                user_id=count.counted_by_user_id,
                payload={
                    "material_article_number": created.material_article_number,
                    "difference_type": created.difference_type,
                },
            )
        return created


class ListInventoryCountsUseCase:
    def __init__(self, inventory_repository: InventoryRepositoryPort) -> None:
        self._inventory_repository = inventory_repository

    def execute(self) -> list[InventoryCountRecord]:
        return self._inventory_repository.list_inventory_counts()


class CreateStockCorrectionUseCase:
    def __init__(
        self,
        inventory_repository: InventoryRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._inventory_repository = inventory_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: CreateStockCorrectionCommand) -> StockCorrectionRecord:
        inventory_count = self._inventory_repository.get_inventory_count(command.inventory_count_id)
        correction = StockCorrectionRequest(
            inventory_count_id=inventory_count.id,
            material_article_number=inventory_count.material_article_number,
            correction_mm=inventory_count.difference_mm,
            requested_by_user_id=command.requested_by_user_id,
            comment=command.comment,
        )
        created = self._inventory_repository.create_stock_correction(
            inventory_count_id=correction.inventory_count_id,
            material_article_number=correction.material_article_number,
            correction_mm=correction.correction_mm,
            requested_by_user_id=correction.requested_by_user_id,
            comment=correction.comment,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="stock_correction",
                entity_id=str(created.id),
                action="created",
                user_id=correction.requested_by_user_id,
                payload={
                    "inventory_count_id": created.inventory_count_id,
                    "correction_mm": created.correction_mm,
                },
            )
        return created


class ConfirmStockCorrectionUseCase:
    def __init__(
        self,
        inventory_repository: InventoryRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._inventory_repository = inventory_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeStockCorrectionStatusCommand) -> StockCorrectionRecord:
        updated = self._inventory_repository.update_stock_correction_status(
            correction_id=command.correction_id,
            status="confirmed",
            acting_user_id=command.acting_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="stock_correction",
                entity_id=str(updated.id),
                action="confirmed",
                user_id=command.acting_user_id,
            )
        return updated


class CancelStockCorrectionUseCase:
    def __init__(
        self,
        inventory_repository: InventoryRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._inventory_repository = inventory_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeStockCorrectionStatusCommand) -> StockCorrectionRecord:
        updated = self._inventory_repository.update_stock_correction_status(
            correction_id=command.correction_id,
            status="canceled",
            acting_user_id=command.acting_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="stock_correction",
                entity_id=str(updated.id),
                action="canceled",
                user_id=command.acting_user_id,
            )
        return updated
