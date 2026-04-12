"""Repository contract for comments on business entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CommentRecord:
    id: int
    entity_type: str
    entity_id: str
    text: str
    created_by_user_id: int
    created_at: datetime


class CommentRepositoryPort(Protocol):
    def save_comment(
        self,
        *,
        entity_type: str,
        entity_id: str,
        text: str,
        created_by_user_id: int,
    ) -> CommentRecord:
        """Persist one comment."""

    def list_by_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[CommentRecord]:
        """List comments for one entity context."""
