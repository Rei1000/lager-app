from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pytest

from application.dtos import ChangeErpTransferStatusCommand, CreateErpTransferRequestCommand
from application.use_cases.erp_transfer_use_cases import (
    ApproveErpTransferUseCase,
    CreateErpTransferRequestUseCase,
    ListErpTransferRequestsUseCase,
    MarkErpTransferFailedUseCase,
    MarkErpTransferReadyUseCase,
    MarkErpTransferSentUseCase,
)
from ports.audit_log_port import AuditLogPort, AuditLogRecord
from ports.erp_transfer_repository_port import ErpTransferRepositoryPort, ErpTransferRequestRecord
from ports.erp_write_port import ErpWritePort


@dataclass
class FakeErpTransferRepository(ErpTransferRepositoryPort):
    records: list[ErpTransferRequestRecord] = field(default_factory=list)

    def create_transfer_request(
        self,
        *,
        order_id: str,
        material_article_number: str,
        requested_by_user_id: int,
        payload: dict[str, Any] | None,
    ) -> ErpTransferRequestRecord:
        record = ErpTransferRequestRecord(
            id=len(self.records) + 1,
            order_id=order_id,
            material_article_number=material_article_number,
            status="draft",
            requested_by_user_id=requested_by_user_id,
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
        self.records.append(record)
        return record

    def list_transfer_requests(self) -> list[ErpTransferRequestRecord]:
        return list(self.records)

    def get_transfer_request(self, transfer_id: int) -> ErpTransferRequestRecord:
        for item in self.records:
            if item.id == transfer_id:
                return item
        raise ValueError("ERP-Transfer nicht gefunden")

    def update_transfer_status(
        self,
        *,
        transfer_id: int,
        status: str,
        acting_user_id: int,
        failure_reason: str | None = None,
    ) -> ErpTransferRequestRecord:
        current = self.get_transfer_request(transfer_id)
        updated = ErpTransferRequestRecord(
            id=current.id,
            order_id=current.order_id,
            material_article_number=current.material_article_number,
            status=status,
            requested_by_user_id=current.requested_by_user_id,
            payload=current.payload,
            created_at=current.created_at,
            ready_by_user_id=acting_user_id if status == "ready" else current.ready_by_user_id,
            approved_by_user_id=acting_user_id if status == "approved" else current.approved_by_user_id,
            sent_by_user_id=acting_user_id if status == "sent" else current.sent_by_user_id,
            failed_by_user_id=acting_user_id if status == "failed" else current.failed_by_user_id,
            ready_at=datetime.now(timezone.utc) if status == "ready" else current.ready_at,
            approved_at=datetime.now(timezone.utc) if status == "approved" else current.approved_at,
            sent_at=datetime.now(timezone.utc) if status == "sent" else current.sent_at,
            failed_at=datetime.now(timezone.utc) if status == "failed" else current.failed_at,
            failure_reason=failure_reason if status == "failed" else None,
        )
        index = self.records.index(current)
        self.records[index] = updated
        return updated


@dataclass
class FakeErpWritePort(ErpWritePort):
    should_fail: bool = False
    sent_payloads: list[dict[str, Any]] = field(default_factory=list)
    sent_contexts: list[dict[str, Any] | None] = field(default_factory=list)

    def send_transfer(
        self,
        *,
        transfer_payload: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        self.sent_payloads.append(transfer_payload)
        self.sent_contexts.append(context)
        if self.should_fail:
            raise ValueError("ERP nicht erreichbar")
        return {"transfer_state": "accepted"}


@dataclass
class FakeAuditLogPort(AuditLogPort):
    events: list[AuditLogRecord] = field(default_factory=list)

    def log_event(
        self,
        *,
        entity_type: str,
        entity_id: str | None,
        action: str,
        user_id: int | None,
        payload: dict[str, object] | None = None,
        comment: str | None = None,
    ) -> AuditLogRecord:
        record = AuditLogRecord(
            id=len(self.events) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            occurred_at=datetime.now(timezone.utc),
            payload=payload,
            comment=comment,
        )
        self.events.append(record)
        return record

    def list_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        return self.events[:limit]


def test_create_and_list_erp_transfer_requests_use_cases() -> None:
    repo = FakeErpTransferRepository()
    create_use_case = CreateErpTransferRequestUseCase(transfer_repository=repo)
    list_use_case = ListErpTransferRequestsUseCase(transfer_repository=repo)

    created = create_use_case.execute(
        CreateErpTransferRequestCommand(
            order_id="ORD-10",
            material_article_number="ART-001",
            requested_by_user_id=7,
            payload={"amount_mm": 4000},
        )
    )
    listed = list_use_case.execute()

    assert created.status == "draft"
    assert len(listed) == 1
    assert listed[0].order_id == "ORD-10"


def test_mark_erp_transfer_status_use_cases() -> None:
    repo = FakeErpTransferRepository()
    erp_write_port = FakeErpWritePort()
    created = repo.create_transfer_request(
        order_id="ORD-20",
        material_article_number="ART-002",
        requested_by_user_id=2,
        payload={"amount_mm": 5000},
    )
    ready_use_case = MarkErpTransferReadyUseCase(transfer_repository=repo)
    approve_use_case = ApproveErpTransferUseCase(transfer_repository=repo)
    sent_use_case = MarkErpTransferSentUseCase(
        transfer_repository=repo,
        erp_write_port=erp_write_port,
    )
    fail_use_case = MarkErpTransferFailedUseCase(transfer_repository=repo)

    ready = ready_use_case.execute(
        ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=3)
    )
    approved = approve_use_case.execute(
        ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=4)
    )
    sent = sent_use_case.execute(
        ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=5)
    )

    retry_seed = repo.create_transfer_request(
        order_id="ORD-21",
        material_article_number="ART-002",
        requested_by_user_id=2,
        payload=None,
    )
    failed = fail_use_case.execute(
        ChangeErpTransferStatusCommand(
            transfer_id=retry_seed.id,
            acting_user_id=5,
            failure_reason="ERP-Wartung",
        )
    )

    assert ready.status == "ready"
    assert approved.status == "approved"
    assert sent.status == "sent"
    assert erp_write_port.sent_payloads[0]["order_id"] == "ORD-20"
    assert failed.status == "failed"
    assert failed.failure_reason == "ERP-Wartung"


