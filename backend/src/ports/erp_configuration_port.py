"""Contracts for ERP profile/endpoints/mapping configuration access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ErpProfileConfig:
    profile_id: str
    name: str
    base_url: str


@dataclass(frozen=True)
class ErpEndpointConfig:
    endpoint_id: str
    profile_id: str
    function_key: str
    http_method: str
    path_template: str


@dataclass(frozen=True)
class ErpFieldMappingConfig:
    endpoint_id: str
    app_field: str
    erp_field: str
    direction: str


class ErpConfigurationPort(Protocol):
    def get_profile(self, profile_name: str) -> ErpProfileConfig:
        """Return one configured ERP profile."""

    def get_endpoint(self, profile_id: str, function_key: str) -> ErpEndpointConfig:
        """Return endpoint config for one profile/function."""

    def list_field_mappings(self, endpoint_id: str, direction: str) -> list[ErpFieldMappingConfig]:
        """Return field mappings for one endpoint and direction."""
