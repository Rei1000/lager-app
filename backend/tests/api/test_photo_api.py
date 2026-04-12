from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_get_photo_content_use_case,
    get_list_photos_for_entity_use_case,
    get_upload_photo_use_case,
)
from ports.file_storage_port import StoredFile
from ports.photo_repository_port import PhotoRecord


def _photo_record(photo_id: int = 1) -> PhotoRecord:
    return PhotoRecord(
        id=photo_id,
        entity_type="inventory_count",
        entity_id="7",
        file_key="file-1.jpg",
        original_filename="count.jpg",
        content_type="image/jpeg",
        uploaded_by_user_id=2,
        uploaded_at=datetime.now(timezone.utc),
        comment="Belegfoto",
    )


def test_photo_upload_and_list_endpoints() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeUploadPhotoUseCase:
        def execute(self, _command: object) -> PhotoRecord:
            return _photo_record(photo_id=5)

    class FakeListPhotoUseCase:
        def execute(self, _command: object) -> list[PhotoRecord]:
            return [_photo_record(photo_id=5)]

    app.dependency_overrides[get_upload_photo_use_case] = lambda: FakeUploadPhotoUseCase()
    app.dependency_overrides[get_list_photos_for_entity_use_case] = lambda: FakeListPhotoUseCase()
    client = TestClient(app)

    upload_response = client.post(
        "/photos",
        data={
            "entity_type": "inventory_count",
            "entity_id": "7",
            "comment": "Belegfoto",
        },
        files={"file": ("count.jpg", b"binary", "image/jpeg")},
    )
    list_response = client.get("/photos?entity_type=inventory_count&entity_id=7")

    assert upload_response.status_code == 201
    assert upload_response.json()["id"] == 5
    assert list_response.status_code == 200
    assert list_response.json()[0]["file_url"] == "/photos/5/file"
    app.dependency_overrides.clear()


def test_photo_download_endpoint_returns_file_content() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="leitung",
        role_code="leitung",
        role_name="Leitung",
    )

    class FakeGetPhotoContentUseCase:
        def execute(self, _photo_id: int) -> tuple[PhotoRecord, StoredFile]:
            return _photo_record(), StoredFile(content=b"photo-content", content_type="image/jpeg")

    app.dependency_overrides[get_get_photo_content_use_case] = lambda: FakeGetPhotoContentUseCase()
    client = TestClient(app)

    response = client.get("/photos/1/file")

    assert response.status_code == 200
    assert response.content == b"photo-content"
    assert response.headers["content-type"].startswith("image/jpeg")
    app.dependency_overrides.clear()


def test_photo_upload_requires_lager_plus_role() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=3,
        username="gast",
        role_code="gast",
        role_name="Gast",
    )
    client = TestClient(app)

    response = client.post(
        "/photos",
        data={"entity_type": "material", "entity_id": "ART-1"},
        files={"file": ("m.jpg", b"binary", "image/jpeg")},
    )

    assert response.status_code == 403
    app.dependency_overrides.clear()
