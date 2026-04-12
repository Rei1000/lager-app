"""SQLAlchemy adapter for photo metadata repository."""

from __future__ import annotations

from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.photo import PhotoModel
from application.errors import NotFoundError
from ports.photo_repository_port import PhotoRecord, PhotoRepositoryPort


class SqlAlchemyPhotoRepository(PhotoRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def create_photo(
        self,
        *,
        entity_type: str,
        entity_id: str,
        file_key: str,
        original_filename: str,
        content_type: str | None,
        uploaded_by_user_id: int,
        comment: str | None,
    ) -> PhotoRecord:
        with self._session_factory() as session:
            model = PhotoModel(
                entity_type=entity_type,
                entity_id=entity_id,
                file_key=file_key,
                original_filename=original_filename,
                content_type=content_type,
                uploaded_by_user_id=uploaded_by_user_id,
                comment=comment,
            )
            session.add(model)
            self._commit_or_raise(session, "Foto-Metadaten konnten nicht gespeichert werden")
            session.refresh(model)
            return self._to_record(model)

    def list_photos_for_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[PhotoRecord]:
        with self._session_factory() as session:
            models = (
                session.query(PhotoModel)
                .filter(
                    PhotoModel.entity_type == entity_type,
                    PhotoModel.entity_id == entity_id,
                )
                .order_by(PhotoModel.id.desc())
                .all()
            )
            return [self._to_record(model) for model in models]

    def get_photo(self, photo_id: int) -> PhotoRecord:
        with self._session_factory() as session:
            model = session.get(PhotoModel, photo_id)
            if model is None:
                raise NotFoundError(f"Foto nicht gefunden: {photo_id}")
            return self._to_record(model)

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_record(model: PhotoModel) -> PhotoRecord:
        return PhotoRecord(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            file_key=model.file_key,
            original_filename=model.original_filename,
            content_type=model.content_type,
            uploaded_by_user_id=model.uploaded_by_user_id,
            uploaded_at=model.uploaded_at,
            comment=model.comment,
        )