def test_mark_sent_requires_approved_state() -> None:
    repo = FakeErpTransferRepository()
    erp_write_port = FakeErpWritePort()
    created = repo.create_transfer_request(
        order_id="ORD-30",
        material_article_number="ART-003",
        requested_by_user_id=9,
        payload=None,
    )
    ready_use_case = MarkErpTransferReadyUseCase(transfer_repository=repo)
    sent_use_case = MarkErpTransferSentUseCase(
        transfer_repository=repo,
        erp_write_port=erp_write_port,
    )
    ready_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=2))

    with pytest.raises(ValueError):
        sent_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=3))

    assert erp_write_port.sent_payloads == []


def test_mark_sent_sets_failed_on_erp_write_error() -> None:
    repo = FakeErpTransferRepository()
    erp_write_port = FakeErpWritePort(should_fail=True)
    audit_log_port = FakeAuditLogPort()
    created = repo.create_transfer_request(
        order_id="ORD-40",
        material_article_number="ART-004",
        requested_by_user_id=9,
        payload={"amount_mm": 1234},
    )
    ready_use_case = MarkErpTransferReadyUseCase(transfer_repository=repo)
    approve_use_case = ApproveErpTransferUseCase(transfer_repository=repo)
    sent_use_case = MarkErpTransferSentUseCase(
        transfer_repository=repo,
        erp_write_port=erp_write_port,
        audit_log_port=audit_log_port,
    )
    ready_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=2))
    approve_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=2))

    failed = sent_use_case.execute(
        ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=3)
    )

    assert failed.status == "failed"
    assert failed.failure_reason == "ERP nicht erreichbar"
    assert [event.action for event in audit_log_port.events] == ["send_attempted", "failed"]


def test_mark_sent_writes_send_attempt_and_success_audit_events() -> None:
    repo = FakeErpTransferRepository()
    erp_write_port = FakeErpWritePort()
    audit_log_port = FakeAuditLogPort()
    created = repo.create_transfer_request(
        order_id="ORD-50",
        material_article_number="ART-005",
        requested_by_user_id=4,
        payload={"amount_mm": 3000},
    )
    ready_use_case = MarkErpTransferReadyUseCase(transfer_repository=repo)
    approve_use_case = ApproveErpTransferUseCase(transfer_repository=repo)
    sent_use_case = MarkErpTransferSentUseCase(
        transfer_repository=repo,
        erp_write_port=erp_write_port,
        audit_log_port=audit_log_port,
    )
    ready_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=2))
    approve_use_case.execute(ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=2))

    sent = sent_use_case.execute(
        ChangeErpTransferStatusCommand(transfer_id=created.id, acting_user_id=3)
    )

    assert sent.status == "sent"
    assert [event.action for event in audit_log_port.events] == ["send_attempted", "sent"]
