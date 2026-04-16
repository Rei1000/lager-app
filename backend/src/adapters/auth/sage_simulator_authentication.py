"""Simulator ERP authentication adapter backed by persisted users."""

from __future__ import annotations

from adapters.erp.sage_simulator_data import SIMULATOR_USERS
from ports.auth_identity_port import AuthIdentityPort
from ports.password_hasher_port import PasswordHasherPort
from ports.erp_authentication_port import ErpAuthenticatedIdentity, ErpAuthenticationPort

SIMULATOR_EXTERNAL_REFERENCE_BY_USERNAME = {
    seed.username: seed.erp_user_reference for seed in SIMULATOR_USERS
}


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
        login_username = username.strip()
        if not login_username or not password:
            return None

        external_reference = SIMULATOR_EXTERNAL_REFERENCE_BY_USERNAME.get(login_username, login_username)
        record = self._auth_identity_port.get_by_erp_user_reference(external_reference)
        if record is None:
            # Backward-compatible fallback for already seeded legacy references.
            record = self._auth_identity_port.get_by_erp_user_reference(login_username)
            if record is not None:
                external_reference = login_username
        if record is None:
            # Final fallback for local test fixtures not keyed by ERP reference.
            record = self._auth_identity_port.get_by_username(login_username)
            if record is not None:
                external_reference = login_username
        if record is None or not record.is_active:
            return None
        if not self._password_hasher.verify_password(password, record.password_hash):
            return None

        return ErpAuthenticatedIdentity(
            external_user_reference=external_reference,
            username=record.username,
        )
