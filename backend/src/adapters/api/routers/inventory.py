"""Inventory and stock correction API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import (
    require_authenticated_user,
    require_lager_plus,
    require_leitung_or_admin,
)
from adapters.api.dependencies.use_cases import (
    get_cancel_stock_correction_use_case,
    get_compare_inventory_to_reference_use_case,
    get_confirm_stock_correction_use_case,
    get_create_inventory_count_use_case,
    get_create_stock_correction_use_case,
    get_list_inventory_counts_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.inventory import (
    ChangeStockCorrectionStatusRequest,
    CompareInventoryRequest,
    CreateInventoryCountRequest,
    CreateStockCorrectionRequest,
    InventoryCountResponse,
    InventoryDifferenceResponse,
    StockCorrectionResponse,
)
from application.dtos import (
    ChangeStockCorrectionStatusCommand,
    CompareInventoryToReferenceCommand,
    CreateInventoryCountCommand,
    CreateStockCorrectionCommand,
)
from application.use_cases.inventory_use_cases import (
    CancelStockCorrectionUseCase,
    CompareInventoryToReferenceUseCase,
    ConfirmStockCorrectionUseCase,
    CreateInventoryCountUseCase,
    CreateStockCorrectionUseCase,
    ListInventoryCountsUseCase,
)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/counts", response_model=list[InventoryCountResponse])
def list_inventory_counts(
    use_case: ListInventoryCountsUseCase = Depends(get_list_inventory_counts_use_case),
) -> list[InventoryCountResponse]:
    counts = use_case.execute()
    return [InventoryCountResponse.from_record(item) for item in counts]


@router.post("/counts", response_model=InventoryCountResponse, status_code=201)
def create_inventory_count(
    payload: CreateInventoryCountRequest,
    use_case: CreateInventoryCountUseCase = Depends(get_create_inventory_count_use_case),
    _current_user=Depends(require_lager_plus),
) -> InventoryCountResponse:
    try:
        count = use_case.execute(
            CreateInventoryCountCommand(
                material_article_number=payload.material_article_number,
                counted_stock_mm=payload.counted_stock_mm,
                counted_by_user_id=payload.counted_by_user_id,
                comment=payload.comment,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return InventoryCountResponse.from_record(count)


@router.post("/compare", response_model=InventoryDifferenceResponse)
def compare_inventory_to_reference(
    payload: CompareInventoryRequest,
    use_case: CompareInventoryToReferenceUseCase = Depends(get_compare_inventory_to_reference_use_case),
) -> InventoryDifferenceResponse:
    try:
        difference = use_case.execute(
            CompareInventoryToReferenceCommand(
                material_article_number=payload.material_article_number,
                counted_stock_mm=payload.counted_stock_mm,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return InventoryDifferenceResponse.from_domain(difference)


@router.post("/corrections", response_model=StockCorrectionResponse, status_code=201)
def create_stock_correction(
    payload: CreateStockCorrectionRequest,
    use_case: CreateStockCorrectionUseCase = Depends(get_create_stock_correction_use_case),
) -> StockCorrectionResponse:
    try:
        correction = use_case.execute(
            CreateStockCorrectionCommand(
                inventory_count_id=payload.inventory_count_id,
                requested_by_user_id=payload.requested_by_user_id,
                comment=payload.comment,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return StockCorrectionResponse.from_record(correction)


@router.post("/corrections/{correction_id}/confirm", response_model=StockCorrectionResponse)
def confirm_stock_correction(
    correction_id: int,
    payload: ChangeStockCorrectionStatusRequest,
    use_case: ConfirmStockCorrectionUseCase = Depends(get_confirm_stock_correction_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> StockCorrectionResponse:
    try:
        correction = use_case.execute(
            ChangeStockCorrectionStatusCommand(
                correction_id=correction_id,
                acting_user_id=payload.acting_user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return StockCorrectionResponse.from_record(correction)


@router.post("/corrections/{correction_id}/cancel", response_model=StockCorrectionResponse)
def cancel_stock_correction(
    correction_id: int,
    payload: ChangeStockCorrectionStatusRequest,
    use_case: CancelStockCorrectionUseCase = Depends(get_cancel_stock_correction_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> StockCorrectionResponse:
    try:
        correction = use_case.execute(
            ChangeStockCorrectionStatusCommand(
                correction_id=correction_id,
                acting_user_id=payload.acting_user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return StockCorrectionResponse.from_record(correction)
