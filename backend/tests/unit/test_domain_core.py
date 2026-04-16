from __future__ import annotations

import pytest

from domain.entities import AppOrder, MaterialType, RestStockAccount
from domain.order_plan_cutting import calculate_cutting_plan_demand_mm
from domain.services import (
    calculate_available_mm,
    calculate_traffic_light,
    evaluate_orders_sequentially,
)
from domain.value_objects import TrafficLight


def test_availability_ignores_rest_stock_by_default() -> None:
    available = calculate_available_mm(
        erp_stock_mm=20_000,
        open_erp_orders_mm=5_000,
        app_reservations_mm=4_000,
        rest_stock_mm=3_000,
        include_rest_stock=False,
    )
    assert available == 11_000


def test_availability_includes_rest_stock_only_when_enabled() -> None:
    available = calculate_available_mm(
        erp_stock_mm=20_000,
        open_erp_orders_mm=5_000,
        app_reservations_mm=4_000,
        rest_stock_mm=3_000,
        include_rest_stock=True,
    )
    assert available == 14_000


def test_traffic_light_green_when_full_stock_is_sufficient() -> None:
    light = calculate_traffic_light(
        demand_mm=8_000,
        available_without_rest_mm=9_000,
        available_with_optional_rest_mm=9_000,
        include_rest_stock=False,
    )
    assert light is TrafficLight.GREEN


def test_traffic_light_yellow_when_only_rest_makes_it_possible() -> None:
    light = calculate_traffic_light(
        demand_mm=8_000,
        available_without_rest_mm=7_500,
        available_with_optional_rest_mm=8_500,
        include_rest_stock=True,
    )
    assert light is TrafficLight.YELLOW


def test_traffic_light_red_when_rest_is_not_enabled() -> None:
    light = calculate_traffic_light(
        demand_mm=8_000,
        available_without_rest_mm=7_500,
        available_with_optional_rest_mm=8_500,
        include_rest_stock=False,
    )
    assert light is TrafficLight.RED


def test_traffic_light_boundary_is_green_when_exactly_fulfillable_without_rest() -> None:
    light = calculate_traffic_light(
        demand_mm=8_000,
        available_without_rest_mm=8_000,
        available_with_optional_rest_mm=8_000,
        include_rest_stock=False,
    )
    assert light is TrafficLight.GREEN


def test_traffic_light_boundary_is_yellow_when_exactly_fulfillable_with_rest() -> None:
    light = calculate_traffic_light(
        demand_mm=8_000,
        available_without_rest_mm=7_000,
        available_with_optional_rest_mm=8_000,
        include_rest_stock=True,
    )
    assert light is TrafficLight.YELLOW


def test_entities_hold_domain_data_without_infrastructure() -> None:
    material = MaterialType(
        article_number="ART-001",
        name="Stahlprofil 40x40",
        min_rest_length_mm=300,
    )
    rest_account = RestStockAccount(material_article_number="ART-001", total_rest_stock_mm=1_200)
    order = AppOrder(
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=True,
    )
    assert material.article_number == "ART-001"
    assert rest_account.total_rest_stock_mm == 1_200
    # Brutto = 4×1000 + (4−1)×3 = 4009 (einzige führende Schnittplan-Logik)
    assert order.total_demand_mm == 4_009
    assert order.total_demand_mm == calculate_cutting_plan_demand_mm(4, 1000, 3.0).gross_mm


def test_sequential_evaluation_is_priority_order_based() -> None:
    first = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )

    evaluated = evaluate_orders_sequentially(
        orders=[second, first],
        erp_stock_mm=8_000,
        open_erp_orders_mm=0,
        rest_stock_mm=0,
    )

    assert evaluated[0].priority_order == 1
    assert evaluated[0].traffic_light is TrafficLight.GREEN
    assert evaluated[0].disposition_available_before_mm == 8_000
    assert evaluated[1].traffic_light is TrafficLight.RED
    assert evaluated[1].disposition_available_before_mm == 3_000


