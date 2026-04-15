"""Order HTTP router as pure API adapter."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import (
    RequestUser,
    require_authenticated_user,
    require_lager_plus,
    require_leitung_or_admin,
)
from adapters.api.dependencies.use_cases import (
    get_get_order_detail_use_case,
    get_list_orders_detailed_use_case,
    get_create_order_use_case,
    get_link_erp_order_use_case,
    get_recalculate_orders_use_case,
    get_reprioritize_orders_use_case,
    get_reserve_order_use_case,
)
from adapters.api.errors import map_value_error
from adapters.api.schemas.orders import (
    CreateOrderRequest,
    LinkErpOrderRequest,
    OrderResponse,
    RecalculateOrdersRequest,
    ReprioritizeOrdersRequest,
)
from application.dtos import (
    CreateOrderCommand,
    LinkErpOrderCommand,
    RecalculateOrdersCommand,
    ReprioritizeOrdersCommand,
    ReserveOrderCommand,
)
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.link_erp_order_use_case import LinkErpOrderUseCase
from application.use_cases.orders_read_use_cases import (
    GetOrderDetailUseCase,
    ListOrdersDetailedUseCase,
)
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("", response_model=list[OrderResponse])
def list_orders(
    status: str | None = None,
    material_article_number: str | None = None,
    use_case: ListOrdersDetailedUseCase = Depends(get_list_orders_detailed_use_case),
) -> list[OrderResponse]:
    orders = use_case.execute(status=status, material_article_number=material_article_number)
    return [OrderResponse.from_domain(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: str,
    use_case: GetOrderDetailUseCase = Depends(get_get_order_detail_use_case),
) -> OrderResponse:
    try:
        order = use_case.execute(order_id)
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return OrderResponse.from_domain(order)


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    payload: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
    current_user: RequestUser = Depends(require_lager_plus),
) -> OrderResponse:
    try:
        order = use_case.execute(
            CreateOrderCommand(
                order_id=payload.order_id,
                material_article_number=payload.material_article_number,
                quantity=payload.quantity,
                part_length_mm=payload.part_length_mm,
                kerf_mm=payload.kerf_mm,
                include_rest_stock=payload.include_rest_stock,
                acting_user_id=current_user.user_id,
                customer_name=payload.customer_name,
                due_date=payload.due_date,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return OrderResponse.from_domain(order)


@router.post("/{order_id}/reserve", response_model=OrderResponse)
def reserve_order(
    order_id: str,
    use_case: ReserveOrderUseCase = Depends(get_reserve_order_use_case),
    current_user: RequestUser = Depends(require_lager_plus),
) -> OrderResponse:
    try:
        order = use_case.execute(
            ReserveOrderCommand(order_id=order_id, acting_user_id=current_user.user_id)
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return OrderResponse.from_domain(order)


@router.post("/reprioritize", response_model=list[OrderResponse])
def reprioritize_orders(
    payload: ReprioritizeOrdersRequest,
    use_case: ReprioritizeOrdersUseCase = Depends(get_reprioritize_orders_use_case),
    current_user: RequestUser = Depends(require_leitung_or_admin),
) -> list[OrderResponse]:
    try:
        orders = use_case.execute(
            ReprioritizeOrdersCommand(
                material_article_number=payload.material_article_number,
                ordered_ids=payload.ordered_ids,
                acting_user_id=current_user.user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return [OrderResponse.from_domain(order) for order in orders]


@router.post("/{order_id}/link-erp", response_model=OrderResponse)
def link_erp_order(
    order_id: str,
    payload: LinkErpOrderRequest,
    use_case: LinkErpOrderUseCase = Depends(get_link_erp_order_use_case),
    current_user: RequestUser = Depends(require_leitung_or_admin),
) -> OrderResponse:
    try:
        order = use_case.execute(
            LinkErpOrderCommand(
                order_id=order_id,
                erp_order_number=payload.erp_order_number,
                acting_user_id=current_user.user_id,
            )
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return OrderResponse.from_domain(order)


@router.post("/recalculate", response_model=list[OrderResponse])
def recalculate_orders(
    payload: RecalculateOrdersRequest,
    use_case: RecalculateOrdersUseCase = Depends(get_recalculate_orders_use_case),
) -> list[OrderResponse]:
    try:
        orders = use_case.execute(
            RecalculateOrdersCommand(material_article_number=payload.material_article_number)
        )
    except ValueError as exc:
        raise map_value_error(exc) from exc
    return [OrderResponse.from_domain(order) for order in orders]
