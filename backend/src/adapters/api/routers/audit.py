"""Audit log API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from adapters.api.dependencies.auth import require_leitung_or_admin
from adapters.api.dependencies.use_cases import get_list_audit_logs_use_case
from adapters.api.schemas.audit import AuditLogResponse
from application.use_cases.audit_log_use_cases import ListAuditLogsUseCase

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit"],
    dependencies=[Depends(require_leitung_or_admin)],
)


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    use_case: ListAuditLogsUseCase = Depends(get_list_audit_logs_use_case),
) -> list[AuditLogResponse]:
    records = use_case.execute(entity_type=entity_type, entity_id=entity_id, limit=limit)
    return [AuditLogResponse.from_record(record) for record in records]
