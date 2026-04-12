"""Authentication and authorization dependencies for API routers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fastapi import Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from adapters.api.dependencies.use_cases import (
    get_auth_token_service,
    get_current_user_use_case,
)
from application.use_cases.auth_use_cases import GetCurrentUserUseCase
from ports.auth_identity_port import AuthIdentityRecord
from ports.auth_token_port import AuthTokenPort

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@dataclass(frozen=True)
class RequestUser:
    user_id: int
    username: str
    role_code: str
    role_name: str
    login_type: str = "admin"
    selected_connection: str = "sage-simulator"


def get_current_request_user(
    token: str = Depends(oauth2_scheme),
    token_service: AuthTokenPort = Depends(get_auth_token_service),
    current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> RequestUser:
    try:
        payload = token_service.decode_access_token(token)
        user_id = int(payload.sub)
        identity: AuthIdentityRecord = current_user_use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nicht authentifiziert",
        ) from exc
    return RequestUser(
        user_id=identity.user_id,
        username=identity.username,
        role_code=identity.role_code,
        role_name=identity.role_name,
        login_type=payload.login_type,
        selected_connection=payload.selected_connection,
    )


def require_authenticated_user(
    current_user: RequestUser = Depends(get_current_request_user),
) -> RequestUser:
    return current_user


def require_any_role(*role_codes: str) -> Callable[[RequestUser], RequestUser]:
    allowed = set(role_codes)

    def checker(current_user: RequestUser = Depends(require_authenticated_user)) -> RequestUser:
        if current_user.role_code not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff verweigert",
            )
        return current_user

    return checker


def require_role(role_code: str) -> Callable[[RequestUser], RequestUser]:
    return require_any_role(role_code)


require_lager_plus = require_any_role("lager", "leitung", "admin")
require_leitung_or_admin = require_any_role("leitung", "admin")


def require_admin_user(
    current_user: RequestUser = Depends(require_role("admin")),
) -> RequestUser:
    return current_user
