from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from adapters.api.app import app
from adapters.api.dependencies.auth import RequestUser, require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_auth_token_service,
    get_create_order_use_case,
    get_current_user_use_case,
    get_reprioritize_orders_use_case,
    get_reserve_order_use_case,
    get_update_order_use_case,
)
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.errors import NotFoundError
from domain.entities import AppOrder
from domain.value_objects import TrafficLight
from ports.auth_identity_port import AuthIdentityRecord
from ports.stock_snapshot_port import StockSnapshot

from tests.application.test_create_order_use_case import (
    _FailingAuditLogPort,
    _FakeOrderRepository,
    _FixedSnapshot,
)


def _make_order(order_id: str, priority: int = 1, status: str = "draft") -> AppOrder:
    order = AppOrder(
        order_id=order_id,
        material_article_number="ART-001",
        quantity=2,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=priority,
        status=status,
    )
    order.traffic_light = TrafficLight.GREEN
    return order


def test_create_order_endpoint_returns_created_order() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeCreateOrderUseCase:
        def execute(self, _command: object) -> AppOrder:
            return _make_order("A100", priority=2, status="draft")

    app.dependency_overrides[get_create_order_use_case] = lambda: FakeCreateOrderUseCase()
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "A100",
            "material_article_number": "ART-001",
            "quantity": 2,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["order_id"] == "A100"
    assert response.json()["traffic_light"] == "green"
    app.dependency_overrides.clear()


def test_create_order_persists_optional_customer_and_due_date() -> None:
    """POST /orders: optionale Felder werden im Use Case normalisiert und in OrderResponse ausgegeben."""
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    repo = _FakeOrderRepository()
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    real_uc = CreateOrderUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=None,
    )
    app.dependency_overrides[get_create_order_use_case] = lambda: real_uc
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "opt-fields-1",
            "material_article_number": "ART-001",
            "quantity": 1,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
            "customer_name": "  Kunde X  ",
            "due_date": "2026-07-20",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["customer_name"] == "Kunde X"
    assert body["due_date"] == "2026-07-20"
    saved = repo.get_by_id("opt-fields-1")
    assert saved is not None
    assert saved.customer_name == "Kunde X"
    assert saved.due_date == date(2026, 7, 20)
    app.dependency_overrides.clear()


def test_post_orders_returns_201_when_audit_log_fails() -> None:
    """Echtes CreateOrderUseCase mit fehlendem Audit: API bleibt erfolgreich (201)."""
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    repo = _FakeOrderRepository()
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    real_uc = CreateOrderUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=_FailingAuditLogPort(),
    )
    app.dependency_overrides[get_create_order_use_case] = lambda: real_uc
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "api-audit-fail-1",
            "material_article_number": "ART-001",
            "quantity": 1,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["order_id"] == "api-audit-fail-1"
    assert len(repo.orders) == 1
    app.dependency_overrides.clear()


