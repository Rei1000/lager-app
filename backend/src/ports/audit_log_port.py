"""Port contract for structured audit logging."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class AuditLogRecord:
    id: int
    entity_type: str
    entity_id: str | None
    action: str
    user_id: int | None
    occurred_at: datetime
    payload: dict[str, Any] | None = None
    comment: str | None = None


class AuditLogPort(Protocol):
    def log_event(
        self,
        *,
        entity_type: str,
        entity_id: str | None,
        action: str,
        user_id: int | None,
        payload: dict[str, Any] | None = None,
        comment: str | None = None,
    ) -> AuditLogRecord:
        """Persist one audit event."""

    def list_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        """List audit events with optional filtering."""
