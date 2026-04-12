"""Port for issuing and decoding auth access tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthTokenPayload:
    sub: str
    role: str
    login_type: str
    selected_connection: str
    exp: int


class AuthTokenPort(Protocol):
    def issue_access_token(
        self,
        *,
        user_id: int,
        role_code: str,
        login_type: str = "admin",
        selected_connection: str = "sage-simulator",
    ) -> str:
        """Create signed access token."""

    def decode_access_token(self, token: str) -> AuthTokenPayload:
        """Decode and verify access token."""
