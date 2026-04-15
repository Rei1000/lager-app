export const DEFAULT_LOGIN_URL = "http://localhost:3001/login";

type ResolveMobileAppUrlArgs = {
  envUrl?: string | null;
  loginPath?: string;
};

function toLoginUrl(candidate: string, loginPath: string): string | null {
  try {
    const normalized = candidate.trim();
    if (!normalized) {
      return null;
    }
    const url = new URL(normalized);
    if (url.pathname === "/" || url.pathname === "") {
      url.pathname = loginPath;
      url.search = "";
      url.hash = "";
    }
    return url.toString();
  } catch {
    return null;
  }
}

export function resolveMobileAppUrl({
  envUrl = null,
  loginPath = "/login",
}: ResolveMobileAppUrlArgs = {}): string {
  const envTarget = toLoginUrl(envUrl ?? "", loginPath);
  if (envTarget) {
    return envTarget;
  }

  return DEFAULT_LOGIN_URL;
}
