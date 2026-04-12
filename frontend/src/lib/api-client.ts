import { API_BASE_URL } from "@/lib/config";
import { clearAuthToken, getAuthToken, setAuthSessionContext, setAuthToken } from "@/lib/auth-session";
import type {
  CommentDto,
  CurrentUserDto,
  CuttingMachineDto,
  DashboardOverviewDto,
  ErpEndpointDto,
  ErpMappingDto,
  ErpProfileDto,
  InventoryCountDto,
  InventoryDifferenceDto,
  LoginResponseDto,
  MaterialLookupDto,
  PhotoDto,
  OrderDto,
  StockCorrectionDto,
  UserDto,
  ErpOrderValidationDto,
  ErpTransferRequestDto,
} from "@/lib/types";

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status: number | null
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const { headers: incomingHeaders, ...restInit } = init ?? {};
  const headers = new Headers(incomingHeaders);
  const body = restInit.body;
  const isFormDataBody = typeof FormData !== "undefined" && body instanceof FormData;
  if (!headers.has("Content-Type") && !isFormDataBody) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...restInit,
      headers,
    });
  } catch {
    throw new ApiClientError("Server nicht erreichbar. Bitte Verbindung pruefen.", null);
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    if (payload?.detail) {
      throw new ApiClientError(payload.detail, response.status);
    }
    const text = await response.text().catch(() => "");
    if (text.trim()) {
      throw new ApiClientError(text, response.status);
    }
    throw new ApiClientError(`Anfrage fehlgeschlagen (HTTP ${response.status})`, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(payload: {
  username: string;
  password: string;
  login_type: "erp" | "admin";
  selected_connection: "sage-simulator" | "sage-connect" | "middleware";
}): Promise<LoginResponseDto> {
  const response = await request<LoginResponseDto>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAuthToken(response.access_token);
  setAuthSessionContext({
    user_id: response.user_id,
    username: response.username,
    role_code: response.role_code,
    login_type: response.login_type,
    selected_connection: response.selected_connection,
  });
  return response;
}

export async function fetchCurrentUser(): Promise<CurrentUserDto> {
  return request<CurrentUserDto>("/auth/me", { method: "GET" });
}

export function logout(): void {
  clearAuthToken();
}

export async function fetchHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health", { method: "GET" });
}

export async function createOrder(payload: {
  order_id: string;
  material_article_number: string;
  quantity: number;
  part_length_mm: number;
  kerf_mm: number;
  include_rest_stock: boolean;
}): Promise<OrderDto> {
  return request<OrderDto>("/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function reserveOrder(orderId: string): Promise<OrderDto> {
  return request<OrderDto>(`/orders/${orderId}/reserve`, { method: "POST" });
}

export async function reprioritizeOrders(payload: {
  material_article_number: string;
  ordered_ids: string[];
}): Promise<OrderDto[]> {
  return request<OrderDto[]>("/orders/reprioritize", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function linkErpOrder(payload: {
  order_id: string;
  erp_order_number: string;
}): Promise<OrderDto> {
  return request<OrderDto>(`/orders/${payload.order_id}/link-erp`, {
    method: "POST",
    body: JSON.stringify({ erp_order_number: payload.erp_order_number }),
  });
}

export async function recalculateOrders(payload: {
  material_article_number: string;
}): Promise<OrderDto[]> {
  return request<OrderDto[]>("/orders/recalculate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchOrders(params?: {
  status?: string;
  material_article_number?: string;
}): Promise<OrderDto[]> {
  const search = new URLSearchParams();
  if (params?.status) {
    search.set("status", params.status);
  }
  if (params?.material_article_number) {
    search.set("material_article_number", params.material_article_number);
  }
  const query = search.toString();
  const path = query ? `/orders?${query}` : "/orders";
  return request<OrderDto[]>(path, { method: "GET" });
}

export async function fetchOrderById(orderId: string): Promise<OrderDto> {
  return request<OrderDto>(`/orders/${encodeURIComponent(orderId)}`, { method: "GET" });
}

export async function fetchDashboardOverview(): Promise<DashboardOverviewDto> {
  return request<DashboardOverviewDto>("/dashboard/overview", { method: "GET" });
}

export async function fetchErpProfiles(): Promise<ErpProfileDto[]> {
  return request<ErpProfileDto[]>("/admin/erp-profiles", { method: "GET" });
}

export async function createErpProfile(payload: {
  name: string;
  erp_type?: string | null;
  connection_type?: string | null;
  base_url?: string | null;
  tenant_code?: string | null;
}): Promise<ErpProfileDto> {
  return request<ErpProfileDto>("/admin/erp-profiles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchErpProfile(profileId: number): Promise<ErpProfileDto> {
  return request<ErpProfileDto>(`/admin/erp-profiles/${profileId}`, {
    method: "GET",
  });
}

export async function fetchEndpoints(): Promise<ErpEndpointDto[]> {
  return request<ErpEndpointDto[]>("/admin/endpoints", { method: "GET" });
}

export async function createEndpoint(payload: {
  erp_profile_id: number;
  functional_key: string;
  http_method: string;
  path_template: string;
}): Promise<ErpEndpointDto> {
  return request<ErpEndpointDto>("/admin/endpoints", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchMappings(): Promise<ErpMappingDto[]> {
  return request<ErpMappingDto[]>("/admin/mappings", { method: "GET" });
}

export async function createMapping(payload: {
  endpoint_id: number;
  app_field: string;
  erp_field: string;
  direction: "app_to_erp" | "erp_to_app";
}): Promise<ErpMappingDto> {
  return request<ErpMappingDto>("/admin/mappings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCuttingMachines(): Promise<CuttingMachineDto[]> {
  return request<CuttingMachineDto[]>("/admin/cutting-machines", { method: "GET" });
}

export async function createCuttingMachine(payload: {
  machine_code?: string | null;
  name: string;
  kerf_mm?: number | null;
  is_active: boolean;
}): Promise<CuttingMachineDto> {
  return request<CuttingMachineDto>("/admin/cutting-machines", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchUsers(): Promise<UserDto[]> {
  return request<UserDto[]>("/admin/users", { method: "GET" });
}

export async function createUser(payload: {
  username: string;
  password: string;
  role_id: number;
  display_name?: string | null;
  email?: string | null;
  is_active: boolean;
  erp_user_reference?: string | null;
}): Promise<UserDto> {
  return request<UserDto>("/admin/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchInventoryCounts(): Promise<InventoryCountDto[]> {
  return request<InventoryCountDto[]>("/inventory/counts", { method: "GET" });
}

export async function createInventoryCount(payload: {
  material_article_number: string;
  counted_stock_mm: number;
  counted_by_user_id: number;
  comment?: string | null;
}): Promise<InventoryCountDto> {
  return request<InventoryCountDto>("/inventory/counts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function compareInventory(payload: {
  material_article_number: string;
  counted_stock_mm: number;
}): Promise<InventoryDifferenceDto> {
  return request<InventoryDifferenceDto>("/inventory/compare", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createStockCorrection(payload: {
  inventory_count_id: number;
  requested_by_user_id: number;
  comment?: string | null;
}): Promise<StockCorrectionDto> {
  return request<StockCorrectionDto>("/inventory/corrections", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function confirmStockCorrection(payload: {
  correction_id: number;
  acting_user_id: number;
}): Promise<StockCorrectionDto> {
  return request<StockCorrectionDto>(`/inventory/corrections/${payload.correction_id}/confirm`, {
    method: "POST",
    body: JSON.stringify({ acting_user_id: payload.acting_user_id }),
  });
}

export async function cancelStockCorrection(payload: {
  correction_id: number;
  acting_user_id: number;
}): Promise<StockCorrectionDto> {
  return request<StockCorrectionDto>(`/inventory/corrections/${payload.correction_id}/cancel`, {
    method: "POST",
    body: JSON.stringify({ acting_user_id: payload.acting_user_id }),
  });
}

export async function uploadPhoto(payload: {
  entity_type: string;
  entity_id: string;
  file: File;
  comment?: string | null;
}): Promise<PhotoDto> {
  const body = new FormData();
  body.set("entity_type", payload.entity_type);
  body.set("entity_id", payload.entity_id);
  body.set("file", payload.file);
  if (payload.comment) {
    body.set("comment", payload.comment);
  }
  return request<PhotoDto>("/photos", {
    method: "POST",
    body,
  });
}

export async function listPhotosForEntity(payload: {
  entity_type: string;
  entity_id: string;
}): Promise<PhotoDto[]> {
  const search = new URLSearchParams();
  search.set("entity_type", payload.entity_type);
  search.set("entity_id", payload.entity_id);
  return request<PhotoDto[]>(`/photos?${search.toString()}`, { method: "GET" });
}

export async function createComment(payload: {
  entity_type: string;
  entity_id: string;
  text: string;
}): Promise<CommentDto> {
  return request<CommentDto>("/comments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listCommentsForEntity(payload: {
  entity_type: string;
  entity_id: string;
}): Promise<CommentDto[]> {
  const search = new URLSearchParams();
  search.set("entity_type", payload.entity_type);
  search.set("entity_id", payload.entity_id);
  return request<CommentDto[]>(`/comments?${search.toString()}`, { method: "GET" });
}

export async function searchMaterials(query: string): Promise<MaterialLookupDto[]> {
  const encoded = encodeURIComponent(query);
  return request<MaterialLookupDto[]>(`/materials/search?query=${encoded}`, {
    method: "GET",
  });
}

export async function getMaterialByArticleNumber(
  articleNumber: string
): Promise<MaterialLookupDto> {
  return request<MaterialLookupDto>(`/materials/${encodeURIComponent(articleNumber)}`, {
    method: "GET",
  });
}

export async function fetchErpMaterial(reference: string): Promise<Record<string, unknown>> {
  const response = await request<{ payload: Record<string, unknown> }>(
    `/erp/materials/${encodeURIComponent(reference)}`,
    { method: "GET" }
  );
  return response.payload;
}

export async function fetchErpMaterialStock(reference: string): Promise<Record<string, unknown>> {
  const response = await request<{ payload: Record<string, unknown> }>(
    `/erp/materials/${encodeURIComponent(reference)}/stock`,
    { method: "GET" }
  );
  return response.payload;
}

export async function fetchErpOrderValidation(reference: string): Promise<ErpOrderValidationDto> {
  return request<ErpOrderValidationDto>(`/erp/orders/${encodeURIComponent(reference)}/validate`, {
    method: "GET",
  });
}

export async function fetchErpTransfers(): Promise<ErpTransferRequestDto[]> {
  return request<ErpTransferRequestDto[]>("/erp/transfers", { method: "GET" });
}

export async function createErpTransfer(payload: {
  order_id: string;
  material_article_number: string;
  requested_by_user_id: number;
  payload?: Record<string, unknown> | null;
}): Promise<ErpTransferRequestDto> {
  return request<ErpTransferRequestDto>("/erp/transfers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function markErpTransferReady(payload: {
  transfer_id: number;
  acting_user_id: number;
}): Promise<ErpTransferRequestDto> {
  return request<ErpTransferRequestDto>(`/erp/transfers/${payload.transfer_id}/ready`, {
    method: "POST",
    body: JSON.stringify({ acting_user_id: payload.acting_user_id }),
  });
}

export async function approveErpTransfer(payload: {
  transfer_id: number;
  acting_user_id: number;
}): Promise<ErpTransferRequestDto> {
  return request<ErpTransferRequestDto>(`/erp/transfers/${payload.transfer_id}/approve`, {
    method: "POST",
    body: JSON.stringify({ acting_user_id: payload.acting_user_id }),
  });
}

export async function markErpTransferSent(payload: {
  transfer_id: number;
  acting_user_id: number;
}): Promise<ErpTransferRequestDto> {
  return request<ErpTransferRequestDto>(`/erp/transfers/${payload.transfer_id}/send`, {
    method: "POST",
    body: JSON.stringify({ acting_user_id: payload.acting_user_id }),
  });
}

export async function markErpTransferFailed(payload: {
  transfer_id: number;
  acting_user_id: number;
  failure_reason?: string | null;
}): Promise<ErpTransferRequestDto> {
  return request<ErpTransferRequestDto>(`/erp/transfers/${payload.transfer_id}/fail`, {
    method: "POST",
    body: JSON.stringify({
      acting_user_id: payload.acting_user_id,
      failure_reason: payload.failure_reason ?? null,
    }),
  });
}
