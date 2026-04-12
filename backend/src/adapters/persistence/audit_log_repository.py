"""SQLAlchemy adapter for audit log port."""

from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.audit import AuditLogModel
from ports.audit_log_port import AuditLogPort, AuditLogRecord


class SqlAlchemyAuditLogRepository(AuditLogPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def log_event(
        self,
        *,
        entity_type: str,
        entity_id: str | None,
        action: str,
        user_id: int | None,
        payload: dict[str, Any] | None = None,
        comment: str | None = None,
    ) -> AuditLogRecord:
        with self._session_factory() as session:
            model = AuditLogModel(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                user_id=user_id,
                payload_json=payload,
                comment=comment,
            )
            session.add(model)
            self._commit_or_raise(session, "Audit-Event konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_record(model)

    def list_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        with self._session_factory() as session:
            query = session.query(AuditLogModel)
            if entity_type:
                query = query.filter(AuditLogModel.entity_type == entity_type)
            if entity_id:
                query = query.filter(AuditLogModel.entity_id == entity_id)
            rows = query.order_by(AuditLogModel.id.desc()).limit(limit).all()
            return [self._to_record(row) for row in rows]

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_record(model: AuditLogModel) -> AuditLogRecord:
        return AuditLogRecord(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            action=model.action,
            user_id=model.user_id,
            occurred_at=model.occurred_at,
            payload=model.payload_json,
            comment=model.comment,
        )
