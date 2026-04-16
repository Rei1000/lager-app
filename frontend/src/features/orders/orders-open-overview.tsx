"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { AppOrderListingCard } from "@/features/orders/app-order-listing-card";
import {
  AppOrdersMaterialDndBlock,
  type AppOrderRenderContext,
} from "@/features/orders/app-orders-material-dnd-block";
import { MobileMaterialReorderSheet } from "@/features/orders/mobile-material-reorder-sheet";
import { OrderEditModal } from "@/features/orders/order-edit-modal";
import { SimulatorMaterialFilterInputs } from "@/features/orders/simulator-material-filter-inputs";
import {
  matchesArticleNumberSimulatorFilters,
  type SimulatorSearchFilters,
} from "@/features/orders/simulator-material-search-constants";
import { ApiClientError, fetchOrders, fetchSimulatorOpenOrders, reprioritizeOrders } from "@/lib/api-client";
import { useNarrowViewport } from "@/lib/use-narrow-viewport";
import type { OrderDto, SimulatorOpenOrderDto } from "@/lib/types";

function formatRequiredMeters(requiredM: number): string {
  return `${requiredM.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 3 })} m`;
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

const TRAFFIC_LIGHT_QUERY_VALUES = ["red", "yellow", "green"] as const;
type TrafficLightQueryValue = (typeof TRAFFIC_LIGHT_QUERY_VALUES)[number];

function parseTrafficLightQuery(value: string | null): TrafficLightQueryValue | "" {
  if (!value) {
    return "";
  }
  const v = value.trim().toLowerCase();
  return TRAFFIC_LIGHT_QUERY_VALUES.includes(v as TrafficLightQueryValue) ? (v as TrafficLightQueryValue) : "";
}

/** Select-Wert fuer Auftraege ohne customer_name (intern, Kollision mit echten Namen praktisch ausgeschlossen). */
const CUSTOMER_FILTER_NONE = "__ohne_kunde__";

function matchesCustomerFilter(
  customerFilter: string,
  customerName: string | null | undefined
): boolean {
  if (!customerFilter) {
    return true;
  }
  const name = customerName?.trim() ?? "";
  if (customerFilter === CUSTOMER_FILTER_NONE) {
    return name === "";
  }
  return name === customerFilter;
}

/** Select-Werte Fälligkeit (intern). */
const DUE_DATE_FILTER_OVERDUE = "overdue";
const DUE_DATE_FILTER_TODAY = "today";
const DUE_DATE_FILTER_THIS_WEEK = "this_week";
const DUE_DATE_FILTER_NONE = "none";

type DueDateFilterValue =
  | ""
  | typeof DUE_DATE_FILTER_OVERDUE
  | typeof DUE_DATE_FILTER_TODAY
  | typeof DUE_DATE_FILTER_THIS_WEEK
  | typeof DUE_DATE_FILTER_NONE;

/** ISO-Datum YYYY-MM-DD aus lokalem Datum (Vergleich mit Backend due_date). */
function toLocalYmd(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Montag der Kalenderwoche in lokaler Zeit (Mo–So), ISO-üblich. */
function startOfWeekMondayLocal(ref: Date): Date {
  const d = new Date(ref.getFullYear(), ref.getMonth(), ref.getDate());
  const dow = d.getDay();
  const deltaToMonday = dow === 0 ? -6 : 1 - dow;
  d.setDate(d.getDate() + deltaToMonday);
  return d;
}

/**
 * due_date aus Order (YYYY-MM-DD). Ungültige/leere Werte → null.
 * „Diese Woche“: due liegt zwischen Montag und Sonntag der aktuellen Kalenderwoche (lokal, Grenzen inklusive),
 * Vergleich als ISO-Datum-Strings.
 */
function parseDueYmd(value: string | null | undefined): string | null {
  const t = value?.trim() ?? "";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(t)) {
    return null;
  }
  return t;
}

function matchesDueDateFilter(
  dueDateRaw: string | null | undefined,
  filter: DueDateFilterValue,
  cal: { todayYmd: string; weekStartYmd: string; weekEndYmd: string }
): boolean {
  if (!filter) {
    return true;
  }
  const due = parseDueYmd(dueDateRaw);
  if (!due) {
    return filter === DUE_DATE_FILTER_NONE;
  }
  if (filter === DUE_DATE_FILTER_NONE) {
    return false;
  }
  if (filter === DUE_DATE_FILTER_OVERDUE) {
    return due < cal.todayYmd;
  }
  if (filter === DUE_DATE_FILTER_TODAY) {
    return due === cal.todayYmd;
  }
  if (filter === DUE_DATE_FILTER_THIS_WEEK) {
    return due >= cal.weekStartYmd && due <= cal.weekEndYmd;
  }
  return true;
}

type OrdersOpenOverviewProps = {
  /** Erhoehen, um App- und Simulator-Listen neu zu laden (z. B. nach neuem App-Auftrag). */
  listRefreshToken?: number;
};

export function OrdersOpenOverview({ listRefreshToken = 0 }: OrdersOpenOverviewProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [appOrders, setAppOrders] = useState<OrderDto[]>([]);
  const [simulatorRows, setSimulatorRows] = useState<SimulatorOpenOrderDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [appError, setAppError] = useState<string | null>(null);
  const [simulatorError, setSimulatorError] = useState<string | null>(null);
  const [reprioritizeError, setReprioritizeError] = useState<string | null>(null);
  const [reprioritizeBusyMaterial, setReprioritizeBusyMaterial] = useState<string | null>(null);
  const [reloadAfterReprioritize, setReloadAfterReprioritize] = useState(0);
  const [editingOrder, setEditingOrder] = useState<OrderDto | null>(null);
  const [draggingMaterialKey, setDraggingMaterialKey] = useState<string | null>(null);
  const [mobileReorderMaterial, setMobileReorderMaterial] = useState<string | null>(null);
  const narrowViewport = useNarrowViewport();

  const [materialFilter, setMaterialFilter] = useState({
    textQuery: "",
    mainGroup: "",
    material: "",
    dimension: "",
  });
  const [statusFilter, setStatusFilter] = useState("");
  const [customerFilter, setCustomerFilter] = useState("");
  const [dueDateFilter, setDueDateFilter] = useState<DueDateFilterValue>("");

  /** Direkt aus der URL abgeleitet (queryString als Abhaengigkeit: zuverlaessig bei Client-Navigation). */
  const queryString = searchParams.toString();
  const trafficLightFilter = useMemo(() => {
    const params = new URLSearchParams(queryString);
    return parseTrafficLightQuery(params.get("traffic_light"));
  }, [queryString]);

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

  useEffect(() => {
    if (!narrowViewport) {
      setMobileReorderMaterial(null);
    }
  }, [narrowViewport]);

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

  /** Eindeutige Kundennamen aus geladenen Listen (kein Backend); optional „Ohne Kunde“. */
  const customerSelectOptions = useMemo(() => {
    const names = new Set<string>();
    let hasEmpty = false;
    for (const o of appOrders) {
      const n = o.customer_name?.trim() ?? "";
      if (n) {
        names.add(n);
      } else {
        hasEmpty = true;
      }
    }
    for (const o of simulatorRows) {
      const n = o.customer_name?.trim() ?? "";
      if (n) {
        names.add(n);
      } else {
        hasEmpty = true;
      }
    }
    return {
      sortedNames: [...names].sort((a, b) => a.localeCompare(b, "de")),
      includeOhneKunde: hasEmpty,
    };
  }, [appOrders, simulatorRows]);

  const structuralFilters: SimulatorSearchFilters = useMemo(
    () => ({
      mainGroup: materialFilter.mainGroup,
      material: materialFilter.material,
      dimension: materialFilter.dimension,
    }),
    [materialFilter.mainGroup, materialFilter.material, materialFilter.dimension]
  );

  /** Tages-/Wochengrenzen für Fälligkeitsfilter (neu bei Datenreload oder Filterwechsel). */
  const dueCalendarSnapshot = useMemo(() => {
    const now = new Date();
    const todayYmd = toLocalYmd(now);
    const mon = startOfWeekMondayLocal(now);
    const weekStartYmd = toLocalYmd(mon);
    const sun = new Date(mon.getFullYear(), mon.getMonth(), mon.getDate() + 6);
    const weekEndYmd = toLocalYmd(sun);
    return { todayYmd, weekStartYmd, weekEndYmd };
  }, [listRefreshToken, reloadAfterReprioritize, dueDateFilter]);

  const matchesListingFilters = useCallback(
    (order: OrderDto) => {
      if (statusFilter && order.status !== statusFilter) {
        return false;
      }
      if (trafficLightFilter) {
        const tl = order.traffic_light?.trim().toLowerCase() ?? "";
        if (tl !== trafficLightFilter) {
          return false;
        }
      }
      if (!matchesCustomerFilter(customerFilter, order.customer_name)) {
        return false;
      }
      if (!matchesDueDateFilter(order.due_date, dueDateFilter, dueCalendarSnapshot)) {
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
    [
      statusFilter,
      trafficLightFilter,
      customerFilter,
      dueDateFilter,
      dueCalendarSnapshot,
      structuralFilters,
      materialFilter.textQuery,
    ]
  );

  const materialBlocks = useMemo(() => {
    const materials = [...new Set(appOrders.map((o) => o.material_article_number))].sort((a, b) =>
      a.localeCompare(b, "de")
    );
    return materials
      .map((material) => {
        const fullSequence = materialSequence(appOrders, material);
        const visibleSequence = fullSequence.filter((o) => matchesListingFilters(o));
        /** Repriorisierung im Backend erfordert die vollstaendige ID-Liste je Material — nur bei ungefilterter Sicht erlaubt. */
        const reorderAllowed =
          fullSequence.length >= 2 && fullSequence.length === visibleSequence.length;
        return {
          material,
          fullSequence,
          visibleSequence,
          show: visibleSequence.length > 0,
          reorderAllowed,
        };
      })
      .filter((b) => b.show);
  }, [appOrders, matchesListingFilters]);

  const applyMaterialReorder = useCallback(async (
    materialArticleNumber: string,
    orderedIds: string[]
  ): Promise<boolean> => {
    setReprioritizeError(null);
    setReprioritizeBusyMaterial(materialArticleNumber);
    try {
      await reprioritizeOrders({
        material_article_number: materialArticleNumber,
        ordered_ids: orderedIds,
      });
      setReloadAfterReprioritize((n) => n + 1);
      return true;
    } catch (e) {
      const msg =
        e instanceof ApiClientError ? e.message : e instanceof Error ? e.message : "Reihung konnte nicht gespeichert werden";
      setReprioritizeError(msg);
      return false;
    } finally {
      setReprioritizeBusyMaterial(null);
    }
  }, []);

  const renderAppOrderCard = useCallback((ctx: AppOrderRenderContext) => {
    return (
      <AppOrderListingCard
        order={ctx.order}
        positionLabel={ctx.positionLabel}
        dragPeerCompact={ctx.dragPeerCompact}
        dragActiveSimplified={ctx.dragActiveSimplified}
        reorderUiMode={ctx.reorderUiMode}
        canEdit={canEditAppOrder(ctx.order)}
        onEdit={setEditingOrder}
      />
    );
  }, []);

  const visibleSimulatorOrders = useMemo(() => {
    if (trafficLightFilter) {
      return [];
    }
    const q = materialFilter.textQuery.trim().toLowerCase();
    return [...simulatorRows]
      .filter((order) => (statusFilter ? order.status === statusFilter : true))
      .filter((order) => matchesCustomerFilter(customerFilter, order.customer_name))
      .filter((order) => matchesDueDateFilter(order.due_date, dueDateFilter, dueCalendarSnapshot))
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
  }, [
    simulatorRows,
    statusFilter,
    customerFilter,
    dueDateFilter,
    dueCalendarSnapshot,
    trafficLightFilter,
    structuralFilters,
    materialFilter.textQuery,
  ]);

  const trafficLightBannerClass =
    trafficLightFilter === "red"
      ? "border-l-4 border-red-600 bg-red-50 text-red-950"
      : trafficLightFilter === "yellow"
        ? "border-l-4 border-amber-500 bg-amber-50 text-amber-950"
        : trafficLightFilter === "green"
          ? "border-l-4 border-emerald-600 bg-emerald-50 text-emerald-950"
          : "";

  const trafficLightLabel =
    trafficLightFilter === "red"
      ? "Rot"
      : trafficLightFilter === "yellow"
        ? "Gelb"
        : trafficLightFilter === "green"
          ? "Gruen"
          : "";

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

      {trafficLightFilter ? (
        <div
          className={`flex flex-wrap items-center justify-between gap-3 rounded-lg px-4 py-3 shadow-sm ${trafficLightBannerClass}`}
          role="status"
          aria-live="polite"
        >
          <div className="min-w-0">
            <p className="text-sm font-semibold tracking-tight">Ampel: {trafficLightLabel}</p>
            <p className="mt-0.5 text-xs font-normal opacity-90">
              Es werden nur App-Auftraege mit passendem <code className="rounded bg-black/5 px-1 py-0.5 text-[11px]">traffic_light</code>{" "}
              angezeigt. ERP-Simulator-Auftraege sind bei diesem Filter ausgeblendet.
            </p>
          </div>
          <button
            type="button"
            className="shrink-0 rounded-md border border-black/10 bg-white px-3 py-2 text-sm font-medium text-slate-900 shadow-sm touch-manipulation hover:bg-white/90"
            onClick={() => {
              router.replace("/orders", { scroll: false });
            }}
          >
            Ampel-Filter entfernen
          </button>
        </div>
      ) : null}

      {loading ? <p className="text-sm text-slate-600">Lade Daten...</p> : null}

      <div className="grid gap-3 rounded border border-slate-200 p-3">
        <p className="text-xs font-medium text-slate-600">
          Filter gelten fuer <strong>beide</strong> Listen: Volltext, Kunde, Fälligkeit, Hauptgruppe/Material/Dimension
          (ueber Artikelnummer, Schema wie Simulator) und Status (exakter Code; App- und ERP-Sim-Status koennen sich
          unterscheiden). <span className="text-slate-500">Fälligkeit „Diese Woche“: Montag bis Sonntag der lokalen
          Kalenderwoche (ISO-Woche, Mo–So), Vergleich mit <code className="text-[11px]">due_date</code>.</span>
        </p>
        <SimulatorMaterialFilterInputs
          values={materialFilter}
          onChange={setMaterialFilter}
          textQueryLabel="Volltext"
          textQueryPlaceholder="APP-Nummer, Artikel, Status ..."
        />
        <label className="grid max-w-md gap-1">
          Kunde
          <select
            className="h-10 min-h-[44px] w-full max-w-md rounded-md border border-slate-300 px-3 text-sm"
            value={customerFilter}
            onChange={(e) => setCustomerFilter(e.target.value)}
          >
            <option value="">Alle</option>
            {customerSelectOptions.includeOhneKunde ? (
              <option value={CUSTOMER_FILTER_NONE}>Ohne Kunde</option>
            ) : null}
            {customerSelectOptions.sortedNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="grid max-w-md gap-1">
          Fälligkeit
          <select
            className="h-10 min-h-[44px] w-full max-w-md rounded-md border border-slate-300 px-3 text-sm"
            value={dueDateFilter}
            onChange={(e) => setDueDateFilter(e.target.value as DueDateFilterValue)}
          >
            <option value="">Alle</option>
            <option value={DUE_DATE_FILTER_OVERDUE}>Überfällig</option>
            <option value={DUE_DATE_FILTER_TODAY}>Heute</option>
            <option value={DUE_DATE_FILTER_THIS_WEEK}>Diese Woche</option>
            <option value={DUE_DATE_FILTER_NONE}>Ohne Fälligkeit</option>
          </select>
        </label>
        <label className="grid max-w-md gap-1">
          Status (App und ERP-Simulator, gleicher Code-Vergleich)
          <select
            className="h-10 min-h-[44px] w-full max-w-md rounded-md border border-slate-300 px-3 text-sm"
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
        {trafficLightFilter ? (
          <p className="text-xs text-slate-600">
            Ampel-Filter aktiv (URL: <code className="text-[11px]">?traffic_light={trafficLightFilter}</code>) — gleiche
            Anzeige wie oben; ERP-Simulator bleibt ausgeblendet.
          </p>
        ) : null}
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
          {materialBlocks.map(({ material, visibleSequence, reorderAllowed }) => (
            <div
              key={material}
              className={
                draggingMaterialKey && draggingMaterialKey !== material
                  ? "grid gap-2 opacity-[0.4] transition-opacity duration-200"
                  : draggingMaterialKey === material
                    ? "relative z-[8] grid gap-2 transition-opacity duration-200"
                    : "grid gap-2 transition-opacity duration-200"
              }
            >
              <p className="text-xs font-medium text-slate-700">
                Material: <span className="font-mono">{material}</span>
                {reorderAllowed && visibleSequence.length > 1 ? (
                  <>
                    <span className="hidden font-normal text-slate-600 sm:inline">
                      {" "}
                      — Reihenfolge per Drag &amp; Drop anpassen (nur dieses Material; vollstaendige Liste wird
                      gespeichert).
                    </span>
                    <span className="font-normal text-slate-600 sm:hidden">
                      {" "}
                      — Reihenfolge auf dem Smartphone ueber «Reihenfolge aendern» (nur dieses Material).
                    </span>
                  </>
                ) : null}
              </p>
              {reprioritizeBusyMaterial === material ? (
                <p className="text-xs text-slate-600">Speichere neue Reihenfolge …</p>
              ) : null}

              <div className="hidden sm:block">
                <AppOrdersMaterialDndBlock
                  materialArticleNumber={material}
                  sequence={visibleSequence}
                  reorderDisabled={loading || reprioritizeBusyMaterial !== null || !reorderAllowed}
                  isOrderDimmed={() => false}
                  onDragEndReorder={async (ids) => {
                    await applyMaterialReorder(material, ids);
                  }}
                  onMaterialDragActiveChange={setDraggingMaterialKey}
                  renderCard={renderAppOrderCard}
                />
              </div>

              <div className="grid gap-2 sm:hidden">
                {reorderAllowed ? (
                  <button
                    type="button"
                    className="flex min-h-11 w-full items-center justify-center rounded-lg border border-emerald-700 bg-emerald-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm touch-manipulation hover:bg-emerald-700"
                    onClick={() => setMobileReorderMaterial(material)}
                  >
                    Reihenfolge aendern
                  </button>
                ) : null}
                <ul className="grid gap-2">
                  {visibleSequence.map((order, index) => {
                    const posLabel = `${index + 1} von ${visibleSequence.length}`;
                    const oid = order.order_id ?? "";
                    return (
                      <li
                        key={oid || `${material}-${index}`}
                        className="flex rounded border border-emerald-200 bg-emerald-50/40 p-2.5 text-sm"
                      >
                        <AppOrderListingCard
                          order={order}
                          positionLabel={posLabel}
                          dragPeerCompact={false}
                          dragActiveSimplified={false}
                          reorderUiMode="default"
                          canEdit={canEditAppOrder(order)}
                          onEdit={setEditingOrder}
                        />
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>

      <MobileMaterialReorderSheet
        materialArticleNumber={mobileReorderMaterial}
        sequence={mobileReorderMaterial ? materialSequence(appOrders, mobileReorderMaterial) : []}
        reorderDisabled={loading || reprioritizeBusyMaterial !== null}
        isOrderDimmed={() => false}
        onClose={() => setMobileReorderMaterial(null)}
        onCommitReorder={async (orderedIds) => {
          if (!mobileReorderMaterial) {
            return false;
          }
          return applyMaterialReorder(mobileReorderMaterial, orderedIds);
        }}
        onMaterialDragActiveChange={setDraggingMaterialKey}
        renderCard={renderAppOrderCard}
      />

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
