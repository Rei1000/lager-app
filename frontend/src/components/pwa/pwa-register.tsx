"use client";

import { useEffect } from "react";

export function PwaRegister() {
  useEffect(() => {
    if (typeof window === "undefined" || !("serviceWorker" in navigator)) {
      return;
    }
    const isProduction = process.env.NODE_ENV === "production";
    const syncServiceWorker = async () => {
      try {
        if (!isProduction) {
          const registrations = await navigator.serviceWorker.getRegistrations();
          await Promise.all(registrations.map((registration) => registration.unregister()));
          return;
        }
        await navigator.serviceWorker.register("/sw.js");
      } catch {
        // Registrierung bleibt optional, die App funktioniert auch ohne SW.
      }
    };
    void syncServiceWorker();
  }, []);

  return null;
}
