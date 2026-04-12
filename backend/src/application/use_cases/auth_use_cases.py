"""Use cases for authentication and current identity resolution."""

from __future__ import annotations

from dataclasses import dataclass

from application.dtos import LoginCommand
from application.errors import AuthenticationError, AuthorizationError
from ports.auth_identity_port import AuthIdentityPort, AuthIdentityRecord
from ports.auth_token_port import AuthTokenPort
from ports.erp_authentication_port import ErpAuthenticationPort
from ports.password_hasher_port import PasswordHasherPort


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    token_type: str
    expires_in_seconds: int
    user_id: int
    username: str
    role_code: str
    login_type: str
    selected_connection: str


class LoginUseCase:
    def __init__(
        self,
        auth_identity_port: AuthIdentityPort,
        password_hasher: PasswordHasherPort,
        auth_token_port: AuthTokenPort,
        erp_auth_ports: dict[str, ErpAuthenticationPort],
        access_token_ttl_seconds: int,
    ) -> None:
        self._auth_identity_port = auth_identity_port
        self._password_hasher = password_hasher
        self._auth_token_port = auth_token_port
        self._erp_auth_ports = erp_auth_ports
        self._access_token_ttl_seconds = access_token_ttl_seconds

    def execute(self, command: LoginCommand) -> LoginResult:
        username = command.username.strip()
        login_type = command.login_type.strip().lower()
        selected_connection = command.selected_connection.strip().lower()
        if not username or not command.password or not login_type or not selected_connection:
            raise AuthenticationError("Ungueltige Anmeldedaten")

        if login_type == "admin":
            identity = self._authenticate_admin(username=username, password=command.password)
        elif login_type == "erp":
            identity = self._authenticate_erp(
                username=username,
                password=command.password,
                selected_connection=selected_connection,
            )
        else:
            raise AuthenticationError("Ungueltige Anmeldedaten")

        token = self._auth_token_port.issue_access_token(
            user_id=identity.user_id,
            role_code=identity.role_code,
            login_type=login_type,
            selected_connection=selected_connection,
        )
        return LoginResult(
            access_token=token,
            token_type="bearer",
            expires_in_seconds=self._access_token_ttl_seconds,
            user_id=identity.user_id,
            username=identity.username,
            role_code=identity.role_code,
            login_type=login_type,
            selected_connection=selected_connection,
        )

    def _authenticate_admin(self, *, username: str, password: str) -> AuthIdentityRecord:
        identity = self._auth_identity_port.get_by_username(username)
        if identity is None or not identity.is_active:
            raise AuthenticationError("Ungueltige Anmeldedaten")
        if not self._password_hasher.verify_password(password, identity.password_hash):
            raise AuthenticationError("Ungueltige Anmeldedaten")
        return identity

    def _authenticate_erp(
        self,
        *,
        username: str,
        password: str,
        selected_connection: str,
    ) -> AuthIdentityRecord:
        erp_auth_port = self._erp_auth_ports.get(selected_connection)
        if erp_auth_port is None:
            raise ValueError("Verbindung noch nicht unterstuetzt")

        erp_identity = erp_auth_port.authenticate(username=username, password=password)
        if erp_identity is None:
            raise AuthenticationError("Ungueltige Anmeldedaten")

        app_identity = self._auth_identity_port.get_by_erp_user_reference(erp_identity.external_user_reference)
        if app_identity is None or not app_identity.is_active:
            raise AuthorizationError("Keine App-Rolle zugeordnet")
        return app_identity


class GetCurrentUserUseCase:
    def __init__(self, auth_identity_port: AuthIdentityPort) -> None:
        self._auth_identity_port = auth_identity_port

    def execute(self, user_id: int) -> AuthIdentityRecord:
        identity = self._auth_identity_port.get_by_id(user_id)
        if identity is None or not identity.is_active:
            raise AuthenticationError("Benutzer nicht authentifiziert")
        return identity
