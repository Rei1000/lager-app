"""Read model for material availability used in order plan preview (ERP/simulator-backed)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OpenMaterialOrderDemand:
    order_reference: str
    required_m: float
    status: str


@dataclass(frozen=True)
class MaterialPlanAvailabilitySnapshot:
    material_reference: str
    description: str
    stock_m: float
    in_pipeline_m: float
    available_m: float
    open_orders: tuple[OpenMaterialOrderDemand, ...]


class MaterialPlanAvailabilityPort(Protocol):
    def get_snapshot(self, material_reference: str) -> MaterialPlanAvailabilitySnapshot | None:
        """Return availability snapshot for the material, or None if unknown."""
