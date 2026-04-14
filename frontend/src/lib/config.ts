const DEFAULT_API_BASE_URL = "http://localhost:8001";
const API_PORT = "8001";

function resolveClientApiBaseUrl(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  const protocol = window.location.protocol === "https:" ? "https" : "http";
  const hostname =
    window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
      ? "localhost"
      : window.location.hostname;
  return `${protocol}://${hostname}:${API_PORT}`;
}

const serverConfiguredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

export const API_BASE_URL =
  resolveClientApiBaseUrl() ?? serverConfiguredApiBaseUrl ?? DEFAULT_API_BASE_URL;
