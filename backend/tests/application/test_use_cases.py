from __future__ import annotations

from dataclasses import dataclass

import pytest

from application.dtos import (
    CreateOrderCommand,
    LinkErpOrderCommand,
    RecalculateOrdersCommand,
    ReprioritizeOrdersCommand,
    ReserveOrderCommand,
)
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.link_erp_order_use_case import LinkErpOrderUseCase
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase
from domain.entities import AppOrder
from domain.value_objects import TrafficLight
from ports.erp_order_link_port import ErpOrderLinkPort
from ports.order_repository_port import OrderRepositoryPort
from ports.stock_snapshot_port import StockSnapshot, StockSnapshotPort


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