def test_post_reprioritize_returns_200_when_audit_log_fails() -> None:
    """Echtes ReprioritizeOrdersUseCase mit fehlendem Audit: API bleibt erfolgreich (200)."""
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    repo = _FakeOrderRepository()
    repo.orders.extend(
        [
            AppOrder(
                order_id="api-reprio-a",
                material_article_number="ART-001",
                quantity=1,
                part_length_mm=1000,
                kerf_mm=0,
                include_rest_stock=False,
                priority_order=1,
            ),
            AppOrder(
                order_id="api-reprio-b",
                material_article_number="ART-001",
                quantity=1,
                part_length_mm=1000,
                kerf_mm=0,
                include_rest_stock=False,
                priority_order=2,
            ),
        ]
    )
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    real_uc = ReprioritizeOrdersUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=_FailingAuditLogPort(),
    )

    def _uc() -> ReprioritizeOrdersUseCase:
        return real_uc

    app.dependency_overrides[get_reprioritize_orders_use_case] = _uc
    client = TestClient(app)

    response = client.post(
        "/orders/reprioritize",
        json={
            "material_article_number": "ART-001",
            "ordered_ids": ["api-reprio-b", "api-reprio-a"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body[0]["order_id"] == "api-reprio-b"
    assert body[0]["priority_order"] == 1
    saved_b = next(o for o in repo.orders if o.order_id == "api-reprio-b")
    assert saved_b.priority_order == 1
    app.dependency_overrides.clear()


def test_reserve_order_endpoint_returns_reserved_order() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeReserveOrderUseCase:
        def execute(self, _command: object) -> AppOrder:
            return _make_order("A200", priority=1, status="reserved")

    app.dependency_overrides[get_reserve_order_use_case] = lambda: FakeReserveOrderUseCase()
    client = TestClient(app)

    response = client.post("/orders/A200/reserve")

    assert response.status_code == 200
    assert response.json()["status"] == "reserved"
    app.dependency_overrides.clear()


def test_reserve_order_endpoint_maps_not_found_to_404() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeReserveOrderUseCase:
        def execute(self, _command: object) -> AppOrder:
            raise NotFoundError("Auftrag nicht gefunden: A404")

    app.dependency_overrides[get_reserve_order_use_case] = lambda: FakeReserveOrderUseCase()
    client = TestClient(app)

    response = client.post("/orders/A404/reserve")

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_reprioritize_orders_endpoint_returns_reordered_list() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=2,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeReprioritizeOrdersUseCase:
        def execute(self, _command: object) -> list[AppOrder]:
            return [
                _make_order("A2", priority=1, status="draft"),
                _make_order("A1", priority=2, status="draft"),
            ]

    app.dependency_overrides[get_reprioritize_orders_use_case] = lambda: FakeReprioritizeOrdersUseCase()
    client = TestClient(app)

    response = client.post(
        "/orders/reprioritize",
        json={
            "material_article_number": "ART-001",
            "ordered_ids": ["A2", "A1"],
        },
    )

    assert response.status_code == 200
    assert response.json()[0]["order_id"] == "A2"
    assert response.json()[0]["priority_order"] == 1
    app.dependency_overrides.clear()


def test_list_orders_endpoint_returns_orders_with_fields() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeListOrdersUseCase:
        def execute(self, **_kwargs: object) -> list[AppOrder]:
            return [
                _make_order("A1", priority=1, status="checked"),
                _make_order("A2", priority=2, status="reserved"),
            ]

    from adapters.api.dependencies.use_cases import get_list_orders_detailed_use_case

    app.dependency_overrides[get_list_orders_detailed_use_case] = lambda: FakeListOrdersUseCase()
    client = TestClient(app)

    response = client.get("/orders")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["status"] == "checked"
    app.dependency_overrides.clear()


def test_patch_order_returns_updated_order() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeUpdateOrderUseCase:
        def execute(self, command: object) -> AppOrder:
            oid = getattr(command, "order_id", "")
            o = _make_order(str(oid), priority=1, status="draft")
            o.quantity = getattr(command, "quantity", 2)
            return o

    app.dependency_overrides[get_update_order_use_case] = lambda: FakeUpdateOrderUseCase()
    client = TestClient(app)

    response = client.patch(
        "/orders/E1",
        json={"quantity": 5, "part_length_mm": 1000, "kerf_mm": 0},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5
    app.dependency_overrides.clear()


def test_get_order_detail_endpoint_returns_one_order() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )

    class FakeGetOrderDetailUseCase:
        def execute(self, _order_id: str) -> AppOrder:
            return _make_order("A42", priority=3, status="reserved")

    from adapters.api.dependencies.use_cases import get_get_order_detail_use_case

    app.dependency_overrides[get_get_order_detail_use_case] = lambda: FakeGetOrderDetailUseCase()
    client = TestClient(app)

    response = client.get("/orders/A42")

    assert response.status_code == 200
    assert response.json()["order_id"] == "A42"
    app.dependency_overrides.clear()


def test_orders_endpoint_without_token_returns_401() -> None:
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "A100",
            "material_article_number": "ART-001",
            "quantity": 2,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
        },
    )

    assert response.status_code == 401


def test_orders_endpoint_with_invalid_token_returns_401() -> None:
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "A100",
            "material_article_number": "ART-001",
            "quantity": 2,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
        },
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_orders_endpoint_with_valid_token_returns_success() -> None:
    class FakeCurrentUserUseCase:
        def execute(self, _user_id: int) -> AuthIdentityRecord:
            return AuthIdentityRecord(
                user_id=1,
                username="lager",
                password_hash="ignored",
                role_code="lager",
                role_name="Lager",
                is_active=True,
            )

    class FakeCreateOrderUseCase:
        def execute(self, _command: object) -> AppOrder:
            return _make_order("A100", priority=2, status="draft")

    token = get_auth_token_service().issue_access_token(user_id=1, role_code="lager")
    app.dependency_overrides[get_current_user_use_case] = lambda: FakeCurrentUserUseCase()
    app.dependency_overrides[get_create_order_use_case] = lambda: FakeCreateOrderUseCase()
    client = TestClient(app)

    response = client.post(
        "/orders",
        json={
            "order_id": "A100",
            "material_article_number": "ART-001",
            "quantity": 2,
            "part_length_mm": 1000,
            "kerf_mm": 0,
            "include_rest_stock": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["order_id"] == "A100"
    app.dependency_overrides.clear()


def test_reprioritize_unauthenticated_returns_401() -> None:
    client = TestClient(app)

    response = client.post(
        "/orders/reprioritize",
        json={
            "material_article_number": "ART-001",
            "ordered_ids": ["A2", "A1"],
        },
    )

    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_link_erp_requires_leitung_or_admin() -> None:
    app.dependency_overrides[require_authenticated_user] = lambda: RequestUser(
        user_id=1,
        username="lager",
        role_code="lager",
        role_name="Lager",
    )
    client = TestClient(app)

    response = client.post(
        "/orders/A100/link-erp",
        json={"erp_order_number": "ERP-42"},
    )

    assert response.status_code == 403
    app.dependency_overrides.clear()
