"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { TrafficLightIndicator } from "@/components/shared/traffic-light-indicator";
import { appOrderStatusLabelDe } from "@/features/orders/app-order-copy";
import { AppOrdersMaterialDndBlock } from "@/features/orders/app-orders-material-dnd-block";
import { OrderEditModal } from "@/features/orders/order-edit-modal";
import { SimulatorMaterialFilterInputs } from "@/features/orders/simulator-material-filter-inputs";
import {
  matchesArticleNumberSimulatorFilters,
  type SimulatorSearchFilters,
} from "@/features/orders/simulator-material-search-constants";
import { ApiClientError, fetchOrders, fetchSimulatorOpenOrders, reprioritizeOrders } from "@/lib/api-client";
import { useCoarsePointer } from "@/lib/use-coarse-pointer";
import { cn } from "@/lib/utils";
import type { OrderDto, SimulatorOpenOrderDto } from "@/lib/types";

function formatRequiredMeters(requiredM: number): string {
  return `${requiredM.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 3 })} m`;
}

function appOrderPrimaryLabel(order: OrderDto): string {
  return order.display_order_code?.trim() || order.order_id || "—";
}

/** Gleiche Sortierung wie Backend-Disposition: Material, dann priority_order. */
function sortAppOrdersForDisposition(orders: OrderDto[]): OrderDto[] {
  return [...orders].sort((a, b) => {
    const mat = a.material_article_number.localeCompare(b.material_article_number, "de");
    if (mat !== 0) {
      return mat;
    }
    return (a.priority_order ?? 1_000_000_000) - (b.priority_order ?? 1_000_000_000);
  });
}

function materialSequence(allAppOrders: OrderDto[], materialArticleNumber: string): OrderDto[] {
  return sortAppOrdersForDisposition(
    allAppOrders.filter((o) => o.material_article_number === materialArticleNumber && o.order_id)
  );
}

