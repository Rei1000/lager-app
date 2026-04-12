"""Pydantic schemas for authentication endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from adapters.api.dependencies.auth import RequestUser
from application.use_cases.auth_use_cases import LoginResult


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    login_type: Literal["erp", "admin"]
    selected_connection: Literal["sage-simulator", "sage-connect", "middleware"]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in_seconds: int
    user_id: int
    username: str
    role_code: str
    login_type: str
    selected_connection: str

    @classmethod
    def from_use_case_result(cls, result: LoginResult) -> "LoginResponse":
        return cls(
            access_token=result.access_token,
            token_type=result.token_type,
            expires_in_seconds=result.expires_in_seconds,
            user_id=result.user_id,
            username=result.username,
            role_code=result.role_code,
            login_type=result.login_type,
            selected_connection=result.selected_connection,
        )


class CurrentUserResponse(BaseModel):
    user_id: int
    username: str
    role_code: str
    role_name: str
    login_type: str
    selected_connection: str

    @classmethod
    def from_request_user(cls, user: RequestUser) -> "CurrentUserResponse":
        return cls(
            user_id=user.user_id,
            username=user.username,
            role_code=user.role_code,
            role_name=user.role_name,
            login_type=user.login_type,
            selected_connection=user.selected_connection,
        )
