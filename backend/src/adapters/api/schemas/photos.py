"""Schemas for photo upload and listing endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ports.photo_repository_port import PhotoRecord


class PhotoResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    uploaded_by_user_id: int
    uploaded_at: datetime
    comment: str | None
    original_filename: str
    content_type: str | None
    file_url: str

    @classmethod
    def from_record(cls, record: PhotoRecord) -> "PhotoResponse":
        return cls(
            id=record.id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            uploaded_by_user_id=record.uploaded_by_user_id,
            uploaded_at=record.uploaded_at,
            comment=record.comment,
            original_filename=record.original_filename,
            content_type=record.content_type,
            file_url=f"/photos/{record.id}/file",
        )
