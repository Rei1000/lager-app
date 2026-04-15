"""Application tests for PreviewOrderPlanUseCase (fakes, no DB/simulator)."""

from __future__ import annotations

import pytest

from application.dtos import PreviewOrderPlanCommand
from application.errors import NotFoundError
from application.use_cases.preview_order_plan_use_case import PreviewOrderPlanUseCase
from ports.material_lookup_port import MaterialLookupRecord, MaterialLookupPort
from ports.material_plan_availability_port import (
    MaterialPlanAvailabilityPort,
    MaterialPlanAvailabilitySnapshot,
    OpenMaterialOrderDemand,
)


class FakeMaterialLookup(MaterialLookupPort):
    def __init__(self, record: MaterialLookupRecord | None) -> None:
        self._record = record

    def search_materials(self, query: str) -> list[MaterialLookupRecord]:
        raise NotImplementedError

    def get_by_article_number(self, article_number: str) -> MaterialLookupRecord:
        if self._record is None:
            raise NotFoundError("missing")
        return self._record


class FakeAvailability(MaterialPlanAvailabilityPort):
    def __init__(self, snapshot: MaterialPlanAvailabilitySnapshot | None) -> None:
        self._snapshot = snapshot

    def get_snapshot(self, material_reference: str) -> MaterialPlanAvailabilitySnapshot | None:
        return self._snapshot


def _snapshot(available_m: float) -> MaterialPlanAvailabilitySnapshot:
    return MaterialPlanAvailabilitySnapshot(
        material_reference="ART-1",
        description="Test",
        stock_m=100.0,
        in_pipeline_m=10.0,
        available_m=available_m,
        open_orders=(
            OpenMaterialOrderDemand(order_reference="ORD-1", required_m=5.0, status="open"),
        ),
    )


def test_preview_computes_demand_and_feasible_when_stock_sufficient() -> None:
    material = MaterialLookupRecord(
        article_number="ART-1",
        name="Profil",
        profile=None,
        erp_stock_m=100.0,
        rest_stock_m=None,
    )
    use_case = PreviewOrderPlanUseCase(
        material_lookup_port=FakeMaterialLookup(material),
        material_plan_availability_port=FakeAvailability(_snapshot(available_m=50.0)),
    )
    result = use_case.execute(
        PreviewOrderPlanCommand(
            article_number="ART-1",
            quantity=2,
            part_length_mm=1000,
            kerf_mm=2,
            rest_piece_consideration_requested=False,
        )
    )
    assert result.net_required_mm == 2000
    assert result.kerf_total_mm == 2
    assert result.gross_required_mm == 2002
    assert result.gross_required_m == pytest.approx(2.002)
    assert result.feasible is True
    assert result.open_orders[0].order_reference == "ORD-1"


def test_preview_not_feasible_when_demand_exceeds_available() -> None:
    material = MaterialLookupRecord(
        article_number="ART-1",
        name="Profil",
        profile=None,
        erp_stock_m=100.0,
        rest_stock_m=None,
    )
    use_case = PreviewOrderPlanUseCase(
        material_lookup_port=FakeMaterialLookup(material),
        material_plan_availability_port=FakeAvailability(_snapshot(available_m=1.0)),
    )
    result = use_case.execute(
        PreviewOrderPlanCommand(
            article_number="ART-1",
            quantity=10,
            part_length_mm=1000,
            kerf_mm=0,
            rest_piece_consideration_requested=False,
        )
    )
    assert result.gross_required_m == pytest.approx(10.0)
    assert result.feasible is False


def test_availability_none_raises_not_found() -> None:
    material = MaterialLookupRecord(
        article_number="ART-1",
        name="Profil",
        profile=None,
        erp_stock_m=100.0,
        rest_stock_m=None,
    )
    use_case = PreviewOrderPlanUseCase(
        material_lookup_port=FakeMaterialLookup(material),
        material_plan_availability_port=FakeAvailability(None),
    )
    with pytest.raises(NotFoundError):
        use_case.execute(
            PreviewOrderPlanCommand(
                article_number="ART-1",
                quantity=1,
                part_length_mm=1000,
                kerf_mm=0,
                rest_piece_consideration_requested=False,
            )
        )
