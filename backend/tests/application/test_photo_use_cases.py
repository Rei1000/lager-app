from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from application.dtos import ListPhotosForEntityCommand, UploadPhotoCommand
from application.use_cases.photo_use_cases import (
    GetPhotoContentUseCase,
    ListPhotosForEntityUseCase,
    UploadPhotoUseCase,
)
from ports.audit_log_port import AuditLogPort, AuditLogRecord
from ports.file_storage_port import FileStoragePort, StoredFile
from ports.photo_repository_port import PhotoRecord, PhotoRepositoryPort


@dataclass
class FakePhotoRepository(PhotoRepositoryPort):
    records: list[PhotoRecord] = field(default_factory=list)

    def create_photo(
        self,
        *,
        entity_type: str,
        entity_id: str,
        file_key: str,
        original_filename: str,
        content_type: str | None,
        uploaded_by_user_id: int,
        comment: str | None,
    ) -> PhotoRecord:
        record = PhotoRecord(
            id=len(self.records) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            file_key=file_key,
            original_filename=original_filename,
            content_type=content_type,
            uploaded_by_user_id=uploaded_by_user_id,
            uploaded_at=datetime.now(timezone.utc),
            comment=comment,
        )
        self.records.append(record)
        return record

    def list_photos_for_entity(
        self,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[PhotoRecord]:
        return [
            item
            for item in self.records
            if item.entity_type == entity_type and item.entity_id == entity_id
        ]

    def get_photo(self, photo_id: int) -> PhotoRecord:
        for item in self.records:
            if item.id == photo_id:
                return item
        raise ValueError("Foto nicht gefunden")


@dataclass
class FakeStorage(FileStoragePort):
    saved: dict[str, bytes] = field(default_factory=dict)

    def save(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> str:
        key = f"saved-{filename}"
        self.saved[key] = content
        return key

    def load(self, *, file_key: str) -> StoredFile:
        return StoredFile(content=self.saved[file_key], content_type="image/jpeg")

    def delete(self, *, file_key: str) -> None:
        self.saved.pop(file_key, None)


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
        event = AuditLogRecord(
            id=len(self.events) + 1,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            occurred_at=datetime.now(timezone.utc),
            payload=payload,
            comment=comment,
        )
        self.events.append(event)
        return event

    def list_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        return self.events[:limit]


def test_upload_and_list_photos_for_entity() -> None:
    repo = FakePhotoRepository()
    storage = FakeStorage()
    audit = FakeAuditLogPort()
    upload = UploadPhotoUseCase(photo_repository=repo, file_storage=storage, audit_log_port=audit)
    list_use_case = ListPhotosForEntityUseCase(photo_repository=repo)

    created = upload.execute(
        UploadPhotoCommand(
            entity_type="inventory_count",
            entity_id="5",
            original_filename="count.jpg",
            content=b"binary-data",
            content_type="image/jpeg",
            uploaded_by_user_id=2,
            comment="Nachtschicht",
        )
    )
    listed = list_use_case.execute(
        ListPhotosForEntityCommand(entity_type="inventory_count", entity_id="5")
    )

    assert created.file_key == "saved-count.jpg"
    assert len(listed) == 1
    assert listed[0].comment == "Nachtschicht"
    assert [event.action for event in audit.events] == ["uploaded"]


def test_get_photo_content_loads_from_storage() -> None:
    repo = FakePhotoRepository()
    storage = FakeStorage()
    upload = UploadPhotoUseCase(photo_repository=repo, file_storage=storage)
    get_content = GetPhotoContentUseCase(photo_repository=repo, file_storage=storage)
    created = upload.execute(
        UploadPhotoCommand(
            entity_type="material",
            entity_id="ART-001",
            original_filename="mat.jpg",
            content=b"material-photo",
            uploaded_by_user_id=1,
        )
    )

    metadata, stored = get_content.execute(created.id)

    assert metadata.original_filename == "mat.jpg"
    assert stored.content == b"material-photo"
