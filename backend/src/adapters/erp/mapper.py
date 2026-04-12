"""Config-driven ERP field mapping helpers."""

from __future__ import annotations

from typing import Any

from ports.erp_configuration_port import ErpFieldMappingConfig


def apply_mappings(
    payload: dict[str, Any],
    mappings: list[ErpFieldMappingConfig],
    *,
    fallback_identity: bool = True,
) -> dict[str, Any]:
    """Map payload keys according to endpoint mapping configuration."""
    mapped: dict[str, Any] = {}

    consumed_app_fields: set[str] = set()
    for mapping in mappings:
        if mapping.app_field in payload:
            mapped[mapping.erp_field] = payload[mapping.app_field]
            consumed_app_fields.add(mapping.app_field)

    if fallback_identity:
        for key, value in payload.items():
            if key not in consumed_app_fields:
                mapped[key] = value

    return mapped


def apply_reverse_mappings(
    payload: dict[str, Any],
    mappings: list[ErpFieldMappingConfig],
    *,
    fallback_identity: bool = True,
) -> dict[str, Any]:
    """Map ERP payload keys back to internal keys."""
    mapped: dict[str, Any] = {}

    consumed_erp_fields: set[str] = set()
    for mapping in mappings:
        if mapping.erp_field in payload:
            mapped[mapping.app_field] = payload[mapping.erp_field]
            consumed_erp_fields.add(mapping.erp_field)

    if fallback_identity:
        for key, value in payload.items():
            if key not in consumed_erp_fields:
                mapped[key] = value

    return mapped
