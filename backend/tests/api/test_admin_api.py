from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
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
from ports.admin_configuration_port import (
    CuttingMachineRecord,
    ErpEndpointRecord,
    ErpFieldMappingRecord,
    ErpProfileRecord,
    UserRecord,
)


def test_list_and_create_erp_profiles_endpoints() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeListErpProfilesUseCase:
        def execute(self) -> list[ErpProfileRecord]:
            return [
                ErpProfileRecord(
                    id=1,
                    name="default",
                    erp_type="rest",
                    connection_type="http",
                    base_url="https://erp.example",
                    tenant_code="TENANT-A",
                )
            ]

    class FakeCreateErpProfilesUseCase:
        def execute(self, _command: object) -> ErpProfileRecord:
            return ErpProfileRecord(
                id=2,
                name="new",
                erp_type=None,
                connection_type=None,
                base_url=None,
                tenant_code=None,
            )

    app.dependency_overrides[get_list_erp_profiles_use_case] = lambda: FakeListErpProfilesUseCase()
    app.dependency_overrides[get_create_erp_profile_use_case] = lambda: FakeCreateErpProfilesUseCase()
    client = TestClient(app)

    list_response = client.get("/admin/erp-profiles")
    create_response = client.post("/admin/erp-profiles", json={"name": "new"})

    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "default"
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 2
    app.dependency_overrides.clear()


