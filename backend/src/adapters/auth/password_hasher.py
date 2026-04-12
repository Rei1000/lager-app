"""Password hashing adapter using PBKDF2-HMAC."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os

from ports.password_hasher_port import PasswordHasherPort


class Pbkdf2PasswordHasher(PasswordHasherPort):
    _algorithm = "sha256"
    _iterations = 210_000

    def hash_password(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("Passwort darf nicht leer sein")
        salt = os.urandom(16)
        derived = hashlib.pbkdf2_hmac(
            self._algorithm,
            plain_password.encode("utf-8"),
            salt,
            self._iterations,
        )
        salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
        hash_b64 = base64.urlsafe_b64encode(derived).decode("ascii")
        return f"pbkdf2_{self._algorithm}${self._iterations}${salt_b64}${hash_b64}"

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        try:
            scheme, iterations, salt_b64, hash_b64 = stored_hash.split("$", maxsplit=3)
            if scheme != f"pbkdf2_{self._algorithm}":
                return False
            salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
            expected = base64.urlsafe_b64decode(hash_b64.encode("ascii"))
            derived = hashlib.pbkdf2_hmac(
                self._algorithm,
                plain_password.encode("utf-8"),
                salt,
                int(iterations),
            )
            return hmac.compare_digest(derived, expected)
        except (ValueError, TypeError):
            return False
