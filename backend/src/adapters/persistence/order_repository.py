"""SQLAlchemy implementation of OrderRepositoryPort."""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from adapters.persistence.db import get_session
from adapters.persistence.models.material import MaterialTypeModel
from adapters.persistence.models.orders import AppOrderModel
from domain.entities import AppOrder
from domain.order_plan_cutting import calculate_cutting_plan_demand_mm
from domain.value_objects import TrafficLight
from ports.order_repository_port import OrderRepositoryPort


class SqlAlchemyOrderRepository(OrderRepositoryPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def list_all(self) -> list[AppOrder]:
        with self._session_factory() as session:
            rows = (
                session.query(AppOrderModel)
                .options(joinedload(AppOrderModel.material_type))
                .order_by(AppOrderModel.priority_order.asc().nulls_last(), AppOrderModel.id.asc())
                .all()
            )
            return [self._to_domain(r) for r in rows]

    def get_by_id(self, order_id: str) -> AppOrder | None:
        with self._session_factory() as session:
            row = self._get_model(session, order_id)
            if row is None:
                return None
            return self._to_domain(row)

    def list_by_material(self, material_article_number: str) -> list[AppOrder]:
        normalized = material_article_number.strip()
        with self._session_factory() as session:
            rows = (
                session.query(AppOrderModel)
                .join(MaterialTypeModel)
                .options(joinedload(AppOrderModel.material_type))
                .filter(MaterialTypeModel.article_number == normalized)
                .order_by(AppOrderModel.priority_order.asc().nulls_last(), AppOrderModel.id.asc())
                .all()
            )
            return [self._to_domain(r) for r in rows]

    def save(self, order: AppOrder) -> None:
        with self._session_factory() as session:
            existing = self._get_model(session, order.order_id or "")
            if existing is None:
                self._insert(session, order)
            else:
                self._update(session, existing, order)
            session.commit()

    def _get_model(self, session: Session, order_id: str) -> AppOrderModel | None:
        base = session.query(AppOrderModel).options(joinedload(AppOrderModel.material_type))
        if order_id.isdigit():
            row = base.filter(AppOrderModel.id == int(order_id)).one_or_none()
            if row is not None:
                return row
        return (
            session.query(AppOrderModel)
            .options(joinedload(AppOrderModel.material_type))
            .filter(AppOrderModel.external_order_id == order_id)
            .one_or_none()
        )

    def _to_domain(self, model: AppOrderModel) -> AppOrder:
        material = model.material_type
        article = material.article_number
        kerf = float(model.kerf_mm_snapshot) if model.kerf_mm_snapshot is not None else 0.0
        light: TrafficLight | None = None
        if model.traffic_light:
            try:
                light = TrafficLight(model.traffic_light)
            except ValueError:
                light = None
        oid = model.external_order_id if model.external_order_id else str(model.id)
        desc = (material.name or "").strip() or None
        return AppOrder(
            order_id=oid,
            material_article_number=article,
            quantity=model.quantity,
            part_length_mm=model.part_length_mm,
            kerf_mm=int(round(kerf)),
            include_rest_stock=bool(model.include_rest_stock),
            status=model.status,
            priority_order=model.priority_order,
            traffic_light=light,
            erp_order_number=model.erp_order_number,
            created_by_user_id=model.created_by_user_id,
            persisted_row_id=int(model.id),
            customer_name=model.customer_name,
            due_date=model.due_date,
            material_description=desc,
        )

    def _insert(self, session: Session, order: AppOrder) -> None:
        if not order.order_id:
            raise ValueError("order_id ist fuer neuen Auftrag erforderlich")
        if order.created_by_user_id is None:
            raise ValueError("created_by_user_id ist fuer neuen Auftrag erforderlich")
        material = (
            session.query(MaterialTypeModel)
            .filter(MaterialTypeModel.article_number == order.material_article_number.strip())
            .one_or_none()
        )
        if material is None:
            raise ValueError(f"Material nicht gefunden: {order.material_article_number}")
        kerf_dec = Decimal(str(order.kerf_mm))
        demand = calculate_cutting_plan_demand_mm(
            quantity=order.quantity,
            part_length_mm=order.part_length_mm,
            kerf_mm=float(order.kerf_mm),
        )
        gross_m = Decimal(demand.gross_mm) / Decimal("1000")
        model = AppOrderModel(
            external_order_id=order.order_id,
            material_type_id=material.id,
            created_by_user_id=order.created_by_user_id,
            quantity=order.quantity,
            part_length_mm=order.part_length_mm,
            kerf_mm_snapshot=kerf_dec,
            include_rest_stock=order.include_rest_stock,
            calculated_total_demand_m=gross_m,
            demand_from_full_stock_m=gross_m,
            demand_from_rest_stock_m=Decimal("0"),
            shortage_m=Decimal("0"),
            traffic_light=order.traffic_light.value if order.traffic_light is not None else None,
            status=order.status,
            priority_order=order.priority_order,
            erp_order_number=order.erp_order_number,
            customer_name=order.customer_name,
            due_date=order.due_date,
        )
        session.add(model)
        session.flush()
        order.persisted_row_id = int(model.id)
        order.material_description = (material.name or "").strip() or None

    def _update(self, session: Session, model: AppOrderModel, order: AppOrder) -> None:
        kerf_dec = Decimal(str(order.kerf_mm))
        demand = calculate_cutting_plan_demand_mm(
            quantity=order.quantity,
            part_length_mm=order.part_length_mm,
            kerf_mm=float(order.kerf_mm),
        )
        gross_m = Decimal(demand.gross_mm) / Decimal("1000")
        model.quantity = order.quantity
        model.part_length_mm = order.part_length_mm
        model.kerf_mm_snapshot = kerf_dec
        model.include_rest_stock = order.include_rest_stock
        model.calculated_total_demand_m = gross_m
        model.demand_from_full_stock_m = gross_m
        model.traffic_light = order.traffic_light.value if order.traffic_light is not None else None
        model.status = order.status
        model.priority_order = order.priority_order
        model.erp_order_number = order.erp_order_number
        model.customer_name = order.customer_name
        model.due_date = order.due_date