def test_get_and_update_erp_profile_endpoints() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeGetErpProfileUseCase:
        def execute(self, profile_id: int) -> ErpProfileRecord:
            return ErpProfileRecord(
                id=profile_id,
                name="default",
                erp_type="rest",
                connection_type="http",
                base_url="https://erp.example",
                tenant_code="TENANT-A",
            )

    class FakeUpdateErpProfileUseCase:
        def execute(self, _command: object) -> ErpProfileRecord:
            return ErpProfileRecord(
                id=1,
                name="updated",
                erp_type="rest",
                connection_type="http",
                base_url="https://erp-new.example",
                tenant_code="TENANT-B",
            )

    app.dependency_overrides[get_get_erp_profile_use_case] = lambda: FakeGetErpProfileUseCase()
    app.dependency_overrides[get_update_erp_profile_use_case] = lambda: FakeUpdateErpProfileUseCase()
    client = TestClient(app)

    get_response = client.get("/admin/erp-profiles/1")
    put_response = client.put(
        "/admin/erp-profiles/1",
        json={
            "name": "updated",
            "erp_type": "rest",
            "connection_type": "http",
            "base_url": "https://erp-new.example",
            "tenant_code": "TENANT-B",
        },
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == 1
    assert put_response.status_code == 200
    assert put_response.json()["name"] == "updated"
    app.dependency_overrides.clear()


def test_list_and_create_endpoints() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeListEndpointsUseCase:
        def execute(self) -> list[ErpEndpointRecord]:
            return [
                ErpEndpointRecord(
                    id=10,
                    erp_profile_id=1,
                    functional_key="material.search",
                    http_method="GET",
                    path_template="/materials/search",
                )
            ]

    class FakeCreateEndpointUseCase:
        def execute(self, _command: object) -> ErpEndpointRecord:
            return ErpEndpointRecord(
                id=11,
                erp_profile_id=1,
                functional_key="material.get",
                http_method="GET",
                path_template="/materials/get",
            )

    app.dependency_overrides[get_list_endpoints_use_case] = lambda: FakeListEndpointsUseCase()
    app.dependency_overrides[get_create_endpoint_use_case] = lambda: FakeCreateEndpointUseCase()
    client = TestClient(app)

    list_response = client.get("/admin/endpoints")
    create_response = client.post(
        "/admin/endpoints",
        json={
            "erp_profile_id": 1,
            "functional_key": "material.get",
            "http_method": "GET",
            "path_template": "/materials/get",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["functional_key"] == "material.search"
    assert create_response.status_code == 201
    assert create_response.json()["id"] == 11
    app.dependency_overrides.clear()


def test_list_and_create_mappings() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeListMappingsUseCase:
        def execute(self) -> list[ErpFieldMappingRecord]:
            return [
                ErpFieldMappingRecord(
                    id=5,
                    endpoint_id=10,
                    app_field="material_reference",
                    erp_field="material_no",
                    direction="app_to_erp",
                )
            ]

    class FakeCreateMappingUseCase:
        def execute(self, _command: object) -> ErpFieldMappingRecord:
            return ErpFieldMappingRecord(
                id=6,
                endpoint_id=10,
                app_field="material_id",
                erp_field="id",
                direction="erp_to_app",
            )

    app.dependency_overrides[get_list_field_mappings_use_case] = lambda: FakeListMappingsUseCase()
    app.dependency_overrides[get_create_field_mapping_use_case] = lambda: FakeCreateMappingUseCase()
    client = TestClient(app)

    list_response = client.get("/admin/mappings")
    create_response = client.post(
        "/admin/mappings",
        json={
            "endpoint_id": 10,
            "app_field": "material_id",
            "erp_field": "id",
            "direction": "erp_to_app",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["direction"] == "app_to_erp"
    assert create_response.status_code == 201
    assert create_response.json()["direction"] == "erp_to_app"
    app.dependency_overrides.clear()


def test_list_and_create_cutting_machines() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeListCuttingMachinesUseCase:
        def execute(self) -> list[CuttingMachineRecord]:
            return [
                CuttingMachineRecord(
                    id=3,
                    machine_code="S-01",
                    name="Saege 1",
                    kerf_mm=3.2,
                    is_active=True,
                )
            ]

    class FakeCreateCuttingMachineUseCase:
        def execute(self, _command: object) -> CuttingMachineRecord:
            return CuttingMachineRecord(
                id=4,
                machine_code="S-02",
                name="Saege 2",
                kerf_mm=2.8,
                is_active=True,
            )

    app.dependency_overrides[get_list_cutting_machines_use_case] = lambda: FakeListCuttingMachinesUseCase()
    app.dependency_overrides[get_create_cutting_machine_use_case] = (
        lambda: FakeCreateCuttingMachineUseCase()
    )
    client = TestClient(app)

    list_response = client.get("/admin/cutting-machines")
    create_response = client.post(
        "/admin/cutting-machines",
        json={
            "machine_code": "S-02",
            "name": "Saege 2",
            "kerf_mm": 2.8,
            "is_active": True,
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Saege 1"
    assert create_response.status_code == 201
    assert create_response.json()["machine_code"] == "S-02"
    app.dependency_overrides.clear()


def test_list_and_create_users() -> None:
    app.dependency_overrides[require_admin_user] = lambda: None
    class FakeListUsersUseCase:
        def execute(self) -> list[UserRecord]:
            return [
                UserRecord(
                    id=9,
                    username="admin",
                    role_id=1,
                    display_name="Admin",
                    email="admin@example.com",
                    is_active=True,
                    erp_user_reference=None,
                )
            ]

    class FakeCreateUserUseCase:
        def execute(self, _command: object) -> UserRecord:
            return UserRecord(
                id=10,
                username="planner",
                role_id=2,
                display_name="Planer",
                email="planner@example.com",
                is_active=True,
                erp_user_reference="ERP-U-1",
            )

    app.dependency_overrides[get_list_users_use_case] = lambda: FakeListUsersUseCase()
    app.dependency_overrides[get_create_user_use_case] = lambda: FakeCreateUserUseCase()
    client = TestClient(app)

    list_response = client.get("/admin/users")
    create_response = client.post(
        "/admin/users",
        json={
            "username": "planner",
            "password": "testpass-123",
            "role_id": 2,
            "display_name": "Planer",
            "email": "planner@example.com",
            "is_active": True,
            "erp_user_reference": "ERP-U-1",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["username"] == "admin"
    assert create_response.status_code == 201
    assert create_response.json()["username"] == "planner"
    app.dependency_overrides.clear()
