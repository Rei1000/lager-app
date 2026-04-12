"""Application-facing repository contracts for orders."""

from __future__ import annotations

from typing import Protocol

from domain.entities import AppOrder


class OrderRepositoryPort(Protocol):
    def list_all(self) -> list[AppOrder]:
        """Return all orders."""

    def get_by_id(self, order_id: str) -> AppOrder | None:
        """Return one order by ID or None."""

    def list_by_material(self, material_article_number: str) -> list[AppOrder]:
        """Return all orders of one material."""

    def save(self, order: AppOrder) -> None:
        """Persist one order."""
