import { describe, expect, it, vi } from "vitest";

import { getAuthSessionContext } from "@/lib/auth-session";
import {
  ApiClientError,
  approveErpTransfer,
  createComment,
  createOrder,
  fetchErpTransfers,
  fetchErpOrderValidation,
  fetchCurrentUser,
  fetchHealth,
  listCommentsForEntity,
  listPhotosForEntity,
  login,
  searchMaterials,
  uploadPhoto,
} from "@/lib/api-client";

describe("api client", () => {
  it("calls health endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok" }),
      })
    );

    const payload = await fetchHealth();
    expect(payload.status).toBe("ok");
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/health",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("sends create order request payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => ({
          order_id: "A1",
          display_order_code: "APP-000001",
          persisted_row_id: 1,
          material_article_number: "ART-001",
          quantity: 1,
          part_length_mm: 1000,
          kerf_mm: 0,
          include_rest_stock: false,
          status: "draft",
          priority_order: 1,
          traffic_light: "green",
          erp_order_number: null,
          total_demand_mm: 1000,
        }),
      })
    );

    const payload = await createOrder({
      order_id: "A1",
      material_article_number: "ART-001",
      quantity: 1,
      part_length_mm: 1000,
      kerf_mm: 0,
      include_rest_stock: false,
    });

    expect(payload.order_id).toBe("A1");
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/orders",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("calls material search endpoint with query parameter", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [
          {
            article_number: "ART-001",
            name: "Stahlprofil 40x40",
            profile: "40x40",
            erp_stock_m: 120,
            rest_stock_m: 12,
          },
        ],
      })
    );

    const payload = await searchMaterials("ART-001");
    expect(payload).toHaveLength(1);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/materials/search?query=ART-001",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("stores token on login and uses it for authenticated call", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access_token: "token-abc",
          token_type: "bearer",
          expires_in_seconds: 3600,
          user_id: 1,
          username: "admin",
          role_code: "admin",
          login_type: "admin",
          selected_connection: "sage-simulator",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          user_id: 1,
          username: "admin",
          role_code: "admin",
          role_name: "Admin",
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    await login({
      username: "admin",
      password: "secret123",
      login_type: "admin",
      selected_connection: "sage-simulator",
    });
    const me = await fetchCurrentUser();

    expect(me.role_code).toBe("admin");
    const secondCall = fetchMock.mock.calls[1];
    expect(secondCall[0]).toBe("http://localhost:8001/auth/me");
    expect(secondCall[1]?.method).toBe("GET");
    const headers = secondCall[1]?.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer token-abc");
    const authContext = getAuthSessionContext();
    expect(authContext?.login_type).toBe("admin");
    expect(authContext?.selected_connection).toBe("sage-simulator");
  });

  it("maps 401 login response to ApiClientError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({
          detail: "Ungueltige Anmeldedaten",
        }),
      })
    );

    await expect(
      login({
        username: "admin",
        password: "wrong",
        login_type: "admin",
        selected_connection: "sage-simulator",
      })
    ).rejects.toMatchObject({
      name: "ApiClientError",
      status: 401,
      message: "Ungueltige Anmeldedaten",
    });
  });

  it("maps 400 unsupported connection to ApiClientError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({
          detail: "Verbindung noch nicht unterstuetzt",
        }),
      })
    );

    await expect(
      login({
        username: "sim-user",
        password: "secret123",
        login_type: "erp",
        selected_connection: "middleware",
      })
    ).rejects.toMatchObject({
      name: "ApiClientError",
      status: 400,
      message: "Verbindung noch nicht unterstuetzt",
    });
  });

  it("calls ERP order validation endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          reference: "ERP-42",
          is_valid: true,
        }),
      })
    );

    const payload = await fetchErpOrderValidation("ERP-42");
    expect(payload.is_valid).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/erp/orders/ERP-42/validate",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("calls ERP transfer list endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      })
    );

    const payload = await fetchErpTransfers();
    expect(payload).toHaveLength(0);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/erp/transfers",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("calls ERP transfer approve endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          id: 1,
          order_id: "ORD-1",
          material_article_number: "ART-001",
          status: "approved",
          requested_by_user_id: 1,
          payload: null,
          created_at: "2026-04-11T00:00:00Z",
          ready_by_user_id: 2,
          approved_by_user_id: 3,
          sent_by_user_id: null,
          failed_by_user_id: null,
          ready_at: "2026-04-11T00:00:00Z",
          approved_at: "2026-04-11T00:00:10Z",
          sent_at: null,
          failed_at: null,
          failure_reason: null,
        }),
      })
    );

    const payload = await approveErpTransfer({ transfer_id: 1, acting_user_id: 3 });
    expect(payload.status).toBe("approved");
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/erp/transfers/1/approve",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("calls photos list endpoint with entity filter", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      })
    );

    const payload = await listPhotosForEntity({
      entity_type: "material",
      entity_id: "ART-001",
    });

    expect(payload).toHaveLength(0);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/photos?entity_type=material&entity_id=ART-001",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("sends multipart request for photo upload", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 1,
        entity_type: "material",
        entity_id: "ART-001",
        uploaded_by_user_id: 1,
        uploaded_at: "2026-04-11T00:00:00Z",
        comment: "Dokumentation",
        original_filename: "m.jpg",
        content_type: "image/jpeg",
        file_url: "/photos/1/file",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const file = new File(["binary"], "m.jpg", { type: "image/jpeg" });
    const payload = await uploadPhoto({
      entity_type: "material",
      entity_id: "ART-001",
      file,
      comment: "Dokumentation",
    });

    expect(payload.id).toBe(1);
    const requestOptions = fetchMock.mock.calls[0][1];
    expect(requestOptions.method).toBe("POST");
    expect(requestOptions.body instanceof FormData).toBe(true);
  });

  it("calls comments list endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      })
    );

    const payload = await listCommentsForEntity({
      entity_type: "order",
      entity_id: "A-1",
    });

    expect(payload).toHaveLength(0);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/comments?entity_type=order&entity_id=A-1",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("calls comments create endpoint", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => ({
          id: 1,
          entity_type: "order",
          entity_id: "A-1",
          text: "Hinweis",
          created_by_user_id: 2,
          created_at: "2026-04-11T00:00:00Z",
        }),
      })
    );

    const payload = await createComment({
      entity_type: "order",
      entity_id: "A-1",
      text: "Hinweis",
    });

    expect(payload.id).toBe(1);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8001/comments",
      expect.objectContaining({ method: "POST" })
    );
  });
});
