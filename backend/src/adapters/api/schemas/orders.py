"""Pydantic schemas for order API endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from domain.entities import AppOrder


class CreateOrderRequest(BaseModel):
    order_id: str = Field(min_length=1)
    material_article_number: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    part_length_mm: int = Field(gt=0)
    kerf_mm: int = Field(ge=0)
    include_rest_stock: bool


class ReprioritizeOrdersRequest(BaseModel):
    material_article_number: str = Field(min_length=1)
    ordered_ids: list[str] = Field(min_length=1)


class LinkErpOrderRequest(BaseModel):
    erp_order_number: str = Field(min_length=1)


class RecalculateOrdersRequest(BaseModel):
    material_article_number: str = Field(min_length=1)


class OrderResponse(BaseModel):
    order_id: str | None
    display_order_code: str
    persisted_row_id: int | None
    material_article_number: str
    quantity: int
    part_length_mm: int
    kerf_mm: int
    include_rest_stock: bool
    status: str
    priority_order: int | None
    traffic_light: str | None
    erp_order_number: str | None
    total_demand_mm: int

    @classmethod
    def from_domain(cls, order: AppOrder) -> "OrderResponse":
        if order.persisted_row_id is not None:
            display = f"APP-{order.persisted_row_id:06d}"
        else:
            display = (order.order_id or "").strip()
        return cls(
            order_id=order.order_id,
            display_order_code=display,
            persisted_row_id=order.persisted_row_id,
            material_article_number=order.material_article_number,
            quantity=order.quantity,
            part_length_mm=order.part_length_mm,
            kerf_mm=order.kerf_mm,
            include_rest_stock=order.include_rest_stock,
            status=order.status,
            priority_order=order.priority_order,
            traffic_light=order.traffic_light.value if order.traffic_light is not None else None,
            erp_order_number=order.erp_order_number,
            total_demand_mm=order.total_demand_mm,
        )


class DashboardOverviewResponse(BaseModel):
    open_orders_count: int
    critical_orders_count: int
    open_orders: list[OrderResponse]
