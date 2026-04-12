from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from application.dtos import (
    ChangeStockCorrectionStatusCommand,
    CompareInventoryToReferenceCommand,
    CreateInventoryCountCommand,
    CreateStockCorrectionCommand,
)
from application.use_cases.inventory_use_cases import (
    CancelStockCorrectionUseCase,
    CompareInventoryToReferenceUseCase,
    ConfirmStockCorrectionUseCase,
    CreateInventoryCountUseCase,
    CreateStockCorrectionUseCase,
    ListInventoryCountsUseCase,
)
from ports.inventory_repository_port import (
    InventoryCountRecord,
    InventoryRepositoryPort,
    StockCorrectionRecord,
)
from ports.stock_snapshot_port import StockSnapshot, StockSnapshotPort


@dataclass
class FakeStockSnapshotPort(StockSnapshotPort):
    snapshot: StockSnapshot

    def get_snapshot(self, material_article_number: str) -> StockSnapshot:
        return self.snapshot


@dataclass
class FakeInventoryRepository(InventoryRepositoryPort):
    counts: list[InventoryCountRecord] = field(default_factory=list)
    corrections: list[StockCorrectionRecord] = field(default_factory=list)

    def create_inventory_count(
        self,
        *,
        material_article_number: str,
        counted_stock_mm: int,
        reference_stock_mm: int,
        difference_mm: int,
        difference_type: str,
        counted_by_user_id: int,
        comment: str | None,
    ) -> InventoryCountRecord:
        record = InventoryCountRecord(
            id=len(self.counts) + 1,
            material_article_number=material_article_number,
            counted_stock_mm=counted_stock_mm,
            reference_stock_mm=reference_stock_mm,
            difference_mm=difference_mm,
            difference_type=difference_type,
            status="recorded",
            counted_by_user_id=counted_by_user_id,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        self.counts.append(record)
        return record

    def list_inventory_counts(self) -> list[InventoryCountRecord]:
        return self.counts

    def get_inventory_count(self, inventory_count_id: int) -> InventoryCountRecord:
        for count in self.counts:
            if count.id == inventory_count_id:
                return count
        raise ValueError("Inventurzaehlung nicht gefunden")

    def create_stock_correction(
        self,
        *,
        inventory_count_id: int,
        material_article_number: str,
        correction_mm: int,
        requested_by_user_id: int,
        comment: str | None,
    ) -> StockCorrectionRecord:
        correction = StockCorrectionRecord(
            id=len(self.corrections) + 1,
            inventory_count_id=inventory_count_id,
            material_article_number=material_article_number,
            correction_mm=correction_mm,
            status="requested",
            requested_by_user_id=requested_by_user_id,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        self.corrections.append(correction)
        return correction

    def get_stock_correction(self, correction_id: int) -> StockCorrectionRecord:
        for correction in self.corrections:
            if correction.id == correction_id:
                return correction
        raise ValueError("Korrekturvorgang nicht gefunden")

    def update_stock_correction_status(
        self,
        *,
        correction_id: int,
        status: str,
        acting_user_id: int,
    ) -> StockCorrectionRecord:
        current = self.get_stock_correction(correction_id)
        updated = StockCorrectionRecord(
            id=current.id,
            inventory_count_id=current.inventory_count_id,
            material_article_number=current.material_article_number,
            correction_mm=current.correction_mm,
            status=status,
            requested_by_user_id=current.requested_by_user_id,
            comment=current.comment,
            created_at=current.created_at,
            confirmed_by_user_id=acting_user_id if status == "confirmed" else None,
            confirmed_at=datetime.now(timezone.utc) if status == "confirmed" else None,
            canceled_by_user_id=acting_user_id if status == "canceled" else None,
            canceled_at=datetime.now(timezone.utc) if status == "canceled" else None,
        )
        idx = self.corrections.index(current)
        self.corrections[idx] = updated
        return updated


def test_create_inventory_count_use_case_persists_difference() -> None:
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=12_000,
            open_erp_orders_mm=1_000,
            app_reservations_mm=500,
            rest_stock_mm=2_000,
        )
    )
    repo = FakeInventoryRepository()
    use_case = CreateInventoryCountUseCase(inventory_repository=repo, stock_snapshot_port=stock)

    created = use_case.execute(
        CreateInventoryCountCommand(
            material_article_number="ART-001",
            counted_stock_mm=11_000,
            counted_by_user_id=1,
            comment="zaehlung schicht A",
        )
    )

    assert created.reference_stock_mm == 12_500
    assert created.difference_mm == -1_500
    assert created.difference_type == "deficit"


def test_list_inventory_counts_use_case_returns_records() -> None:
    repo = FakeInventoryRepository(
        counts=[
            InventoryCountRecord(
                id=1,
                material_article_number="ART-001",
                counted_stock_mm=1_000,
                reference_stock_mm=1_000,
                difference_mm=0,
                difference_type="equal",
                status="recorded",
                counted_by_user_id=1,
                comment=None,
                created_at=datetime.now(timezone.utc),
            )
        ]
    )
    use_case = ListInventoryCountsUseCase(inventory_repository=repo)

    result = use_case.execute()

    assert len(result) == 1
    assert result[0].material_article_number == "ART-001"


def test_compare_inventory_to_reference_use_case_returns_difference() -> None:
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=10_000,
            open_erp_orders_mm=0,
            app_reservations_mm=500,
            rest_stock_mm=500,
        )
    )
    use_case = CompareInventoryToReferenceUseCase(stock_snapshot_port=stock)

    difference = use_case.execute(
        CompareInventoryToReferenceCommand(material_article_number="ART-001", counted_stock_mm=9_000)
    )

    assert difference.reference_stock_mm == 10_000
    assert difference.difference_mm == -1_000


def test_create_confirm_and_cancel_stock_correction_use_cases() -> None:
    repo = FakeInventoryRepository(
        counts=[
            InventoryCountRecord(
                id=1,
                material_article_number="ART-001",
                counted_stock_mm=9_000,
                reference_stock_mm=10_000,
                difference_mm=-1_000,
                difference_type="deficit",
                status="recorded",
                counted_by_user_id=1,
                comment=None,
                created_at=datetime.now(timezone.utc),
            )
        ]
    )
    create_use_case = CreateStockCorrectionUseCase(inventory_repository=repo)
    confirm_use_case = ConfirmStockCorrectionUseCase(inventory_repository=repo)
    cancel_use_case = CancelStockCorrectionUseCase(inventory_repository=repo)

    created = create_use_case.execute(
        CreateStockCorrectionCommand(
            inventory_count_id=1,
            requested_by_user_id=2,
            comment="pruefen",
        )
    )
    confirmed = confirm_use_case.execute(
        ChangeStockCorrectionStatusCommand(correction_id=created.id, acting_user_id=3)
    )
    canceled = cancel_use_case.execute(
        ChangeStockCorrectionStatusCommand(correction_id=created.id, acting_user_id=4)
    )

    assert created.status == "requested"
    assert confirmed.status == "confirmed"
    assert canceled.status == "canceled"
