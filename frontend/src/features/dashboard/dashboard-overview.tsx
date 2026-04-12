"use client";

import { useEffect, useState } from "react";

import { fetchDashboardOverview, fetchErpMaterialStock, fetchErpOrderValidation } from "@/lib/api-client";
import type { DashboardOverviewDto, OrderDto } from "@/lib/types";

function trafficLightClass(light: string | null): string {
  if (light === "green") {
    return "bg-green-100 text-green-800";
  }
  if (light === "yellow") {
    return "bg-yellow-100 text-yellow-800";
  }
  if (light === "red") {
    return "bg-red-100 text-red-800";
  }
  return "bg-slate-100 text-slate-700";
}

function orderKey(order: OrderDto, index: number): string {
  return order.order_id ?? `${order.material_article_number}-${index}`;
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
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="rounded border border-slate-200 p-3">
          <p className="text-xs uppercase text-slate-500">Offene Auftraege</p>
          <p className="text-2xl font-semibold">{overview?.open_orders_count ?? "-"}</p>
        </div>
        <div className="rounded border border-slate-200 p-3">
          <p className="text-xs uppercase text-slate-500">Kritische Auftraege (rot)</p>
          <p className="text-2xl font-semibold">{overview?.critical_orders_count ?? "-"}</p>
        </div>
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
                  <span className="font-medium">{order.order_id ?? "-"}</span>
                  <span>Status: {order.status}</span>
                  <span>Prio: {order.priority_order ?? "-"}</span>
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${trafficLightClass(order.traffic_light)}`}
                  >
                    {order.traffic_light ?? "-"}
                  </span>
                </div>
                <p>Material: {order.material_article_number}</p>
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
