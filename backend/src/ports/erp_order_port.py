"""Contracts for ERP order-related calls."""

from __future__ import annotations

from typing import Any, Protocol


class ErpOrderPort(Protocol):
    def list_orders_by_material(self, material_reference: str) -> list[dict[str, Any]]:
        """Return ERP orders for one material reference."""

    def validate_order_reference(self, order_reference: str) -> bool:
        """Validate if one ERP order reference exists."""
