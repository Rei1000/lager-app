"use client";

import { useEffect, useMemo, useState } from "react";

import { SimulatorMaterialFilterInputs } from "@/features/orders/simulator-material-filter-inputs";
import {
  matchesArticleNumberSimulatorFilters,
  type SimulatorSearchFilters,
} from "@/features/orders/simulator-material-search-constants";
import { fetchSimulatorOpenOrders } from "@/lib/api-client";
import type { SimulatorOpenOrderDto } from "@/lib/types";

function formatRequiredMeters(requiredM: number): string {
  return `${requiredM.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 3 })} m`;
}

export function OrdersOpenOverview() {
  const [rows, setRows] = useState<SimulatorOpenOrderDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [materialFilter, setMaterialFilter] = useState({
    textQuery: "",
    mainGroup: "",
    material: "",
    dimension: "",
  });
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setLoadError(null);
      try {
        const data = await fetchSimulatorOpenOrders();
        if (active) {
          setRows(data);
        }
      } catch (err) {
        if (active) {
          setLoadError(err instanceof Error ? err.message : "Unbekannter Fehler");
          setRows([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, []);

  const statusOptions = useMemo(() => {
    const unique = new Set(rows.map((r) => r.status));
    return [...unique].sort((a, b) => a.localeCompare(b, "de"));
  }, [rows]);

  const structuralFilters: SimulatorSearchFilters = useMemo(
    () => ({
      mainGroup: materialFilter.mainGroup,
      material: materialFilter.material,
      dimension: materialFilter.dimension,
    }),
    [materialFilter.mainGroup, materialFilter.material, materialFilter.dimension]
  );

  const visibleOrders = useMemo(() => {
    const q = materialFilter.textQuery.trim().toLowerCase();
    return [...rows]
      .filter((order) => (statusFilter ? order.status === statusFilter : true))
      .filter((order) => matchesArticleNumberSimulatorFilters(order.material_no, structuralFilters))
      .filter((order) => {
        if (!q) {
          return true;
        }
        const hay = [
          order.order_no,
          order.material_no,
          order.material_description,
          order.customer_name,
        ]
          .join(" ")
          .toLowerCase();
        return hay.includes(q);
      })
      .sort((a, b) => a.order_no.localeCompare(b.order_no, "de"));
  }, [rows, statusFilter, structuralFilters, materialFilter.textQuery]);

  return (
    <div className="grid gap-4">
      <div>
        <h2 className="text-lg font-medium">Offene Auftraege (Simulator Sage)</h2>
        <p className="text-xs text-slate-600">
          Datenquelle: ERP-Simulator — dieselben Auftraege wie unter Simulator-Test.
        </p>
      </div>

      {loadError ? <p className="text-sm text-red-600">Fehler: {loadError}</p> : null}
      {loading ? <p className="text-sm text-slate-600">Lade Auftraege...</p> : null}

      <div className="grid gap-3 rounded border border-slate-200 p-3">
        <p className="text-xs font-medium text-slate-600">Filter</p>
        <SimulatorMaterialFilterInputs
          values={materialFilter}
          onChange={setMaterialFilter}
          textQueryLabel="Volltext (Auftrag, Artikel, Bezeichnung, Kunde)"
          textQueryPlaceholder="Teilstring, filtert live"
        />
        <label className="grid max-w-md gap-1">
          Status
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Alle</option>
            {statusOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <ul className="grid gap-2">
        {!loading && !loadError && rows.length === 0 ? (
          <li className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            Keine Simulator-Auftraege geliefert.
          </li>
        ) : null}
        {!loading && rows.length > 0 && visibleOrders.length === 0 ? (
          <li className="rounded border border-dashed border-amber-200 bg-amber-50/50 p-3 text-sm text-amber-950">
            Keine Auftraege passen zu diesen Filtern.
          </li>
        ) : null}
        {visibleOrders.map((order) => (
          <li key={order.order_no} className="rounded border border-slate-200 p-3 text-sm sm:p-4">
            <div className="grid gap-1">
              <p className="font-medium">
                Auftrag: <span className="font-mono text-slate-900">{order.order_no}</span>
              </p>
              <p>
                Material: <span className="font-mono">{order.material_no}</span>
                {order.material_description ? (
                  <span className="text-slate-700"> — {order.material_description}</span>
                ) : null}
              </p>
              <p className="text-slate-700">
                Bedarf: {formatRequiredMeters(order.required_m)} · Status: {order.status}
                {order.priority ? (
                  <span className="text-slate-600"> · Prioritaet: {order.priority}</span>
                ) : null}
              </p>
              {order.customer_name ? (
                <p className="text-slate-600">Kunde: {order.customer_name}</p>
              ) : null}
              {order.due_date ? (
                <p className="text-slate-600">Faellig: {order.due_date}</p>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
