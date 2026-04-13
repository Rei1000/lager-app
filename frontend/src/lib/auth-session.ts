const AUTH_TOKEN_KEY = "lager_app_auth_token";
const AUTH_CONTEXT_KEY = "lager_app_auth_context";
const LOGIN_CONNECTION_KEY = "lager_app_login_connection";
const authListeners = new Set<() => void>();

let authTokenMemory: string | null = null;
let authContextMemory: AuthSessionContext | null = null;

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

function notifyAuthListeners(): void {
  for (const listener of authListeners) {
    listener();
  }
}

export function subscribeAuthSession(listener: () => void): () => void {
  authListeners.add(listener);
  return () => {
    authListeners.delete(listener);
  };
}

export function getAuthToken(): string | null {
  return authTokenMemory;
}

export function setAuthToken(token: string): void {
  authTokenMemory = token;
  notifyAuthListeners();
}

export function getAuthSessionContext(): AuthSessionContext | null {
  return authContextMemory;
}

export function setAuthSessionContext(context: AuthSessionContext): void {
  authContextMemory = context;
  notifyAuthListeners();
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
  authTokenMemory = null;
  authContextMemory = null;
  if (!isBrowser()) {
    notifyAuthListeners();
    return;
  }
  // Cleanup old persisted entries from previous app versions.
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
  window.localStorage.removeItem(AUTH_CONTEXT_KEY);
  notifyAuthListeners();
}
