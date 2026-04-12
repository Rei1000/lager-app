"""Stock snapshot contract for application orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StockSnapshot:
    erp_stock_mm: int
    open_erp_orders_mm: int
    app_reservations_mm: int
    rest_stock_mm: int


class StockSnapshotPort(Protocol):
    def get_snapshot(self, material_article_number: str) -> StockSnapshot:
        """Return stock inputs for one material."""
