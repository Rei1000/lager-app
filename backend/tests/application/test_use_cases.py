from __future__ import annotations

from dataclasses import dataclass

import pytest

from application.dtos import (
    CreateOrderCommand,
    LinkErpOrderCommand,
    RecalculateOrdersCommand,
    ReprioritizeOrdersCommand,
    ReserveOrderCommand,
    UpdateOrderCommand,
)
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.link_erp_order_use_case import LinkErpOrderUseCase
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase
from application.use_cases.update_order_use_case import UpdateOrderUseCase
from domain.entities import AppOrder
from domain.value_objects import TrafficLight
from ports.erp_order_link_port import ErpOrderLinkPort
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshot, StockSnapshotPort

from application.errors import NotFoundError

from tests.application.test_create_order_use_case import _FailingAuditLogPort


@dataclass
class FakeOrderRepository(OrderRepositoryPort):
    orders: list[AppOrder]

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
        existing = self.get_by_id(order.order_id or "")
        if existing is None:
            self.orders.append(order)
            return
        idx = self.orders.index(existing)
        self.orders[idx] = order


@dataclass
class FakeStockSnapshotPort(StockSnapshotPort):
    snapshot: StockSnapshot

    def get_snapshot(self, material_article_number: str) -> StockSnapshot:
        return self.snapshot


@dataclass
class FakeErpOrderLinkPort(ErpOrderLinkPort):
    existing_references: set[str]

    def exists_order_reference(self, erp_order_number: str) -> bool:
        return erp_order_number in self.existing_references


def test_create_order_use_case_persists_new_order_with_next_priority() -> None:
    repo = FakeOrderRepository(
        orders=[
            AppOrder(
                order_id="A1",
                material_article_number="ART-001",
                quantity=2,
                part_length_mm=1000,
                kerf_mm=0,
                include_rest_stock=False,
                priority_order=1,
            )
        ]
    )
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=10_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    use_case = CreateOrderUseCase(order_repository=repo, stock_snapshot_port=stock)

    created = use_case.execute(
        CreateOrderCommand(
            order_id="A2",
            material_article_number="ART-001",
            quantity=3,
            part_length_mm=1000,
            kerf_mm=0,
            include_rest_stock=False,
            acting_user_id=1,
        )
    )

    assert created.order_id == "A2"
    assert created.priority_order == 2
    assert len(repo.orders) == 2


def test_recalculate_orders_use_case_updates_traffic_lights() -> None:
    first = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        order_id="A2",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )
    repo = FakeOrderRepository(orders=[first, second])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=6_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    use_case = RecalculateOrdersUseCase(order_repository=repo, stock_snapshot_port=stock)

    updated = use_case.execute(RecalculateOrdersCommand(material_article_number="ART-001"))

    assert updated[0].traffic_light is TrafficLight.GREEN
    assert updated[1].traffic_light is TrafficLight.RED


def test_reserve_order_use_case_moves_status_to_reserved() -> None:
    order = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status="checked",
        priority_order=1,
    )
    repo = FakeOrderRepository(orders=[order])
    use_case = ReserveOrderUseCase(order_repository=repo)

    reserved = use_case.execute(ReserveOrderCommand(order_id="A1", acting_user_id=1))

    assert reserved.status == "reserved"


def test_reprioritize_orders_use_case_applies_new_order_and_recalculates() -> None:
    first = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        order_id="A2",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )
    repo = FakeOrderRepository(orders=[first, second])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=6_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    use_case = ReprioritizeOrdersUseCase(order_repository=repo, stock_snapshot_port=stock)

    reprioritized = use_case.execute(
        ReprioritizeOrdersCommand(
            material_article_number="ART-001",
            ordered_ids=["A2", "A1"],
            acting_user_id=2,
        )
    )

    assert reprioritized[0].order_id == "A2"
    assert reprioritized[0].priority_order == 1
    assert reprioritized[0].traffic_light is TrafficLight.GREEN
    assert reprioritized[1].traffic_light is TrafficLight.RED
    assert repo.get_by_id("A2") is not None
    assert repo.get_by_id("A2").priority_order == 1
    assert repo.get_by_id("A1") is not None
    assert repo.get_by_id("A1").priority_order == 2


def test_reprioritize_succeeds_even_if_snapshot_app_reservations_mm_is_huge() -> None:
    """Simulator-Snapshot kann aggregiertes app_only enthalten; die sequentielle Ampel nutzt nur ERP-Stückgut minus Pipeline."""
    first = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        order_id="A2",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )
    repo = FakeOrderRepository(orders=[first, second])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=50_000,
            open_erp_orders_mm=0,
            app_reservations_mm=999_999_999,
            rest_stock_mm=0,
        )
    )
    use_case = ReprioritizeOrdersUseCase(order_repository=repo, stock_snapshot_port=stock)

    reprioritized = use_case.execute(
        ReprioritizeOrdersCommand(
            material_article_number="ART-001",
            ordered_ids=["A1", "A2"],
            acting_user_id=1,
        )
    )

    assert len(reprioritized) == 2
    assert reprioritized[0].traffic_light is TrafficLight.GREEN
    assert reprioritized[1].traffic_light is TrafficLight.GREEN


