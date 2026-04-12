from __future__ import annotations

from dataclasses import dataclass

from adapters.auth.password_hasher import Pbkdf2PasswordHasher
from adapters.auth.sage_simulator_authentication import SageSimulatorAuthenticationAdapter
from ports.auth_identity_port import AuthIdentityPort, AuthIdentityRecord


@dataclass
class FakeAuthIdentityPort(AuthIdentityPort):
    records: dict[str, AuthIdentityRecord]

    def get_by_username(self, username: str) -> AuthIdentityRecord | None:
        for record in self.records.values():
            if record.username == username:
                return record
        return None

    def get_by_id(self, user_id: int) -> AuthIdentityRecord | None:
        for record in self.records.values():
            if record.user_id == user_id:
                return record
        return None

    def get_by_erp_user_reference(self, erp_user_reference: str) -> AuthIdentityRecord | None:
        return self.records.get(erp_user_reference)


def test_simulator_authentication_uses_persisted_identity() -> None:
    hasher = Pbkdf2PasswordHasher()
    record = AuthIdentityRecord(
        user_id=1,
        username="sim-lager",
        password_hash=hasher.hash_password("SimLager123!"),
        role_code="lager",
        role_name="Lager",
        is_active=True,
    )
    adapter = SageSimulatorAuthenticationAdapter(
        auth_identity_port=FakeAuthIdentityPort(records={"sim-lager": record}),
        password_hasher=hasher,
    )

    identity = adapter.authenticate("sim-lager", "SimLager123!")

    assert identity is not None
    assert identity.external_user_reference == "sim-lager"
    assert identity.username == "sim-lager"


def test_simulator_authentication_rejects_invalid_password() -> None:
    hasher = Pbkdf2PasswordHasher()
    record = AuthIdentityRecord(
        user_id=1,
        username="sim-lager",
        password_hash=hasher.hash_password("SimLager123!"),
        role_code="lager",
        role_name="Lager",
        is_active=True,
    )
    adapter = SageSimulatorAuthenticationAdapter(
        auth_identity_port=FakeAuthIdentityPort(records={"sim-lager": record}),
        password_hasher=hasher,
    )

    identity = adapter.authenticate("sim-lager", "wrong")

    assert identity is None


def test_simulator_authentication_supports_seed_user_references() -> None:
    hasher = Pbkdf2PasswordHasher()
    records = {
        "sage_admin": AuthIdentityRecord(
            user_id=1,
            username="sage_admin",
            password_hash=hasher.hash_password("SageAdmin123!"),
            role_code="admin",
            role_name="Admin",
            is_active=True,
        ),
        "sage_leitung": AuthIdentityRecord(
            user_id=2,
            username="sage_leitung",
            password_hash=hasher.hash_password("SageLeitung123!"),
            role_code="leitung",
            role_name="Leitung",
            is_active=True,
        ),
        "sage_lager": AuthIdentityRecord(
            user_id=3,
            username="sage_lager",
            password_hash=hasher.hash_password("SageLager123!"),
            role_code="lager",
            role_name="Lager",
            is_active=True,
        ),
    }
    adapter = SageSimulatorAuthenticationAdapter(
        auth_identity_port=FakeAuthIdentityPort(records=records),
        password_hasher=hasher,
    )

    assert adapter.authenticate("sage_admin", "SageAdmin123!") is not None
    assert adapter.authenticate("sage_leitung", "SageLeitung123!") is not None
    assert adapter.authenticate("sage_lager", "SageLager123!") is not None
