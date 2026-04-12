from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.use_cases.erp_read_use_cases import (
    GetErpMaterialStockUseCase,
    GetErpMaterialUseCase,
    ValidateErpOrderReferenceUseCase,
)
from ports.erp_material_port import ErpMaterialPort
from ports.erp_order_port import ErpOrderPort


@dataclass
class FakeErpMaterialPort(ErpMaterialPort):
    material_payload: dict[str, Any]
    stock_payload: dict[str, Any]

    def search_materials(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        return [self.material_payload]

    def get_material(self, material_reference: str) -> dict[str, Any]:
        return self.material_payload if material_reference == "MAT-1" else {}

    def get_material_stock(self, material_reference: str) -> dict[str, Any]:
        return self.stock_payload if material_reference == "MAT-1" else {}


@dataclass
class FakeErpOrderPort(ErpOrderPort):
    valid_references: set[str]

    def list_orders_by_material(self, material_reference: str) -> list[dict[str, Any]]:
        return []

    def validate_order_reference(self, order_reference: str) -> bool:
        return order_reference in self.valid_references


def test_get_erp_material_use_case_returns_payload() -> None:
    port = FakeErpMaterialPort(
        material_payload={"material_reference": "MAT-1", "name": "Steel"},
        stock_payload={"material_reference": "MAT-1", "stock_m": 10.5},
    )
    use_case = GetErpMaterialUseCase(erp_material_port=port)

    payload = use_case.execute("MAT-1")

    assert payload["name"] == "Steel"


def test_get_erp_material_stock_use_case_returns_payload() -> None:
    port = FakeErpMaterialPort(
        material_payload={"material_reference": "MAT-1", "name": "Steel"},
        stock_payload={"material_reference": "MAT-1", "stock_m": 10.5},
    )
    use_case = GetErpMaterialStockUseCase(erp_material_port=port)

    payload = use_case.execute("MAT-1")

    assert payload["stock_m"] == 10.5


def test_validate_erp_order_reference_use_case_returns_boolean() -> None:
    use_case = ValidateErpOrderReferenceUseCase(erp_order_port=FakeErpOrderPort({"ERP-42"}))

    assert use_case.execute("ERP-42") is True
    assert use_case.execute("ERP-404") is False
