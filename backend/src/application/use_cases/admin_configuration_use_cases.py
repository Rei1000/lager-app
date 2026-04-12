"""Use cases for admin configuration CRUD orchestration."""

from __future__ import annotations

from application.dtos import (
    CreateCuttingMachineCommand,
    CreateEndpointCommand,
    CreateErpProfileCommand,
    CreateFieldMappingCommand,
    CreateUserCommand,
    UpdateErpProfileCommand,
)
from ports.admin_configuration_port import (
    AdminConfigurationPort,
    CuttingMachineRecord,
    ErpEndpointRecord,
    ErpFieldMappingRecord,
    ErpProfileRecord,
    UserRecord,
)


class ListErpProfilesUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self) -> list[ErpProfileRecord]:
        return self._admin_configuration_port.list_erp_profiles()


class GetErpProfileUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, profile_id: int) -> ErpProfileRecord:
        return self._admin_configuration_port.get_erp_profile(profile_id)


class CreateErpProfileUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: CreateErpProfileCommand) -> ErpProfileRecord:
        return self._admin_configuration_port.create_erp_profile(
            name=command.name,
            erp_type=command.erp_type,
            connection_type=command.connection_type,
            base_url=command.base_url,
            tenant_code=command.tenant_code,
        )


class UpdateErpProfileUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: UpdateErpProfileCommand) -> ErpProfileRecord:
        return self._admin_configuration_port.update_erp_profile(
            profile_id=command.profile_id,
            name=command.name,
            erp_type=command.erp_type,
            connection_type=command.connection_type,
            base_url=command.base_url,
            tenant_code=command.tenant_code,
        )


class ListEndpointsUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self) -> list[ErpEndpointRecord]:
        return self._admin_configuration_port.list_endpoints()


class CreateEndpointUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: CreateEndpointCommand) -> ErpEndpointRecord:
        return self._admin_configuration_port.create_endpoint(
            erp_profile_id=command.erp_profile_id,
            functional_key=command.functional_key,
            http_method=command.http_method,
            path_template=command.path_template,
        )


class ListFieldMappingsUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self) -> list[ErpFieldMappingRecord]:
        return self._admin_configuration_port.list_mappings()


class CreateFieldMappingUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: CreateFieldMappingCommand) -> ErpFieldMappingRecord:
        return self._admin_configuration_port.create_mapping(
            endpoint_id=command.endpoint_id,
            app_field=command.app_field,
            erp_field=command.erp_field,
            direction=command.direction,
        )


class ListCuttingMachinesUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self) -> list[CuttingMachineRecord]:
        return self._admin_configuration_port.list_cutting_machines()


class CreateCuttingMachineUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: CreateCuttingMachineCommand) -> CuttingMachineRecord:
        return self._admin_configuration_port.create_cutting_machine(
            machine_code=command.machine_code,
            name=command.name,
            kerf_mm=command.kerf_mm,
            is_active=command.is_active,
        )


class ListUsersUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self) -> list[UserRecord]:
        return self._admin_configuration_port.list_users()


class CreateUserUseCase:
    def __init__(self, admin_configuration_port: AdminConfigurationPort) -> None:
        self._admin_configuration_port = admin_configuration_port

    def execute(self, command: CreateUserCommand) -> UserRecord:
        return self._admin_configuration_port.create_user(
            username=command.username,
            password=command.password,
            role_id=command.role_id,
            display_name=command.display_name,
            email=command.email,
            is_active=command.is_active,
            erp_user_reference=command.erp_user_reference,
        )
