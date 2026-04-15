"""Material plan availability: ERP simulator plus app-only pipeline (no double count)."""

from __future__ import annotations

from adapters.erp.material_plan_availability_sage_simulator_adapter import SageSimulatorMaterialPlanAvailabilityAdapter
from domain.material_pipeline import app_only_additional_pipeline_mm
from ports.material_plan_availability_port import (
    MaterialPlanAvailabilityPort,
    MaterialPlanAvailabilitySnapshot,
    OpenMaterialOrderDemand,
)
from ports.order_repository_port import OrderRepositoryPort


class AppAwareMaterialPlanAvailabilityAdapter(MaterialPlanAvailabilityPort):
    def __init__(
        self,
        inner: SageSimulatorMaterialPlanAvailabilityAdapter,
        order_repository: OrderRepositoryPort,
    ) -> None:
        self._inner = inner
        self._order_repository = order_repository

    def get_snapshot(self, material_reference: str) -> MaterialPlanAvailabilitySnapshot | None:
        base = self._inner.get_snapshot(material_reference)
        if base is None:
            return None
        orders = self._order_repository.list_by_material(material_reference.strip())
        erp_refs = {o.order_reference for o in base.open_orders}
        app_mm = app_only_additional_pipeline_mm(orders, erp_refs)
        app_additional_m = app_mm / 1000.0
        combined_in_pipeline = round(float(base.in_pipeline_m) + app_additional_m, 3)
        available_m = round(float(base.stock_m) - combined_in_pipeline, 3)
        extra: list[OpenMaterialOrderDemand] = []
        for o in orders:
            if o.status in ("done", "canceled"):
                continue
            ref = (o.erp_order_number or "").strip()
            if ref and ref in erp_refs:
                continue
            extra.append(
                OpenMaterialOrderDemand(
                    order_reference=f"app:{o.order_id}",
                    required_m=round(o.total_demand_mm / 1000.0, 6),
                    status=o.status,
                )
            )
        merged_open = tuple([*base.open_orders, *extra])
        return MaterialPlanAvailabilitySnapshot(
            material_reference=base.material_reference,
            description=base.description,
            stock_m=base.stock_m,
            in_pipeline_m=combined_in_pipeline,
            available_m=available_m,
            open_orders=merged_open,
        )
