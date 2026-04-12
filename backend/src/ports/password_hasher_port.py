"""Port for password hashing and verification."""

from __future__ import annotations

from typing import Protocol


class PasswordHasherPort(Protocol):
    def hash_password(self, plain_password: str) -> str:
        """Hash plain password for storage."""

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        """Verify plain password against stored hash."""
