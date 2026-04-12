"""Schemas for simple entity comments."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ports.comment_repository_port import CommentRecord


class CreateCommentRequest(BaseModel):
    entity_type: str = Field(min_length=1)
    entity_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    text: str
    created_by_user_id: int
    created_at: datetime

    @classmethod
    def from_record(cls, record: CommentRecord) -> "CommentResponse":
        return cls(
            id=record.id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            text=record.text,
            created_by_user_id=record.created_by_user_id,
            created_at=record.created_at,
        )
