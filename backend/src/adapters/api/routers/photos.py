"""Photo upload/list/download API router."""

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from adapters.api.dependencies.auth import (
    RequestUser,
    require_authenticated_user,
    require_lager_plus,
)
from adapters.api.dependencies.use_cases import (
    get_get_photo_content_use_case,
    get_list_photos_for_entity_use_case,
    get_upload_photo_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.photos import PhotoResponse
from application.dtos import ListPhotosForEntityCommand, UploadPhotoCommand
from application.use_cases.photo_use_cases import (
    GetPhotoContentUseCase,
    ListPhotosForEntityUseCase,
    UploadPhotoUseCase,
)

router = APIRouter(
    prefix="/photos",
    tags=["photos"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=PhotoResponse, status_code=201)
async def upload_photo(
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    comment: str | None = Form(default=None),
    file: UploadFile = File(...),
    use_case: UploadPhotoUseCase = Depends(get_upload_photo_use_case),
    current_user: RequestUser = Depends(require_lager_plus),
) -> PhotoResponse:
    try:
        created = use_case.execute(
            UploadPhotoCommand(
                entity_type=entity_type,
                entity_id=entity_id,
                original_filename=file.filename or "upload.bin",
                content=await file.read(),
                content_type=file.content_type,
                uploaded_by_user_id=current_user.user_id,
                comment=comment,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return PhotoResponse.from_record(created)


@router.get("", response_model=list[PhotoResponse])
def list_photos_for_entity(
    entity_type: str,
    entity_id: str,
    use_case: ListPhotosForEntityUseCase = Depends(get_list_photos_for_entity_use_case),
) -> list[PhotoResponse]:
    try:
        photos = use_case.execute(
            ListPhotosForEntityCommand(
                entity_type=entity_type,
                entity_id=entity_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return [PhotoResponse.from_record(item) for item in photos]


@router.get("/{photo_id}/file")
def download_photo_file(
    photo_id: int,
    use_case: GetPhotoContentUseCase = Depends(get_get_photo_content_use_case),
) -> StreamingResponse:
    try:
        metadata, stored = use_case.execute(photo_id)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    media_type = metadata.content_type or stored.content_type or "application/octet-stream"
    return StreamingResponse(
        BytesIO(stored.content),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{metadata.original_filename}"'},
    )
