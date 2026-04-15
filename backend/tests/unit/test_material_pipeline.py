from __future__ import annotations

from domain.entities import AppOrder
from domain.material_pipeline import app_only_additional_pipeline_mm


def test_app_only_skips_when_erp_reference_matches_simulator() -> None:
    erp_refs = {"SAGE-ORD-2026-001"}
    orders = [
        AppOrder(
            order_id="1",
            material_article_number="420-VA-012",
            quantity=1,
            part_length_mm=1000,
            kerf_mm=0,
            include_rest_stock=False,
            status="checked",
            erp_order_number="SAGE-ORD-2026-001",
        )
    ]
    assert app_only_additional_pipeline_mm(orders, erp_refs) == 0


def test_app_only_counts_unlinked_open_order() -> None:
    orders = [
        AppOrder(
            order_id="x",
            material_article_number="420-VA-012",
            quantity=2,
            part_length_mm=1000,
            kerf_mm=0,
            include_rest_stock=False,
            status="checked",
            erp_order_number=None,
        )
    ]
    assert app_only_additional_pipeline_mm(orders, set()) == 2000


def test_app_only_ignores_done() -> None:
    orders = [
        AppOrder(
            order_id="x",
            material_article_number="420-VA-012",
            quantity=2,
            part_length_mm=1000,
            kerf_mm=0,
            include_rest_stock=False,
            status="done",
            erp_order_number=None,
        )
    ]
    assert app_only_additional_pipeline_mm(orders, set()) == 0
