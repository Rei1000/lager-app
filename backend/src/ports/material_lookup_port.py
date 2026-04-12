"""Port for material lookup used by scan/search flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MaterialLookupRecord:
    article_number: str
    name: str
    profile: str | None
    erp_stock_m: float | None
    rest_stock_m: float | None


class MaterialLookupPort(Protocol):
    def search_materials(self, query: str) -> list[MaterialLookupRecord]:
        """Search materials by article number or name."""

    def get_by_article_number(self, article_number: str) -> MaterialLookupRecord:
        """Return one material by article number."""
