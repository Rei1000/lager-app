"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { SimulatorMaterialFilterInputs } from "@/features/orders/simulator-material-filter-inputs";
import { matchesSimulatorMaterialFilters } from "@/features/orders/simulator-material-search-constants";
import { fetchSimulatorMaterialStock, searchSimulatorMaterials } from "@/lib/api-client";
import type { SimulatorMaterialSearchDto } from "@/lib/types";

export type SimulatorMaterialSearchHit = {
  article_number: string;
  description: string;
  stock_m: number | null;
};

type SimulatorMaterialSearchPanelProps = {
  /** Wird aufgerufen, wenn der Nutzer einen Treffer auswählt (Artikelnummer). */
  onPickArticle: (articleNumber: string) => void;
  /** Optional: Überschrift anpassen */
  title?: string;
};

export function SimulatorMaterialSearchPanel({
  onPickArticle,
  title = "Materialsuche (Simulator)",
}: SimulatorMaterialSearchPanelProps) {
  const [filters, setFilters] = useState({
    textQuery: "",
    mainGroup: "",
    material: "",
    dimension: "",
  });
  const [searchLoading, setSearchLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<SimulatorMaterialSearchHit[]>([]);
  const [searchStatusText, setSearchStatusText] = useState<string | null>(null);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setHasSearched(true);
    setSearchLoading(true);
    setSearchError(null);
    setSearchStatusText(null);
    setSearchResults([]);

    const filterPayload = {
      mainGroup: filters.mainGroup,
      material: filters.material,
      dimension: filters.dimension,
    };

    try {
      const rawResults = await searchSimulatorMaterials(filters.textQuery.trim());
      const filteredResults = rawResults.filter((item) =>
        matchesSimulatorMaterialFilters(item, filterPayload)
      );

      if (filteredResults.length === 0) {
        setSearchStatusText("Keine Treffer");
        return;
      }

      const rows = await Promise.all(
        filteredResults.map(async (item: SimulatorMaterialSearchDto) => {
          try {
            const stockPayload = await fetchSimulatorMaterialStock(item.material_no);
            return {
              article_number: item.material_no,
              description: item.description,
              stock_m: stockPayload.stock_m,
            };
          } catch {
            return {
              article_number: item.material_no,
              description: item.description,
              stock_m: null,
            };
          }
        })
      );
      setSearchResults(rows);
      setSearchStatusText(`${rows.length} Treffer`);
    } catch {
      setSearchError("Fehler beim Laden");
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <div className="grid gap-2 rounded border border-dashed border-slate-200 p-2">
      <p className="text-xs font-medium text-slate-600">{title}</p>
      <form className="grid gap-2" onSubmit={handleSearch}>
        <SimulatorMaterialFilterInputs
          values={filters}
          onChange={setFilters}
        />
        <Button className="w-full sm:w-auto" type="submit" disabled={searchLoading}>
          {searchLoading ? "Suche..." : "Suche ausfuehren"}
        </Button>
      </form>
      {searchError ? <p className="text-xs text-red-600">{searchError}</p> : null}
      {hasSearched && searchStatusText ? <p className="text-xs text-slate-600">{searchStatusText}</p> : null}
      {searchResults.length > 0 ? (
        <ul className="max-h-48 overflow-y-auto border border-slate-100">
          {searchResults.map((row) => (
            <li key={row.article_number} className="border-b border-slate-100 last:border-0">
              <button
                type="button"
                className="w-full px-2 py-1.5 text-left text-xs hover:bg-slate-50"
                onClick={() => onPickArticle(row.article_number)}
              >
                <span className="font-medium">{row.article_number}</span>
                <span className="text-slate-600"> — {row.description}</span>
                {row.stock_m != null ? (
                  <span className="block text-slate-500">Lager (Simulator): {row.stock_m} m</span>
                ) : null}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
