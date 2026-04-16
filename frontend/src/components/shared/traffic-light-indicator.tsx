"use client";

import { cn } from "@/lib/utils";
import { useNarrowViewport } from "@/lib/use-narrow-viewport";

/** Reines Mapping API-Wert → Darstellung (keine Berechnung). */
const TRAFFIC_LIGHT_STYLE: Record<
  string,
  { dotClass: string; label: string; shortLabel: string; title: string }
> = {
  green: {
    dotClass: "bg-[#16a34a]",
    label: "Machbar",
    shortLabel: "OK",
    title: "Auftrag ist in aktueller Reihenfolge vollständig machbar",
  },
  yellow: {
    dotClass: "bg-[#eab308]",
    label: "Eingeschränkt",
    shortLabel: "Teilw.",
    title: "Auftrag ist nur mit Einschränkungen (Reststücke) machbar",
  },
  red: {
    dotClass: "bg-[#dc2626]",
    label: "Nicht machbar",
    shortLabel: "Nein",
    title: "Auftrag ist in aktueller Reihenfolge nicht machbar",
  },
};

export type TrafficLightIndicatorProps = {
  trafficLight: string | null | undefined;
  /** Kurzbeschriftung neben dem Punkt (Standard: an). */
  showLabel?: boolean;
  className?: string;
};

/**
 * Dispositions-Ampel: nur Darstellung von `traffic_light` (green / yellow / red).
 */
export function TrafficLightIndicator({
  trafficLight,
  showLabel = true,
  className,
}: TrafficLightIndicatorProps) {
  const narrow = useNarrowViewport();
  const code = trafficLight?.trim().toLowerCase() ?? "";
  const meta = code ? TRAFFIC_LIGHT_STYLE[code] : null;

  if (!meta) {
    return (
      <span
        className={cn("inline-flex items-center gap-2", className)}
        title={trafficLight ? `Unbekannter Ampel-Code: ${trafficLight}` : undefined}
      >
        <span
          className="inline-block h-3 w-3 shrink-0 rounded-full bg-slate-300"
          aria-hidden
        />
        {showLabel ? <span className="text-sm text-slate-600">—</span> : null}
      </span>
    );
  }

  return (
    <span
      className={cn("inline-flex items-center gap-1.5 sm:gap-2", className)}
      title={meta.title}
      role="img"
      aria-label={`Disposition: ${meta.label}`}
    >
      <span
        className={cn(
          "inline-block shrink-0 rounded-full ring-1 ring-black/10",
          narrow ? "h-2.5 w-2.5" : "h-3 w-3",
          meta.dotClass
        )}
        aria-hidden
      />
      {showLabel ? (
        <span
          className={cn(
            "font-medium text-slate-800",
            narrow ? "max-w-[3.25rem] truncate text-[11px] leading-tight" : "text-sm"
          )}
        >
          {narrow ? meta.shortLabel : meta.label}
        </span>
      ) : null}
    </span>
  );
}
