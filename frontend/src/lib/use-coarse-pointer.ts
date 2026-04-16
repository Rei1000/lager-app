import { useSyncExternalStore } from "react";

/**
 * true: z. B. Touch — Tap oeffnet Bearbeitung; false: Maus — Doppelklick.
 */
export function useCoarsePointer(): boolean {
  return useSyncExternalStore(
    (onStoreChange) => {
      if (typeof window === "undefined") {
        return () => {};
      }
      const mq = window.matchMedia("(pointer: coarse)");
      mq.addEventListener("change", onStoreChange);
      return () => mq.removeEventListener("change", onStoreChange);
    },
    () => (typeof window !== "undefined" ? window.matchMedia("(pointer: coarse)").matches : false),
    () => false
  );
}
