"""Internal Sage simulator endpoints used by configurable ERP profile mappings."""

from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException, Query

from adapters.erp.sage_simulator_data import (
    get_material,
    get_material_stock,
    get_order,
    list_materials,
    list_orders_by_material,
    send_transfer,
)

router = APIRouter(
    prefix="/simulator/sage",
    tags=["sage-simulator"],
    include_in_schema=False,
)


@router.get("/materials/search")
def search_materials(q: str = Query(default="")) -> list[dict[str, object]]:
    return list_materials(q)


@router.get("/materials/get")
def material_get(material_no: str = Query(...)) -> dict[str, object]:
    payload = get_material(material_no)
    if payload is None:
        raise HTTPException(status_code=404, detail="Material nicht gefunden")
    return payload


@router.get("/materials/stock")
def material_stock_get(material_no: str = Query(...)) -> dict[str, object]:
    payload = get_material_stock(material_no)
    if payload is None:
        raise HTTPException(status_code=404, detail="Bestand nicht gefunden")
    return payload


@router.get("/orders/by-material")
def orders_by_material(material_no: str = Query(...)) -> list[dict[str, object]]:
    return list_orders_by_material(material_no)


@router.get("/orders/get")
def order_get(order_no: str = Query(...)) -> dict[str, object]:
    payload = get_order(order_no)
    if payload is None:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    return payload


@router.post("/transfers/{transfer_id}/send")
def transfer_send(
    transfer_id: str,
    payload: dict[str, object] | None = Body(default=None),
) -> dict[str, object]:
    return send_transfer(transfer_id, payload or {})
