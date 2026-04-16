"""API dependency wiring (PostgreSQL repositories, Sage simulator for ERP reads)."""

from __future__ import annotations

from pathlib import Path

from adapters.auth.password_hasher import Pbkdf2PasswordHasher
from adapters.auth.sage_simulator_authentication import SageSimulatorAuthenticationAdapter
from adapters.auth.token_service import HmacTokenService
from adapters.erp.app_aware_material_plan_availability_adapter import AppAwareMaterialPlanAvailabilityAdapter
from adapters.erp.base_client import DynamicErpBaseClient
from adapters.erp.gateway import DynamicErpGatewayAdapter
from adapters.erp.http_client import UrllibHttpClient
from adapters.erp.material_plan_availability_sage_simulator_adapter import (
    SageSimulatorMaterialPlanAvailabilityAdapter,
)
from adapters.erp.simulator_erp_order_link_adapter import SimulatorErpOrderLinkAdapter
from adapters.persistence.audit_log_repository import SqlAlchemyAuditLogRepository
from adapters.persistence.admin_configuration_repository import (
    SqlAlchemyAdminConfigurationRepository,
)
from adapters.persistence.auth_identity_repository import SqlAlchemyAuthIdentityRepository
from adapters.persistence.comment_repository import SqlAlchemyCommentRepository
from adapters.persistence.erp_configuration_repository import SqlAlchemyErpConfigurationRepository
from adapters.persistence.erp_transfer_repository import SqlAlchemyErpTransferRepository
from adapters.persistence.database_stock_snapshot_adapter import DatabaseStockSnapshotAdapter
from adapters.persistence.inventory_repository import SqlAlchemyInventoryRepository
from adapters.persistence.material_lookup_repository import SqlAlchemyMaterialLookupRepository
from adapters.persistence.order_repository import SqlAlchemyOrderRepository
from adapters.persistence.photo_repository import SqlAlchemyPhotoRepository
from adapters.storage.local_file_storage import LocalFileStorageAdapter
from application.use_cases.auth_use_cases import GetCurrentUserUseCase, LoginUseCase
from application.use_cases.audit_log_use_cases import ListAuditLogsUseCase
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
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.comment_use_cases import (
    CreateCommentUseCase,
    ListCommentsForEntityUseCase,
)
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
from application.use_cases.erp_transfer_use_cases import (
    ApproveErpTransferUseCase,
    CreateErpTransferRequestUseCase,
    ListErpTransferRequestsUseCase,
    MarkErpTransferFailedUseCase,
    MarkErpTransferReadyUseCase,
    MarkErpTransferSentUseCase,
)
from application.use_cases.material_lookup_use_cases import (
    GetMaterialByArticleNumberUseCase,
    SearchMaterialsUseCase,
)
from application.use_cases.photo_use_cases import (
    GetPhotoContentUseCase,
    ListPhotosForEntityUseCase,
    UploadPhotoUseCase,
)
from application.use_cases.preview_order_plan_use_case import PreviewOrderPlanUseCase
from application.use_cases.orders_read_use_cases import (
    GetDashboardOverviewUseCase,
    GetOrderDetailUseCase,
    ListOrdersDetailedUseCase,
)
from application.use_cases.recalculate_orders_use_case import RecalculateOrdersUseCase
from application.use_cases.reprioritize_orders_use_case import ReprioritizeOrdersUseCase
from application.use_cases.reserve_order_use_case import ReserveOrderUseCase
from application.use_cases.update_order_use_case import UpdateOrderUseCase
from config.settings import settings


_order_repository = SqlAlchemyOrderRepository()
_stock_snapshot_port = DatabaseStockSnapshotAdapter(order_repository=_order_repository)
_sage_simulator_availability_inner = SageSimulatorMaterialPlanAvailabilityAdapter()
_material_plan_availability_adapter = AppAwareMaterialPlanAvailabilityAdapter(
    inner=_sage_simulator_availability_inner,
    order_repository=_order_repository,
)
_erp_order_link_port = SimulatorErpOrderLinkAdapter()
_password_hasher = Pbkdf2PasswordHasher()
_admin_configuration_repository = SqlAlchemyAdminConfigurationRepository(password_hasher=_password_hasher)
_inventory_repository = SqlAlchemyInventoryRepository()
_material_lookup_repository = SqlAlchemyMaterialLookupRepository()
_photo_repository = SqlAlchemyPhotoRepository()
_comment_repository = SqlAlchemyCommentRepository()
_auth_identity_repository = SqlAlchemyAuthIdentityRepository()
_erp_configuration_repository = SqlAlchemyErpConfigurationRepository()
_erp_transfer_repository = SqlAlchemyErpTransferRepository()
_audit_log_repository = SqlAlchemyAuditLogRepository()
_erp_http_client = UrllibHttpClient()
_erp_base_client = DynamicErpBaseClient(
    profile_name=settings.erp_profile_name,
    configuration_port=_erp_configuration_repository,
    http_client=_erp_http_client,
)
_erp_gateway_adapter = DynamicErpGatewayAdapter(
    profile_name=settings.erp_profile_name,
    configuration_port=_erp_configuration_repository,
    base_client=_erp_base_client,
)
_photo_storage_adapter = LocalFileStorageAdapter(
    base_directory=Path(settings.photo_upload_directory),
)
_auth_token_service = HmacTokenService(
    secret_key=settings.auth_secret_key,
    ttl_seconds=settings.auth_access_token_ttl_seconds,
)
_erp_auth_ports = {
    "sage-simulator": SageSimulatorAuthenticationAdapter(
        auth_identity_port=_auth_identity_repository,
        password_hasher=_password_hasher,
    ),
}


