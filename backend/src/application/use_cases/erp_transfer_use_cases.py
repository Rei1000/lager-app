"""Use cases for controlled ERP write preparation flow."""

from __future__ import annotations

from application.dtos import ChangeErpTransferStatusCommand, CreateErpTransferRequestCommand
from domain.entities import ErpTransferRequest
from ports.audit_log_port import AuditLogPort
from ports.erp_transfer_repository_port import ErpTransferRepositoryPort, ErpTransferRequestRecord
from ports.erp_write_port import ErpWritePort


class CreateErpTransferRequestUseCase:
    def __init__(
        self,
        transfer_repository: ErpTransferRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._transfer_repository = transfer_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: CreateErpTransferRequestCommand) -> ErpTransferRequestRecord:
        transfer = ErpTransferRequest(
            order_id=command.order_id,
            material_article_number=command.material_article_number,
            requested_by_user_id=command.requested_by_user_id,
            payload=command.payload,
        )
        created = self._transfer_repository.create_transfer_request(
            order_id=transfer.order_id,
            material_article_number=transfer.material_article_number,
            requested_by_user_id=transfer.requested_by_user_id,
            payload=transfer.payload,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(created.id),
                action="created",
                user_id=transfer.requested_by_user_id,
                payload={
                    "order_id": transfer.order_id,
                    "material_article_number": transfer.material_article_number,
                },
            )
        return created


class ListErpTransferRequestsUseCase:
    def __init__(self, transfer_repository: ErpTransferRepositoryPort) -> None:
        self._transfer_repository = transfer_repository

    def execute(self) -> list[ErpTransferRequestRecord]:
        return self._transfer_repository.list_transfer_requests()


class MarkErpTransferReadyUseCase:
    def __init__(
        self,
        transfer_repository: ErpTransferRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._transfer_repository = transfer_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeErpTransferStatusCommand) -> ErpTransferRequestRecord:
        current = self._transfer_repository.get_transfer_request(command.transfer_id)
        transfer = ErpTransferRequest(
            order_id=current.order_id,
            material_article_number=current.material_article_number,
            requested_by_user_id=current.requested_by_user_id,
            payload=current.payload,
            status=current.status,
            failure_reason=current.failure_reason,
            created_at=current.created_at,
            ready_at=current.ready_at,
            approved_at=current.approved_at,
            sent_at=current.sent_at,
            failed_at=current.failed_at,
        )
        transfer.transition_to("ready")
        updated = self._transfer_repository.update_transfer_status(
            transfer_id=command.transfer_id,
            status=transfer.status,
            acting_user_id=command.acting_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(updated.id),
                action="ready",
                user_id=command.acting_user_id,
            )
        return updated


class MarkErpTransferSentUseCase:
    def __init__(
        self,
        transfer_repository: ErpTransferRepositoryPort,
        erp_write_port: ErpWritePort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._transfer_repository = transfer_repository
        self._erp_write_port = erp_write_port
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeErpTransferStatusCommand) -> ErpTransferRequestRecord:
        current = self._transfer_repository.get_transfer_request(command.transfer_id)
        transfer = ErpTransferRequest(
            order_id=current.order_id,
            material_article_number=current.material_article_number,
            requested_by_user_id=current.requested_by_user_id,
            payload=current.payload,
            status=current.status,
            failure_reason=current.failure_reason,
            created_at=current.created_at,
            ready_at=current.ready_at,
            approved_at=current.approved_at,
            sent_at=current.sent_at,
            failed_at=current.failed_at,
        )
        transfer.transition_to("sent")
        write_payload = {
            "transfer_id": current.id,
            "order_id": current.order_id,
            "material_article_number": current.material_article_number,
            "payload": current.payload or {},
        }
        write_context = {"transfer_id": current.id}
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(current.id),
                action="send_attempted",
                user_id=command.acting_user_id,
            )
        try:
            erp_response = self._erp_write_port.send_transfer(
                transfer_payload=write_payload,
                context=write_context,
            )
        except ValueError as exc:
            failure_reason = str(exc)
            failed = self._transfer_repository.update_transfer_status(
                transfer_id=command.transfer_id,
                status="failed",
                acting_user_id=command.acting_user_id,
                failure_reason=failure_reason,
            )
            if self._audit_log_port is not None:
                self._audit_log_port.log_event(
                    entity_type="erp_transfer",
                    entity_id=str(failed.id),
                    action="failed",
                    user_id=command.acting_user_id,
                    comment=failure_reason,
                )
            return failed
        updated = self._transfer_repository.update_transfer_status(
            transfer_id=command.transfer_id,
            status=transfer.status,
            acting_user_id=command.acting_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(updated.id),
                action="sent",
                user_id=command.acting_user_id,
                payload={"erp_response_received": bool(erp_response)},
            )
        return updated


class MarkErpTransferFailedUseCase:
    def __init__(
        self,
        transfer_repository: ErpTransferRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._transfer_repository = transfer_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeErpTransferStatusCommand) -> ErpTransferRequestRecord:
        current = self._transfer_repository.get_transfer_request(command.transfer_id)
        transfer = ErpTransferRequest(
            order_id=current.order_id,
            material_article_number=current.material_article_number,
            requested_by_user_id=current.requested_by_user_id,
            payload=current.payload,
            status=current.status,
            failure_reason=current.failure_reason,
            created_at=current.created_at,
            ready_at=current.ready_at,
            approved_at=current.approved_at,
            sent_at=current.sent_at,
            failed_at=current.failed_at,
        )
        transfer.transition_to("failed")
        updated = self._transfer_repository.update_transfer_status(
            transfer_id=command.transfer_id,
            status=transfer.status,
            acting_user_id=command.acting_user_id,
            failure_reason=command.failure_reason,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(updated.id),
                action="failed",
                user_id=command.acting_user_id,
                comment=command.failure_reason,
            )
        return updated


class ApproveErpTransferUseCase:
    def __init__(
        self,
        transfer_repository: ErpTransferRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._transfer_repository = transfer_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: ChangeErpTransferStatusCommand) -> ErpTransferRequestRecord:
        current = self._transfer_repository.get_transfer_request(command.transfer_id)
        transfer = ErpTransferRequest(
            order_id=current.order_id,
            material_article_number=current.material_article_number,
            requested_by_user_id=current.requested_by_user_id,
            payload=current.payload,
            status=current.status,
            failure_reason=current.failure_reason,
            created_at=current.created_at,
            ready_at=current.ready_at,
            approved_at=current.approved_at,
            sent_at=current.sent_at,
            failed_at=current.failed_at,
        )
        transfer.transition_to("approved")
        updated = self._transfer_repository.update_transfer_status(
            transfer_id=command.transfer_id,
            status=transfer.status,
            acting_user_id=command.acting_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="erp_transfer",
                entity_id=str(updated.id),
                action="approved",
                user_id=command.acting_user_id,
            )
        return updated
