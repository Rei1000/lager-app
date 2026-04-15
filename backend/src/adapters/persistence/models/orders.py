"""Order-related infrastructure ORM models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.access import UserModel
    from adapters.persistence.models.material import CuttingMachineModel, MaterialTypeModel

class AppOrderModel(Base):
    __tablename__ = "app_orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_app_orders_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    external_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    material_type_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("material_types.id"),
        nullable=False,
    )
    created_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    part_length_mm: Mapped[int] = mapped_column(Integer(), nullable=False)
    cutting_machine_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("cutting_machines.id"),
    )
    kerf_mm_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    include_rest_stock: Mapped[bool | None] = mapped_column(Boolean())
    calculated_total_demand_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    demand_from_full_stock_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    demand_from_rest_stock_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    shortage_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    traffic_light: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    priority_order: Mapped[int | None] = mapped_column(Integer())
    erp_order_number: Mapped[str | None] = mapped_column(String(100))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date())
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    material_type: Mapped["MaterialTypeModel"] = relationship(back_populates="app_orders")
    created_by_user: Mapped["UserModel"] = relationship(back_populates="app_orders")
    cutting_machine: Mapped["CuttingMachineModel | None"] = relationship(back_populates="app_orders")
    status_history_entries: Mapped[list["OrderStatusHistoryModel"]] = relationship(
        back_populates="app_order"
    )


class OrderStatusHistoryModel(Base):
    __tablename__ = "order_status_history"
    __table_args__ = (
        CheckConstraint(
            "old_status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_order_status_history_old_status",
        ),
        CheckConstraint(
            "new_status IN ('draft','checked','reserved','linked','confirmed','done','canceled')",
            name="ck_order_status_history_new_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    app_order_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("app_orders.id"),
        nullable=False,
    )
    old_status: Mapped[str] = mapped_column(String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    app_order: Mapped[AppOrderModel] = relationship(back_populates="status_history_entries")
    changed_by_user: Mapped["UserModel"] = relationship(back_populates="status_history_entries")
