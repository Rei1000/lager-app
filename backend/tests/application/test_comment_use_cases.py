from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from application.dtos import CreateCommentCommand, ListCommentsForEntityCommand
from application.use_cases.comment_use_cases import (
    CreateCommentUseCase,
    ListCommentsForEntityUseCase,
)
from ports.comment_repository_port import CommentRecord, CommentRepositoryPort


@dataclass
class FakeCommentRepository(CommentRepositoryPort):
    records: list[CommentRecord] = field(default_factory=list)

    def save_comment(
        self,
        *,
        entity_type: str,
        entity_id: str,
        text: str,
        created_by_user_id: int,
    ) -> CommentRecord:
        record = CommentRecord(
            id=len(self.records) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            text=text,
            created_by_user_id=created_by_user_id,
            created_at=datetime.now(timezone.utc),
        )
        self.records.append(record)
        return record

    def list_by_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[CommentRecord]:
        return [
            item
            for item in self.records
            if item.entity_type == entity_type and item.entity_id == entity_id
        ]


def test_create_comment_use_case_saves_entity_bound_comment() -> None:
    repo = FakeCommentRepository()
    use_case = CreateCommentUseCase(comment_repository=repo)

    created = use_case.execute(
        CreateCommentCommand(
            entity_type="order",
            entity_id="A-1",
            text="Bitte Prioritaet pruefen",
            created_by_user_id=2,
        )
    )

    assert created.id == 1
    assert created.entity_type == "order"
    assert created.text == "Bitte Prioritaet pruefen"


def test_list_comments_for_entity_use_case_filters_by_context() -> None:
    repo = FakeCommentRepository()
    creator = CreateCommentUseCase(comment_repository=repo)
    lister = ListCommentsForEntityUseCase(comment_repository=repo)
    creator.execute(
        CreateCommentCommand(
            entity_type="material",
            entity_id="ART-001",
            text="Oberflaeche pruefen",
            created_by_user_id=1,
        )
    )
    creator.execute(
        CreateCommentCommand(
            entity_type="material",
            entity_id="ART-999",
            text="anderer Kontext",
            created_by_user_id=1,
        )
    )

    comments = lister.execute(
        ListCommentsForEntityCommand(entity_type="material", entity_id="ART-001")
    )

    assert len(comments) == 1
    assert comments[0].entity_id == "ART-001"
