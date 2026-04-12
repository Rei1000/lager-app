"""Use cases for photo upload and retrieval."""

from __future__ import annotations

from application.dtos import ListPhotosForEntityCommand, UploadPhotoCommand
from domain.entities import PhotoAttachment
from ports.audit_log_port import AuditLogPort
from ports.file_storage_port import FileStoragePort, StoredFile
from ports.photo_repository_port import PhotoRecord, PhotoRepositoryPort


class UploadPhotoUseCase:
    def __init__(
        self,
        *,
        photo_repository: PhotoRepositoryPort,
        file_storage: FileStoragePort,
        audit_log_port: AuditLogPort | None = None,
    ) -> None:
        self._photo_repository = photo_repository
        self._file_storage = file_storage
        self._audit_log_port = audit_log_port

    def execute(self, command: UploadPhotoCommand) -> PhotoRecord:
        attachment = PhotoAttachment(
            entity_type=command.entity_type,
            entity_id=command.entity_id,
            uploaded_by_user_id=command.uploaded_by_user_id,
            comment=command.comment,
        )
        file_key = self._file_storage.save(
            filename=command.original_filename,
            content=command.content,
            content_type=command.content_type,
        )
        created = self._photo_repository.create_photo(
            entity_type=attachment.entity_type,
            entity_id=attachment.entity_id,
            file_key=file_key,
            original_filename=command.original_filename,
            content_type=command.content_type,
            uploaded_by_user_id=attachment.uploaded_by_user_id,
            comment=attachment.comment,
        )
        if self._audit_log_port is not None:
            self._audit_log_port.log_event(
                entity_type="photo",
                entity_id=str(created.id),
                action="uploaded",
                user_id=attachment.uploaded_by_user_id,
                payload={
                    "context_entity_type": created.entity_type,
                    "context_entity_id": created.entity_id,
                },
                comment=created.comment,
            )
        return created


class ListPhotosForEntityUseCase:
    def __init__(self, *, photo_repository: PhotoRepositoryPort) -> None:
        self._photo_repository = photo_repository

    def execute(self, command: ListPhotosForEntityCommand) -> list[PhotoRecord]:
        return self._photo_repository.list_photos_for_entity(
            entity_type=command.entity_type,
            entity_id=command.entity_id,
        )


class GetPhotoContentUseCase:
    def __init__(
        self,
        *,
        photo_repository: PhotoRepositoryPort,
        file_storage: FileStoragePort,
    ) -> None:
        self._photo_repository = photo_repository
        self._file_storage = file_storage

    def execute(self, photo_id: int) -> tuple[PhotoRecord, StoredFile]:
        metadata = self._photo_repository.get_photo(photo_id)
        stored = self._file_storage.load(file_key=metadata.file_key)
        return metadata, stored