def test_reprioritize_succeeds_when_audit_log_fails() -> None:
    """Audit ist nachgelagert: Reihung bleibt gueltig, Use Case wirft nicht."""
    first = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        order_id="A2",
        material_article_number="ART-001",
        quantity=4,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )
    repo = FakeOrderRepository(orders=[first, second])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=6_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    use_case = ReprioritizeOrdersUseCase(
        order_repository=repo,
        stock_snapshot_port=stock,
        audit_log_port=_FailingAuditLogPort(),
    )

    reprioritized = use_case.execute(
        ReprioritizeOrdersCommand(
            material_article_number="ART-001",
            ordered_ids=["A2", "A1"],
            acting_user_id=2,
        )
    )

    assert len(reprioritized) == 2
    assert reprioritized[0].order_id == "A2"
    assert repo.get_by_id("A2") is not None
    assert repo.get_by_id("A2").priority_order == 1


def test_reprioritize_persists_when_stock_pool_is_underwater_no_exception() -> None:
    """Knapp/unterdeckt: interner Stückgut-Rest kann negativ werden; Ampel rot, keine Exception."""
    first = AppOrder(
        order_id="U1",
        material_article_number="ART-UW",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    second = AppOrder(
        order_id="U2",
        material_article_number="ART-UW",
        quantity=5,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=2,
    )
    repo = FakeOrderRepository(orders=[first, second])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=3_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    use_case = ReprioritizeOrdersUseCase(order_repository=repo, stock_snapshot_port=stock)

    out = use_case.execute(
        ReprioritizeOrdersCommand(
            material_article_number="ART-UW",
            ordered_ids=["U2", "U1"],
            acting_user_id=1,
        )
    )

    assert len(out) == 2
    assert out[0].order_id == "U2"
    assert out[0].priority_order == 1
    assert out[1].traffic_light is TrafficLight.RED
    assert out[0].disposition_available_before_mm >= 0
    assert out[1].disposition_available_before_mm >= 0


def test_update_order_use_case_changes_quantity_and_recalculates() -> None:
    order = AppOrder(
        order_id="E1",
        material_article_number="ART-001",
        quantity=2,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        priority_order=1,
    )
    repo = FakeOrderRepository(orders=[order])
    stock = FakeStockSnapshotPort(
        snapshot=StockSnapshot(
            erp_stock_mm=50_000,
            open_erp_orders_mm=0,
            app_reservations_mm=0,
            rest_stock_mm=0,
        )
    )
    recalc = RecalculateOrdersUseCase(order_repository=repo, stock_snapshot_port=stock)
    uc = UpdateOrderUseCase(order_repository=repo, recalculate_orders_use_case=recalc, audit_log_port=None)
    out = uc.execute(
        UpdateOrderCommand(
            order_id="E1",
            quantity=10,
            part_length_mm=1000,
            kerf_mm=0,
            acting_user_id=1,
        )
    )
    assert out.quantity == 10
    saved = repo.get_by_id("E1")
    assert saved is not None
    assert saved.quantity == 10


def test_update_order_use_case_rejects_done_status() -> None:
    order = AppOrder(
        order_id="E2",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status="done",
        priority_order=1,
    )
    repo = FakeOrderRepository(orders=[order])
    recalc = RecalculateOrdersUseCase(
        order_repository=repo,
        stock_snapshot_port=FakeStockSnapshotPort(
            snapshot=StockSnapshot(erp_stock_mm=1, open_erp_orders_mm=0, app_reservations_mm=0, rest_stock_mm=0)
        ),
    )
    uc = UpdateOrderUseCase(order_repository=repo, recalculate_orders_use_case=recalc, audit_log_port=None)
    with pytest.raises(ValueError, match="Abgeschlossene"):
        uc.execute(
            UpdateOrderCommand(
                order_id="E2",
                quantity=2,
                part_length_mm=1000,
                kerf_mm=0,
                acting_user_id=1,
            )
        )


def test_update_order_use_case_not_found() -> None:
    repo = FakeOrderRepository(orders=[])
    recalc = RecalculateOrdersUseCase(
        order_repository=repo,
        stock_snapshot_port=FakeStockSnapshotPort(
            snapshot=StockSnapshot(erp_stock_mm=1, open_erp_orders_mm=0, app_reservations_mm=0, rest_stock_mm=0)
        ),
    )
    uc = UpdateOrderUseCase(order_repository=repo, recalculate_orders_use_case=recalc, audit_log_port=None)
    with pytest.raises(NotFoundError):
        uc.execute(
            UpdateOrderCommand(
                order_id="missing",
                quantity=1,
                part_length_mm=1000,
                kerf_mm=0,
                acting_user_id=1,
            )
        )


def test_link_erp_order_use_case_links_and_transitions_status() -> None:
    order = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status="reserved",
        priority_order=1,
    )
    repo = FakeOrderRepository(orders=[order])
    erp_port = FakeErpOrderLinkPort(existing_references={"SAGE-ORD-2026-001"})
    use_case = LinkErpOrderUseCase(order_repository=repo, erp_order_link_port=erp_port)

    linked = use_case.execute(
        LinkErpOrderCommand(order_id="A1", erp_order_number="SAGE-ORD-2026-001", acting_user_id=3)
    )

    assert linked.status == "linked"
    assert linked.erp_order_number == "SAGE-ORD-2026-001"


def test_link_erp_order_use_case_rejects_unknown_reference() -> None:
    order = AppOrder(
        order_id="A1",
        material_article_number="ART-001",
        quantity=1,
        part_length_mm=1000,
        kerf_mm=0,
        include_rest_stock=False,
        status="reserved",
        priority_order=1,
    )
    repo = FakeOrderRepository(orders=[order])
    erp_port = FakeErpOrderLinkPort(existing_references=set())
    use_case = LinkErpOrderUseCase(order_repository=repo, erp_order_link_port=erp_port)

    with pytest.raises(ValueError):
        use_case.execute(
            LinkErpOrderCommand(order_id="A1", erp_order_number="ERP-99", acting_user_id=3)
        )
