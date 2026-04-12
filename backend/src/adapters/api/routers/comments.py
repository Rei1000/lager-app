"""Comment API router for simple entity-bound communication."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import (
    RequestUser,
    require_authenticated_user,
    require_lager_plus,
)
from adapters.api.dependencies.use_cases import (
    get_create_comment_use_case,
    get_list_comments_for_entity_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.comments import CommentResponse, CreateCommentRequest
from application.dtos import CreateCommentCommand, ListCommentsForEntityCommand
from application.use_cases.comment_use_cases import (
    CreateCommentUseCase,
    ListCommentsForEntityUseCase,
)

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=CommentResponse, status_code=201)
def create_comment(
    payload: CreateCommentRequest,
    use_case: CreateCommentUseCase = Depends(get_create_comment_use_case),
    current_user: RequestUser = Depends(require_lager_plus),
) -> CommentResponse:
    try:
        created = use_case.execute(
            CreateCommentCommand(
                entity_type=payload.entity_type,
                entity_id=payload.entity_id,
                text=payload.text,
                created_by_user_id=current_user.user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return CommentResponse.from_record(created)


@router.get("", response_model=list[CommentResponse])
def list_comments(
    entity_type: str,
    entity_id: str,
    use_case: ListCommentsForEntityUseCase = Depends(get_list_comments_for_entity_use_case),
) -> list[CommentResponse]:
    try:
        comments = use_case.execute(
            ListCommentsForEntityCommand(
                entity_type=entity_type,
                entity_id=entity_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return [CommentResponse.from_record(item) for item in comments]
