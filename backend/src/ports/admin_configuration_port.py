"""Ports for technical admin configuration management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ErpProfileRecord:
    id: int
    name: str
    erp_type: str | None
    connection_type: str | None
    base_url: str | None
    tenant_code: str | None


@dataclass(frozen=True)
class ErpEndpointRecord:
    id: int
    erp_profile_id: int
    functional_key: str
    http_method: str
    path_template: str


@dataclass(frozen=True)
class ErpFieldMappingRecord:
    id: int
    endpoint_id: int
    app_field: str
    erp_field: str
    direction: str


@dataclass(frozen=True)
class CuttingMachineRecord:
    id: int
    machine_code: str | None
    name: str
    kerf_mm: float | None
    is_active: bool


@dataclass(frozen=True)
class UserRecord:
    id: int
    username: str
    display_name: str | None
    email: str | None
    role_id: int
    is_active: bool
    erp_user_reference: str | None


class AdminConfigurationPort(Protocol):
    def list_erp_profiles(self) -> list[ErpProfileRecord]:
        """Return all ERP profiles."""

    def get_erp_profile(self, profile_id: int) -> ErpProfileRecord:
        """Return one ERP profile by ID."""

    def create_erp_profile(
        self,
        *,
        name: str,
        erp_type: str | None,
        connection_type: str | None,
        base_url: str | None,
        tenant_code: str | None,
    ) -> ErpProfileRecord:
        """Create one ERP profile."""

    def update_erp_profile(
        self,
        *,
        profile_id: int,
        name: str,
        erp_type: str | None,
        connection_type: str | None,
        base_url: str | None,
        tenant_code: str | None,
    ) -> ErpProfileRecord:
        """Update one ERP profile."""

    def list_endpoints(self) -> list[ErpEndpointRecord]:
        """Return all configured ERP endpoints."""

    def create_endpoint(
        self,
        *,
        erp_profile_id: int,
        functional_key: str,
        http_method: str,
        path_template: str,
    ) -> ErpEndpointRecord:
        """Create one ERP endpoint config."""

    def list_mappings(self) -> list[ErpFieldMappingRecord]:
        """Return all field mappings."""

    def create_mapping(
        self,
        *,
        endpoint_id: int,
        app_field: str,
        erp_field: str,
        direction: str,
    ) -> ErpFieldMappingRecord:
        """Create one field mapping."""

    def list_cutting_machines(self) -> list[CuttingMachineRecord]:
        """Return all cutting machines."""

    def create_cutting_machine(
        self,
        *,
        machine_code: str | None,
        name: str,
        kerf_mm: float | None,
        is_active: bool,
    ) -> CuttingMachineRecord:
        """Create one cutting machine."""

    def list_users(self) -> list[UserRecord]:
        """Return all users."""

    def create_user(
        self,
        *,
        username: str,
        password: str,
        role_id: int,
        display_name: str | None,
        email: str | None,
        is_active: bool,
        erp_user_reference: str | None,
    ) -> UserRecord:
        """Create one user."""
