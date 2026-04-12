from __future__ import annotations

import pytest

from domain.entities import Comment


def test_comment_validates_minimal_fields() -> None:
    comment = Comment(
        entity_type="erp_transfer",
        entity_id="10",
        text="Freigabe mit Hinweis",
        created_by_user_id=3,
    )

    assert comment.entity_type == "erp_transfer"


def test_comment_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        Comment(
            entity_type="order",
            entity_id="A-1",
            text=" ",
            created_by_user_id=3,
        )
