"""Validates ERP order references against the in-process Sage simulator dataset."""

from __future__ import annotations

from adapters.erp.sage_simulator_data import get_order
from ports.erp_order_link_port import ErpOrderLinkPort


class SimulatorErpOrderLinkAdapter(ErpOrderLinkPort):
    def exists_order_reference(self, erp_order_number: str) -> bool:
        normalized = erp_order_number.strip()
        if not normalized:
            return False
        return get_order(normalized) is not None
