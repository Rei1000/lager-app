"""Access-related infrastructure ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.orders import AppOrderModel, OrderStatusHistoryModel


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())

    users: Mapped[list["UserModel"]] = relationship(back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text(), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255))
    role_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("roles.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    erp_user_reference: Mapped[str | None] = mapped_column(String(100))
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

    role: Mapped[RoleModel] = relationship(back_populates="users")
    app_orders: Mapped[list["AppOrderModel"]] = relationship(back_populates="created_by_user")
    status_history_entries: Mapped[list["OrderStatusHistoryModel"]] = relationship(
        back_populates="changed_by_user"
    )
