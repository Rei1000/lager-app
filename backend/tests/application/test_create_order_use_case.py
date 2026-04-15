"""CreateOrderUseCase: persist App order, material link, sequential evaluation (fakes, no DB)."""

from __future__ import annotations

from datetime import date

from adapters.api.schemas.orders import OrderResponse
from application.dtos import CreateOrderCommand
from application.use_cases.create_order_use_case import CreateOrderUseCase
from domain.entities import AppOrder
from domain.value_objects import TrafficLight
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshot, StockSnapshotPort


class _FakeOrderRepository(OrderRepositoryPort):
    def __init__(self) -> None:
        self.orders: list[AppOrder] = []

    def list_all(self) -> list[AppOrder]:
        return list(self.orders)

    def get_by_id(self, order_id: str) -> AppOrder | None:
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def list_by_material(self, material_article_number: str) -> list[AppOrder]:
        return [o for o in self.orders if o.material_article_number == material_article_number]

    def save(self, order: AppOrder) -> None:
        for idx, existing in enumerate(self.orders):
            if existing.order_id == order.order_id:
                self.orders[idx] = order
                return
        self.orders.append(order)


class _FixedSnapshot(StockSnapshotPort):
    def __init__(self, snapshot: StockSnapshot) -> None:
        self._snapshot = snapshot

    def get_snapshot(self, material_article_number: str) -> StockSnapshot:
        return self._snapshot


def test_create_order_persists_app_order_with_material_and_evaluates_traffic_light() -> None:
    """Neuer Auftrag wird gespeichert, materialbezogen verknüpft, Priorität fortlaufend."""
    repo = _FakeOrderRepository()
    # Großzügiger Bestand: Ampel grün für ersten Auftrag
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    uc = CreateOrderUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=None,
    )
    created = uc.execute(
        CreateOrderCommand(
            order_id="ext-new-1",
            material_article_number="100-FE-025",
            quantity=2,
            part_length_mm=1000,
            kerf_mm=2,
            include_rest_stock=False,
            acting_user_id=42,
        )
    )
    assert created.order_id == "ext-new-1"
    assert created.material_article_number == "100-FE-025"
    assert created.status == "draft"
    assert created.priority_order == 1
    assert created.traffic_light is TrafficLight.GREEN
    assert len(repo.orders) == 1
    assert repo.get_by_id("ext-new-1") is not None


def test_create_order_second_on_same_material_gets_next_priority() -> None:
    repo = _FakeOrderRepository()
    repo.orders.append(
        AppOrder(
            order_id="existing",
            material_article_number="ART-X",
            quantity=1,
            part_length_mm=500,
            kerf_mm=0,
            include_rest_stock=False,
            status="draft",
            priority_order=1,
            created_by_user_id=1,
        )
    )
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    uc = CreateOrderUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=None,
    )
    created = uc.execute(
        CreateOrderCommand(
            order_id="ext-new-2",
            material_article_number="ART-X",
            quantity=1,
            part_length_mm=500,
            kerf_mm=0,
            include_rest_stock=False,
            acting_user_id=1,
        )
    )
    assert created.priority_order == 2


class _FailingAuditLogPort:
    """Simuliert fehlgeschlagenes Audit (z. B. IntegrityError -> ValueError im Adapter)."""

    def log_event(
        self,
        *,
        entity_type: str,
        entity_id: str | None,
        action: str,
        user_id: int | None,
        payload: dict | None = None,
        comment: str | None = None,
    ) -> object:
        raise ValueError("Audit-Event konnte nicht gespeichert werden")

    def list_events(self, **kwargs: object) -> list:
        return []


def test_create_order_succeeds_when_audit_log_fails() -> None:
    """Audit ist nachgelagert: Order bleibt gueltig, Use Case wirft nicht."""
    repo = _FakeOrderRepository()
    snapshot = StockSnapshot(
        erp_stock_mm=10_000_000,
        open_erp_orders_mm=0,
        app_reservations_mm=0,
        rest_stock_mm=0,
    )
    uc = CreateOrderUseCase(
        order_repository=repo,
        stock_snapshot_port=_FixedSnapshot(snapshot),
        audit_log_port=_FailingAuditLogPort(),
    )
    created = uc.execute(
        CreateOrderCommand(
            order_id="ext-audit-fail",
            material_article_number="100-FE-025",
            quantity=1,
            part_length_mm=1000,
            kerf_mm=0,
            include_rest_stock=False,
            acting_user_id=1,
        )
    )
    assert created.order_id == "ext-audit-fail"
    assert len(repo.orders) == 1
    assert repo.get_by_id("ext-audit-fail") is not None


def test_order_response_display_order_code_uses_persisted_row_id() -> None:
    order = AppOrder(
        order_id="client-uuid-1",
        material_article_number="ART-1",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        persisted_row_id=42,
        customer_name="Demo-Kunde",
        due_date=date(2026, 5, 1),
        material_description="Profil X",
    )
    order.traffic_light = TrafficLight.GREEN
    response = OrderResponse.from_domain(order)
    assert response.display_order_code == "APP-000042"
    assert response.persisted_row_id == 42
    assert response.material_description == "Profil X"
    assert response.required_m == 1.0
    assert response.customer_name == "Demo-Kunde"
    assert response.due_date == date(2026, 5, 1)
