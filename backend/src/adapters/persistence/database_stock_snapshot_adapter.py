"""Stock snapshot from DB material row + ERP simulator pipeline + app-only demand."""

from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from adapters.erp.sage_simulator_data import get_material_availability
from adapters.persistence.db import get_session
from adapters.persistence.models.material import MaterialTypeModel
from domain.material_pipeline import app_only_additional_pipeline_mm
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshot, StockSnapshotPort


class DatabaseStockSnapshotAdapter(StockSnapshotPort):
    """Baut StockSnapshot fuer Dispositionslogik aus ERP-Simulator und App-Auftraegen."""

    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        session_factory: Callable[[], Session] = get_session,
    ) -> None:
        self._order_repository = order_repository
        self._session_factory = session_factory

    def get_snapshot(self, material_article_number: str) -> StockSnapshot:
        normalized = material_article_number.strip()
        with self._session_factory() as session:
            mat = (
                session.query(MaterialTypeModel)
                .filter(MaterialTypeModel.article_number == normalized)
                .one_or_none()
            )
        if mat is None:
            return StockSnapshot(
                erp_stock_mm=0,
                open_erp_orders_mm=0,
                app_reservations_mm=0,
                rest_stock_mm=0,
            )

        rest_stock_mm = int(round(float(mat.rest_stock_m) * 1000)) if mat.rest_stock_m is not None else 0

        payload = get_material_availability(normalized)
        orders = self._order_repository.list_by_material(normalized)
        erp_refs: set[str] = set()
        open_erp_orders_mm = 0
        erp_stock_mm = int(round(float(mat.erp_stock_m) * 1000)) if mat.erp_stock_m is not None else 0

        if payload is not None:
            erp_stock_mm = int(round(float(payload["stock_m"]) * 1000))
            open_erp_orders_mm = int(round(float(payload["in_pipeline_m"]) * 1000))
            for row in payload.get("open_orders") or []:
                erp_refs.add(str(row["order_no"]))

        app_mm = app_only_additional_pipeline_mm(orders, erp_refs)

        return StockSnapshot(
            erp_stock_mm=erp_stock_mm,
            open_erp_orders_mm=open_erp_orders_mm,
            app_reservations_mm=app_mm,
            rest_stock_mm=rest_stock_mm,
        )
