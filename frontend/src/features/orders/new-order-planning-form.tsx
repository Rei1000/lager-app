"use client";

import { FormEvent, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  ApiClientError,
  fetchSimulatorMaterialAvailability,
  getMaterialByArticleNumber,
  searchSimulatorMaterials,
} from "@/lib/api-client";
import type { MaterialLookupDto, SimulatorMaterialAvailabilityDto, SimulatorMaterialSearchDto } from "@/lib/types";

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

function roundMeters(value: number): number {
  return Math.round(value * 1000) / 1000;
}

export function NewOrderPlanningForm() {
  const [articleInput, setArticleInput] = useState("");
  const [material, setMaterial] = useState<MaterialLookupDto | null>(null);
  const [availability, setAvailability] = useState<SimulatorMaterialAvailabilityDto | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingMaterial, setLoadingMaterial] = useState(false);

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

  const selectedSaw = useMemo(
    () => SAW_OPTIONS.find((s) => s.id === selectedSawId) ?? SAW_OPTIONS[0],
    [selectedSawId]
  );
  const effectiveKerfMm =
    selectedSaw.kerfMm !== null && selectedSaw.kerfMm !== undefined
      ? selectedSaw.kerfMm
      : Math.max(0, Number(manualKerfMm.replace(",", ".")) || 0);

  const qtyNum = Math.max(0, Math.floor(Number(quantity.replace(",", ".")) || 0));
  const partLenMm = Math.max(0, Number(partLengthMm.replace(",", ".")) || 0);

  const { nettoMm, verschnittMm, gesamtMm, gesamtM } = useMemo(() => {
    if (qtyNum < 1) {
      return { nettoMm: 0, verschnittMm: 0, gesamtMm: 0, gesamtM: 0 };
    }
    const net = qtyNum * partLenMm;
    const waste = (qtyNum - 1) * effectiveKerfMm;
    const totalMm = net + waste;
    return {
      nettoMm: net,
      verschnittMm: waste,
      gesamtMm: totalMm,
      gesamtM: roundMeters(totalMm / 1000),
    };
  }, [qtyNum, partLenMm, effectiveKerfMm]);

  const decision =
    availability !== null && qtyNum >= 1
      ? gesamtM <= availability.available_m + 1e-9
        ? "possible"
        : "short"
      : "unknown";

  async function loadMaterialForArticle(articleNumber: string) {
    const normalized = articleNumber.trim();
    if (!normalized) {
      setLoadError("Bitte Artikelnummer eingeben");
      setMaterial(null);
      setAvailability(null);
      return;
    }

    const gen = ++loadGen.current;
    setLoadingMaterial(true);
    setLoadError(null);
    setMaterial(null);
    setAvailability(null);

    try {
      const mat = await getMaterialByArticleNumber(normalized);
      if (gen !== loadGen.current) {
        return;
      }
      const canonical = mat.article_number.trim();
      const avail = await fetchSimulatorMaterialAvailability(canonical);
      if (gen !== loadGen.current) {
        return;
      }
      setMaterial(mat);
      setAvailability(avail);
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
      setAvailability(null);
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
        <ul className="grid gap-1 text-slate-700">
          <li>
            Nettobedarf: {roundMeters(nettoMm / 1000)} m ({nettoMm.toFixed(1)} mm)
          </li>
          <li>
            Verschnitt: {roundMeters(verschnittMm / 1000)} m ({verschnittMm.toFixed(1)} mm)
          </li>
          <li className="font-medium">
            Gesamtbedarf: {gesamtM} m ({gesamtMm.toFixed(1)} mm)
          </li>
        </ul>
        <p className="text-xs text-slate-500">
          Formeln: Netto = Stück × Länge; Verschnitt = (Stück − 1) × Kerf; Gesamt = Netto + Verschnitt.
        </p>
      </section>

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">D) Verfügbarkeit</h2>
        {availability ? (
          <ul className="grid gap-1">
            <li>Bestand: {availability.stock_m} m</li>
            <li>In Pipeline: {availability.in_pipeline_m} m</li>
            <li>Verfügbar: {availability.available_m} m</li>
            <li className="font-medium">Gesamtbedarf (Plan): {gesamtM} m</li>
          </ul>
        ) : (
          <p className="text-slate-600">Material laden, um Verfügbarkeit zu sehen.</p>
        )}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">E) Auftragsbelastung</h2>
        {availability ? (
          <>
            <p className="text-slate-700">
              In Pipeline (Summe gebundener Bedarf):{" "}
              <span className="font-medium">{availability.in_pipeline_m} m</span>
            </p>
            <p className="text-xs text-slate-600">Offene zugehörige Aufträge (aus Verfügbarkeits-API):</p>
            {availability.open_orders.length === 0 ? (
              <p className="text-slate-600">Keine offenen Aufträge für dieses Material.</p>
            ) : (
              <ul className="grid gap-2">
                {availability.open_orders.map((o) => (
                  <li key={o.order_no} className="rounded border border-slate-200 p-2">
                    <p>Auftragsnummer: {o.order_no}</p>
                    <p>Benötigte Meter: {o.required_m}</p>
                    <p>Status: {o.status}</p>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <p className="text-slate-600">Material laden für Auftragsliste.</p>
        )}
      </section>

      <section className="grid gap-2 rounded-lg border border-slate-200 bg-amber-50/80 p-3 sm:p-4">
        <h2 className="text-base font-semibold text-slate-900">F) Entscheidungshilfe</h2>
        {availability && qtyNum >= 1 ? (
          decision === "possible" ? (
            <p className="font-medium text-emerald-800">Auftrag möglich (Verfügbar ≥ Gesamtbedarf).</p>
          ) : (
            <p className="font-medium text-red-800">Nicht genügend Material (Verfügbar &lt; Gesamtbedarf).</p>
          )
        ) : (
          <p className="text-slate-600">Material laden und Stückzahl ≥ 1 eingeben.</p>
        )}
      </section>
    </div>
  );
}
