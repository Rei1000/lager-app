from __future__ import annotations

from adapters.erp.sage_simulator_data import (
    get_material_availability,
    SIMULATOR_MATERIALS,
    SIMULATOR_OPEN_ORDERS,
    SIMULATOR_USERS,
    get_material_stock,
    get_order,
    list_open_orders,
    list_orders_by_material,
)


def test_simulator_seed_contains_expected_baseline_data() -> None:
    assert len(SIMULATOR_USERS) == 3
    assert len(SIMULATOR_MATERIALS) == 30
    assert len(SIMULATOR_OPEN_ORDERS) >= 5


def test_simulator_users_have_distinct_references() -> None:
    references = {user.erp_user_reference for user in SIMULATOR_USERS}
    assert references == {
        "ERP-SAGE-USER-ADMIN-001",
        "ERP-SAGE-USER-LEITUNG-001",
        "ERP-SAGE-USER-LAGER-001",
    }


def test_simulator_material_stock_and_order_lookup_work() -> None:
    stock = get_material_stock("100-FE-010")
    assert stock is not None
    assert stock["stock_m"] > 0
    assert stock["description"] == "Stangenmaterial Stahl 10 mm"

    order = get_order("SAGE-ORD-2026-001")
    assert order is not None
    assert order["material_no"] == "420-VA-012"

    material_orders = list_orders_by_material("100-FE-025")
    assert material_orders


def test_simulator_open_orders_and_availability_work() -> None:
    open_orders = list_open_orders()
    assert len(open_orders) == 5
    assert all(order["required_m"] > 0 for order in open_orders)

    availability = get_material_availability("420-VA-012")
    assert availability is not None
    assert availability["stock_m"] == 93.0
    assert availability["in_pipeline_m"] == 37.2
    assert availability["available_m"] == 55.8
    assert len(availability["open_orders"]) == 2
