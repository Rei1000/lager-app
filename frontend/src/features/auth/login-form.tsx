"use client";

import { MouseEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Input } from "@/components/ui/input";
import { MobileEntryQr } from "@/features/auth/mobile-entry-qr";
import {
  getPreferredLoginConnection,
  setPreferredLoginConnection,
} from "@/lib/auth-session";
import { ApiClientError, fetchCurrentUser, login } from "@/lib/api-client";

console.warn("[login-debug] login-form module loaded");

function debugLogin(message: string, details?: Record<string, unknown>) {
  if (details) {
    console.info(`[login-debug] ${message}`, details);
    return;
  }
  console.info(`[login-debug] ${message}`);
}

function mapLoginError(error: unknown): string {
  if (error instanceof ApiClientError) {
    if (error.status === null) {
      return "Server nicht erreichbar.";
    }
    if (error.status === 401) {
      return "Ungueltiger Benutzername oder Passwort.";
    }
    if (error.status === 403) {
      return "Fuer diesen Benutzer ist keine Rolle zugewiesen.";
    }
    if (error.status === 400) {
      if (error.message.toLowerCase().includes("verbindung noch nicht unterstuetzt")) {
        return "Diese Verbindung wird aktuell nicht unterstuetzt.";
      }
      return error.message;
    }
    if (error.status >= 500) {
      return "Technischer Serverfehler. Bitte spaeter erneut versuchen.";
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unbekannter Fehler";
}

export function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [selectedConnection, setSelectedConnection] = useState<
    "sage-simulator" | "sage-connect" | "middleware"
  >("sage-simulator");
  const [loginType, setLoginType] = useState<"erp" | "admin">("erp");
  const [message, setMessage] = useState<string | null>("Noch kein Login-Request gesendet.");
  const [submitting, setSubmitting] = useState(false);
  const [debugStatus, setDebugStatus] = useState("idle");

  useEffect(() => {
    try {
      const preferredConnection = getPreferredLoginConnection();
      if (preferredConnection) {
        setSelectedConnection(preferredConnection);
      }
    } catch (error) {
      debugLogin("preferred connection konnte nicht geladen werden", {
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }, []);

  useEffect(() => {
    setDebugStatus("hydrated");
    debugLogin("login-form hydrated");
  }, []);

  async function handleLoginSubmit(event?: MouseEvent<HTMLButtonElement>) {
    event?.preventDefault();
    if (submitting) {
      setDebugStatus("submit_ignored_submitting");
      debugLogin("submit ignoriert", {
        clientReady: typeof window !== "undefined",
        submitting,
      });
      return;
    }
    debugLogin("submit gestartet", {
      loginType,
      selectedConnection,
      username,
      hasPassword: Boolean(password),
    });
    setDebugStatus("submit_started");
    setSubmitting(true);
    setMessage(null);
    try {
      setDebugStatus("request_sent");
      debugLogin("request wird gesendet", {
        login_type: loginType,
        selected_connection: selectedConnection,
        username,
      });
      await login({
        username,
        password,
        login_type: loginType,
        selected_connection: selectedConnection,
      });
      setDebugStatus("response_received");
      debugLogin("login-response erhalten");
      setPreferredLoginConnection(selectedConnection);
      const currentUser = await fetchCurrentUser();
      debugLogin("current-user geladen", {
        username: currentUser.username,
        role_code: currentUser.role_code,
        role_name: currentUser.role_name,
      });
      setMessage(`Angemeldet als ${currentUser.username} (${currentUser.role_name})`);
      setPassword("");
      setDebugStatus("redirecting");
      debugLogin("redirect nach dashboard");
      router.push("/dashboard");
    } catch (err) {
      setDebugStatus(`error:${err instanceof Error ? err.message : String(err)}`);
      debugLogin("submit fehlgeschlagen", {
        error: err instanceof Error ? err.message : String(err),
      });
      setMessage(mapLoginError(err));
    } finally {
      debugLogin("submit beendet");
      setSubmitting(false);
    }
  }

  return (
    <div className="grid gap-3">
      <label className="grid gap-1 text-sm">
        Verbindung
        <select
          className="h-11 rounded-md border border-slate-300 px-3 text-base"
          value={selectedConnection}
          onChange={(event) =>
            setSelectedConnection(event.target.value as "sage-simulator" | "sage-connect" | "middleware")
          }
        >
          <option value="sage-simulator">sage-simulator</option>
          <option value="sage-connect">sage-connect</option>
          <option value="middleware">middleware</option>
        </select>
      </label>

      <label className="grid gap-1 text-sm">
        Login-Modus
        <select
          className="h-11 rounded-md border border-slate-300 px-3 text-base"
          value={loginType}
          onChange={(event) => setLoginType(event.target.value as "erp" | "admin")}
        >
          <option value="erp">ERP-Benutzer</option>
          <option value="admin">Admin</option>
        </select>
      </label>

      <label className="grid gap-1 text-sm">
        Benutzername
        <Input value={username} onChange={(event) => setUsername(event.target.value)} required />
      </label>

      <label className="grid gap-1 text-sm">
        Passwort
        <Input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
      </label>

      <button
        type="button"
        className="inline-flex min-h-11 items-center justify-center rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={submitting}
        onPointerDown={() => {
          setDebugStatus("pointer_down");
          debugLogin("raw button pointer down");
        }}
        onClick={(event) => {
          setDebugStatus("clicked");
          debugLogin("raw button click");
          void handleLoginSubmit(event);
        }}
      >
        {submitting ? "Anmeldung..." : "Anmelden"}
      </button>
      <MobileEntryQr />
      <p className="text-xs text-slate-500">Debug-Status: {debugStatus}</p>
      <p className="text-xs text-slate-500">
        State: submitting={submitting ? "true" : "false"}
      </p>
      {message ? <p className="text-sm text-slate-700">{message}</p> : null}
    </div>
  );
}