function canEditAppOrder(order: OrderDto): boolean {
  return order.status !== "done" && order.status !== "canceled";
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
  const [reprioritizeError, setReprioritizeError] = useState<string | null>(null);
  const [reprioritizeBusyMaterial, setReprioritizeBusyMaterial] = useState<string | null>(null);
  const [reloadAfterReprioritize, setReloadAfterReprioritize] = useState(0);
  const [editingOrder, setEditingOrder] = useState<OrderDto | null>(null);
  const coarsePointer = useCoarsePointer();

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
  }, [listRefreshToken, reloadAfterReprioritize]);

  /** Vereinigung der Status-Codes aus App und ERP-Sim (gleiche Filtersemantik: exakter String-Vergleich). */
  const combinedStatusOptions = useMemo(() => {
    const unique = new Set<string>();
    for (const r of appOrders) {
      unique.add(r.status);
    }
    for (const r of simulatorRows) {
      unique.add(r.status);
    }
    return [...unique].sort((a, b) => a.localeCompare(b, "de"));
  }, [appOrders, simulatorRows]);

  const structuralFilters: SimulatorSearchFilters = useMemo(
    () => ({
      mainGroup: materialFilter.mainGroup,
      material: materialFilter.material,
      dimension: materialFilter.dimension,
    }),
    [materialFilter.mainGroup, materialFilter.material, materialFilter.dimension]
  );

  const matchesListingFilters = useCallback(
    (order: OrderDto) => {
      if (statusFilter && order.status !== statusFilter) {
        return false;
      }
      if (!matchesArticleNumberSimulatorFilters(order.material_article_number.trim(), structuralFilters)) {
        return false;
      }
      const q = materialFilter.textQuery.trim().toLowerCase();
      if (!q) {
        return true;
      }
      const hay = [
        order.display_order_code ?? "",
        order.order_id ?? "",
        order.material_article_number,
        order.material_description ?? "",
        order.customer_name ?? "",
        order.due_date ?? "",
        order.status,
        String(order.total_demand_mm),
      ]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    },
    [statusFilter, structuralFilters, materialFilter.textQuery]
  );

  const materialBlocks = useMemo(() => {
    const materials = [...new Set(appOrders.map((o) => o.material_article_number))].sort((a, b) =>
      a.localeCompare(b, "de")
    );
    return materials
      .map((material) => {
        const sequence = materialSequence(appOrders, material);
        const show = sequence.some((o) => matchesListingFilters(o));
        return { material, sequence, show };
      })
      .filter((b) => b.show);
  }, [appOrders, matchesListingFilters]);

  const applyMaterialReorder = useCallback(async (materialArticleNumber: string, orderedIds: string[]) => {
    setReprioritizeError(null);
    setReprioritizeBusyMaterial(materialArticleNumber);
    try {
      await reprioritizeOrders({
        material_article_number: materialArticleNumber,
        ordered_ids: orderedIds,
      });
      setReloadAfterReprioritize((n) => n + 1);
    } catch (e) {
      const msg =
        e instanceof ApiClientError ? e.message : e instanceof Error ? e.message : "Reihung konnte nicht gespeichert werden";
      setReprioritizeError(msg);
    } finally {
      setReprioritizeBusyMaterial(null);
    }
  }, []);

  const visibleSimulatorOrders = useMemo(() => {
    const q = materialFilter.textQuery.trim().toLowerCase();
    return [...simulatorRows]
      .filter((order) => (statusFilter ? order.status === statusFilter : true))
      .filter((order) => matchesArticleNumberSimulatorFilters(order.material_no.trim(), structuralFilters))
      .filter((order) => {
        if (!q) {
          return true;
        }
        const hay = [
          order.order_no,
          order.material_no,
          order.material_description,
          order.customer_name,
          order.due_date ?? "",
          order.status,
          String(order.priority ?? ""),
        ]
          .join(" ")
          .toLowerCase();
        return hay.includes(q);
      })
      .sort((a, b) => a.order_no.localeCompare(b.order_no, "de"));
  }, [simulatorRows, statusFilter, structuralFilters, materialFilter.textQuery]);

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
        <p className="text-xs font-medium text-slate-600">
          Filter gelten fuer <strong>beide</strong> Listen: Volltext, Hauptgruppe/Material/Dimension (ueber
          Artikelnummer, Schema wie Simulator) und Status (exakter Code; App- und ERP-Sim-Status koennen sich
          unterscheiden).
        </p>
        <SimulatorMaterialFilterInputs
          values={materialFilter}
          onChange={setMaterialFilter}
          textQueryLabel="Volltext"
          textQueryPlaceholder="APP-Nummer, Artikel, Status ..."
        />
        <label className="grid max-w-md gap-1">
          Status (App und ERP-Simulator, gleicher Code-Vergleich)
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Alle Status</option>
            {combinedStatusOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <section className="grid gap-3" aria-labelledby="app-orders-heading">
        <h3 id="app-orders-heading" className="text-base font-semibold text-slate-900">
          Lager-App: App-Auftraege
        </h3>
        <p className="text-xs text-slate-600">
          Gespeicherte Dispositionsauftraege. Die <strong>Ampel</strong> beschreibt die Lage in der{" "}
          <strong>Reihenfolge / Disposition</strong> am Material (nicht dieselbe Frage wie die Planungsvorschau beim
          Entwurf). <strong>Nur App-Auftraege</strong> koennen pro Material per Drag &amp; Drop neu gereiht werden
          (vollstaendige Liste je Material wird gespeichert); ERP-Simulator-Auftraege haben eine eigene Liste und bleiben
          read-only.
        </p>
        {appError ? <p className="text-sm text-red-600">Fehler: {appError}</p> : null}
        {reprioritizeError ? (
          <p className="text-sm text-red-600" role="alert">
            Reihung: {reprioritizeError}
          </p>
        ) : null}
        {!loading && !appError && appOrders.length === 0 ? (
          <p className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            Keine App-Auftraege vorhanden.
          </p>
        ) : null}
        {!loading && appOrders.length > 0 && materialBlocks.length === 0 ? (
          <p className="rounded border border-dashed border-amber-200 bg-amber-50/50 p-3 text-sm text-amber-950">
            Keine App-Auftraege passen zu diesen Filtern.
          </p>
        ) : null}
        <div className="grid gap-6">
          {materialBlocks.map(({ material, sequence }) => (
            <div key={material} className="grid gap-2">
              <p className="text-xs font-medium text-slate-700">
                Material: <span className="font-mono">{material}</span>
                {sequence.length > 1 ? (
                  <span className="font-normal text-slate-600">
                    {" "}
                    — Reihenfolge per Drag &amp; Drop anpassen (nur dieses Material; vollstaendige Liste wird
                    gespeichert).
                  </span>
                ) : null}
              </p>
              {reprioritizeBusyMaterial === material ? (
                <p className="text-xs text-slate-600">Speichere neue Reihenfolge …</p>
              ) : null}
              <AppOrdersMaterialDndBlock
                materialArticleNumber={material}
                sequence={sequence}
                reorderDisabled={loading || reprioritizeBusyMaterial !== null || sequence.length < 2}
                isOrderDimmed={(o) => !matchesListingFilters(o)}
                onDragEndReorder={(ids) => applyMaterialReorder(material, ids)}
                renderCard={({ order, positionLabel }) => {
                  const canEdit = canEditAppOrder(order);
                  return (
                  <div className="relative">
                    {canEdit && order.order_id ? (
                      <button
                        type="button"
                        className="absolute right-0 top-0 z-10 rounded border border-emerald-200 bg-white/95 p-1.5 text-emerald-900 shadow-sm hover:bg-emerald-50"
                        aria-label="Auftrag bearbeiten"
                        title="Bearbeiten"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingOrder(order);
                        }}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          aria-hidden
                        >
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                        </svg>
                      </button>
                    ) : null}
                    <div
                      className={cn(canEdit && "pr-11")}
                      onClick={
                        canEdit && coarsePointer
                          ? () => {
                              setEditingOrder(order);
                            }
                          : undefined
                      }
                      onDoubleClick={
                        canEdit && !coarsePointer
                          ? () => {
                              setEditingOrder(order);
                            }
                          : undefined
                      }
                      role={canEdit ? "button" : undefined}
                      tabIndex={canEdit ? 0 : undefined}
                      onKeyDown={
                        canEdit
                          ? (e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                setEditingOrder(order);
                              }
                            }
                          : undefined
                      }
                    >
                  <>
                    <p className="font-semibold text-emerald-950">
                      <span className="rounded bg-emerald-700 px-1.5 py-0.5 text-xs font-semibold uppercase text-white">
                        App-Auftrag
                      </span>{" "}
                      <span className="text-lg font-semibold tracking-tight text-slate-900">
                        {appOrderPrimaryLabel(order)}
                      </span>
                    </p>
                    <p className="text-xs text-slate-700">
                      <span className="font-medium">App-Disposition (nur Lager-App, gleiches Material):</span> Position{" "}
                      <span className="font-mono">{positionLabel}</span> · Reihenfolge-Index{" "}
                      <span className="font-mono">{order.priority_order ?? "—"}</span> — die Ampel wird im Backend nach
                      dieser Reihenfolge fuer <span className="font-mono">{order.material_article_number}</span>{" "}
                      berechnet (ohne ERP-Einzelreihen).
                    </p>
                    {order.order_id ? (
                      <p className="text-xs text-slate-600">
                        Technische Speicherreferenz (API): <span className="font-mono">{order.order_id}</span>
                      </p>
                    ) : null}
                    <p>
                      Material: <span className="font-mono">{order.material_article_number}</span>
                      {order.material_description ? (
                        <span className="text-slate-700"> — {order.material_description}</span>
                      ) : null}
                    </p>
                    <p className="text-slate-700">
                      Menge: {order.quantity} × {order.part_length_mm} mm · Kerf {order.kerf_mm} mm · Bedarf:{" "}
                      {order.required_m.toLocaleString("de-DE", { maximumFractionDigits: 3 })} m (wie ERP-Sim{" "}
                      <code className="text-xs">required_m</code>)
                    </p>
                    <p className="text-slate-700">
                      <span className="font-medium">Workflow-Status (Lager-App):</span>{" "}
                      {appOrderStatusLabelDe(order.status)} <span className="text-slate-500">({order.status})</span>
                    </p>
                    <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-slate-700">
                      <span className="font-medium">Ampel (Disposition):</span>
                      <TrafficLightIndicator trafficLight={order.traffic_light} />
                    </p>
                    {order.disposition_available_before_m != null ? (
                      <p className="text-slate-700">
                        <span className="font-medium">Verfuegbar vor diesem App-Auftrag (Stueckgut, sequentiell):</span>{" "}
                        {order.disposition_available_before_m.toLocaleString("de-DE", {
                          maximumFractionDigits: 3,
                        })}{" "}
                        m
                        <span className="text-xs text-slate-500">
                          {" "}
                          — nur App-Reihenfolge; ERP-offene Auftraege sind als Pipeline aggregiert, keine gemischte
                          Gesamtwarteschlange.
                        </span>
                      </p>
                    ) : null}
                    {order.customer_name ? (
                      <p className="text-slate-600">Kunde (dispositiv): {order.customer_name}</p>
                    ) : null}
                    {order.due_date ? <p className="text-slate-600">Faellig (Wunsch): {order.due_date}</p> : null}
                    {order.erp_order_number ? (
                      <p className="text-xs text-slate-600">
                        ERP-Referenz: <span className="font-mono">{order.erp_order_number}</span>
                      </p>
                    ) : null}
                    <p className="text-xs text-slate-600">
                      Reihenfolge am Material (App, niedrig = frueher; Drag &amp; Drop aendert persistiert):{" "}
                      <span className="font-medium text-slate-800">{order.priority_order ?? "—"}</span>
                    </p>
                  </>
                    </div>
                  </div>
                  );
                }}
              />
            </div>
          ))}
        </div>
      </section>

      <OrderEditModal
        order={editingOrder}
        onClose={() => setEditingOrder(null)}
        onSaved={() => setReloadAfterReprioritize((n) => n + 1)}
      />

      <section className="grid gap-3" aria-labelledby="sim-orders-heading">
        <h3 id="sim-orders-heading" className="text-base font-semibold text-slate-900">
          ERP-Simulator: Demo-Auftraege (read-only)
        </h3>
        <p className="text-xs text-slate-600">
          Entspricht offenen ERP-Demo-Auftraegen (z. B. Sage-Simulator). Nicht mit App-<strong>APP-…</strong>-Nummern
          verwechseln. Diese Liste ist <strong>read-only</strong>; die Reihenfolge der ERP-Demo-Auftraege wird hier nicht
          geaendert und bildet <strong>keine</strong> gemeinsame Gesamt-Warteschlange mit den App-Auftraegen ab.
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
                  Bedarf: {formatRequiredMeters(order.required_m)} · Status (ERP-Demo): {order.status}
                  {order.priority ? (
                    <span className="text-slate-600"> · Prioritaet (ERP-Demo-Code): {order.priority}</span>
                  ) : null}
                </p>
                {order.customer_name ? (
                  <p className="text-slate-600">Kunde (ERP-Demo): {order.customer_name}</p>
                ) : null}
                {order.due_date ? (
                  <p className="text-slate-600">Faellig (ERP-Demo): {order.due_date}</p>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
