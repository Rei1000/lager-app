"""Contracts for ERP material-related calls."""

from __future__ import annotations

from typing import Any, Protocol


class ErpMaterialPort(Protocol):
    def search_materials(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        """Search ERP materials with dynamic criteria."""

    def get_material(self, material_reference: str) -> dict[str, Any]:
        """Get one ERP material by reference."""

    def get_material_stock(self, material_reference: str) -> dict[str, Any]:
        """Get one ERP stock payload for a material reference."""
