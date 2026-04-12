from __future__ import annotations

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, get_current_request_user
from adapters.api.dependencies.use_cases import get_login_use_case
from application.errors import AuthenticationError
from application.use_cases.auth_use_cases import LoginResult


def test_login_endpoint_returns_access_token() -> None:
    class FakeLoginUseCase:
        def execute(self, _command: object) -> LoginResult:
            return LoginResult(
                access_token="token-123",
                token_type="bearer",
                expires_in_seconds=3600,
                user_id=1,
                username="admin",
                role_code="admin",
                login_type="admin",
                selected_connection="sage-simulator",
            )

    app.dependency_overrides[get_login_use_case] = lambda: FakeLoginUseCase()
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "secret123",
            "login_type": "admin",
            "selected_connection": "sage-simulator",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-123"
    assert response.json()["login_type"] == "admin"
    app.dependency_overrides.clear()


def test_login_endpoint_returns_401_on_invalid_credentials() -> None:
    class FakeLoginUseCase:
        def execute(self, _command: object) -> LoginResult:
            raise AuthenticationError("Ungueltige Anmeldedaten")

    app.dependency_overrides[get_login_use_case] = lambda: FakeLoginUseCase()
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "wrong",
            "login_type": "admin",
            "selected_connection": "sage-simulator",
        },
    )

    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_login_endpoint_returns_400_for_unsupported_connection() -> None:
    class FakeLoginUseCase:
        def execute(self, _command: object) -> LoginResult:
            raise ValueError("Verbindung noch nicht unterstuetzt")

    app.dependency_overrides[get_login_use_case] = lambda: FakeLoginUseCase()
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={
            "username": "lager",
            "password": "secret123",
            "login_type": "erp",
            "selected_connection": "middleware",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verbindung noch nicht unterstuetzt"
    app.dependency_overrides.clear()


def test_admin_endpoints_require_authentication() -> None:
    client = TestClient(app)
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_endpoints_require_admin_role() -> None:
    def fake_lager_user() -> RequestUser:
        return RequestUser(user_id=2, username="lager", role_code="lager", role_name="Lager")

    app.dependency_overrides[get_current_request_user] = fake_lager_user
    client = TestClient(app)

    response = client.get("/admin/users")

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_inventory_endpoints_require_authentication() -> None:
    client = TestClient(app)
    response = client.get("/inventory/counts")
    assert response.status_code == 401
