"""Use cases for simple entity-bound comments."""

from __future__ import annotations

from application.dtos import CreateCommentCommand, ListCommentsForEntityCommand
from domain.entities import Comment
from ports.audit_log_port import AuditLogPort
from ports.comment_repository_port import CommentRecord, CommentRepositoryPort


class CreateCommentUseCase:
    def __init__(
        self,
        *,
        comment_repository: CommentRepositoryPort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._comment_repository = comment_repository
        self._audit_log_port = audit_log_port

    def execute(self, command: CreateCommentCommand) -> CommentRecord:
        comment = Comment(
            entity_type=command.entity_type,
            entity_id=command.entity_id,
            text=command.text,
            created_by_user_id=command.created_by_user_id,
        )
        created = self._comment_repository.save_comment(
            entity_type=comment.entity_type,
            entity_id=comment.entity_id,
            text=comment.text,
            created_by_user_id=comment.created_by_user_id,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="comment",
                entity_id=str(created.id),
                action="created",
                user_id=created.created_by_user_id,
                payload={
                    "context_entity_type": created.entity_type,
                    "context_entity_id": created.entity_id,
                },
            )
        return created


class ListCommentsForEntityUseCase:
    def __init__(self, *, comment_repository: CommentRepositoryPort) -> None:
        self._comment_repository = comment_repository

    def execute(self, command: ListCommentsForEntityCommand) -> list[CommentRecord]:
        return self._comment_repository.list_by_entity(
            entity_type=command.entity_type,
            entity_id=command.entity_id,
        )
