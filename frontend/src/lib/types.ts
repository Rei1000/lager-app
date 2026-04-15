export type OrderDto = {
  order_id: string | null;
  material_article_number: string;
  quantity: number;
  part_length_mm: number;
  kerf_mm: number;
  include_rest_stock: boolean;
  status: string;
  priority_order: number | null;
  traffic_light: string | null;
  erp_order_number: string | null;
  total_demand_mm: number;
};

export type ErpProfileDto = {
  id: number;
  name: string;
  erp_type: string | null;
  connection_type: string | null;
  base_url: string | null;
  tenant_code: string | null;
};

export type ErpEndpointDto = {
  id: number;
  erp_profile_id: number;
  functional_key: string;
  http_method: string;
  path_template: string;
};

export type ErpMappingDto = {
  id: number;
  endpoint_id: number;
  app_field: string;
  erp_field: string;
  direction: "app_to_erp" | "erp_to_app";
};

export type CuttingMachineDto = {
  id: number;
  machine_code: string | null;
  name: string;
  kerf_mm: number | null;
  is_active: boolean;
};

export type UserDto = {
  id: number;
  username: string;
  role_id: number;
  display_name: string | null;
  email: string | null;
  is_active: boolean;
  erp_user_reference: string | null;
};

export type InventoryCountDto = {
  id: number;
  material_article_number: string;
  counted_stock_mm: number;
  reference_stock_mm: number;
  difference_mm: number;
  difference_type: string;
  status: string;
  counted_by_user_id: number;
  comment: string | null;
  created_at: string;
};

export type InventoryDifferenceDto = {
  material_article_number: string;
  counted_stock_mm: number;
  reference_stock_mm: number;
  difference_mm: number;
  difference_type: string;
};

export type StockCorrectionDto = {
  id: number;
  inventory_count_id: number;
  material_article_number: string;
  correction_mm: number;
  status: string;
  requested_by_user_id: number;
  confirmed_by_user_id: number | null;
  canceled_by_user_id: number | null;
  comment: string | null;
  created_at: string;
  confirmed_at: string | null;
  canceled_at: string | null;
};

export type MaterialLookupDto = {
  article_number: string;
  name: string;
  profile: string | null;
  erp_stock_m: number | null;
  rest_stock_m: number | null;
};

export type SimulatorMaterialSearchDto = {
  material_no: string;
  description: string;
  profile: string | null;
  shape: string | null;
  size_mm: string | null;
  material_group_code: string | null;
  material_group: string | null;
  material_code: string | null;
  material: string | null;
  dimension_code: string | null;
  dimension_mm: number | null;
  unit: string | null;
};

export type SimulatorMaterialStockDto = {
  material_no: string;
  description?: string;
  stock_m: number;
  rest_stock_m: number;
  stock_as_of: string;
};

export type PhotoDto = {
  id: number;
  entity_type: string;
  entity_id: string;
  uploaded_by_user_id: number;
  uploaded_at: string;
  comment: string | null;
  original_filename: string;
  content_type: string | null;
  file_url: string;
};

export type CommentDto = {
  id: number;
  entity_type: string;
  entity_id: string;
  text: string;
  created_by_user_id: number;
  created_at: string;
};

export type LoginResponseDto = {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  user_id: number;
  username: string;
  role_code: string;
  login_type: "erp" | "admin";
  selected_connection: "sage-simulator" | "sage-connect" | "middleware";
};

export type CurrentUserDto = {
  user_id: number;
  username: string;
  role_code: string;
  role_name: string;
  login_type: "erp" | "admin";
  selected_connection: "sage-simulator" | "sage-connect" | "middleware";
};

export type DashboardOverviewDto = {
  open_orders_count: number;
  critical_orders_count: number;
  open_orders: OrderDto[];
};

export type ErpOrderValidationDto = {
  reference: string;
  is_valid: boolean;
};

export type ErpTransferRequestDto = {
  id: number;
  order_id: string;
  material_article_number: string;
  status: "draft" | "ready" | "approved" | "sent" | "failed";
  requested_by_user_id: number;
  payload: Record<string, unknown> | null;
  created_at: string;
  ready_by_user_id: number | null;
  approved_by_user_id: number | null;
  sent_by_user_id: number | null;
  failed_by_user_id: number | null;
  ready_at: string | null;
  approved_at: string | null;
  sent_at: string | null;
  failed_at: string | null;
  failure_reason: string | null;
};
