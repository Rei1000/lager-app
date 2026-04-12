"""SQLAlchemy adapter for material lookup."""

from __future__ import annotations

from typing import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.material import MaterialTypeModel
from application.errors import NotFoundError
from ports.material_lookup_port import MaterialLookupPort, MaterialLookupRecord


class SqlAlchemyMaterialLookupRepository(MaterialLookupPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def search_materials(self, query: str) -> list[MaterialLookupRecord]:
        search = f"%{query.strip()}%"
        with self._session_factory() as session:
            materials = (
                session.query(MaterialTypeModel)
                .filter(
                    MaterialTypeModel.is_active.is_(True),
                    or_(
                        MaterialTypeModel.article_number.ilike(search),
                        MaterialTypeModel.name.ilike(search),
                    ),
                )
                .order_by(MaterialTypeModel.article_number.asc())
                .limit(25)
                .all()
            )
            return [self._to_record(material) for material in materials]

    def get_by_article_number(self, article_number: str) -> MaterialLookupRecord:
        with self._session_factory() as session:
            material = (
                session.query(MaterialTypeModel)
                .filter(
                    MaterialTypeModel.article_number == article_number,
                    MaterialTypeModel.is_active.is_(True),
                )
                .one_or_none()
            )
            if material is None:
                raise NotFoundError(f"Material nicht gefunden: {article_number}")
            return self._to_record(material)

    @staticmethod
    def _to_record(model: MaterialTypeModel) -> MaterialLookupRecord:
        return MaterialLookupRecord(
            article_number=model.article_number,
            name=model.name,
            profile=model.profile,
            erp_stock_m=float(model.erp_stock_m) if model.erp_stock_m is not None else None,
            rest_stock_m=float(model.rest_stock_m) if model.rest_stock_m is not None else None,
        )
