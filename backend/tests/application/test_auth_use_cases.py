from __future__ import annotations

from dataclasses import dataclass

import pytest

from adapters.auth.password_hasher import Pbkdf2PasswordHasher
from adapters.auth.token_service import HmacTokenService
from application.dtos import LoginCommand
from application.errors import AuthenticationError, AuthorizationError
from application.use_cases.auth_use_cases import GetCurrentUserUseCase, LoginUseCase
from ports.auth_identity_port import AuthIdentityPort, AuthIdentityRecord
from ports.erp_authentication_port import ErpAuthenticatedIdentity, ErpAuthenticationPort


@dataclass
class FakeAuthIdentityPort(AuthIdentityPort):
    identities: list[AuthIdentityRecord]

    def get_by_username(self, username: str) -> AuthIdentityRecord | None:
        for identity in self.identities:
            if identity.username == username:
                return identity
        return None

    def get_by_id(self, user_id: int) -> AuthIdentityRecord | None:
        for identity in self.identities:
            if identity.user_id == user_id:
                return identity
        return None

    def get_by_erp_user_reference(self, erp_user_reference: str) -> AuthIdentityRecord | None:
        for identity in self.identities:
            if identity.username == erp_user_reference:
                return identity
        return None


@dataclass
class FakeErpAuthenticationPort(ErpAuthenticationPort):
    users: dict[str, str]

    def authenticate(self, username: str, password: str) -> ErpAuthenticatedIdentity | None:
        expected_password = self.users.get(username)
        if expected_password != password:
            return None
        return ErpAuthenticatedIdentity(external_user_reference=username, username=username)


def test_login_use_case_returns_token_for_valid_credentials() -> None:
    hasher = Pbkdf2PasswordHasher()
    identity = AuthIdentityRecord(
        user_id=1,
        username="admin",
        password_hash=hasher.hash_password("secret123"),
        role_code="admin",
        role_name="Admin",
        is_active=True,
    )
    identity_port = FakeAuthIdentityPort(identities=[identity])
    token_service = HmacTokenService(secret_key="test-secret", ttl_seconds=600)
    use_case = LoginUseCase(
        auth_identity_port=identity_port,
        password_hasher=hasher,
        auth_token_port=token_service,
        erp_auth_ports={"sage-simulator": FakeErpAuthenticationPort(users={})},
        access_token_ttl_seconds=600,
    )

    result = use_case.execute(
        LoginCommand(
            username="admin",
            password="secret123",
            login_type="admin",
            selected_connection="sage-simulator",
        )
    )

    assert result.token_type == "bearer"
    assert result.username == "admin"
    decoded = token_service.decode_access_token(result.access_token)
    assert decoded.sub == "1"
    assert decoded.role == "admin"
    assert decoded.login_type == "admin"
    assert decoded.selected_connection == "sage-simulator"


def test_login_use_case_rejects_invalid_credentials() -> None:
    hasher = Pbkdf2PasswordHasher()
    identity = AuthIdentityRecord(
        user_id=1,
        username="admin",
        password_hash=hasher.hash_password("secret123"),
        role_code="admin",
        role_name="Admin",
        is_active=True,
    )
    identity_port = FakeAuthIdentityPort(identities=[identity])
    token_service = HmacTokenService(secret_key="test-secret", ttl_seconds=600)
    use_case = LoginUseCase(
        auth_identity_port=identity_port,
        password_hasher=hasher,
        auth_token_port=token_service,
        erp_auth_ports={"sage-simulator": FakeErpAuthenticationPort(users={})},
        access_token_ttl_seconds=600,
    )

    with pytest.raises(AuthenticationError):
        use_case.execute(
            LoginCommand(
                username="admin",
                password="wrong",
                login_type="admin",
                selected_connection="sage-simulator",
            )
        )


def test_erp_login_use_case_returns_token_for_valid_simulator_credentials() -> None:
    hasher = Pbkdf2PasswordHasher()
    identity = AuthIdentityRecord(
        user_id=2,
        username="sim-lager",
        password_hash=hasher.hash_password("not-used"),
        role_code="lager",
        role_name="Lager",
        is_active=True,
    )
    identity_port = FakeAuthIdentityPort(identities=[identity])
    token_service = HmacTokenService(secret_key="test-secret", ttl_seconds=600)
    use_case = LoginUseCase(
        auth_identity_port=identity_port,
        password_hasher=hasher,
        auth_token_port=token_service,
        erp_auth_ports={"sage-simulator": FakeErpAuthenticationPort(users={"sim-lager": "SimLager123!"})},
        access_token_ttl_seconds=600,
    )

    result = use_case.execute(
        LoginCommand(
            username="sim-lager",
            password="SimLager123!",
            login_type="erp",
            selected_connection="sage-simulator",
        )
    )

    assert result.role_code == "lager"
    assert result.login_type == "erp"
    assert result.selected_connection == "sage-simulator"


def test_erp_login_use_case_rejects_unsupported_connection() -> None:
    hasher = Pbkdf2PasswordHasher()
    identity_port = FakeAuthIdentityPort(identities=[])
    token_service = HmacTokenService(secret_key="test-secret", ttl_seconds=600)
    use_case = LoginUseCase(
        auth_identity_port=identity_port,
        password_hasher=hasher,
        auth_token_port=token_service,
        erp_auth_ports={"sage-simulator": FakeErpAuthenticationPort(users={})},
        access_token_ttl_seconds=600,
    )

    with pytest.raises(ValueError, match="Verbindung noch nicht unterstuetzt"):
        use_case.execute(
            LoginCommand(
                username="sim-user",
                password="pw",
                login_type="erp",
                selected_connection="middleware",
            )
        )


def test_erp_login_use_case_rejects_user_without_app_role_mapping() -> None:
    hasher = Pbkdf2PasswordHasher()
    identity_port = FakeAuthIdentityPort(identities=[])
    token_service = HmacTokenService(secret_key="test-secret", ttl_seconds=600)
    use_case = LoginUseCase(
        auth_identity_port=identity_port,
        password_hasher=hasher,
        auth_token_port=token_service,
        erp_auth_ports={"sage-simulator": FakeErpAuthenticationPort(users={"sim-lager": "SimLager123!"})},
        access_token_ttl_seconds=600,
    )

    with pytest.raises(AuthorizationError, match="Keine App-Rolle zugeordnet"):
        use_case.execute(
            LoginCommand(
                username="sim-lager",
                password="SimLager123!",
                login_type="erp",
                selected_connection="sage-simulator",
            )
        )


def test_get_current_user_use_case_returns_identity() -> None:
    identity = AuthIdentityRecord(
        user_id=1,
        username="lager",
        password_hash="unused",
        role_code="lager",
        role_name="Lager",
        is_active=True,
    )
    use_case = GetCurrentUserUseCase(auth_identity_port=FakeAuthIdentityPort([identity]))

    result = use_case.execute(1)

    assert result.role_code == "lager"
