"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { TrafficLightIndicator } from "@/components/shared/traffic-light-indicator";
import { fetchDashboardOverview, fetchErpMaterialStock, fetchErpOrderValidation } from "@/lib/api-client";
import type { DashboardOverviewDto, OrderDto } from "@/lib/types";

function orderKey(order: OrderDto, index: number): string {
  return (
    (order.persisted_row_id != null ? String(order.persisted_row_id) : null) ??
    order.order_id ??
    `${order.material_article_number}-${index}`
  );
}

function orderDisplayLabel(order: OrderDto): string {
  return order.display_order_code?.trim() || order.order_id || "—";
}

function formatErpStock(payload: Record<string, unknown>): string {
  const stockMm = payload.stock_mm;
  if (typeof stockMm === "number") {
    return `${stockMm} mm`;
  }
  const stockM = payload.stock_m;
  if (typeof stockM === "number") {
    return `${stockM} m`;
  }
  return "nicht verfuegbar";
}

export function DashboardOverview() {
  const [overview, setOverview] = useState<DashboardOverviewDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [erpInfoByOrderKey, setErpInfoByOrderKey] = useState<
    Record<
      string,
      {
        stockLabel: string;
        validationLabel: string;
      }
    >
  >({});

  useEffect(() => {
    void fetchDashboardOverview()
      .then((payload) => {
        setOverview(payload);
        setError(null);
      })
      .catch((err: Error) => {
        setError(err.message);
      });
  }, []);

  useEffect(() => {
    const openOrders = overview?.open_orders ?? [];
    if (openOrders.length === 0) {
      setErpInfoByOrderKey({});
      return;
    }
    let active = true;

    async function loadErpIndicators() {
      const entries = await Promise.all(
        openOrders.slice(0, 5).map(async (order, index) => {
          const key = orderKey(order, index);
          let stockLabel = "nicht verfuegbar";
          let validationLabel = "keine ERP-Referenz";

          try {
            const payload = await fetchErpMaterialStock(order.material_article_number);
            stockLabel = formatErpStock(payload);
          } catch {
            stockLabel = "nicht verfuegbar";
          }

          if (order.erp_order_number) {
            try {
              const validation = await fetchErpOrderValidation(order.erp_order_number);
              validationLabel = validation.is_valid ? "gueltig" : "ungueltig";
            } catch {
              validationLabel = "nicht verfuegbar";
            }
          }
          return [key, { stockLabel, validationLabel }] as const;
        })
      );

      if (active) {
        setErpInfoByOrderKey(Object.fromEntries(entries));
      }
    }

    void loadErpIndicators();
    return () => {
      active = false;
    };
  }, [overview]);

  return (
    <div className="grid gap-4">
      <div className="rounded border border-slate-200 p-3">
        <p className="text-xs uppercase text-slate-500">Offene Auftraege</p>
        <p className="text-2xl font-semibold">{overview?.open_orders_count ?? "-"}</p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Link
          href="/orders?traffic_light=red"
          className="group block cursor-pointer rounded-lg border border-red-200/90 bg-white p-3 shadow-sm outline-none transition hover:border-red-300 hover:bg-red-50/60 hover:shadow-md active:scale-[0.99] active:bg-red-50/80"
        >
          <p className="text-xs uppercase text-red-800/90">Kritische Auftraege (rot)</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{overview?.red_count ?? "-"}</p>
          <p className="mt-2 text-[11px] text-slate-600 group-hover:text-slate-800">
            Zur gefilterten Auftragsuebersicht
          </p>
        </Link>
        <Link
          href="/orders?traffic_light=yellow"
          className="group block cursor-pointer rounded-lg border border-amber-200/90 bg-white p-3 shadow-sm outline-none transition hover:border-amber-300 hover:bg-amber-50/60 hover:shadow-md active:scale-[0.99] active:bg-amber-50/80"
        >
          <p className="text-xs uppercase text-amber-900/90">Eingeschränkte Auftraege (gelb)</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{overview?.yellow_count ?? "-"}</p>
          <p className="mt-2 text-[11px] text-slate-600 group-hover:text-slate-800">
            Zur gefilterten Auftragsuebersicht
          </p>
        </Link>
        <Link
          href="/orders?traffic_light=green"
          className="group block cursor-pointer rounded-lg border border-emerald-200/90 bg-white p-3 shadow-sm outline-none transition hover:border-emerald-300 hover:bg-emerald-50/60 hover:shadow-md active:scale-[0.99] active:bg-emerald-50/80"
        >
          <p className="text-xs uppercase text-emerald-900/90">Machbare Auftraege (gruen)</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{overview?.green_count ?? "-"}</p>
          <p className="mt-2 text-[11px] text-slate-600 group-hover:text-slate-800">
            Zur gefilterten Auftragsuebersicht
          </p>
        </Link>
      </div>

      <div className="grid gap-2">
        <h2 className="text-lg font-medium">Offene Auftraege</h2>
        <ul className="grid gap-2">
          {(overview?.open_orders ?? []).length === 0 ? (
            <li className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
              Keine Auftraege vorhanden.
            </li>
          ) : null}
          {(overview?.open_orders ?? []).map((order, index) => {
            const key = orderKey(order, index);
            const erpInfo = erpInfoByOrderKey[key];
            return (
              <li key={key} className="grid gap-1 rounded border border-slate-200 p-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{orderDisplayLabel(order)}</span>
                  <span>Status: {order.status}</span>
                  <span>Reihenfolge (auto): {order.priority_order ?? "-"}</span>
                  <TrafficLightIndicator trafficLight={order.traffic_light} />
                </div>
                <p>
                  Material: {order.material_article_number}
                  {order.material_description ? (
                    <span className="text-slate-700"> — {order.material_description}</span>
                  ) : null}
                </p>
                {order.customer_name ? <p>Kunde (dispositiv): {order.customer_name}</p> : null}
                {order.due_date ? <p>Faellig (Wunsch): {order.due_date}</p> : null}
                <div className="grid gap-0.5 rounded border border-slate-200 bg-slate-50 p-2 text-xs text-slate-700">
                  <p className="font-medium">ERP</p>
                  <p>Bestand: {erpInfo?.stockLabel ?? "nicht verfuegbar"}</p>
                  <p>Referenz: {erpInfo?.validationLabel ?? "nicht verfuegbar"}</p>
                </div>
              </li>
            );
          })}
        </ul>
      </div>

      <p className="text-xs text-slate-600">ERP-Daten werden fuer die ersten 5 offenen Auftraege geladen.</p>

      {error ? <p className="text-sm text-red-600">Fehler: {error}</p> : null}
    </div>
  );
}
