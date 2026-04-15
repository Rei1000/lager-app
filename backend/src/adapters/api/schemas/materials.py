"""Pydantic schemas for material lookup endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from application.dtos import OrderPlanPreviewResult
from ports.material_lookup_port import MaterialLookupRecord


class MaterialLookupResponse(BaseModel):
    article_number: str
    name: str
    profile: str | None
    erp_stock_m: float | None
    rest_stock_m: float | None

    @classmethod
    def from_record(cls, record: MaterialLookupRecord) -> "MaterialLookupResponse":
        return cls(
            article_number=record.article_number,
            name=record.name,
            profile=record.profile,
            erp_stock_m=record.erp_stock_m,
            rest_stock_m=record.rest_stock_m,
        )


class OrderPlanPreviewRequest(BaseModel):
    article_number: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    part_length_mm: int = Field(ge=1)
    kerf_mm: float = Field(ge=0)
    rest_piece_consideration_requested: bool = False


class OrderPlanOpenOrderResponse(BaseModel):
    order_reference: str
    required_m: float
    status: str


class OrderPlanPreviewResponse(BaseModel):
    article_number: str
    material_name: str
    stock_m: float
    in_pipeline_m: float
    available_m: float
    open_orders: list[OrderPlanOpenOrderResponse]
    net_required_mm: int
    kerf_total_mm: int
    gross_required_mm: int
    net_required_m: float
    kerf_total_m: float
    gross_required_m: float
    feasible: bool

    @classmethod
    def from_result(cls, result: OrderPlanPreviewResult) -> "OrderPlanPreviewResponse":
        return cls(
            article_number=result.article_number,
            material_name=result.material_name,
            stock_m=result.stock_m,
            in_pipeline_m=result.in_pipeline_m,
            available_m=result.available_m,
            open_orders=[
                OrderPlanOpenOrderResponse(
                    order_reference=o.order_reference,
                    required_m=o.required_m,
                    status=o.status,
                )
                for o in result.open_orders
            ],
            net_required_mm=result.net_required_mm,
            kerf_total_mm=result.kerf_total_mm,
            gross_required_mm=result.gross_required_mm,
            net_required_m=result.net_required_m,
            kerf_total_m=result.kerf_total_m,
            gross_required_m=result.gross_required_m,
            feasible=result.feasible,
        )