def get_create_order_use_case() -> CreateOrderUseCase:
    return CreateOrderUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
        audit_log_port=_audit_log_repository,
    )


def get_recalculate_orders_use_case() -> RecalculateOrdersUseCase:
    return RecalculateOrdersUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
    )


def get_update_order_use_case() -> UpdateOrderUseCase:
    return UpdateOrderUseCase(
        order_repository=_order_repository,
        recalculate_orders_use_case=RecalculateOrdersUseCase(
            order_repository=_order_repository,
            stock_snapshot_port=_stock_snapshot_port,
        ),
        audit_log_port=_audit_log_repository,
    )


def get_reserve_order_use_case() -> ReserveOrderUseCase:
    return ReserveOrderUseCase(
        order_repository=_order_repository,
        audit_log_port=_audit_log_repository,
    )


def get_reprioritize_orders_use_case() -> ReprioritizeOrdersUseCase:
    return ReprioritizeOrdersUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
        audit_log_port=_audit_log_repository,
    )


def get_link_erp_order_use_case() -> LinkErpOrderUseCase:
    return LinkErpOrderUseCase(
        order_repository=_order_repository,
        erp_order_link_port=_erp_order_link_port,
        audit_log_port=_audit_log_repository,
    )


def get_list_erp_profiles_use_case() -> ListErpProfilesUseCase:
    return ListErpProfilesUseCase(admin_configuration_port=_admin_configuration_repository)


def get_get_erp_profile_use_case() -> GetErpProfileUseCase:
    return GetErpProfileUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_erp_profile_use_case() -> CreateErpProfileUseCase:
    return CreateErpProfileUseCase(admin_configuration_port=_admin_configuration_repository)


def get_update_erp_profile_use_case() -> UpdateErpProfileUseCase:
    return UpdateErpProfileUseCase(admin_configuration_port=_admin_configuration_repository)


def get_list_endpoints_use_case() -> ListEndpointsUseCase:
    return ListEndpointsUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_endpoint_use_case() -> CreateEndpointUseCase:
    return CreateEndpointUseCase(admin_configuration_port=_admin_configuration_repository)


def get_list_field_mappings_use_case() -> ListFieldMappingsUseCase:
    return ListFieldMappingsUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_field_mapping_use_case() -> CreateFieldMappingUseCase:
    return CreateFieldMappingUseCase(admin_configuration_port=_admin_configuration_repository)


def get_list_cutting_machines_use_case() -> ListCuttingMachinesUseCase:
    return ListCuttingMachinesUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_cutting_machine_use_case() -> CreateCuttingMachineUseCase:
    return CreateCuttingMachineUseCase(admin_configuration_port=_admin_configuration_repository)


def get_list_users_use_case() -> ListUsersUseCase:
    return ListUsersUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase(admin_configuration_port=_admin_configuration_repository)


def get_create_inventory_count_use_case() -> CreateInventoryCountUseCase:
    return CreateInventoryCountUseCase(
        inventory_repository=_inventory_repository,
        stock_snapshot_port=_stock_snapshot_port,
        audit_log_port=_audit_log_repository,
    )


def get_list_inventory_counts_use_case() -> ListInventoryCountsUseCase:
    return ListInventoryCountsUseCase(inventory_repository=_inventory_repository)


def get_compare_inventory_to_reference_use_case() -> CompareInventoryToReferenceUseCase:
    return CompareInventoryToReferenceUseCase(stock_snapshot_port=_stock_snapshot_port)


def get_create_stock_correction_use_case() -> CreateStockCorrectionUseCase:
    return CreateStockCorrectionUseCase(
        inventory_repository=_inventory_repository,
        audit_log_port=_audit_log_repository,
    )


def get_confirm_stock_correction_use_case() -> ConfirmStockCorrectionUseCase:
    return ConfirmStockCorrectionUseCase(
        inventory_repository=_inventory_repository,
        audit_log_port=_audit_log_repository,
    )


