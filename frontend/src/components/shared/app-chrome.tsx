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
  { href: "/admin/simulator-test", label: "Simulator-Test" },
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
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

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

  useEffect(() => {
    setMobileNavOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!mobileNavOpen) {
      return;
    }
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMobileNavOpen(false);
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [mobileNavOpen]);

  function handleLogout() {
    logout();
    setAuthContext(null);
    setHasToken(false);
    router.replace("/login");
  }

  if (isLoginRoute) {
    return <>{children}</>;
  }

  if (!mounted || !hasToken) {
    return (
      <main className="mx-auto w-full max-w-5xl p-3 sm:p-6">
        <section className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
          Weiterleitung zur Anmeldung...
        </section>
      </main>
    );
  }

  return (
    <>
      {shouldShowNavigation ? (
        <>
          <nav className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
            <div className="mx-auto flex max-w-5xl items-center justify-end px-3 py-2 md:hidden">
              <button
                type="button"
                className="inline-flex min-h-10 min-w-10 items-center justify-center rounded-md border border-slate-200 bg-white text-xl leading-none text-slate-800 hover:bg-slate-50"
                aria-expanded={mobileNavOpen}
                aria-controls="mobile-app-nav-drawer"
                aria-label="Hauptmenü öffnen"
                onClick={() => setMobileNavOpen(true)}
              >
                <span aria-hidden>☰</span>
              </button>
            </div>
            <div className="mx-auto hidden w-full max-w-5xl gap-2 p-3 text-sm md:grid md:grid-cols-4">
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
              <div className="mx-auto hidden w-full max-w-5xl px-3 pb-3 text-xs text-slate-600 md:block sm:px-6">
                Angemeldet als {authContext.username} ({loginTypeLabel(authContext.login_type)} -{" "}
                {authContext.selected_connection})
              </div>
            ) : null}
          </nav>
          {mobileNavOpen ? (
            <div
              className="fixed inset-0 z-50 md:hidden"
              id="mobile-app-nav-drawer"
              role="dialog"
              aria-modal="true"
              aria-label="Hauptmenü"
            >
              <button
                type="button"
                className="absolute inset-0 bg-slate-900/40"
                aria-label="Menü schließen"
                onClick={() => setMobileNavOpen(false)}
              />
              <div className="absolute right-0 top-0 z-10 flex h-full w-[min(100%,20rem)] flex-col border-l border-slate-200 bg-white shadow-xl">
                <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2">
                  <span className="text-sm font-medium text-slate-800">Menü</span>
                  <button
                    type="button"
                    className="inline-flex min-h-9 min-w-9 items-center justify-center rounded-md border border-slate-200 text-sm text-slate-700 hover:bg-slate-50"
                    aria-label="Menü schließen"
                    onClick={() => setMobileNavOpen(false)}
                  >
                    ✕
                  </button>
                </div>
                {authContext ? (
                  <p className="border-b border-slate-100 px-3 py-2 text-xs text-slate-600">
                    Angemeldet als {authContext.username} ({loginTypeLabel(authContext.login_type)} -{" "}
                    {authContext.selected_connection})
                  </p>
                ) : null}
                <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-3">
                  {visibleItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="rounded-md border border-slate-200 px-3 py-2.5 text-center text-sm text-slate-800 hover:bg-slate-50"
                      onClick={() => setMobileNavOpen(false)}
                    >
                      {item.label}
                    </Link>
                  ))}
                  <Button
                    className="mt-auto w-full"
                    onClick={() => {
                      setMobileNavOpen(false);
                      handleLogout();
                    }}
                  >
                    Logout
                  </Button>
                </div>
              </div>
            </div>
          ) : null}
        </>
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
