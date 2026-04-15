"""Pure helpers for combining ERP simulator pipeline with app-only order demand."""

from __future__ import annotations

from domain.entities import AppOrder

CLOSED_APP_STATUSES = frozenset({"done", "canceled"})


def app_only_additional_pipeline_mm(
    app_orders: list[AppOrder],
    erp_order_references: set[str],
) -> int:
    """Summe Brutto-Bedarf (mm) fuer App-Auftraege, die nicht bereits in der ERP-Pipeline stehen.

    Ein App-Auftrag mit gesetztem erp_order_number, der in erp_order_references vorkommt,
    zaehlt nicht (bereits in ERP-/Simulator-Pipeline enthalten).
    """
    total_mm = 0
    for order in app_orders:
        if order.status in CLOSED_APP_STATUSES:
            continue
        ref = (order.erp_order_number or "").strip()
        if ref and ref in erp_order_references:
            continue
        total_mm += order.total_demand_mm
    return total_mm
