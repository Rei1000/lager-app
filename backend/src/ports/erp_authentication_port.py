"""Port for ERP-side user authentication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ErpAuthenticatedIdentity:
    external_user_reference: str
    username: str


class ErpAuthenticationPort(Protocol):
    def authenticate(self, username: str, password: str) -> ErpAuthenticatedIdentity | None:
        """Authenticate one ERP user and return external identity reference."""
