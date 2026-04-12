"""Port contract for binary file storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredFile:
    content: bytes
    content_type: str | None


class FileStoragePort(Protocol):
    def save(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> str:
        """Store one file and return file key/path."""

    def load(self, *, file_key: str) -> StoredFile:
        """Load one stored file by key/path."""

    def delete(self, *, file_key: str) -> None:
        """Delete one stored file by key/path."""
