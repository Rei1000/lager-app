"""Ports for authentication identity loading."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthIdentityRecord:
    user_id: int
    username: str
    password_hash: str
    role_code: str
    role_name: str
    is_active: bool


class AuthIdentityPort(Protocol):
    def get_by_username(self, username: str) -> AuthIdentityRecord | None:
        """Load one identity by username."""

    def get_by_id(self, user_id: int) -> AuthIdentityRecord | None:
        """Load one identity by user ID."""

    def get_by_erp_user_reference(self, erp_user_reference: str) -> AuthIdentityRecord | None:
        """Load one app identity by mapped ERP user reference."""
