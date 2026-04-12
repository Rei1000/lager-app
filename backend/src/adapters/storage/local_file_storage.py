"""Local filesystem file storage adapter."""

from __future__ import annotations

from pathlib import Path
import re
from uuid import uuid4

from application.errors import NotFoundError
from ports.file_storage_port import FileStoragePort, StoredFile

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class LocalFileStorageAdapter(FileStoragePort):
    def __init__(self, *, base_directory: Path) -> None:
        self._base_directory = base_directory
        self._base_directory.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> str:
        suffix = Path(filename).suffix.lower()
        safe_stem = _SAFE_FILENAME_RE.sub("-", Path(filename).stem).strip("-") or "upload"
        generated = f"{uuid4().hex}-{safe_stem}{suffix}"
        target = self._base_directory / generated
        target.write_bytes(content)
        return generated

    def load(self, *, file_key: str) -> StoredFile:
        target = self._base_directory / file_key
        if not target.exists() or not target.is_file():
            raise NotFoundError(f"Datei nicht gefunden: {file_key}")
        return StoredFile(content=target.read_bytes(), content_type=None)

    def delete(self, *, file_key: str) -> None:
        target = self._base_directory / file_key
        if target.exists() and target.is_file():
            target.unlink()
