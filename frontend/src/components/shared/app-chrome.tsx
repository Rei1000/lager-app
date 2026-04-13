"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { logout } from "@/lib/api-client";
import {
  AuthSessionContext,
  getAuthSessionContext,
  getAuthToken,
  subscribeAuthSession,
} from "@/lib/auth-session";

type NavigationItem = {
  href: string;
  label: string;
};

const ADMIN_ITEMS: NavigationItem[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/orders", label: "Orders" },
  { href: "/inventory", label: "Inventur" },
  { href: "/scan", label: "Scan" },
  { href: "/erp-transfers", label: "ERP-Transfer" },
  { href: "/admin", label: "Admin" },
];

const LEITUNG_ITEMS: NavigationItem[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/orders", label: "Orders" },
  { href: "/inventory", label: "Inventur" },
  { href: "/erp-transfers", label: "ERP-Transfer" },
];

const LAGER_ITEMS: NavigationItem[] = [
  { href: "/scan", label: "Scan" },
  { href: "/orders", label: "Orders" },
  { href: "/inventory", label: "Inventur" },
];

export function getVisibleNavigationItems(roleCode: string | null): NavigationItem[] {
  if (!roleCode) {
    return [{ href: "/login", label: "Login" }];
  }
  if (roleCode === "admin") {
    return ADMIN_ITEMS;
  }
  if (roleCode === "leitung") {
    return LEITUNG_ITEMS;
  }
  if (roleCode === "lager") {
    return LAGER_ITEMS;
  }
  return [{ href: "/login", label: "Login" }];
}

function hasSupportedRole(roleCode: string | null): boolean {
  return roleCode === "admin" || roleCode === "leitung" || roleCode === "lager";
}

function loginTypeLabel(loginType: string): string {
  return loginType === "admin" ? "Admin" : "ERP";
}

type AppChromeProps = {
  children: ReactNode;
};

export function AppChrome({ children }: AppChromeProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [authContext, setAuthContext] = useState<AuthSessionContext | null>(null);
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    const syncAuthState = () => {
      setAuthContext(getAuthSessionContext());
      setHasToken(Boolean(getAuthToken()));
    };
    setMounted(true);
    syncAuthState();
    return subscribeAuthSession(syncAuthState);
  }, []);

  const roleCode = authContext?.role_code ?? null;
  const visibleItems = useMemo(() => getVisibleNavigationItems(roleCode), [roleCode]);
  const isLoginRoute = pathname === "/login";
  const isAuthenticated = hasToken && authContext !== null;
  const shouldBlockByMissingRole =
    mounted && isAuthenticated && !hasSupportedRole(roleCode) && !isLoginRoute;
  const shouldShowNavigation = mounted && isAuthenticated && hasSupportedRole(roleCode) && !isLoginRoute;

  useEffect(() => {
    if (!mounted) {
      return;
    }
    if (isLoginRoute) {
      if (isAuthenticated && hasSupportedRole(roleCode)) {
        router.replace("/dashboard");
      }
      return;
    }
    if (!hasToken) {
      router.replace("/login");
    }
  }, [mounted, isLoginRoute, isAuthenticated, roleCode, hasToken, router]);

  function handleLogout() {
    logout();
    setAuthContext(null);
    setHasToken(false);
    router.replace("/login");
  }

  if (isLoginRoute) {
    return <>{children}</>;
  }

  return (
    <>
      {shouldShowNavigation ? (
        <nav className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
          <div className="mx-auto grid w-full max-w-5xl gap-2 p-3 text-sm sm:grid-cols-4">
            {visibleItems.map((item) => (
              <Link
                key={item.href}
                className="rounded-md border border-slate-200 px-3 py-2 text-center"
                href={item.href}
              >
                {item.label}
              </Link>
            ))}
            <Button className="w-full sm:w-auto" onClick={handleLogout}>
              Logout
            </Button>
          </div>
          {authContext ? (
            <div className="mx-auto w-full max-w-5xl px-3 pb-3 text-xs text-slate-600 sm:px-6">
              Angemeldet als {authContext.username} ({loginTypeLabel(authContext.login_type)} -{" "}
              {authContext.selected_connection})
            </div>
          ) : null}
        </nav>
      ) : null}
      {shouldBlockByMissingRole ? (
        <main className="mx-auto w-full max-w-5xl p-3 sm:p-6">
          <section className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
            <p className="font-medium text-red-700">Fuer diesen Benutzer ist keine Rolle zugewiesen.</p>
            <p className="pt-2 text-slate-700">Bitte Admin kontaktieren.</p>
          </section>
        </main>
      ) : (
        children
      )}
    </>
  );
}
