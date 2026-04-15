const DEFAULT_API_BASE_URL = "http://localhost:8001";
const serverConfiguredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();

export const API_BASE_URL = serverConfiguredApiBaseUrl || DEFAULT_API_BASE_URL;
