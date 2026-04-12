"""Photo attachment metadata ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.access import UserModel


class PhotoModel(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255))
    uploaded_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    comment: Mapped[str | None] = mapped_column(Text())

    uploaded_by_user: Mapped["UserModel"] = relationship(foreign_keys=[uploaded_by_user_id])
