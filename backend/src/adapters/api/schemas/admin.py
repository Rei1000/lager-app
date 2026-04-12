"""Pydantic schemas for admin configuration endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ports.admin_configuration_port import (
    CuttingMachineRecord,
    ErpEndpointRecord,
    ErpFieldMappingRecord,
    ErpProfileRecord,
    UserRecord,
)


class ErpProfileRequest(BaseModel):
    name: str = Field(min_length=1)
    erp_type: str | None = None
    connection_type: str | None = None
    base_url: str | None = None
    tenant_code: str | None = None


class ErpProfileResponse(BaseModel):
    id: int
    name: str
    erp_type: str | None
    connection_type: str | None
    base_url: str | None
    tenant_code: str | None

    @classmethod
    def from_record(cls, record: ErpProfileRecord) -> "ErpProfileResponse":
        return cls(
            id=record.id,
            name=record.name,
            erp_type=record.erp_type,
            connection_type=record.connection_type,
            base_url=record.base_url,
            tenant_code=record.tenant_code,
        )


class ErpEndpointRequest(BaseModel):
    erp_profile_id: int = Field(gt=0)
    functional_key: str = Field(min_length=1)
    http_method: str = Field(min_length=1)
    path_template: str = Field(min_length=1)


class ErpEndpointResponse(BaseModel):
    id: int
    erp_profile_id: int
    functional_key: str
    http_method: str
    path_template: str

    @classmethod
    def from_record(cls, record: ErpEndpointRecord) -> "ErpEndpointResponse":
        return cls(
            id=record.id,
            erp_profile_id=record.erp_profile_id,
            functional_key=record.functional_key,
            http_method=record.http_method,
            path_template=record.path_template,
        )


class ErpFieldMappingRequest(BaseModel):
    endpoint_id: int = Field(gt=0)
    app_field: str = Field(min_length=1)
    erp_field: str = Field(min_length=1)
    direction: str = Field(pattern="^(app_to_erp|erp_to_app)$")


class ErpFieldMappingResponse(BaseModel):
    id: int
    endpoint_id: int
    app_field: str
    erp_field: str
    direction: str

    @classmethod
    def from_record(cls, record: ErpFieldMappingRecord) -> "ErpFieldMappingResponse":
        return cls(
            id=record.id,
            endpoint_id=record.endpoint_id,
            app_field=record.app_field,
            erp_field=record.erp_field,
            direction=record.direction,
        )


class CuttingMachineRequest(BaseModel):
    machine_code: str | None = None
    name: str = Field(min_length=1)
    kerf_mm: float | None = Field(default=None, ge=0)
    is_active: bool = True


class CuttingMachineResponse(BaseModel):
    id: int
    machine_code: str | None
    name: str
    kerf_mm: float | None
    is_active: bool

    @classmethod
    def from_record(cls, record: CuttingMachineRecord) -> "CuttingMachineResponse":
        return cls(
            id=record.id,
            machine_code=record.machine_code,
            name=record.name,
            kerf_mm=record.kerf_mm,
            is_active=record.is_active,
        )


class UserRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=8)
    role_id: int = Field(gt=0)
    display_name: str | None = None
    email: str | None = None
    is_active: bool = True
    erp_user_reference: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    role_id: int
    display_name: str | None
    email: str | None
    is_active: bool
    erp_user_reference: str | None

    @classmethod
    def from_record(cls, record: UserRecord) -> "UserResponse":
        return cls(
            id=record.id,
            username=record.username,
            role_id=record.role_id,
            display_name=record.display_name,
            email=record.email,
            is_active=record.is_active,
            erp_user_reference=record.erp_user_reference,
        )
