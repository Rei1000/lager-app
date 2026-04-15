"""Maps Sage in-memory simulator availability into the material plan availability port."""

from __future__ import annotations

from adapters.erp.sage_simulator_data import get_material_availability
from ports.material_plan_availability_port import (
    MaterialPlanAvailabilityPort,
    MaterialPlanAvailabilitySnapshot,
    OpenMaterialOrderDemand,
)


class SageSimulatorMaterialPlanAvailabilityAdapter(MaterialPlanAvailabilityPort):
    def get_snapshot(self, material_reference: str) -> MaterialPlanAvailabilitySnapshot | None:
        normalized = material_reference.strip()
        if not normalized:
            return None
        payload = get_material_availability(normalized)
        if payload is None:
            return None
        open_raw = payload.get("open_orders") or []
        open_orders: list[OpenMaterialOrderDemand] = []
        for row in open_raw:
            open_orders.append(
                OpenMaterialOrderDemand(
                    order_reference=str(row["order_no"]),
                    required_m=float(row["required_m"]),
                    status=str(row["status"]),
                )
            )
        return MaterialPlanAvailabilitySnapshot(
            material_reference=str(payload["material_no"]),
            description=str(payload["description"]),
            stock_m=float(payload["stock_m"]),
            in_pipeline_m=float(payload["in_pipeline_m"]),
            available_m=float(payload["available_m"]),
            open_orders=tuple(open_orders),
        )
