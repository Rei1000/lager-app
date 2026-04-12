"""Signed access token adapter."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from application.errors import AuthenticationError
from ports.auth_token_port import AuthTokenPayload, AuthTokenPort


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


class HmacTokenService(AuthTokenPort):
    def __init__(self, *, secret_key: str, ttl_seconds: int) -> None:
        self._secret_key = secret_key.encode("utf-8")
        self._ttl_seconds = ttl_seconds

    def issue_access_token(
        self,
        *,
        user_id: int,
        role_code: str,
        login_type: str = "admin",
        selected_connection: str = "sage-simulator",
    ) -> str:
        issued_at = int(time.time())
        payload = {
            "sub": str(user_id),
            "role": role_code,
            "login_type": login_type,
            "selected_connection": selected_connection,
            "iat": issued_at,
            "exp": issued_at + self._ttl_seconds,
        }
        payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signature = hmac.new(
            self._secret_key,
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        return f"{payload_part}.{signature}"

    def decode_access_token(self, token: str) -> AuthTokenPayload:
        try:
            payload_part, signature = token.split(".", maxsplit=1)
        except ValueError as exc:
            raise AuthenticationError("Ungueltiges Token") from exc

        expected_signature = hmac.new(
            self._secret_key,
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            raise AuthenticationError("Ungueltiges Token")

        try:
            payload_dict = json.loads(_b64url_decode(payload_part).decode("utf-8"))
            payload = AuthTokenPayload(
                sub=str(payload_dict["sub"]),
                role=str(payload_dict["role"]),
                login_type=str(payload_dict.get("login_type", "admin")),
                selected_connection=str(payload_dict.get("selected_connection", "unknown")),
                exp=int(payload_dict["exp"]),
            )
        except (ValueError, KeyError, TypeError) as exc:
            raise AuthenticationError("Ungueltiges Token") from exc

        if payload.exp < int(time.time()):
            raise AuthenticationError("Token ist abgelaufen")
        return payload
