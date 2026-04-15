"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SimulatorMaterialSearchPanel } from "@/features/orders/simulator-material-search-panel";
import {
  ApiClientError,
  createOrder,
  getMaterialByArticleNumber,
  previewOrderPlan,
} from "@/lib/api-client";
import type { MaterialLookupDto, OrderPlanPreviewDto } from "@/lib/types";

type SawOption = {
  id: string;
  label: string;
  kerfMm: number | null;
};

const SAW_OPTIONS: SawOption[] = [
  { id: "", label: "Keine Auswahl (Kerf manuell)", kerfMm: null },
  { id: "saw-a", label: "Trennsäge A (Demo)", kerfMm: 3 },
  { id: "saw-b", label: "Trennsäge B (Demo)", kerfMm: 2.5 },
];

export type NewOrderPlanningFormProps = {
  /** Nach erfolgreichem POST /orders — z. B. Orders-Liste aktualisieren. */
  onAppOrderSaved?: () => void;
};

export function NewOrderPlanningForm({ onAppOrderSaved }: NewOrderPlanningFormProps) {
  const [articleInput, setArticleInput] = useState("");
  const [material, setMaterial] = useState<MaterialLookupDto | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingMaterial, setLoadingMaterial] = useState(false);

  const [preview, setPreview] = useState<OrderPlanPreviewDto | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const [quantity, setQuantity] = useState("1");
  const [partLengthMm, setPartLengthMm] = useState("1000");
  const [selectedSawId, setSelectedSawId] = useState("");
  const [manualKerfMm, setManualKerfMm] = useState("2");
  const [considerRestPieces, setConsiderRestPieces] = useState(false);

  const [saveLoading, setSaveLoading] = useState(false);
  const [saveFeedback, setSaveFeedback] = useState<{ kind: "success" | "error"; message: string } | null>(null);

  const loadGen = useRef(0);
  const previewGen = useRef(0);
  const saveInFlight = useRef(false);

  const selectedSaw = useMemo(
    () => SAW_OPTIONS.find((s) => s.id === selectedSawId) ?? SAW_OPTIONS[0],
    [selectedSawId]
  );

  const effectiveKerfMm = useMemo(() => {
    if (selectedSaw.kerfMm !== null && selectedSaw.kerfMm !== undefined) {
      return selectedSaw.kerfMm;
    }
    return Math.max(0, Number(manualKerfMm.replace(",", ".")) || 0);
  }, [manualKerfMm, selectedSaw]);

  const runPreview = useCallback(async () => {
    if (!material) {
      setPreview(null);
      setPreviewError(null);
      return;
    }
    const q = Math.floor(Number(quantity.replace(",", ".")) || 0);
    const pl = Math.max(0, Number(partLengthMm.replace(",", ".")) || 0);
    if (q < 1 || pl < 1) {
      setPreview(null);
      setPreviewError(null);
      return;
    }

    const gen = ++previewGen.current;
    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const result = await previewOrderPlan({
        article_number: material.article_number.trim(),
        quantity: q,
        part_length_mm: Math.round(pl),
        kerf_mm: effectiveKerfMm,
        rest_piece_consideration_requested: considerRestPieces,
      });
      if (gen !== previewGen.current) {
        return;
      }
      setPreview(result);
    } catch (err) {
      if (gen !== previewGen.current) {
        return;
      }
      setPreview(null);
      if (err instanceof ApiClientError) {
        setPreviewError(err.message || "Vorschau fehlgeschlagen");
      } else {
        setPreviewError("Vorschau fehlgeschlagen");
      }
    } finally {
      if (gen === previewGen.current) {
        setPreviewLoading(false);
      }
    }
  }, [material, quantity, partLengthMm, effectiveKerfMm, considerRestPieces]);

  useEffect(() => {
    if (!material) {
      return;
    }
    const t = window.setTimeout(() => {
      void runPreview();
    }, 400);
    return () => window.clearTimeout(t);
  }, [material, runPreview]);

  const canSave =
    Boolean(material) &&
    Boolean(preview) &&
    !previewLoading &&
    !saveLoading &&
    Math.floor(Number(quantity.replace(",", ".")) || 0) >= 1 &&
    Math.max(0, Number(partLengthMm.replace(",", ".")) || 0) >= 1;

  async function handleSaveOrder() {
    if (!material || !preview || saveLoading || previewLoading) {
      return;
    }
    if (saveInFlight.current) {
      return;
    }
    const q = Math.floor(Number(quantity.replace(",", ".")) || 0);
    const pl = Math.max(0, Number(partLengthMm.replace(",", ".")) || 0);
    if (q < 1 || pl < 1) {
      return;
    }
    saveInFlight.current = true;
    setSaveLoading(true);
    setSaveFeedback(null);
    const orderId =
      typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
        ? crypto.randomUUID()
        : `app-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    const kerfMmInt = Math.max(0, Math.round(effectiveKerfMm));
    try {
      const saved = await createOrder({
        order_id: orderId,
        material_article_number: material.article_number.trim(),
        quantity: q,
        part_length_mm: Math.round(pl),
        kerf_mm: kerfMmInt,
        include_rest_stock: considerRestPieces,
      });
      const label = saved.display_order_code?.trim() || orderId;
      setSaveFeedback({
        kind: "success",
        message: `App-Auftrag ${label} gespeichert. Die Vorschau wird mit aktualisierter Verfuegbarkeit neu geladen. Unter „Auftraege“ sehen Sie die Ampel fuer die Disposition (nicht dieselbe Aussage wie die Planungsvorschau hier).`,
      });
      onAppOrderSaved?.();
      await runPreview();
    } catch (err) {
      const msg =
        err instanceof ApiClientError
          ? err.message || "Speichern fehlgeschlagen"
          : "Speichern fehlgeschlagen";
      setSaveFeedback({ kind: "error", message: msg });
    } finally {
      setSaveLoading(false);
      saveInFlight.current = false;
    }
  }

  async function loadMaterialForArticle(articleNumber: string) {
    const normalized = articleNumber.trim();
    if (!normalized) {
      setLoadError("Bitte Artikelnummer eingeben");
      setMaterial(null);
      setPreview(null);
      return;
    }

    const gen = ++loadGen.current;
    setLoadingMaterial(true);
    setLoadError(null);
    setMaterial(null);
    setPreview(null);
    setPreviewError(null);

    try {
      const mat = await getMaterialByArticleNumber(normalized);
      if (gen !== loadGen.current) {
        return;
      }
      const canonical = mat.article_number.trim();
      setMaterial(mat);
      setArticleInput(canonical);
    } catch (err) {
      if (gen !== loadGen.current) {
        return;
      }
      if (err instanceof ApiClientError) {
        setLoadError(err.status === 404 ? "Artikel nicht gefunden" : "Fehler beim Laden");
      } else {
        setLoadError("Fehler beim Laden");
      }
    } finally {
      if (gen === loadGen.current) {
        setLoadingMaterial(false);
      }
    }
  }

  function onArticleInputChange(value: string) {
    setArticleInput(value);
    setLoadError(null);
    if (material && value.trim() !== material.article_number.trim()) {
      setMaterial(null);
      setPreview(null);
      setPreviewError(null);
    }
  }

  return (
    <div className="grid gap-6 text-sm text-slate-800">
      <div className="rounded-lg border border-slate-200 bg-slate-50/90 p-3 text-xs text-slate-700">
        <p className="font-medium text-slate-900">Hinweis Planung vs. gespeicherter Auftrag</p>
        <p className="mt-1">
          Die Bereiche <strong>C–E und G</strong> zeigen eine <strong>Planungsvorschau</strong>: „Ist dieser{" "}
          <strong>geplante</strong> Schnitt aktuell materialseitig machbar?“ — gerechnet vom Backend mit
          kombinierter Verfuegbarkeit.
        </p>
        <p className="mt-1">
          Nach dem Speichern (<strong>F</strong>) erscheint der Auftrag unter „Auftraege“ mit einer{" "}
          <strong>Ampel zur Disposition</strong> (Reihenfolge am Material). Das ist eine{" "}
          <strong>andere fachliche Frage</strong> als die Vorschau hier und kann davon abweichen.
        </p>
      </div>
      <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">A) Material auswählen</h2>
        <div className="grid gap-2 sm:grid-cols-[1fr_auto] sm:items-end">
          <label className="grid gap-1">
            Artikelnummer
            <Input
              value={articleInput}
              onChange={(e) => onArticleInputChange(e.target.value)}
              placeholder="z. B. 100-FE-025"
            />
          </label>
          <Button
            type="button"
            className="w-full sm:w-auto"
            disabled={loadingMaterial}
            onClick={() => void loadMaterialForArticle(articleInput)}
          >
            {loadingMaterial ? "Laden..." : "Material laden"}
          </Button>
        </div>
        <p className="text-xs text-slate-500">Scan-Anbindung kann später ergänzt werden.</p>

        <SimulatorMaterialSearchPanel
          title="Materialsuche (Volltext + Filter, wie Simulator-Test)"
          onPickArticle={(articleNo) => {
            setArticleInput(articleNo);
            void loadMaterialForArticle(articleNo);
          }}
        />

        {loadError ? <p className="text-sm text-red-600">{loadError}</p> : null}

        {material ? (
          <div className="rounded border border-slate-100 bg-slate-50 p-2">
            <p>
              <span className="text-slate-600">Artikelnummer:</span> {material.article_number}
            </p>
            <p>
              <span className="text-slate-600">Beschreibung:</span> {material.name}
            </p>
          </div>
        ) : (
          <p className="text-slate-600">Noch kein Material geladen.</p>
        )}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">B) Auftragsparameter</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="grid gap-1">
            Stückzahl
            <Input
              type="number"
              min={1}
              step={1}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </label>
          <label className="grid gap-1">
            Länge pro Teil (mm)
            <Input
              type="number"
              min={0}
              step={1}
              value={partLengthMm}
              onChange={(e) => setPartLengthMm(e.target.value)}
            />
          </label>
        </div>
        <label className="grid gap-1">
          Trennmaschine
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={selectedSawId}
            onChange={(e) => setSelectedSawId(e.target.value)}
          >
            {SAW_OPTIONS.map((s) => (
              <option key={s.id || "none"} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        {selectedSaw.kerfMm !== null && selectedSaw.kerfMm !== undefined ? (
          <p className="text-slate-700">
            Kerf (mm): <span className="font-medium">{selectedSaw.kerfMm}</span> (aus Maschine)
          </p>
        ) : (
          <label className="grid gap-1">
            Kerf manuell (mm)
            <Input
              type="number"
              min={0}
              step={0.1}
              value={manualKerfMm}
              onChange={(e) => setManualKerfMm(e.target.value)}
            />
          </label>
        )}
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={considerRestPieces}
            onChange={(e) => setConsiderRestPieces(e.target.checked)}
          />
          Reststücke berücksichtigen (noch ohne Auswirkung)
        </label>
      </section>

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">C) Berechnung (Vorschau)</h2>
        <p className="text-xs text-slate-600">
          Nur fuer den <strong>aktuell geplanten</strong> Schnitt — noch kein gespeicherter App-Auftrag.
        </p>
        {previewLoading ? <p className="text-slate-600">Berechnung wird aktualisiert...</p> : null}
        {previewError ? <p className="text-sm text-red-600">{previewError}</p> : null}
        {preview ? (
          <ul className="grid gap-1 text-slate-700">
            <li>
              Nettobedarf: {preview.net_required_m} m ({preview.net_required_mm} mm)
            </li>
            <li>
              Verschnitt: {preview.kerf_total_m} m ({preview.kerf_total_mm} mm)
            </li>
            <li className="font-medium">
              Gesamtbedarf: {preview.gross_required_m} m ({preview.gross_required_mm} mm)
            </li>
          </ul>
        ) : (
          <p className="text-slate-600">
            {material ? "Parameter prüfen (Stückzahl ≥ 1, Länge ≥ 1 mm) für Backend-Vorschau." : "Zuerst Material laden."}
          </p>
        )}
        <p className="text-xs text-slate-500">
          Werte kommen aus dem Backend (Netto = Stück × Länge; Verschnitt = (Stück − 1) × Kerf).
        </p>
      </section>

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">D) Verfügbarkeit (Vorschau)</h2>
        <p className="text-xs text-slate-600">
          Zeigt Bestand/Pipeline/Verfuegbar fuer <strong>diese Planung</strong> (ein Plan, kombinierte Pipeline inkl.
          App-Bedarf).
        </p>
        {preview ? (
          <ul className="grid gap-1">
            <li>Bestand: {preview.stock_m} m</li>
            <li>In Pipeline: {preview.in_pipeline_m} m</li>
            <li>Verfügbar: {preview.available_m} m</li>
            <li className="font-medium">Gesamtbedarf (Plan): {preview.gross_required_m} m</li>
          </ul>
        ) : (
          <p className="text-slate-600">Vorschau erscheint nach gültigen Parametern.</p>
        )}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">E) Auftragsbelastung (Vorschau)</h2>
        <p className="text-xs text-slate-600">
          Offene Auftraege aus ERP-Simulator und App in der Pipeline-Ansicht — Kontext fuer Ihre Planung, nicht die
          Ampel des spaeter gespeicherten Auftrags.
        </p>
        {preview ? (
          <>
            <p className="text-slate-700">
              In Pipeline (Summe gebundener Bedarf):{" "}
              <span className="font-medium">{preview.in_pipeline_m} m</span>
            </p>
            <p className="text-xs text-slate-600">Offene zugehörige Aufträge (Backend):</p>
            {preview.open_orders.length === 0 ? (
              <p className="text-slate-600">Keine offenen Aufträge für dieses Material.</p>
            ) : (
              <ul className="grid gap-2">
                {preview.open_orders.map((o) => (
                  <li key={o.order_reference} className="rounded border border-slate-200 p-2">
                    <p>Auftragsnummer: {o.order_reference}</p>
                    <p>Benötigte Meter: {o.required_m}</p>
                    <p>Status: {o.status}</p>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <p className="text-slate-600">Vorschau laden.</p>
        )}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">F) Auftrag speichern (App-Datenbank)</h2>
        <p className="text-xs text-slate-600">
          Speichern legt einen App-Auftrag per Backend an (POST /orders). Sie erhalten eine{" "}
          <strong>App-Auftragsnummer</strong> (z. B. APP-000042). Workflow-Status initial: Entwurf (<code>draft</code>
          ). Reststueck-Checkbox wird als <code>include_rest_stock</code> mitgegeben; die <strong>Ampel</strong> fuer den
          gespeicherten Auftrag kommt aus der <strong>Dispositionslogik</strong> im Backend, nicht aus dieser Vorschau.
        </p>
        {saveFeedback ? (
          <p
            className={
              saveFeedback.kind === "success" ? "text-sm font-medium text-emerald-800" : "text-sm text-red-600"
            }
            role="status"
          >
            {saveFeedback.message}
          </p>
        ) : null}
        <Button
          type="button"
          className="w-full max-w-md sm:w-auto"
          disabled={!canSave}
          onClick={() => void handleSaveOrder()}
        >
          {saveLoading ? "Speichern..." : "Auftrag speichern"}
        </Button>
        {!preview && material ? (
          <p className="text-xs text-slate-500">Zuerst gueltige Vorschau abwarten (Berechnung C).</p>
        ) : null}
      </section>

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-amber-50/80 p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">G) Entscheidungshilfe (Vorschau)</h2>
        <p className="text-xs text-slate-700">
          Nur Aussage fuer <strong>diesen Plan</strong> (Machbarkeit nach Verfuegbarkeit), nicht fuer die spaetere
          Dispositions-Ampel nach Speichern.
        </p>
        {preview ? (
          preview.feasible ? (
            <p className="font-medium text-emerald-800">Geplanter Schnitt materialseitig machbar (Verfügbar ≥ Gesamtbedarf).</p>
          ) : (
            <p className="font-medium text-red-800">Nach dieser Vorschau nicht genügend Material (Verfügbar &lt; Gesamtbedarf).</p>
          )
        ) : (
          <p className="text-slate-600">Vorschau abwarten.</p>
        )}
      </section>
    </div>
  );
}
