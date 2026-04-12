"""ERP transfer preparation ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.access import UserModel


class ErpTransferRequestModel(Base):
    __tablename__ = "erp_transfer_requests"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','ready','approved','sent','failed')",
            name="ck_erp_transfer_requests_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    material_article_number: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    payload_json: Mapped[dict | None] = mapped_column(JSONB())
    requested_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    ready_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    approved_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    sent_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    failed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
    )
    failure_reason: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    requested_by_user: Mapped["UserModel"] = relationship(foreign_keys=[requested_by_user_id])
    ready_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[ready_by_user_id])
    approved_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[approved_by_user_id])
    sent_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[sent_by_user_id])
    failed_by_user: Mapped["UserModel | None"] = relationship(foreign_keys=[failed_by_user_id])
