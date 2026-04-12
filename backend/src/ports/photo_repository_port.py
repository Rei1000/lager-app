"""Repository contract for photo metadata records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class PhotoRecord:
    id: int
    entity_type: str
    entity_id: str
    file_key: str
    original_filename: str
    content_type: str | None
    uploaded_by_user_id: int
    uploaded_at: datetime
    comment: str | None = None


class PhotoRepositoryPort(Protocol):
    def create_photo(
        self,
        *,
        entity_type: str,
        entity_id: str,
        file_key: str,
        original_filename: str,
        content_type: str | None,
        uploaded_by_user_id: int,
        comment: str | None,
    ) -> PhotoRecord:
        """Persist one photo metadata record."""

    def list_photos_for_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[PhotoRecord]:
        """List photos by entity context."""

    def get_photo(self, photo_id: int) -> PhotoRecord:
        """Return one photo by ID."""
