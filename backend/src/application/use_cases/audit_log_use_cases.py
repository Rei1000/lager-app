"""Read use case for audit events."""

from __future__ import annotations

from ports.audit_log_port import AuditLogPort, AuditLogRecord


class ListAuditLogsUseCase:
    def __init__(self, audit_log_port: AuditLogPort) -> None:
        self._audit_log_port = audit_log_port

    def execute(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        normalized_limit = max(1, min(limit, 500))
        return self._audit_log_port.list_events(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=normalized_limit,
        )
