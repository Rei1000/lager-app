"""Pydantic schemas for material lookup endpoints."""

from __future__ import annotations

from pydantic import BaseModel

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
