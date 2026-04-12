const AUTH_TOKEN_KEY = "lager_app_auth_token";
const AUTH_CONTEXT_KEY = "lager_app_auth_context";
const LOGIN_CONNECTION_KEY = "lager_app_login_connection";

export type AuthSessionContext = {
  user_id: number;
  username: string;
  role_code: string;
  login_type: "erp" | "admin";
  selected_connection: "sage-simulator" | "sage-connect" | "middleware";
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function getAuthToken(): string | null {
  if (!isBrowser()) {
    return null;
  }
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function getAuthSessionContext(): AuthSessionContext | null {
  if (!isBrowser()) {
    return null;
  }
  const raw = window.localStorage.getItem(AUTH_CONTEXT_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthSessionContext;
  } catch {
    return null;
  }
}

export function setAuthSessionContext(context: AuthSessionContext): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(AUTH_CONTEXT_KEY, JSON.stringify(context));
}

export function getPreferredLoginConnection():
  | "sage-simulator"
  | "sage-connect"
  | "middleware"
  | null {
  if (!isBrowser()) {
    return null;
  }
  const value = window.localStorage.getItem(LOGIN_CONNECTION_KEY);
  if (value === "sage-simulator" || value === "sage-connect" || value === "middleware") {
    return value;
  }
  return null;
}

export function setPreferredLoginConnection(
  value: "sage-simulator" | "sage-connect" | "middleware"
): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(LOGIN_CONNECTION_KEY, value);
}

export function clearAuthToken(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
  window.localStorage.removeItem(AUTH_CONTEXT_KEY);
}
