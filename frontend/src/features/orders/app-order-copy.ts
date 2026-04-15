/**
 * Reine UI-Texte / Zuordnungen — keine Fachlogik (Domain bleibt englisch: draft, green, …).
 */

export const APP_ORDER_STATUS_LABEL_DE: Record<string, string> = {
  draft: "Entwurf",
  checked: "Geprueft",
  reserved: "Reserviert",
  linked: "Mit ERP verknuepft",
  confirmed: "Bestaetigt",
  done: "Erledigt",
  canceled: "Storniert",
};

export function appOrderStatusLabelDe(code: string): string {
  return APP_ORDER_STATUS_LABEL_DE[code] ?? code;
}

export const TRAFFIC_LIGHT_LABEL_DE: Record<string, string> = {
  green: "Gruen",
  yellow: "Gelb",
  red: "Rot",
};

export function trafficLightLabelDe(code: string | null | undefined): string {
  if (!code) {
    return "—";
  }
  return TRAFFIC_LIGHT_LABEL_DE[code] ?? code;
}
