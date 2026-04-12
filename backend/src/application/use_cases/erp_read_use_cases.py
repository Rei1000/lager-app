"""Use cases for ERP read operations."""

from __future__ import annotations

from ports.erp_material_port import ErpMaterialPort
from ports.erp_order_port import ErpOrderPort


class GetErpMaterialUseCase:
    def __init__(self, erp_material_port: ErpMaterialPort) -> None:
        self._erp_material_port = erp_material_port

    def execute(self, reference: str) -> dict[str, object]:
        normalized = reference.strip()
        if not normalized:
            raise ValueError("reference darf nicht leer sein")
        payload = self._erp_material_port.get_material(normalized)
        if not payload:
            raise ValueError(f"ERP-Material nicht gefunden: {normalized}")
        return payload


class GetErpMaterialStockUseCase:
    def __init__(self, erp_material_port: ErpMaterialPort) -> None:
        self._erp_material_port = erp_material_port

    def execute(self, reference: str) -> dict[str, object]:
        normalized = reference.strip()
        if not normalized:
            raise ValueError("reference darf nicht leer sein")
        payload = self._erp_material_port.get_material_stock(normalized)
        if not payload:
            raise ValueError(f"ERP-Bestand nicht gefunden: {normalized}")
        return payload


class ValidateErpOrderReferenceUseCase:
    def __init__(self, erp_order_port: ErpOrderPort) -> None:
        self._erp_order_port = erp_order_port

    def execute(self, reference: str) -> bool:
        normalized = reference.strip()
        if not normalized:
            raise ValueError("reference darf nicht leer sein")
        return self._erp_order_port.validate_order_reference(normalized)
