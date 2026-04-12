"""Inventory and stock correction infrastructure ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.access import UserModel


class InventoryCountModel(Base):
    __tablename__ = "inventory_counts"
    __table_args__ = (
        CheckConstraint(
            "difference_type IN ('surplus','deficit','equal')",
            name="ck_inventory_counts_difference_type",
        ),
        CheckConstraint(
            "status IN ('recorded','compared','correction_requested','closed')",
            name="ck_inventory_counts_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    material_article_number: Mapped[str] = mapped_column(String(100), nullable=False)
    counted_stock_mm: Mapped[int] = mapped_column(Integer(), nullable=False)
    reference_stock_mm: Mapped[int] = mapped_column(Integer(), nullable=False)
    difference_mm: Mapped[int] = mapped_column(Integer(), nullable=False)
    difference_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded")
    counted_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    counted_by_user: Mapped["UserModel"] = relationship(foreign_keys=[counted_by_user_id])
    stock_corrections: Mapped[list["StockCorrectionModel"]] = relationship(back_populates="inventory_count")


class StockCorrectionModel(Base):
    __tablename__ = "stock_corrections"
    __table_args__ = (
        CheckConstraint(
            "status IN ('requested','confirmed','canceled')",
            name="ck_stock_corrections_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    inventory_count_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("inventory_counts.id"),
        nullable=False,
    )
    material_article_number: Mapped[str] = mapped_column(String(100), nullable=False)
    correction_mm: Mapped[int] = mapped_column(Integer(), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="requested")
    requested_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    confirmed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    canceled_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    comment: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    inventory_count: Mapped[InventoryCountModel] = relationship(back_populates="stock_corrections")
    requested_by_user: Mapped["UserModel"] = relationship(foreign_keys=[requested_by_user_id])
    confirmed_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[confirmed_by_user_id])
    canceled_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[canceled_by_user_id])
