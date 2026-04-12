"""Simulator ERP authentication adapter backed by persisted users."""

from __future__ import annotations

from ports.auth_identity_port import AuthIdentityPort
from ports.password_hasher_port import PasswordHasherPort
from ports.erp_authentication_port import ErpAuthenticatedIdentity, ErpAuthenticationPort


class SageSimulatorAuthenticationAdapter(ErpAuthenticationPort):
    def __init__(
        self,
        *,
        auth_identity_port: AuthIdentityPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._auth_identity_port = auth_identity_port
        self._password_hasher = password_hasher

    def authenticate(self, username: str, password: str) -> ErpAuthenticatedIdentity | None:
        external_reference = username.strip()
        if not external_reference or not password:
            return None

        # Simulator users are looked up via persisted ERP reference mapping.
        record = self._auth_identity_port.get_by_erp_user_reference(external_reference)
        if record is None or not record.is_active:
            return None
        if not self._password_hasher.verify_password(password, record.password_hash):
            return None

        return ErpAuthenticatedIdentity(
            external_user_reference=external_reference,
            username=record.username,
        )
