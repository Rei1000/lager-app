"""Infrastructure ORM model registry."""

from adapters.persistence.models.access import RoleModel, UserModel
from adapters.persistence.models.audit import AuditLogModel
from adapters.persistence.models.comment import CommentModel
from adapters.persistence.models.erp import (
    ErpAuthConfigModel,
    ErpFieldMappingModel,
    ErpFunctionEndpointModel,
    ErpProfileModel,
)
from adapters.persistence.models.erp_transfer import ErpTransferRequestModel
from adapters.persistence.models.material import (
    CuttingMachineModel,
    MaterialTypeModel,
    RestStockAccountModel,
)
from adapters.persistence.models.inventory import InventoryCountModel, StockCorrectionModel
from adapters.persistence.models.orders import AppOrderModel, OrderStatusHistoryModel
from adapters.persistence.models.photo import PhotoModel

__all__ = [
    "AppOrderModel",
    "AuditLogModel",
    "CuttingMachineModel",
    "CommentModel",
    "ErpAuthConfigModel",
    "ErpFieldMappingModel",
    "ErpFunctionEndpointModel",
    "ErpProfileModel",
    "ErpTransferRequestModel",
    "MaterialTypeModel",
    "InventoryCountModel",
    "OrderStatusHistoryModel",
    "PhotoModel",
    "RestStockAccountModel",
    "RoleModel",
    "StockCorrectionModel",
    "UserModel",
]
