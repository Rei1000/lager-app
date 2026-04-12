from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_create_comment_use_case,
    get_list_comments_for_entity_use_case,
)
from ports.comment_repository_port import CommentRecord


def _record(comment_id: int = 1) -> CommentRecord:
    return CommentRecord(
        id=comment_id,
        entity_type="order",
        entity_id="A-1",
        text="Hinweis",
        created_by_user_id=2,
        created_at=datetime.now(timezone.utc),
    )


def test_comment_create_and_list_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeCreateCommentUseCase:
        def execute(self, _command: object) -> CommentRecord:
            return _record(comment_id=3)

    class FakeListCommentsUseCase:
        def execute(self, _command: object) -> list[CommentRecord]:
            return [_record(comment_id=3)]

    app.dependency_overrides[get_create_comment_use_case] = lambda: FakeCreateCommentUseCase()
    app.dependency_overrides[get_list_comments_for_entity_use_case] = lambda: FakeListCommentsUseCase()
    client = TestClient(app)

    create_response = client.post(
        "/comments",
        json={"entity_type": "order", "entity_id": "A-1", "text": "Bitte pruefen"},
    )
    list_response = client.get("/comments?entity_type=order&entity_id=A-1")

    assert create_response.status_code == 201
    assert create_response.json()["id"] == 3
    assert list_response.status_code == 200
    assert list_response.json()[0]["entity_type"] == "order"
    app.dependency_overrides.clear()


def test_comment_create_requires_lager_plus_role() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=5,
        username="gast",
        role_code="gast",
        role_name="Gast",
    )
    client = TestClient(app)

    response = client.post(
        "/comments",
        json={"entity_type": "material", "entity_id": "ART-1", "text": "Info"},
    )

    assert response.status_code == 403
    app.dependency_overrides.clear()
