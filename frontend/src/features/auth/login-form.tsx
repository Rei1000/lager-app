"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MobileEntryQr } from "@/features/auth/mobile-entry-qr";
import {
  getPreferredLoginConnection,
  setPreferredLoginConnection,
} from "@/lib/auth-session";
import { ApiClientError, fetchCurrentUser, login } from "@/lib/api-client";

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

  useEffect(() => {
    const preferredConnection = getPreferredLoginConnection();
    if (preferredConnection) {
      setSelectedConnection(preferredConnection);
    }
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      await login({
        username,
        password,
        login_type: loginType,
        selected_connection: selectedConnection,
      });
      setPreferredLoginConnection(selectedConnection);
      const currentUser = await fetchCurrentUser();
      setMessage(`Angemeldet als ${currentUser.username} (${currentUser.role_name})`);
      setPassword("");
      router.push("/dashboard");
    } catch (err) {
      setMessage(mapLoginError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="grid gap-3" onSubmit={onSubmit}>
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

      <Button type="submit" disabled={submitting}>
        {submitting ? "Anmeldung..." : "Anmelden"}
      </Button>
      <MobileEntryQr />
      {message ? <p className="text-sm text-slate-700">{message}</p> : null}
    </form>
  );
}
