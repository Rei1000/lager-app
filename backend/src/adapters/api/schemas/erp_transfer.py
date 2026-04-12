"""Schemas for ERP transfer preparation endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ports.erp_transfer_repository_port import ErpTransferRequestRecord


class CreateErpTransferRequest(BaseModel):
    order_id: str = Field(min_length=1)
    material_article_number: str = Field(min_length=1)
    requested_by_user_id: int = Field(gt=0)
    payload: dict[str, Any] | None = None


class ChangeErpTransferStatusRequest(BaseModel):
    acting_user_id: int = Field(gt=0)
    failure_reason: str | None = None


class ErpTransferResponse(BaseModel):
    id: int
    order_id: str
    material_article_number: str
    status: str
    requested_by_user_id: int
    payload: dict[str, Any] | None
    created_at: datetime
    ready_by_user_id: int | None
    approved_by_user_id: int | None
    sent_by_user_id: int | None
    failed_by_user_id: int | None
    ready_at: datetime | None
    approved_at: datetime | None
    sent_at: datetime | None
    failed_at: datetime | None
    failure_reason: str | None

    @classmethod
    def from_record(cls, record: ErpTransferRequestRecord) -> "ErpTransferResponse":
        return cls(
            id=record.id,
            order_id=record.order_id,
            material_article_number=record.material_article_number,
            status=record.status,
            requested_by_user_id=record.requested_by_user_id,
            payload=record.payload,
            created_at=record.created_at,
            ready_by_user_id=record.ready_by_user_id,
            approved_by_user_id=record.approved_by_user_id,
            sent_by_user_id=record.sent_by_user_id,
            failed_by_user_id=record.failed_by_user_id,
            ready_at=record.ready_at,
            approved_at=record.approved_at,
            sent_at=record.sent_at,
            failed_at=record.failed_at,
            failure_reason=record.failure_reason,
        )
