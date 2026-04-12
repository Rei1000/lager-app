from __future__ import annotations

import pytest

from domain.entities import InventoryCount, InventoryDifference, PhotoAttachment, StockCorrectionRequest


def test_inventory_count_computes_difference_and_type() -> None:
    count = InventoryCount(
        material_article_number="ART-INV-1",
        counted_stock_mm=12_000,
        reference_stock_mm=10_000,
        counted_by_user_id=1,
    )

    assert count.difference_mm == 2_000
    assert count.difference_type == "surplus"


def test_inventory_difference_handles_deficit() -> None:
    difference = InventoryDifference(
        material_article_number="ART-INV-1",
        counted_stock_mm=8_500,
        reference_stock_mm=10_000,
    )

    assert difference.difference_mm == -1_500
    assert difference.difference_type == "deficit"


def test_stock_correction_request_status_transitions() -> None:
    correction = StockCorrectionRequest(
        inventory_count_id=1,
        material_article_number="ART-INV-1",
        correction_mm=-1_500,
        requested_by_user_id=3,
    )

    correction.transition_to("confirmed")

    assert correction.status == "confirmed"


def test_stock_correction_request_rejects_zero_amount() -> None:
    with pytest.raises(ValueError):
        StockCorrectionRequest(
            inventory_count_id=1,
            material_article_number="ART-INV-1",
            correction_mm=0,
            requested_by_user_id=3,
        )


def test_photo_attachment_validates_context_and_user() -> None:
    attachment = PhotoAttachment(
        entity_type="inventory_count",
        entity_id="15",
        uploaded_by_user_id=2,
        comment="Schaden sichtbar",
    )

    assert attachment.entity_type == "inventory_count"


def test_photo_attachment_rejects_unknown_context() -> None:
    with pytest.raises(ValueError):
        PhotoAttachment(
            entity_type="unknown",
            entity_id="1",
            uploaded_by_user_id=2,
        )
