"use client";

import { useEffect, useMemo, useState } from "react";

import {
  appOrderStatusLabelDe,
  trafficLightLabelDe,
} from "@/features/orders/app-order-copy";
import { SimulatorMaterialFilterInputs } from "@/features/orders/simulator-material-filter-inputs";
import {
  matchesArticleNumberSimulatorFilters,
  type SimulatorSearchFilters,
} from "@/features/orders/simulator-material-search-constants";
import { fetchOrders, fetchSimulatorOpenOrders } from "@/lib/api-client";
import type { OrderDto, SimulatorOpenOrderDto } from "@/lib/types";

function formatRequiredMeters(requiredM: number): string {
  return `${requiredM.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 3 })} m`;
}

function appOrderPrimaryLabel(order: OrderDto): string {
  return order.display_order_code?.trim() || order.order_id || "—";
}

type OrdersOpenOverviewProps = {
  /** Erhoehen, um App- und Simulator-Listen neu zu laden (z. B. nach neuem App-Auftrag). */
  listRefreshToken?: number;
};

export function OrdersOpenOverview({ listRefreshToken = 0 }: OrdersOpenOverviewProps) {
  const [appOrders, setAppOrders] = useState<OrderDto[]>([]);
  const [simulatorRows, setSimulatorRows] = useState<SimulatorOpenOrderDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [appError, setAppError] = useState<string | null>(null);
  const [simulatorError, setSimulatorError] = useState<string | null>(null);

  const [materialFilter, setMaterialFilter] = useState({
    textQuery: "",
    mainGroup: "",
    material: "",
    dimension: "",
  });
  const [simulatorStatusFilter, setSimulatorStatusFilter] = useState("");
  const [appStatusFilter, setAppStatusFilter] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setAppError(null);
      setSimulatorError(null);
      const [appResult, simResult] = await Promise.allSettled([fetchOrders(), fetchSimulatorOpenOrders()]);
      if (!active) {
        return;
      }
      if (appResult.status === "fulfilled") {
        setAppOrders(appResult.value);
      } else {
        setAppOrders([]);
        setAppError(
          appResult.reason instanceof Error ? appResult.reason.message : "App-Auftraege konnten nicht geladen werden"
        );
      }
      if (simResult.status === "fulfilled") {
        setSimulatorRows(simResult.value);
      } else {
        setSimulatorRows([]);
        setSimulatorError(
          simResult.reason instanceof Error
            ? simResult.reason.message
            : "Simulator-Auftraege konnten nicht geladen werden"
        );
      }
      setLoading(false);
    }
    void load();
    return () => {
      active = false;
    };
  }, [listRefreshToken]);

  const simulatorStatusOptions = useMemo(() => {
    const unique = new Set(simulatorRows.map((r) => r.status));
    return [...unique].sort((a, b) => a.localeCompare(b, "de"));
  }, [simulatorRows]);

  const appStatusOptions = useMemo(() => {
    const unique = new Set(appOrders.map((r) => r.status));
    return [...unique].sort((a, b) => a.localeCompare(b, "de"));
  }, [appOrders]);

  const structuralFilters: SimulatorSearchFilters = useMemo(
    () => ({
      mainGroup: materialFilter.mainGroup,
      material: materialFilter.material,
      dimension: materialFilter.dimension,
    }),
    [materialFilter.mainGroup, materialFilter.material, materialFilter.dimension]
  );

  const visibleAppOrders = useMemo(() => {
    const q = materialFilter.textQuery.trim().toLowerCase();
    return [...appOrders]
      .filter((order) => (appStatusFilter ? order.status === appStatusFilter : true))
      .filter((order) => {
        if (!q) {
          return true;
        }
        const hay = [
          order.display_order_code ?? "",
          order.order_id ?? "",
          order.material_article_number,
          order.status,
          String(order.total_demand_mm),
        ]
          .join(" ")
          .toLowerCase();
        return hay.includes(q);
      })
      .sort((a, b) => appOrderPrimaryLabel(a).localeCompare(appOrderPrimaryLabel(b), "de"));
  }, [appOrders, appStatusFilter, materialFilter.textQuery]);

  const visibleSimulatorOrders = useMemo(() => {
    const q = materialFilter.textQuery.trim().toLowerCase();
    return [...simulatorRows]
      .filter((order) => (simulatorStatusFilter ? order.status === simulatorStatusFilter : true))
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
  }, [simulatorRows, simulatorStatusFilter, structuralFilters, materialFilter.textQuery]);

  return (
    <div className="grid gap-6">
      <div>
        <h2 className="text-lg font-medium">Auftragsuebersicht</h2>
        <p className="text-xs text-slate-600">
          Zwei getrennte Quellen: <strong>App-Auftraege</strong> (Lager-App, editierbar im Workflow) und{" "}
          <strong>ERP-Simulator-Auftraege</strong> (Demo-Daten, nur Lesen). Nummern und Status sind nicht
          dieselben wie im ERP-Produktivsystem.
        </p>
      </div>

      {loading ? <p className="text-sm text-slate-600">Lade Daten...</p> : null}

      <div className="grid gap-3 rounded border border-slate-200 p-3">
        <p className="text-xs font-medium text-slate-600">Filter (Volltext gilt fuer App- und Simulator-Auftraege)</p>
        <SimulatorMaterialFilterInputs
          values={materialFilter}
          onChange={setMaterialFilter}
          textQueryLabel="Volltext"
          textQueryPlaceholder="APP-Nummer, Artikel, Status ..."
        />
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="grid max-w-md gap-1">
            Status App-Auftraege (Domain-Code)
            <select
              className="h-10 rounded-md border border-slate-300 px-3 text-sm"
              value={appStatusFilter}
              onChange={(e) => setAppStatusFilter(e.target.value)}
            >
              <option value="">Alle</option>
              {appStatusOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="grid max-w-md gap-1">
            Status Simulator-Auftraege
            <select
              className="h-10 rounded-md border border-slate-300 px-3 text-sm"
              value={simulatorStatusFilter}
              onChange={(e) => setSimulatorStatusFilter(e.target.value)}
            >
              <option value="">Alle</option>
              {simulatorStatusOptions.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <section className="grid gap-3" aria-labelledby="app-orders-heading">
        <h3 id="app-orders-heading" className="text-base font-semibold text-slate-900">
          Lager-App: App-Auftraege
        </h3>
        <p className="text-xs text-slate-600">
          Gespeicherte Dispositionsauftraege. Die <strong>Ampel</strong> beschreibt die Lage in der{" "}
          <strong>Reihenfolge / Disposition</strong> am Material (nicht dieselbe Frage wie die Planungsvorschau beim
          Entwurf).
        </p>
        {appError ? <p className="text-sm text-red-600">Fehler: {appError}</p> : null}
        {!loading && !appError && appOrders.length === 0 ? (
          <p className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            Keine App-Auftraege vorhanden.
          </p>
        ) : null}
        {!loading && appOrders.length > 0 && visibleAppOrders.length === 0 ? (
          <p className="rounded border border-dashed border-amber-200 bg-amber-50/50 p-3 text-sm text-amber-950">
            Keine App-Auftraege passen zu diesen Filtern.
          </p>
        ) : null}
        <ul className="grid gap-2">
          {visibleAppOrders.map((order) => (
            <li
              key={order.order_id ?? `${order.material_article_number}-${order.priority_order}`}
              className="rounded border border-emerald-200 bg-emerald-50/40 p-3 text-sm sm:p-4"
            >
              <p className="font-semibold text-emerald-950">
                <span className="rounded bg-emerald-700 px-1.5 py-0.5 text-xs font-semibold uppercase text-white">
                  App-Auftrag
                </span>{" "}
                <span className="text-lg font-semibold tracking-tight text-slate-900">
                  {appOrderPrimaryLabel(order)}
                </span>
              </p>
              {order.order_id ? (
                <p className="text-xs text-slate-600">
                  Technische Speicherreferenz (API): <span className="font-mono">{order.order_id}</span>
                </p>
              ) : null}
              <p>
                Material: <span className="font-mono">{order.material_article_number}</span>
              </p>
              <p className="text-slate-700">
                Menge: {order.quantity} × {order.part_length_mm} mm · Kerf {order.kerf_mm} mm · Bedarf gesamt:{" "}
                {(order.total_demand_mm / 1000).toLocaleString("de-DE", { maximumFractionDigits: 3 })} m
              </p>
              <p className="text-slate-700">
                <span className="font-medium">Workflow-Status:</span> {appOrderStatusLabelDe(order.status)}{" "}
                <span className="text-slate-500">({order.status})</span>
              </p>
              <p className="text-slate-700">
                <span className="font-medium">Ampel (Disposition):</span> {trafficLightLabelDe(order.traffic_light)}
                {order.traffic_light ? <span className="text-slate-500"> ({order.traffic_light})</span> : null}
              </p>
              <p className="text-xs text-slate-600">
                Reihenfolge am Material (automatisch vergeben, niedrig = frueher):{" "}
                <span className="font-medium text-slate-800">{order.priority_order ?? "—"}</span>
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section className="grid gap-3" aria-labelledby="sim-orders-heading">
        <h3 id="sim-orders-heading" className="text-base font-semibold text-slate-900">
          ERP-Simulator: Demo-Auftraege (read-only)
        </h3>
        <p className="text-xs text-slate-600">
          Entspricht offenen ERP-Demo-Auftraegen (z. B. Sage-Simulator). Nicht mit App-<strong>APP-…</strong>-Nummern
          verwechseln.
        </p>
        {simulatorError ? <p className="text-sm text-red-600">Fehler: {simulatorError}</p> : null}
        {!loading && !simulatorError && simulatorRows.length === 0 ? (
          <p className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            Keine Simulator-Auftraege geliefert.
          </p>
        ) : null}
        {!loading && simulatorRows.length > 0 && visibleSimulatorOrders.length === 0 ? (
          <p className="rounded border border-dashed border-amber-200 bg-amber-50/50 p-3 text-sm text-amber-950">
            Keine Simulator-Auftraege passen zu diesen Filtern.
          </p>
        ) : null}
        <ul className="grid gap-2">
          {visibleSimulatorOrders.map((order) => (
            <li key={order.order_no} className="rounded border border-slate-200 bg-white p-3 text-sm sm:p-4">
              <div className="grid gap-1">
                <p className="font-medium">
                  <span className="rounded bg-slate-600 px-1.5 py-0.5 text-xs font-semibold uppercase text-white">
                    ERP-Sim
                  </span>{" "}
                  Auftragsnr.: <span className="font-mono text-slate-900">{order.order_no}</span>
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
                    <span className="text-slate-600"> · Prioritaet (Demo): {order.priority}</span>
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
      </section>
    </div>
  );
}
