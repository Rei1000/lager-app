"""Schemas for audit log endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from ports.audit_log_port import AuditLogRecord


class AuditLogResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str | None
    action: str
    user_id: int | None
    occurred_at: datetime
    payload: dict[str, Any] | None
    comment: str | None

    @classmethod
    def from_record(cls, record: AuditLogRecord) -> "AuditLogResponse":
        return cls(
            id=record.id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            action=record.action,
            user_id=record.user_id,
            occurred_at=record.occurred_at,
            payload=record.payload,
            comment=record.comment,
        )
