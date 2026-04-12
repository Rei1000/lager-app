"""SQLAlchemy auth identity adapter."""

from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from adapters.persistence.db import get_session
from adapters.persistence.models.access import UserModel
from ports.auth_identity_port import AuthIdentityPort, AuthIdentityRecord


class SqlAlchemyAuthIdentityRepository(AuthIdentityPort):
    def __init__(self, session_factory: Callable[[], Session] = get_session) -> None:
        self._session_factory = session_factory

    def get_by_username(self, username: str) -> AuthIdentityRecord | None:
        with self._session_factory() as session:
            user = (
                session.query(UserModel)
                .join(UserModel.role)
                .filter(UserModel.username == username)
                .one_or_none()
            )
            if user is None:
                return None
            return self._to_record(user)

    def get_by_id(self, user_id: int) -> AuthIdentityRecord | None:
        with self._session_factory() as session:
            user = session.query(UserModel).join(UserModel.role).filter(UserModel.id == user_id).one_or_none()
            if user is None:
                return None
            return self._to_record(user)

    def get_by_erp_user_reference(self, erp_user_reference: str) -> AuthIdentityRecord | None:
        with self._session_factory() as session:
            user = (
                session.query(UserModel)
                .join(UserModel.role)
                .filter(UserModel.erp_user_reference == erp_user_reference)
                .one_or_none()
            )
            if user is None:
                return None
            return self._to_record(user)

    @staticmethod
    def _to_record(model: UserModel) -> AuthIdentityRecord:
        return AuthIdentityRecord(
            user_id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            role_code=model.role.code,
            role_name=model.role.name,
            is_active=model.is_active,
        )
