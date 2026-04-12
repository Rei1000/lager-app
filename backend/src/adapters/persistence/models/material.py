"""Material-related infrastructure ORM models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.orders import AppOrderModel


class MaterialTypeModel(Base):
    __tablename__ = "material_types"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    article_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    erp_material_id: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str | None] = mapped_column(String(20))
    min_rest_length_mm: Mapped[int | None] = mapped_column(Integer())
    erp_stock_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    rest_stock_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    main_storage_location: Mapped[str | None] = mapped_column(String(100))
    rest_storage_location: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    rest_stock_account: Mapped["RestStockAccountModel | None"] = relationship(
        back_populates="material_type",
        uselist=False,
    )
    app_orders: Mapped[list["AppOrderModel"]] = relationship(back_populates="material_type")


class RestStockAccountModel(Base):
    __tablename__ = "rest_stock_accounts"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    material_type_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("material_types.id"),
        nullable=False,
        unique=True,
    )
    rest_stock_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    total_rest_stock_m: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    storage_location: Mapped[str | None] = mapped_column(String(100))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    material_type: Mapped[MaterialTypeModel] = relationship(back_populates="rest_stock_account")


class CuttingMachineModel(Base):
    __tablename__ = "cutting_machines"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    machine_code: Mapped[str | None] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    kerf_mm: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    app_orders: Mapped[list["AppOrderModel"]] = relationship(back_populates="cutting_machine")
