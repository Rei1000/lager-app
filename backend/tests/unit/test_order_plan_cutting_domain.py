"""Tests for cutting-plan demand calculation (Stück × Länge + (n−1) × Kerf)."""

from __future__ import annotations

import pytest

from domain.order_plan_cutting import calculate_cutting_plan_demand_mm, is_cutting_plan_feasible


def test_net_demand_is_quantity_times_part_length() -> None:
    result = calculate_cutting_plan_demand_mm(quantity=5, part_length_mm=2500, kerf_mm=3)
    assert result.net_mm == 12_500


def test_kerf_waste_is_zero_when_single_piece() -> None:
    result = calculate_cutting_plan_demand_mm(quantity=1, part_length_mm=1000, kerf_mm=3)
    assert result.kerf_waste_mm == 0


def test_kerf_waste_is_quantity_minus_one_times_kerf() -> None:
    result = calculate_cutting_plan_demand_mm(quantity=10, part_length_mm=500, kerf_mm=3)
    assert result.kerf_waste_mm == 9 * 3


def test_gross_is_net_plus_kerf_waste() -> None:
    result = calculate_cutting_plan_demand_mm(quantity=4, part_length_mm=1800, kerf_mm=2)
    assert result.net_mm == 7200
    assert result.kerf_waste_mm == 3 * 2
    assert result.gross_mm == 7206


def test_kerf_zero_yields_no_waste_and_gross_equals_net() -> None:
    result = calculate_cutting_plan_demand_mm(quantity=5, part_length_mm=800, kerf_mm=0.0)
    assert result.kerf_waste_mm == 0
    assert result.gross_mm == result.net_mm == 4000


def test_quantity_zero_raises() -> None:
    with pytest.raises(ValueError, match="quantity"):
        calculate_cutting_plan_demand_mm(quantity=0, part_length_mm=1000, kerf_mm=2)


def test_negative_part_length_raises() -> None:
    with pytest.raises(ValueError, match="part_length_mm"):
        calculate_cutting_plan_demand_mm(quantity=2, part_length_mm=0, kerf_mm=2)


def test_negative_kerf_raises() -> None:
    with pytest.raises(ValueError, match="kerf_mm"):
        calculate_cutting_plan_demand_mm(quantity=2, part_length_mm=1000, kerf_mm=-1)


def test_feasible_when_available_equals_gross_m() -> None:
    assert is_cutting_plan_feasible(gross_m=10.0, available_m=10.0) is True


def test_feasible_when_available_exceeds_gross_m() -> None:
    assert is_cutting_plan_feasible(gross_m=9.5, available_m=10.0) is True


def test_not_feasible_when_available_below_gross_m() -> None:
    assert is_cutting_plan_feasible(gross_m=10.1, available_m=10.0) is False
