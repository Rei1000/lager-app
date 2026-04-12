from __future__ import annotations

import pytest

from domain.entities import ErpTransferRequest


def test_erp_transfer_request_allows_controlled_transitions() -> None:
    transfer = ErpTransferRequest(
        order_id="ORD-1",
        material_article_number="ART-001",
        requested_by_user_id=1,
        payload={"quantity": 5},
    )

    transfer.transition_to("ready")
    transfer.transition_to("approved")
    transfer.transition_to("sent")

    assert transfer.status == "sent"


def test_erp_transfer_request_rejects_invalid_transition() -> None:
    transfer = ErpTransferRequest(
        order_id="ORD-1",
        material_article_number="ART-001",
        requested_by_user_id=1,
    )

    with pytest.raises(ValueError):
        transfer.transition_to("sent")
