from __future__ import annotations

from adapters.erp.sage_simulator_data import (
    SIMULATOR_MATERIALS,
    SIMULATOR_OPEN_ORDERS,
    SIMULATOR_USERS,
    get_material_stock,
    get_order,
    list_orders_by_material,
)


def test_simulator_seed_contains_expected_baseline_data() -> None:
    assert len(SIMULATOR_USERS) == 3
    assert len(SIMULATOR_MATERIALS) >= 10
    assert len(SIMULATOR_OPEN_ORDERS) >= 5


def test_simulator_users_have_distinct_references() -> None:
    references = {user.erp_user_reference for user in SIMULATOR_USERS}
    assert references == {"sage_admin", "sage_leitung", "sage_lager"}


def test_simulator_material_stock_and_order_lookup_work() -> None:
    stock = get_material_stock("ALU-R20-2000")
    assert stock is not None
    assert stock["stock_m"] > 0

    order = get_order("SAGE-ORD-2026-001")
    assert order is not None
    assert order["material_no"] == "ALU-R20-2000"

    material_orders = list_orders_by_material("ALU-R20-2000")
    assert material_orders
