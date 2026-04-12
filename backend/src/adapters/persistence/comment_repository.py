"""SQLAlchemy adapter for comment repository."""

from __future__ import annotations

from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.comment import CommentModel
from ports.comment_repository_port import CommentRecord, CommentRepositoryPort


class SqlAlchemyCommentRepository(CommentRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def save_comment(
        self,
        *,
        entity_type: str,
        entity_id: str,
        text: str,
        created_by_user_id: int,
    ) -> CommentRecord:
        with self._session_factory() as session:
            model = CommentModel(
                entity_type=entity_type,
                entity_id=entity_id,
                text=text,
                created_by_user_id=created_by_user_id,
            )
            session.add(model)
            self._commit_or_raise(session, "Kommentar konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_record(model)

    def list_by_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[CommentRecord]:
        with self._session_factory() as session:
            models = (
                session.query(CommentModel)
                .filter(
                    CommentModel.entity_type == entity_type,
                    CommentModel.entity_id == entity_id,
                )
                .order_by(CommentModel.id.desc())
                .all()
            )
            return [self._to_record(model) for model in models]

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_record(model: CommentModel) -> CommentRecord:
        return CommentRecord(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            text=model.text,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )
