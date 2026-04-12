"""Generic HTTP client abstraction for ERP adapters."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol
from urllib import error, parse, request


class HttpClientPort(Protocol):
    def request(
        self,
        *,
        method: str,
        url: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Execute one HTTP request and return decoded payload."""


@dataclass
class UrllibHttpClient(HttpClientPort):
    timeout_seconds: int = 10

    def request(
        self,
        *,
        method: str,
        url: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        full_url = self._build_url(url, query)
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        request_headers = {"Content-Type": "application/json", **(headers or {})}

        req = request.Request(
            full_url,
            data=payload,
            headers=request_headers,
            method=method.upper(),
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:  # noqa: S310
                raw = response.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except error.HTTPError as exc:
            raise ValueError(f"ERP-Request fehlgeschlagen: HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise ValueError("ERP nicht erreichbar") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("ERP-Antwort ist ungueltig") from exc

    @staticmethod
    def _build_url(url: str, query: dict[str, Any] | None) -> str:
        if not query:
            return url
        return f"{url}?{parse.urlencode(query)}"
