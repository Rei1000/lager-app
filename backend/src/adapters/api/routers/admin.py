"""Admin configuration API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import require_admin_user
from adapters.api.dependencies.use_cases import (
    get_create_cutting_machine_use_case,
    get_create_endpoint_use_case,
    get_create_erp_profile_use_case,
    get_create_field_mapping_use_case,
    get_create_user_use_case,
    get_get_erp_profile_use_case,
    get_list_cutting_machines_use_case,
    get_list_endpoints_use_case,
    get_list_erp_profiles_use_case,
    get_list_field_mappings_use_case,
    get_list_users_use_case,
    get_update_erp_profile_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.admin import (
    CuttingMachineRequest,
    CuttingMachineResponse,
    ErpEndpointRequest,
    ErpEndpointResponse,
    ErpFieldMappingRequest,
    ErpFieldMappingResponse,
    ErpProfileRequest,
    ErpProfileResponse,
    UserRequest,
    UserResponse,
)
from application.dtos import (
    CreateCuttingMachineCommand,
    CreateEndpointCommand,
    CreateErpProfileCommand,
    CreateFieldMappingCommand,
    CreateUserCommand,
    UpdateErpProfileCommand,
)
from application.use_cases.admin_configuration_use_cases import (
    CreateCuttingMachineUseCase,
    CreateEndpointUseCase,
    CreateErpProfileUseCase,
    CreateFieldMappingUseCase,
    CreateUserUseCase,
    GetErpProfileUseCase,
    ListCuttingMachinesUseCase,
    ListEndpointsUseCase,
    ListErpProfilesUseCase,
    ListFieldMappingsUseCase,
    ListUsersUseCase,
    UpdateErpProfileUseCase,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_user)],
)


@router.get("/erp-profiles", response_model=list[ErpProfileResponse])
def list_erp_profiles(
    use_case: ListErpProfilesUseCase = Depends(get_list_erp_profiles_use_case),
) -> list[ErpProfileResponse]:
    profiles = use_case.execute()
    return [ErpProfileResponse.from_record(profile) for profile in profiles]


@router.post("/erp-profiles", response_model=ErpProfileResponse, status_code=201)
def create_erp_profile(
    payload: ErpProfileRequest,
    use_case: CreateErpProfileUseCase = Depends(get_create_erp_profile_use_case),
) -> ErpProfileResponse:
    try:
        profile = use_case.execute(
            CreateErpProfileCommand(
                name=payload.name,
                erp_type=payload.erp_type,
                connection_type=payload.connection_type,
                base_url=payload.base_url,
                tenant_code=payload.tenant_code,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpProfileResponse.from_record(profile)


@router.get("/erp-profiles/{profile_id}", response_model=ErpProfileResponse)
def get_erp_profile(
    profile_id: int,
    use_case: GetErpProfileUseCase = Depends(get_get_erp_profile_use_case),
) -> ErpProfileResponse:
    try:
        profile = use_case.execute(profile_id)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpProfileResponse.from_record(profile)


@router.put("/erp-profiles/{profile_id}", response_model=ErpProfileResponse)
def update_erp_profile(
    profile_id: int,
    payload: ErpProfileRequest,
    use_case: UpdateErpProfileUseCase = Depends(get_update_erp_profile_use_case),
) -> ErpProfileResponse:
    try:
        profile = use_case.execute(
            UpdateErpProfileCommand(
                profile_id=profile_id,
                name=payload.name,
                erp_type=payload.erp_type,
                connection_type=payload.connection_type,
                base_url=payload.base_url,
                tenant_code=payload.tenant_code,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpProfileResponse.from_record(profile)


@router.get("/endpoints", response_model=list[ErpEndpointResponse])
def list_endpoints(
    use_case: ListEndpointsUseCase = Depends(get_list_endpoints_use_case),
) -> list[ErpEndpointResponse]:
    endpoints = use_case.execute()
    return [ErpEndpointResponse.from_record(endpoint) for endpoint in endpoints]


@router.post("/endpoints", response_model=ErpEndpointResponse, status_code=201)
def create_endpoint(
    payload: ErpEndpointRequest,
    use_case: CreateEndpointUseCase = Depends(get_create_endpoint_use_case),
) -> ErpEndpointResponse:
    try:
        endpoint = use_case.execute(
            CreateEndpointCommand(
                erp_profile_id=payload.erp_profile_id,
                functional_key=payload.functional_key,
                http_method=payload.http_method,
                path_template=payload.path_template,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpEndpointResponse.from_record(endpoint)


@router.get("/mappings", response_model=list[ErpFieldMappingResponse])
def list_mappings(
    use_case: ListFieldMappingsUseCase = Depends(get_list_field_mappings_use_case),
) -> list[ErpFieldMappingResponse]:
    mappings = use_case.execute()
    return [ErpFieldMappingResponse.from_record(mapping) for mapping in mappings]


@router.post("/mappings", response_model=ErpFieldMappingResponse, status_code=201)
def create_mapping(
    payload: ErpFieldMappingRequest,
    use_case: CreateFieldMappingUseCase = Depends(get_create_field_mapping_use_case),
) -> ErpFieldMappingResponse:
    try:
        mapping = use_case.execute(
            CreateFieldMappingCommand(
                endpoint_id=payload.endpoint_id,
                app_field=payload.app_field,
                erp_field=payload.erp_field,
                direction=payload.direction,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpFieldMappingResponse.from_record(mapping)


@router.get("/cutting-machines", response_model=list[CuttingMachineResponse])
def list_cutting_machines(
    use_case: ListCuttingMachinesUseCase = Depends(get_list_cutting_machines_use_case),
) -> list[CuttingMachineResponse]:
    machines = use_case.execute()
    return [CuttingMachineResponse.from_record(machine) for machine in machines]


@router.post("/cutting-machines", response_model=CuttingMachineResponse, status_code=201)
def create_cutting_machine(
    payload: CuttingMachineRequest,
    use_case: CreateCuttingMachineUseCase = Depends(get_create_cutting_machine_use_case),
) -> CuttingMachineResponse:
    try:
        machine = use_case.execute(
            CreateCuttingMachineCommand(
                machine_code=payload.machine_code,
                name=payload.name,
                kerf_mm=payload.kerf_mm,
                is_active=payload.is_active,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return CuttingMachineResponse.from_record(machine)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> list[UserResponse]:
    users = use_case.execute()
    return [UserResponse.from_record(user) for user in users]


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
    try:
        user = use_case.execute(
            CreateUserCommand(
                username=payload.username,
                password=payload.password,
                role_id=payload.role_id,
                display_name=payload.display_name,
                email=payload.email,
                is_active=payload.is_active,
                erp_user_reference=payload.erp_user_reference,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return UserResponse.from_record(user)
