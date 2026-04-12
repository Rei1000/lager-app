"""SQLAlchemy adapter for inventory repository port."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.inventory import InventoryCountModel, StockCorrectionModel
from application.errors import NotFoundError
from ports.inventory_repository_port import (
    InventoryCountRecord,
    InventoryRepositoryPort,
    StockCorrectionRecord,
)


class SqlAlchemyInventoryRepository(InventoryRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def create_inventory_count(
        self,
        *,
        material_article_number: str,
        counted_stock_mm: int,
        reference_stock_mm: int,
        difference_mm: int,
        difference_type: str,
        counted_by_user_id: int,
        comment: str | None,
    ) -> InventoryCountRecord:
        with self._session_factory() as session:
            model = InventoryCountModel(
                material_article_number=material_article_number,
                counted_stock_mm=counted_stock_mm,
                reference_stock_mm=reference_stock_mm,
                difference_mm=difference_mm,
                difference_type=difference_type,
                status="recorded",
                counted_by_user_id=counted_by_user_id,
                comment=comment,
            )
            session.add(model)
            self._commit_or_raise(session, "Inventurzaehlung konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_inventory_count_record(model)

    def list_inventory_counts(self) -> list[InventoryCountRecord]:
        with self._session_factory() as session:
            counts = session.query(InventoryCountModel).order_by(InventoryCountModel.id.desc()).all()
            return [self._to_inventory_count_record(model) for model in counts]

    def get_inventory_count(self, inventory_count_id: int) -> InventoryCountRecord:
        with self._session_factory() as session:
            model = session.get(InventoryCountModel, inventory_count_id)
            if model is None:
                raise NotFoundError(f"Inventurzaehlung nicht gefunden: {inventory_count_id}")
            return self._to_inventory_count_record(model)

    def create_stock_correction(
        self,
        *,
        inventory_count_id: int,
        material_article_number: str,
        correction_mm: int,
        requested_by_user_id: int,
        comment: str | None,
    ) -> StockCorrectionRecord:
        with self._session_factory() as session:
            inventory = session.get(InventoryCountModel, inventory_count_id)
            if inventory is None:
                raise NotFoundError(f"Inventurzaehlung nicht gefunden: {inventory_count_id}")

            model = StockCorrectionModel(
                inventory_count_id=inventory_count_id,
                material_article_number=material_article_number,
                correction_mm=correction_mm,
                status="requested",
                requested_by_user_id=requested_by_user_id,
                comment=comment,
            )
            inventory.status = "correction_requested"
            session.add(model)
            self._commit_or_raise(session, "Korrekturvorgang konnte nicht gespeichert werden")
            session.refresh(model)
            return self._to_stock_correction_record(model)

    def get_stock_correction(self, correction_id: int) -> StockCorrectionRecord:
        with self._session_factory() as session:
            model = session.get(StockCorrectionModel, correction_id)
            if model is None:
                raise NotFoundError(f"Korrekturvorgang nicht gefunden: {correction_id}")
            return self._to_stock_correction_record(model)

    def update_stock_correction_status(
        self,
        *,
        correction_id: int,
        status: str,
        acting_user_id: int,
    ) -> StockCorrectionRecord:
        with self._session_factory() as session:
            model = session.get(StockCorrectionModel, correction_id)
            if model is None:
                raise NotFoundError(f"Korrekturvorgang nicht gefunden: {correction_id}")
            if model.status != "requested":
                raise ValueError("Nur angefragte Korrekturen duerfen geaendert werden")
            if status not in {"confirmed", "canceled"}:
                raise ValueError(f"Unbekannter Korrekturstatus: {status}")

            now = datetime.now(timezone.utc)
            model.status = status
            if status == "confirmed":
                model.confirmed_by_user_id = acting_user_id
                model.confirmed_at = now
            else:
                model.canceled_by_user_id = acting_user_id
                model.canceled_at = now

            inventory = session.get(InventoryCountModel, model.inventory_count_id)
            if inventory is not None:
                inventory.status = "closed"

            self._commit_or_raise(session, "Korrekturstatus konnte nicht aktualisiert werden")
            session.refresh(model)
            return self._to_stock_correction_record(model)

    @staticmethod
    def _commit_or_raise(session: Session, message: str) -> None:
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise ValueError(message) from exc

    @staticmethod
    def _to_inventory_count_record(model: InventoryCountModel) -> InventoryCountRecord:
        return InventoryCountRecord(
            id=model.id,
            material_article_number=model.material_article_number,
            counted_stock_mm=model.counted_stock_mm,
            reference_stock_mm=model.reference_stock_mm,
            difference_mm=model.difference_mm,
            difference_type=model.difference_type,
            status=model.status,
            counted_by_user_id=model.counted_by_user_id,
            comment=model.comment,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_stock_correction_record(model: StockCorrectionModel) -> StockCorrectionRecord:
        return StockCorrectionRecord(
            id=model.id,
            inventory_count_id=model.inventory_count_id,
            material_article_number=model.material_article_number,
            correction_mm=model.correction_mm,
            status=model.status,
            requested_by_user_id=model.requested_by_user_id,
            comment=model.comment,
            created_at=model.created_at,
            confirmed_by_user_id=model.confirmed_by_user_id,
            confirmed_at=model.confirmed_at,
            canceled_by_user_id=model.canceled_by_user_id,
            canceled_at=model.canceled_at,
        )
