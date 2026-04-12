"""Optional contract for controlled ERP write handover."""

from __future__ import annotations

from typing import Any, Protocol


class ErpWritePort(Protocol):
    def send_transfer(
        self,
        *,
        transfer_payload: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Send one prepared transfer payload to ERP and return optional response."""
