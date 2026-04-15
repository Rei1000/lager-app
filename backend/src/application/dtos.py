"""Application DTOs for use case commands."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderCommand:
    order_id: str
    material_article_number: str
    quantity: int
    part_length_mm: int
    kerf_mm: int
    include_rest_stock: bool
    acting_user_id: int


@dataclass(frozen=True)
class RecalculateOrdersCommand:
    material_article_number: str


@dataclass(frozen=True)
class ReserveOrderCommand:
    order_id: str
    acting_user_id: int


@dataclass(frozen=True)
class ReprioritizeOrdersCommand:
    material_article_number: str
    ordered_ids: list[str]
    acting_user_id: int


@dataclass(frozen=True)
class LinkErpOrderCommand:
    order_id: str
    erp_order_number: str
    acting_user_id: int


@dataclass(frozen=True)
class CreateErpProfileCommand:
    name: str
    erp_type: str | None
    connection_type: str | None
    base_url: str | None
    tenant_code: str | None


@dataclass(frozen=True)
class UpdateErpProfileCommand:
    profile_id: int
    name: str
    erp_type: str | None
    connection_type: str | None
    base_url: str | None
    tenant_code: str | None


@dataclass(frozen=True)
class CreateEndpointCommand:
    erp_profile_id: int
    functional_key: str
    http_method: str
    path_template: str


@dataclass(frozen=True)
class CreateFieldMappingCommand:
    endpoint_id: int
    app_field: str
    erp_field: str
    direction: str


@dataclass(frozen=True)
class CreateCuttingMachineCommand:
    machine_code: str | None
    name: str
    kerf_mm: float | None
    is_active: bool


@dataclass(frozen=True)
class CreateUserCommand:
    username: str
    password: str
    role_id: int
    display_name: str | None
    email: str | None
    is_active: bool
    erp_user_reference: str | None


@dataclass(frozen=True)
class CreateInventoryCountCommand:
    material_article_number: str
    counted_stock_mm: int
    counted_by_user_id: int
    comment: str | None


@dataclass(frozen=True)
class CompareInventoryToReferenceCommand:
    material_article_number: str
    counted_stock_mm: int


@dataclass(frozen=True)
class CreateStockCorrectionCommand:
    inventory_count_id: int
    requested_by_user_id: int
    comment: str | None


@dataclass(frozen=True)
class ChangeStockCorrectionStatusCommand:
    correction_id: int
    acting_user_id: int


@dataclass(frozen=True)
class SearchMaterialsCommand:
    query: str


@dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str
    login_type: str
    selected_connection: str


@dataclass(frozen=True)
class CreateErpTransferRequestCommand:
    order_id: str
    material_article_number: str
    requested_by_user_id: int
    payload: dict[str, object] | None


@dataclass(frozen=True)
class ChangeErpTransferStatusCommand:
    transfer_id: int
    acting_user_id: int
    failure_reason: str | None = None


@dataclass(frozen=True)
class UploadPhotoCommand:
    entity_type: str
    entity_id: str
    original_filename: str
    content: bytes
    uploaded_by_user_id: int
    content_type: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class ListPhotosForEntityCommand:
    entity_type: str
    entity_id: str


@dataclass(frozen=True)
class CreateCommentCommand:
    entity_type: str
    entity_id: str
    text: str
    created_by_user_id: int


@dataclass(frozen=True)
class ListCommentsForEntityCommand:
    entity_type: str
    entity_id: str


@dataclass(frozen=True)
class PreviewOrderPlanCommand:
    article_number: str
    quantity: int
    part_length_mm: int
    kerf_mm: float
    rest_piece_consideration_requested: bool = False


@dataclass(frozen=True)
class OrderPlanOpenOrderLine:
    order_reference: str
    required_m: float
    status: str


@dataclass(frozen=True)
class OrderPlanPreviewResult:
    article_number: str
    material_name: str
    stock_m: float
    in_pipeline_m: float
    available_m: float
    open_orders: tuple[OrderPlanOpenOrderLine, ...]
    net_required_mm: int
    kerf_total_mm: int
    gross_required_mm: int
    net_required_m: float
    kerf_total_m: float
    gross_required_m: float
    feasible: bool
