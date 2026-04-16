"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Input } from "@/components/ui/input";
import {
  getPreferredLoginConnection,
  setPreferredLoginConnection,
} from "@/lib/auth-session";
import { ApiClientError, fetchCurrentUser, login } from "@/lib/api-client";
import { MobileEntryQr } from "@/features/auth/mobile-entry-qr";
import { resolveMobileAppUrl } from "@/lib/mobile-entry-url";

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
  const mobileEntryUrl = resolveMobileAppUrl({
    envUrl: process.env.NEXT_PUBLIC_MOBILE_APP_URL,
  });

  useEffect(() => {
    try {
      const preferredConnection = getPreferredLoginConnection();
      if (preferredConnection) {
        setSelectedConnection(preferredConnection);
      }
    } catch {
      // Ignoriert: bevorzugte Verbindung ist optional.
    }
  }, []);

  async function handleLoginSubmit() {
    if (submitting) {
      return;
    }
    setSubmitting(true);
    setMessage(null);
    try {
      const loginResponse = await login({
        username,
        password,
        login_type: loginType,
        selected_connection: selectedConnection,
      });
      setPreferredLoginConnection(selectedConnection);
      try {
        const currentUser = await fetchCurrentUser();
        setMessage(`Angemeldet als ${currentUser.username} (${currentUser.role_name})`);
      } catch {
        setMessage(`Angemeldet als ${loginResponse.username} (${loginResponse.role_code})`);
      }
      setPassword("");
      router.replace("/dashboard");
    } catch (err) {
      setMessage(mapLoginError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className="grid gap-3"
      onSubmit={(event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        void handleLoginSubmit();
      }}
    >
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
        type="submit"
        className="inline-flex min-h-11 items-center justify-center rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={submitting}
      >
        {submitting ? "Anmeldung..." : "Anmelden"}
      </button>
      <div className="hidden md:block">
        <MobileEntryQr targetUrl={mobileEntryUrl} />
      </div>
      {message ? <p className="text-sm text-slate-700">{message}</p> : null}
    </form>
  );
}
