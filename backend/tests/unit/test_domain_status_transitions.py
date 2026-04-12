from __future__ import annotations

import pytest

from domain.entities import AppOrder


def test_status_transition_path_is_allowed() -> None:
    order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
    )

    order.transition_to("checked")
    order.transition_to("reserved")
    order.transition_to("linked")
    order.transition_to("confirmed")
    order.transition_to("done")

    assert order.status == "done"


def test_status_can_be_canceled_from_checked_reserved_linked_confirmed() -> None:
    order_checked = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="checked",
    )
    order_checked.transition_to("canceled")
    assert order_checked.status == "canceled"

    order_reserved = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="reserved",
    )
    order_reserved.transition_to("canceled")
    assert order_reserved.status == "canceled"

    order_linked = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="linked",
    )
    order_linked.transition_to("canceled")
    assert order_linked.status == "canceled"

    order_confirmed = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="confirmed",
    )
    order_confirmed.transition_to("canceled")
    assert order_confirmed.status == "canceled"


def test_reserved_to_checked_is_not_allowed() -> None:
    order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="reserved",
    )
    with pytest.raises(ValueError):
        order.transition_to("checked")


def test_terminal_states_do_not_allow_further_transitions() -> None:
    done_order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="done",
    )
    with pytest.raises(ValueError):
        done_order.transition_to("canceled")

    canceled_order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="canceled",
    )
    with pytest.raises(ValueError):
        canceled_order.transition_to("checked")


def test_direct_jump_from_draft_to_confirmed_is_not_allowed() -> None:
    order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="draft",
    )
    with pytest.raises(ValueError):
        order.transition_to("confirmed")


def test_unknown_initial_status_is_rejected() -> None:
    with pytest.raises(ValueError):
        AppOrder(
            material_article_number="ART-001",
            quantity=1,
            part_length_mm=1000,
            kerf_mm=3,
            include_rest_stock=False,
            status="unknown",
        )


def test_unknown_target_status_is_rejected() -> None:
    order = AppOrder(
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=3,
        include_rest_stock=False,
        status="checked",
    )
    with pytest.raises(ValueError):
        order.transition_to("archived")
