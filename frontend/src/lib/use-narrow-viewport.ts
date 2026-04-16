import { useSyncExternalStore } from "react";

/** true bei Viewport max. 639px (unter sm) — z. B. kompakte Ampel-Labels. */
export function useNarrowViewport(): boolean {
  return useSyncExternalStore(
    (onChange) => {
      if (typeof window === "undefined") {
        return () => {};
      }
      const mq = window.matchMedia("(max-width: 639px)");
      mq.addEventListener("change", onChange);
      return () => mq.removeEventListener("change", onChange);
    },
    () => (typeof window !== "undefined" ? window.matchMedia("(max-width: 639px)").matches : false),
    () => false
  );
}
