"""SQLAlchemy adapter for ERP transfer preparation repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.erp_transfer import ErpTransferRequestModel
from application.errors import NotFoundError
from ports.erp_transfer_repository_port import ErpTransferRepositoryPort, ErpTransferRequestRecord


class SqlAlchemyErpTransferRepository(ErpTransferRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def create_transfer_request(
        self,
        *,
        order_id: str,
        material_article_number: str,
        requested_by_user_id: int,
        payload: dict[str, Any] | None,
    ) -> ErpTransferRequestRecord:
        with self._session_factory() as session:
            model = ErpTransferRequestModel(
                order_id=order_id,
                material_article_number=material_article_number,
                status="draft",
                payload_json=payload,
                requested_by_user_id=requested_by_user_id,
            )
            session.add(model)
            self._commit_or_raise(session, "ERP-Transfer konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_record(model)

    def list_transfer_requests(self) -> list[ErpTransferRequestRecord]:
        with self._session_factory() as session:
            models = (
                session.query(ErpTransferRequestModel)
                .order_by(ErpTransferRequestModel.id.desc())
                .all()
            )
            return [self._to_record(model) for model in models]

    def get_transfer_request(self, transfer_id: int) -> ErpTransferRequestRecord:
        with self._session_factory() as session:
            model = session.get(ErpTransferRequestModel, transfer_id)
            if model is None:
                raise NotFoundError(f"ERP-Transfer nicht gefunden: {transfer_id}")
            return self._to_record(model)

    def update_transfer_status(
        self,
        *,
        transfer_id: int,
        status: str,
        acting_user_id: int,
        failure_reason: str | None = None,
    ) -> ErpTransferRequestRecord:
        with self._session_factory() as session:
            model = session.get(ErpTransferRequestModel, transfer_id)
            if model is None:
                raise NotFoundError(f"ERP-Transfer nicht gefunden: {transfer_id}")

            now = datetime.now(timezone.utc)
            model.status = status
            if status == "ready":
                model.ready_by_user_id = acting_user_id
                model.ready_at = now
                model.failure_reason = None
            elif status == "approved":
                model.approved_by_user_id = acting_user_id
                model.approved_at = now
                model.failure_reason = None
            elif status == "sent":
                model.sent_by_user_id = acting_user_id
                model.sent_at = now
                model.failure_reason = None
            elif status == "failed":
                model.failed_by_user_id = acting_user_id
                model.failed_at = now
                model.failure_reason = failure_reason

            self._commit_or_raise(session, "ERP-Transferstatus konnte nicht aktualisiert werden")
            session.refresh(model)
            return self._to_record(model)

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_record(model: ErpTransferRequestModel) -> ErpTransferRequestRecord:
        return ErpTransferRequestRecord(
            id=model.id,
            order_id=model.order_id,
            material_article_number=model.material_article_number,
            status=model.status,
            requested_by_user_id=model.requested_by_user_id,
            payload=model.payload_json,
            created_at=model.created_at,
            ready_by_user_id=model.ready_by_user_id,
            approved_by_user_id=model.approved_by_user_id,
            sent_by_user_id=model.sent_by_user_id,
            failed_by_user_id=model.failed_by_user_id,
            ready_at=model.ready_at,
            approved_at=model.approved_at,
            sent_at=model.sent_at,
            failed_at=model.failed_at,
            failure_reason=model.failure_reason,
        )
