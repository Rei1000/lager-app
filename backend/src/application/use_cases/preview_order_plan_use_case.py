"""Preview order material demand against ERP/simulator availability (read-only)."""

from __future__ import annotations

from application.dtos import (
    OrderPlanOpenOrderLine,
    OrderPlanPreviewResult,
    PreviewOrderPlanCommand,
)
from application.errors import NotFoundError
from domain.order_plan_cutting import calculate_cutting_plan_demand_mm, is_cutting_plan_feasible
from ports.material_lookup_port import MaterialLookupPort
from ports.material_plan_availability_port import MaterialPlanAvailabilityPort


class PreviewOrderPlanUseCase:
    def __init__(
        self,
        material_lookup_port: MaterialLookupPort,
        material_plan_availability_port: MaterialPlanAvailabilityPort,
    ) -> None:
        self._material_lookup_port = material_lookup_port
        self._availability_port = material_plan_availability_port

    def execute(self, command: PreviewOrderPlanCommand) -> OrderPlanPreviewResult:
        article = command.article_number.strip()
        if not article:
            raise ValueError("article_number darf nicht leer sein")

        material = self._material_lookup_port.get_by_article_number(article)
        canonical = material.article_number.strip()

        demand = calculate_cutting_plan_demand_mm(
            quantity=command.quantity,
            part_length_mm=command.part_length_mm,
            kerf_mm=command.kerf_mm,
        )

        snapshot = self._availability_port.get_snapshot(canonical)
        if snapshot is None:
            raise NotFoundError(f"Verfuegbarkeit nicht ermittelbar: {canonical}")

        gross_m = demand.gross_mm / 1000.0
        net_m = demand.net_mm / 1000.0
        kerf_m = demand.kerf_waste_mm / 1000.0

        feasible = is_cutting_plan_feasible(gross_m=gross_m, available_m=snapshot.available_m)

        open_lines = tuple(
            OrderPlanOpenOrderLine(
                order_reference=o.order_reference,
                required_m=o.required_m,
                status=o.status,
            )
            for o in snapshot.open_orders
        )

        return OrderPlanPreviewResult(
            article_number=canonical,
            material_name=material.name,
            stock_m=snapshot.stock_m,
            in_pipeline_m=snapshot.in_pipeline_m,
            available_m=snapshot.available_m,
            open_orders=open_lines,
            net_required_mm=demand.net_mm,
            kerf_total_mm=demand.kerf_waste_mm,
            gross_required_mm=demand.gross_mm,
            net_required_m=round(net_m, 6),
            kerf_total_m=round(kerf_m, 6),
            gross_required_m=round(gross_m, 6),
            feasible=feasible,
        )
