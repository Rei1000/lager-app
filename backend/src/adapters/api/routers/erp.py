"""ERP read API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import (
    require_admin_user,
    require_authenticated_user,
    require_leitung_or_admin,
)
from adapters.api.dependencies.use_cases import (
    get_approve_erp_transfer_use_case,
    get_create_erp_transfer_request_use_case,
    get_erp_material_stock_use_case,
    get_erp_material_use_case,
    get_list_erp_transfer_requests_use_case,
    get_mark_erp_transfer_failed_use_case,
    get_mark_erp_transfer_ready_use_case,
    get_mark_erp_transfer_sent_use_case,
    get_validate_erp_order_reference_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.erp_read import ErpOrderValidationResponse, ErpPayloadResponse
from adapters.api.schemas.erp_transfer import (
    ChangeErpTransferStatusRequest,
    CreateErpTransferRequest,
    ErpTransferResponse,
)
from application.dtos import ChangeErpTransferStatusCommand, CreateErpTransferRequestCommand
from application.use_cases.erp_read_use_cases import (
    GetErpMaterialStockUseCase,
    GetErpMaterialUseCase,
    ValidateErpOrderReferenceUseCase,
)
from application.use_cases.erp_transfer_use_cases import (
    ApproveErpTransferUseCase,
    CreateErpTransferRequestUseCase,
    ListErpTransferRequestsUseCase,
    MarkErpTransferFailedUseCase,
    MarkErpTransferReadyUseCase,
    MarkErpTransferSentUseCase,
)

router = APIRouter(
    prefix="/erp",
    tags=["erp-read"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/materials/{reference}", response_model=ErpPayloadResponse)
def get_erp_material(
    reference: str,
    use_case: GetErpMaterialUseCase = Depends(get_erp_material_use_case),
) -> ErpPayloadResponse:
    try:
        payload = use_case.execute(reference)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpPayloadResponse(payload=payload)


@router.get("/materials/{reference}/stock", response_model=ErpPayloadResponse)
def get_erp_material_stock(
    reference: str,
    use_case: GetErpMaterialStockUseCase = Depends(get_erp_material_stock_use_case),
) -> ErpPayloadResponse:
    try:
        payload = use_case.execute(reference)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpPayloadResponse(payload=payload)


@router.get("/orders/{reference}/validate", response_model=ErpOrderValidationResponse)
def validate_erp_order_reference(
    reference: str,
    use_case: ValidateErpOrderReferenceUseCase = Depends(get_validate_erp_order_reference_use_case),
) -> ErpOrderValidationResponse:
    try:
        is_valid = use_case.execute(reference)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpOrderValidationResponse(reference=reference, is_valid=is_valid)


@router.get("/transfers", response_model=list[ErpTransferResponse])
def list_erp_transfer_requests(
    use_case: ListErpTransferRequestsUseCase = Depends(get_list_erp_transfer_requests_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> list[ErpTransferResponse]:
    transfers = use_case.execute()
    return [ErpTransferResponse.from_record(item) for item in transfers]


@router.post("/transfers", response_model=ErpTransferResponse, status_code=201)
def create_erp_transfer_request(
    payload: CreateErpTransferRequest,
    use_case: CreateErpTransferRequestUseCase = Depends(get_create_erp_transfer_request_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> ErpTransferResponse:
    try:
        transfer = use_case.execute(
            CreateErpTransferRequestCommand(
                order_id=payload.order_id,
                material_article_number=payload.material_article_number,
                requested_by_user_id=payload.requested_by_user_id,
                payload=payload.payload,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpTransferResponse.from_record(transfer)


@router.post("/transfers/{transfer_id}/ready", response_model=ErpTransferResponse)
def mark_erp_transfer_ready(
    transfer_id: int,
    payload: ChangeErpTransferStatusRequest,
    use_case: MarkErpTransferReadyUseCase = Depends(get_mark_erp_transfer_ready_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> ErpTransferResponse:
    try:
        transfer = use_case.execute(
            ChangeErpTransferStatusCommand(
                transfer_id=transfer_id,
                acting_user_id=payload.acting_user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpTransferResponse.from_record(transfer)


@router.post("/transfers/{transfer_id}/approve", response_model=ErpTransferResponse)
def approve_erp_transfer(
    transfer_id: int,
    payload: ChangeErpTransferStatusRequest,
    use_case: ApproveErpTransferUseCase = Depends(get_approve_erp_transfer_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> ErpTransferResponse:
    try:
        transfer = use_case.execute(
            ChangeErpTransferStatusCommand(
                transfer_id=transfer_id,
                acting_user_id=payload.acting_user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpTransferResponse.from_record(transfer)


@router.post("/transfers/{transfer_id}/send", response_model=ErpTransferResponse)
def mark_erp_transfer_sent(
    transfer_id: int,
    payload: ChangeErpTransferStatusRequest,
    use_case: MarkErpTransferSentUseCase = Depends(get_mark_erp_transfer_sent_use_case),
    _current_user=Depends(require_admin_user),
) -> ErpTransferResponse:
    try:
        transfer = use_case.execute(
            ChangeErpTransferStatusCommand(
                transfer_id=transfer_id,
                acting_user_id=payload.acting_user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpTransferResponse.from_record(transfer)


@router.post("/transfers/{transfer_id}/fail", response_model=ErpTransferResponse)
def mark_erp_transfer_failed(
    transfer_id: int,
    payload: ChangeErpTransferStatusRequest,
    use_case: MarkErpTransferFailedUseCase = Depends(get_mark_erp_transfer_failed_use_case),
    _current_user=Depends(require_leitung_or_admin),
) -> ErpTransferResponse:
    try:
        transfer = use_case.execute(
            ChangeErpTransferStatusCommand(
                transfer_id=transfer_id,
                acting_user_id=payload.acting_user_id,
                failure_reason=payload.failure_reason,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return ErpTransferResponse.from_record(transfer)
