"""Schemas for ERP read endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErpPayloadResponse(BaseModel):
    payload: dict[str, Any]


class ErpOrderValidationResponse(BaseModel):
    reference: str
    is_valid: bool
