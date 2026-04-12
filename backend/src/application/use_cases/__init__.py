"""Application use case package."""

from application.use_cases.admin_configuration_use_cases import (
    CreateCuttingMachineUseCase,
    CreateEndpointUseCase,
    CreateErpProfileUseCase,
    CreateFieldMappingUseCase,
    CreateUserUseCase,
    GetErpProfileUseCase,
    ListCuttingMachinesUseCase,
    ListEndpointsUseCase,
    ListErpProfilesUseCase,
    ListFieldMappingsUseCase,
    ListUsersUseCase,
    UpdateErpProfileUseCase,
)
from application.use_cases.auth_use_cases import GetCurrentUserUseCase, LoginResult, LoginUseCase
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.inventory_use_cases import (
    CancelStockCorrectionUseCase,
    CompareInventoryToReferenceUseCase,
    ConfirmStockCorrectionUseCase,
    CreateInventoryCountUseCase,
    CreateStockCorrectionUseCase,
    ListInventoryCountsUseCase,
)
from application.use_cases.link_erp_order_use_case import LinkErpOrderUseCase
from application.use_cases.erp_read_use_cases import (
    GetErpMaterialStockUseCase,
    GetErpMaterialUseCase,
    ValidateErpOrderReferenceUseCase,
)
from application.use_cases.material_lookup_use_cases import (
    GetMaterialByArticleNumberUseCase,
    SearchMaterialsUseCase,
)
from application.use_cases.orders_read_use_cases import (
    GetDashboardOverviewUseCase,
    GetOrderDetailUseCase,
    ListOrdersDetailedUseCase,
)
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase

__all__ = [
    "CreateCuttingMachineUseCase",
    "CreateEndpointUseCase",
    "CreateErpProfileUseCase",
    "CreateFieldMappingUseCase",
    "CreateInventoryCountUseCase",
    "CreateOrderUseCase",
    "CreateStockCorrectionUseCase",
    "CreateUserUseCase",
    "GetCurrentUserUseCase",
    "GetErpMaterialStockUseCase",
    "GetErpMaterialUseCase",
    "GetDashboardOverviewUseCase",
    "GetErpProfileUseCase",
    "GetOrderDetailUseCase",
    "LinkErpOrderUseCase",
    "ListCuttingMachinesUseCase",
    "ListEndpointsUseCase",
    "ListErpProfilesUseCase",
    "ListFieldMappingsUseCase",
    "ListInventoryCountsUseCase",
    "ListUsersUseCase",
    "LoginResult",
    "LoginUseCase",
    "RecalculateOrdersUseCase",
    "ReprioritizeOrdersUseCase",
    "ReserveOrderUseCase",
    "CompareInventoryToReferenceUseCase",
    "ConfirmStockCorrectionUseCase",
    "CancelStockCorrectionUseCase",
    "GetMaterialByArticleNumberUseCase",
    "SearchMaterialsUseCase",
    "ValidateErpOrderReferenceUseCase",
    "ListOrdersDetailedUseCase",
    "UpdateErpProfileUseCase",
]
