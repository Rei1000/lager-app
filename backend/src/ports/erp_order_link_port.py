"""Contract for ERP order reference checks."""

from __future__ import annotations

from typing import Protocol


class ErpOrderLinkPort(Protocol):
    def exists_order_reference(self, erp_order_number: str) -> bool:
        """Check if ERP order reference exists."""
