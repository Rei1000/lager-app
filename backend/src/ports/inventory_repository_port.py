"""Repository contracts for inventory counts and stock corrections."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class InventoryCountRecord:
    id: int
    material_article_number: str
    counted_stock_mm: int
    reference_stock_mm: int
    difference_mm: int
    difference_type: str
    status: str
    counted_by_user_id: int
    comment: str | None
    created_at: datetime


@dataclass(frozen=True)
class StockCorrectionRecord:
    id: int
    inventory_count_id: int
    material_article_number: str
    correction_mm: int
    status: str
    requested_by_user_id: int
    comment: str | None
    created_at: datetime
    confirmed_by_user_id: int | None = None
    confirmed_at: datetime | None = None
    canceled_by_user_id: int | None = None
    canceled_at: datetime | None = None


class InventoryRepositoryPort(Protocol):
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
        """Persist one inventory count."""

    def list_inventory_counts(self) -> list[InventoryCountRecord]:
        """Return all inventory counts."""

    def get_inventory_count(self, inventory_count_id: int) -> InventoryCountRecord:
        """Return one inventory count."""

    def create_stock_correction(
        self,
        *,
        inventory_count_id: int,
        material_article_number: str,
        correction_mm: int,
        requested_by_user_id: int,
        comment: str | None,
    ) -> StockCorrectionRecord:
        """Persist one stock correction request."""

    def get_stock_correction(self, correction_id: int) -> StockCorrectionRecord:
        """Return one stock correction."""

    def update_stock_correction_status(
        self,
        *,
        correction_id: int,
        status: str,
        acting_user_id: int,
    ) -> StockCorrectionRecord:
        """Update one stock correction status."""
