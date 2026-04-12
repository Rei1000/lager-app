"""Pydantic schemas for inventory and stock correction endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from domain.entities import InventoryDifference
from ports.inventory_repository_port import InventoryCountRecord, StockCorrectionRecord


class CreateInventoryCountRequest(BaseModel):
    material_article_number: str = Field(min_length=1)
    counted_stock_mm: int = Field(ge=0)
    counted_by_user_id: int = Field(gt=0)
    comment: str | None = None


class InventoryCountResponse(BaseModel):
    id: int
    material_article_number: str
    counted_stock_mm: int
    reference_stock_mm: int
    difference_mm: int
    difference_type: str
    status: str
    counted_by_user_id: int
    comment: str | None
    created_at: datetime

    @classmethod
    def from_record(cls, record: InventoryCountRecord) -> "InventoryCountResponse":
        return cls(
            id=record.id,
            material_article_number=record.material_article_number,
            counted_stock_mm=record.counted_stock_mm,
            reference_stock_mm=record.reference_stock_mm,
            difference_mm=record.difference_mm,
            difference_type=record.difference_type,
            status=record.status,
            counted_by_user_id=record.counted_by_user_id,
            comment=record.comment,
            created_at=record.created_at,
        )


class CompareInventoryRequest(BaseModel):
    material_article_number: str = Field(min_length=1)
    counted_stock_mm: int = Field(ge=0)


class InventoryDifferenceResponse(BaseModel):
    material_article_number: str
    counted_stock_mm: int
    reference_stock_mm: int
    difference_mm: int
    difference_type: str

    @classmethod
    def from_domain(cls, difference: InventoryDifference) -> "InventoryDifferenceResponse":
        return cls(
            material_article_number=difference.material_article_number,
            counted_stock_mm=difference.counted_stock_mm,
            reference_stock_mm=difference.reference_stock_mm,
            difference_mm=difference.difference_mm,
            difference_type=difference.difference_type,
        )


class CreateStockCorrectionRequest(BaseModel):
    inventory_count_id: int = Field(gt=0)
    requested_by_user_id: int = Field(gt=0)
    comment: str | None = None


class ChangeStockCorrectionStatusRequest(BaseModel):
    acting_user_id: int = Field(gt=0)


class StockCorrectionResponse(BaseModel):
    id: int
    inventory_count_id: int
    material_article_number: str
    correction_mm: int
    status: str
    requested_by_user_id: int
    confirmed_by_user_id: int | None
    canceled_by_user_id: int | None
    comment: str | None
    created_at: datetime
    confirmed_at: datetime | None
    canceled_at: datetime | None

    @classmethod
    def from_record(cls, record: StockCorrectionRecord) -> "StockCorrectionResponse":
        return cls(
            id=record.id,
            inventory_count_id=record.inventory_count_id,
            material_article_number=record.material_article_number,
            correction_mm=record.correction_mm,
            status=record.status,
            requested_by_user_id=record.requested_by_user_id,
            confirmed_by_user_id=record.confirmed_by_user_id,
            canceled_by_user_id=record.canceled_by_user_id,
            comment=record.comment,
            created_at=record.created_at,
            confirmed_at=record.confirmed_at,
            canceled_at=record.canceled_at,
        )
