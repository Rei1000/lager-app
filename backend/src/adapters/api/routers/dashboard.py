"""Dashboard API router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from adapters.api.dependencies.auth import require_authenticated_user
from adapters.api.dependencies.use_cases import get_dashboard_overview_use_case
from adapters.api.schemas.orders import DashboardOverviewResponse, OrderResponse
from application.use_cases.orders_read_use_cases import GetDashboardOverviewUseCase

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    use_case: GetDashboardOverviewUseCase = Depends(get_dashboard_overview_use_case),
) -> DashboardOverviewResponse:
    overview = use_case.execute()
    return DashboardOverviewResponse(
        open_orders_count=overview.open_orders_count,
        critical_orders_count=overview.critical_orders_count,
        open_orders=[OrderResponse.from_domain(order) for order in overview.open_orders],
    )
