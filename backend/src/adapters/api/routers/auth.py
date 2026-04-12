"""Authentication API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import RequestUser, get_current_request_user
from adapters.api.dependencies.use_cases import get_login_use_case
from adapters.api.errors import map_value_error
from adapters.api.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse
from application.dtos import LoginCommand
from application.use_cases.auth_use_cases import LoginUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> LoginResponse:
    try:
        result = use_case.execute(
            LoginCommand(
                username=payload.username,
                password=payload.password,
                login_type=payload.login_type,
                selected_connection=payload.selected_connection,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return LoginResponse.from_use_case_result(result)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: RequestUser = Depends(get_current_request_user)) -> CurrentUserResponse:
    return CurrentUserResponse.from_request_user(current_user)
