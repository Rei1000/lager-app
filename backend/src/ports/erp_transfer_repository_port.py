"""Repository contract for ERP transfer preparation records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class ErpTransferRequestRecord:
    id: int
    order_id: str
    material_article_number: str
    status: str
    requested_by_user_id: int
    payload: dict[str, Any] | None
    created_at: datetime
    ready_by_user_id: int | None = None
    approved_by_user_id: int | None = None
    sent_by_user_id: int | None = None
    failed_by_user_id: int | None = None
    ready_at: datetime | None = None
    approved_at: datetime | None = None
    sent_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None


class ErpTransferRepositoryPort(Protocol):
    def create_transfer_request(
        self,
        *,
        order_id: str,
        material_article_number: str,
        requested_by_user_id: int,
        payload: dict[str, Any] | None,
    ) -> ErpTransferRequestRecord:
        """Persist one ERP transfer request in draft state."""

    def list_transfer_requests(self) -> list[ErpTransferRequestRecord]:
        """Return all ERP transfer requests."""

    def get_transfer_request(self, transfer_id: int) -> ErpTransferRequestRecord:
        """Return one ERP transfer request."""

    def update_transfer_status(
        self,
        *,
        transfer_id: int,
        status: str,
        acting_user_id: int,
        failure_reason: str | None = None,
    ) -> ErpTransferRequestRecord:
        """Update status and audit fields for one transfer request."""
