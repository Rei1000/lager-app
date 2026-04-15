from __future__ import annotations

from unittest.mock import MagicMock

from adapters.erp.app_aware_material_plan_availability_adapter import AppAwareMaterialPlanAvailabilityAdapter
from adapters.erp.material_plan_availability_sage_simulator_adapter import SageSimulatorMaterialPlanAvailabilityAdapter
from domain.entities import AppOrder
from ports.material_plan_availability_port import MaterialPlanAvailabilitySnapshot, OpenMaterialOrderDemand


def test_app_aware_adds_pipeline_for_app_only_orders() -> None:
    inner = MagicMock(spec=SageSimulatorMaterialPlanAvailabilityAdapter)
    inner.get_snapshot.return_value = MaterialPlanAvailabilitySnapshot(
        material_reference="M1",
        description="d",
        stock_m=100.0,
        in_pipeline_m=10.0,
        available_m=90.0,
        open_orders=(
            OpenMaterialOrderDemand(order_reference="ERP-1", required_m=10.0, status="open"),
        ),
    )
    repo = MagicMock()
    repo.list_by_material.return_value = [
        AppOrder(
            order_id="app-1",
            material_article_number="M1",
            quantity=1,
            part_length_mm=2000,
            kerf_mm=0,
            include_rest_stock=False,
            status="checked",
            erp_order_number=None,
        )
    ]
    adapter = AppAwareMaterialPlanAvailabilityAdapter(inner=inner, order_repository=repo)
    snap = adapter.get_snapshot("M1")
    assert snap is not None
    assert snap.in_pipeline_m == 12.0
    assert snap.available_m == 88.0
    assert any(o.order_reference.startswith("app:") for o in snap.open_orders)
