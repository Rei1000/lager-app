"""Material lookup API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import (
    get_material_by_article_number_use_case,
    get_preview_order_plan_use_case,
    get_search_materials_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.materials import (
    MaterialLookupResponse,
    OrderPlanPreviewRequest,
    OrderPlanPreviewResponse,
)
from application.dtos import PreviewOrderPlanCommand, SearchMaterialsCommand
from application.use_cases.material_lookup_use_cases import (
    GetMaterialByArticleNumberUseCase,
    SearchMaterialsUseCase,
)
from application.use_cases.preview_order_plan_use_case import PreviewOrderPlanUseCase

router = APIRouter(
    prefix="/materials",
    tags=["materials"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("/plan-preview", response_model=OrderPlanPreviewResponse)
def preview_order_plan(
    payload: OrderPlanPreviewRequest,
    use_case: PreviewOrderPlanUseCase = Depends(get_preview_order_plan_use_case),
) -> OrderPlanPreviewResponse:
    """Read-only planning preview: demand vs simulator/ERP availability (no order persisted)."""
    try:
        result = use_case.execute(
            PreviewOrderPlanCommand(
                article_number=payload.article_number,
                quantity=payload.quantity,
                part_length_mm=payload.part_length_mm,
                kerf_mm=float(payload.kerf_mm),
                rest_piece_consideration_requested=payload.rest_piece_consideration_requested,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return OrderPlanPreviewResponse.from_result(result)


@router.get("/search", response_model=list[MaterialLookupResponse])
def search_materials(
    query: str = Query(min_length=1),
    use_case: SearchMaterialsUseCase = Depends(get_search_materials_use_case),
) -> list[MaterialLookupResponse]:
    try:
        records = use_case.execute(SearchMaterialsCommand(query=query))
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return [MaterialLookupResponse.from_record(record) for record in records]


@router.get("/{article_number}", response_model=MaterialLookupResponse)
def get_material_by_article_number(
    article_number: str,
    use_case: GetMaterialByArticleNumberUseCase = Depends(get_material_by_article_number_use_case),
) -> MaterialLookupResponse:
    try:
        record = use_case.execute(article_number)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return MaterialLookupResponse.from_record(record)