def test_sequential_evaluation_no_exception_when_net_stock_negative() -> None:
    """Globale Unterdeckung (ERP-Pipeline > Stückgut) darf keine ValueError auslösen."""
    first = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    evaluated = evaluate_orders_sequentially(
        orders=[first],
        erp_stock_mm=1_000,
        open_erp_orders_mm=5_000,
        rest_stock_mm=0,
    )
    assert evaluated[0].traffic_light is TrafficLight.RED
    assert evaluated[0].disposition_available_before_mm == 0


def test_calculate_traffic_light_negative_available_does_not_raise() -> None:
    assert calculate_traffic_light(500, -2_000, -2_000, False) is TrafficLight.RED


def test_sequential_evaluation_requires_same_material() -> None:
    first = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        material_article_number="ART-002",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )

    with pytest.raises(ValueError):
        evaluate_orders_sequentially(
            orders=[first, second],
            erp_stock_mm=5_000,
            open_erp_orders_mm=0,
            rest_stock_mm=0,
        )


def test_orders_without_priority_are_processed_after_prioritized_orders() -> None:
    prioritized = AppOrder(
        material_article_number="ART-001",
        quantity=3,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    unprioritized = AppOrder(
        material_article_number="ART-001",
        quantity=3,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=None,
    )

    evaluated = evaluate_orders_sequentially(
        orders=[unprioritized, prioritized],
        erp_stock_mm=5_000,
        open_erp_orders_mm=0,
        rest_stock_mm=0,
    )

    assert evaluated[0].priority_order == 1
    assert evaluated[0].traffic_light is TrafficLight.GREEN
    assert evaluated[1].priority_order is None
    assert evaluated[1].traffic_light is TrafficLight.RED


def test_rest_stock_has_no_effect_when_option_is_disabled_for_all_orders() -> None:
    first = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )

    evaluated = evaluate_orders_sequentially(
        orders=[first, second],
        erp_stock_mm=6_000,
        open_erp_orders_mm=0,
        rest_stock_mm=10_000,
    )

    assert evaluated[0].traffic_light is TrafficLight.GREEN
    assert evaluated[1].traffic_light is TrafficLight.RED


def test_material_type_validates_min_rest_length() -> None:
    with pytest.raises(ValueError):
        MaterialType(
            article_number="ART-001",
            name="Stahlprofil 40x40",
            min_rest_length_mm=-1,
        )


def test_rest_stock_account_disallows_negative_total() -> None:
    with pytest.raises(ValueError):
        RestStockAccount(material_article_number="ART-001", total_rest_stock_mm=-1)


def test_app_order_validates_quantity_and_lengths() -> None:
    with pytest.raises(ValueError):
        AppOrder(
            material_article_number="ART-001",
            quantity=0,
            part_length_mm=1000,
            kerf_mm=3,
            include_rest_stock=False,
        )

    with pytest.raises(ValueError):
        AppOrder(
            material_article_number="ART-001",
            quantity=1,
            part_length_mm=0,
            kerf_mm=3,
            include_rest_stock=False,
        )

    with pytest.raises(ValueError):
        AppOrder(
            material_article_number="ART-001",
            quantity=1,
            part_length_mm=1000,
            kerf_mm=-1,
            include_rest_stock=False,
        )


def test_domain_services_disallow_negative_stock_inputs() -> None:
    with pytest.raises(ValueError):
        calculate_available_mm(
            erp_stock_mm=-1,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
            include_rest_stock=False,
        )


def test_sequential_evaluation_consumes_rest_stock_for_following_orders() -> None:
    first = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=True,
        priority_order=1,
    )
    second = AppOrder(
        material_article_number="ART-001",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=True,
        priority_order=2,
    )

    evaluated = evaluate_orders_sequentially(
        orders=[first, second],
        erp_stock_mm=3_000,
        open_erp_orders_mm=0,
        rest_stock_mm=6_000,
    )

    assert evaluated[0].traffic_light is TrafficLight.YELLOW
    assert evaluated[1].traffic_light is TrafficLight.RED
