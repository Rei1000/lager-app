"""Comment ORM model for simple entity communication."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.persistence.base import Base

if TYPE_CHECKING:
    from adapters.persistence.models.access import UserModel


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(120), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_by_user: Mapped["UserModel"] = relationship(foreign_keys=[created_by_user_id])
