"""Domain services with pure business calculations."""

from __future__ import annotations

from domain.entities import AppOrder
from domain.value_objects import TrafficLight


def _ensure_non_negative(value: int, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} darf nicht negativ sein")


def calculate_available_mm(
    erp_stock_mm: int,
    open_erp_orders_mm: int,
    app_reservations_mm: int,
    rest_stock_mm: int,
    include_rest_stock: bool,
) -> int:
    _ensure_non_negative(erp_stock_mm, "erp_stock_mm")
    _ensure_non_negative(open_erp_orders_mm, "open_erp_orders_mm")
    _ensure_non_negative(app_reservations_mm, "app_reservations_mm")
    _ensure_non_negative(rest_stock_mm, "rest_stock_mm")
    available = erp_stock_mm - open_erp_orders_mm - app_reservations_mm
    if include_rest_stock:
        available += rest_stock_mm
    return available


def calculate_traffic_light(
    demand_mm: int,
    available_without_rest_mm: int,
    available_with_optional_rest_mm: int,
    include_rest_stock: bool,
) -> TrafficLight:
    _ensure_non_negative(demand_mm, "demand_mm")
    _ensure_non_negative(available_without_rest_mm, "available_without_rest_mm")
    _ensure_non_negative(available_with_optional_rest_mm, "available_with_optional_rest_mm")
    if demand_mm <= available_without_rest_mm:
        return TrafficLight.GREEN
    if include_rest_stock and demand_mm <= available_with_optional_rest_mm:
        return TrafficLight.YELLOW
    return TrafficLight.RED


def evaluate_orders_sequentially(
    orders: list[AppOrder],
    erp_stock_mm: int,
    open_erp_orders_mm: int,
    app_reservations_mm: int,
    rest_stock_mm: int,
) -> list[AppOrder]:
    if not orders:
        return []

    _ensure_non_negative(erp_stock_mm, "erp_stock_mm")
    _ensure_non_negative(open_erp_orders_mm, "open_erp_orders_mm")
    _ensure_non_negative(app_reservations_mm, "app_reservations_mm")
    _ensure_non_negative(rest_stock_mm, "rest_stock_mm")

    material_keys = {order.material_article_number for order in orders}
    if len(material_keys) > 1:
        raise ValueError("Priorisierung ist materialbezogen und darf nicht materialuebergreifend erfolgen")

    sorted_orders = sorted(
        orders,
        key=lambda order: order.priority_order if order.priority_order is not None else 10**9,
    )

    remaining_without_rest = erp_stock_mm - open_erp_orders_mm - app_reservations_mm
    remaining_rest = rest_stock_mm

    for order in sorted_orders:
        demand = order.total_demand_mm
        available_with_rest = remaining_without_rest + (remaining_rest if order.include_rest_stock else 0)
        order.traffic_light = calculate_traffic_light(
            demand_mm=demand,
            available_without_rest_mm=remaining_without_rest,
            available_with_optional_rest_mm=available_with_rest,
            include_rest_stock=order.include_rest_stock,
        )

        if order.traffic_light is TrafficLight.GREEN:
            remaining_without_rest -= demand
        elif order.traffic_light is TrafficLight.YELLOW and order.include_rest_stock:
            use_full = max(remaining_without_rest, 0)
            remaining_without_rest -= use_full
            remaining_rest -= max(demand - use_full, 0)

    return sorted_orders