def get_cancel_stock_correction_use_case() -> CancelStockCorrectionUseCase:
    return CancelStockCorrectionUseCase(
        inventory_repository=_inventory_repository,
        audit_log_port=_audit_log_repository,
    )


def get_search_materials_use_case() -> SearchMaterialsUseCase:
    return SearchMaterialsUseCase(material_lookup_port=_material_lookup_repository)


def get_material_by_article_number_use_case() -> GetMaterialByArticleNumberUseCase:
    return GetMaterialByArticleNumberUseCase(material_lookup_port=_material_lookup_repository)


def get_preview_order_plan_use_case() -> PreviewOrderPlanUseCase:
    return PreviewOrderPlanUseCase(
        material_lookup_port=_material_lookup_repository,
        material_plan_availability_port=_material_plan_availability_adapter,
    )


def get_upload_photo_use_case() -> UploadPhotoUseCase:
    return UploadPhotoUseCase(
        photo_repository=_photo_repository,
        file_storage=_photo_storage_adapter,
        audit_log_port=_audit_log_repository,
    )


def get_list_photos_for_entity_use_case() -> ListPhotosForEntityUseCase:
    return ListPhotosForEntityUseCase(photo_repository=_photo_repository)


def get_get_photo_content_use_case() -> GetPhotoContentUseCase:
    return GetPhotoContentUseCase(
        photo_repository=_photo_repository,
        file_storage=_photo_storage_adapter,
    )


def get_create_comment_use_case() -> CreateCommentUseCase:
    return CreateCommentUseCase(
        comment_repository=_comment_repository,
        audit_log_port=_audit_log_repository,
    )


def get_list_comments_for_entity_use_case() -> ListCommentsForEntityUseCase:
    return ListCommentsForEntityUseCase(comment_repository=_comment_repository)


def get_erp_material_use_case() -> GetErpMaterialUseCase:
    return GetErpMaterialUseCase(erp_material_port=_erp_gateway_adapter)


def get_erp_material_stock_use_case() -> GetErpMaterialStockUseCase:
    return GetErpMaterialStockUseCase(erp_material_port=_erp_gateway_adapter)


def get_validate_erp_order_reference_use_case() -> ValidateErpOrderReferenceUseCase:
    return ValidateErpOrderReferenceUseCase(erp_order_port=_erp_gateway_adapter)


def get_create_erp_transfer_request_use_case() -> CreateErpTransferRequestUseCase:
    return CreateErpTransferRequestUseCase(
        transfer_repository=_erp_transfer_repository,
        audit_log_port=_audit_log_repository,
    )


def get_list_erp_transfer_requests_use_case() -> ListErpTransferRequestsUseCase:
    return ListErpTransferRequestsUseCase(transfer_repository=_erp_transfer_repository)


def get_mark_erp_transfer_ready_use_case() -> MarkErpTransferReadyUseCase:
    return MarkErpTransferReadyUseCase(
        transfer_repository=_erp_transfer_repository,
        audit_log_port=_audit_log_repository,
    )


def get_approve_erp_transfer_use_case() -> ApproveErpTransferUseCase:
    return ApproveErpTransferUseCase(
        transfer_repository=_erp_transfer_repository,
        audit_log_port=_audit_log_repository,
    )


def get_mark_erp_transfer_sent_use_case() -> MarkErpTransferSentUseCase:
    return MarkErpTransferSentUseCase(
        transfer_repository=_erp_transfer_repository,
        erp_write_port=_erp_gateway_adapter,
        audit_log_port=_audit_log_repository,
    )


def get_mark_erp_transfer_failed_use_case() -> MarkErpTransferFailedUseCase:
    return MarkErpTransferFailedUseCase(
        transfer_repository=_erp_transfer_repository,
        audit_log_port=_audit_log_repository,
    )


def get_list_audit_logs_use_case() -> ListAuditLogsUseCase:
    return ListAuditLogsUseCase(audit_log_port=_audit_log_repository)


def get_list_orders_detailed_use_case() -> ListOrdersDetailedUseCase:
    return ListOrdersDetailedUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
    )


def get_get_order_detail_use_case() -> GetOrderDetailUseCase:
    return GetOrderDetailUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
    )


def get_dashboard_overview_use_case() -> GetDashboardOverviewUseCase:
    return GetDashboardOverviewUseCase(
        order_repository=_order_repository,
        stock_snapshot_port=_stock_snapshot_port,
    )


def get_login_use_case() -> LoginUseCase:
    return LoginUseCase(
        auth_identity_port=_auth_identity_repository,
        password_hasher=_password_hasher,
        auth_token_port=_auth_token_service,
        erp_auth_ports=_erp_auth_ports,
        access_token_ttl_seconds=settings.auth_access_token_ttl_seconds,
    )


def get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(auth_identity_port=_auth_identity_repository)


def get_auth_token_service() -> HmacTokenService:
    return _auth_token_service
