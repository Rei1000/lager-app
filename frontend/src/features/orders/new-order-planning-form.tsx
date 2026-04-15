"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiClientError, getMaterialByArticleNumber, previewOrderPlan, searchSimulatorMaterials } from "@/lib/api-client";
import type { MaterialLookupDto, OrderPlanPreviewDto, SimulatorMaterialSearchDto } from "@/lib/types";

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

export function NewOrderPlanningForm() {
  const [articleInput, setArticleInput] = useState("");
  const [material, setMaterial] = useState<MaterialLookupDto | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingMaterial, setLoadingMaterial] = useState(false);

  const [preview, setPreview] = useState<OrderPlanPreviewDto | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SimulatorMaterialSearchDto[]>([]);
  const [searchMessage, setSearchMessage] = useState<string | null>(null);

  const [quantity, setQuantity] = useState("1");
  const [partLengthMm, setPartLengthMm] = useState("1000");
  const [selectedSawId, setSelectedSawId] = useState("");
  const [manualKerfMm, setManualKerfMm] = useState("2");
  const [considerRestPieces, setConsiderRestPieces] = useState(false);

  const loadGen = useRef(0);
  const previewGen = useRef(0);

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

  async function onSearchSimulator(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const q = searchQuery.trim();
    if (!q) {
      setSearchMessage("Suchbegriff eingeben");
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    setSearchMessage(null);
    setSearchResults([]);
    try {
      const rows = await searchSimulatorMaterials(q);
      setSearchResults(rows);
      setSearchMessage(rows.length ? `${rows.length} Treffer` : "Keine Treffer");
    } catch {
      setSearchMessage("Suche fehlgeschlagen");
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <div className="grid gap-6 text-sm text-slate-800">
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

        <form className="grid gap-2 rounded border border-dashed border-slate-200 p-2" onSubmit={onSearchSimulator}>
          <p className="text-xs font-medium text-slate-600">Optional: Simulator-Suche</p>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
            <label className="grid min-w-0 flex-1 gap-1">
              Suchbegriff
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Nummer oder Text"
              />
            </label>
            <Button type="submit" className="w-full sm:w-auto" disabled={searchLoading}>
              {searchLoading ? "..." : "Suchen"}
            </Button>
          </div>
          {searchMessage ? <p className="text-xs text-slate-600">{searchMessage}</p> : null}
          {searchResults.length > 0 ? (
            <ul className="max-h-40 overflow-y-auto border border-slate-100">
              {searchResults.map((row) => (
                <li key={row.material_no} className="border-b border-slate-100 last:border-0">
                  <button
                    type="button"
                    className="w-full px-2 py-1.5 text-left text-xs hover:bg-slate-50"
                    onClick={() => {
                      setArticleInput(row.material_no);
                      void loadMaterialForArticle(row.material_no);
                    }}
                  >
                    <span className="font-medium">{row.material_no}</span>
                    <span className="text-slate-600"> — {row.description}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </form>

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
        <h2 className="text-base font-semibold text-slate-900">C) Berechnung</h2>
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
        <h2 className="text-base font-semibold text-slate-900">D) Verfügbarkeit</h2>
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
        <h2 className="text-base font-semibold text-slate-900">E) Auftragsbelastung</h2>
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

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-amber-50/80 p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">F) Entscheidungshilfe</h2>
        {preview ? (
          preview.feasible ? (
            <p className="font-medium text-emerald-800">Auftrag möglich (Verfügbar ≥ Gesamtbedarf).</p>
          ) : (
            <p className="font-medium text-red-800">Nicht genügend Material (Verfügbar &lt; Gesamtbedarf).</p>
          )
        ) : (
          <p className="text-slate-600">Vorschau abwarten.</p>
        )}
      </section>
    </div>
  );
}
