"use client";

import { useEffect } from "react";

export function PwaRegister() {
  useEffect(() => {
    if (typeof window === "undefined" || !("serviceWorker" in navigator)) {
      return;
    }
    const register = async () => {
      try {
        await navigator.serviceWorker.register("/sw.js");
      } catch {
        // Registrierung bleibt optional, die App funktioniert auch ohne SW.
      }
    };
    void register();
  }, []);

  return null;
}
