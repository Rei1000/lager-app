"use client";

import { TrafficLightIndicator } from "@/components/shared/traffic-light-indicator";
import { appOrderPrimaryLabel, appOrderStatusLabelDe } from "@/features/orders/app-order-copy";
import type { OrderDto } from "@/lib/types";

type AppOrderListingCardProps = {
  order: OrderDto;
  positionLabel: string;
  dragPeerCompact: boolean;
  dragActiveSimplified: boolean;
  reorderUiMode: "default" | "mobileSheet";
  canEdit: boolean;
  onEdit: (order: OrderDto) => void;
};

export function AppOrderListingCard({
  order,
  positionLabel,
  dragPeerCompact,
  dragActiveSimplified,
  reorderUiMode,
  canEdit,
  onEdit,
}: AppOrderListingCardProps) {
  const fmtM = (v: number) => v.toLocaleString("de-DE", { maximumFractionDigits: 3 });

  if (dragActiveSimplified) {
    if (reorderUiMode === "mobileSheet") {
      return (
        <div className="pointer-events-none min-w-0 select-none space-y-0.5">
          <div className="flex items-center justify-between gap-2">
            <p className="min-w-0 truncate text-xs font-semibold text-slate-900">{appOrderPrimaryLabel(order)}</p>
            <TrafficLightIndicator trafficLight={order.traffic_light} showLabel={false} className="shrink-0" />
          </div>
          <p className="text-[10px] leading-tight text-slate-600">
            <span className="tabular-nums">Bed. {fmtM(order.required_m)} m</span>
            <span className="text-slate-400"> · </span>
            <span className="tabular-nums">
              Vor Auftr.{" "}
              {order.disposition_available_before_m != null ? `${fmtM(order.disposition_available_before_m)} m` : "—"}
            </span>
          </p>
        </div>
      );
    }
    return (
      <div className="pointer-events-none min-w-0 select-none">
        <p className="truncate text-xs font-semibold leading-tight text-emerald-950">
          <span className="rounded bg-emerald-700 px-1 py-0.5 text-[9px] font-semibold uppercase text-white">App</span>{" "}
          <span className="text-slate-900">{appOrderPrimaryLabel(order)}</span>
        </p>
        <p className="mt-0.5 text-[10px] text-slate-600">
          Position <span className="font-mono">{positionLabel}</span>
        </p>
      </div>
    );
  }

  const sheetCompact = reorderUiMode === "mobileSheet";

  if (sheetCompact) {
    return (
      <div className="min-w-0 space-y-1">
        <div className="flex items-center justify-between gap-2">
          <p className="min-w-0 truncate text-sm font-semibold leading-tight text-slate-900">
            {appOrderPrimaryLabel(order)}
          </p>
          <TrafficLightIndicator trafficLight={order.traffic_light} showLabel={false} className="shrink-0" />
        </div>
        <div className="space-y-0.5 text-[11px] leading-snug text-slate-700">
          <p>
            <span className="text-slate-500">Bedarf </span>
            <span className="tabular-nums font-medium text-slate-900">{fmtM(order.required_m)} m</span>
          </p>
          <p>
            <span className="text-slate-500">Verfuegbar vor diesem Auftrag </span>
            <span className="tabular-nums font-medium text-slate-900">
              {order.disposition_available_before_m != null ? `${fmtM(order.disposition_available_before_m)} m` : "—"}
            </span>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={
        dragPeerCompact ? "max-sm:space-y-1 space-y-2 sm:space-y-3" : "space-y-2 sm:space-y-3"
      }
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="font-semibold leading-snug text-emerald-950">
            <span className="rounded bg-emerald-700 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-white sm:text-xs">
              App-Auftrag
            </span>{" "}
            <span className="text-base font-semibold tracking-tight text-slate-900 sm:text-lg">
              {appOrderPrimaryLabel(order)}
            </span>
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
          <TrafficLightIndicator trafficLight={order.traffic_light} />
          {canEdit && order.order_id ? (
            <button
              type="button"
              className="flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-emerald-200 bg-white/95 text-emerald-900 shadow-sm hover:bg-emerald-50 sm:min-h-0 sm:min-w-0 sm:rounded sm:p-1.5 touch-manipulation"
              aria-label="Auftrag bearbeiten"
              title="Bearbeiten"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(order);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 sm:h-[18px] sm:w-[18px]"
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
        </div>
      </div>

      <p className="text-xs leading-snug text-slate-700">
        <span className="sm:hidden">
          Position <span className="font-mono">{positionLabel}</span>
          {" · "}Index <span className="font-mono">{order.priority_order ?? "—"}</span>
        </span>
        <span className="hidden sm:inline">
          <span className="font-medium">App-Disposition (nur Lager-App, gleiches Material):</span> Position{" "}
          <span className="font-mono">{positionLabel}</span> · Reihenfolge-Index{" "}
          <span className="font-mono">{order.priority_order ?? "—"}</span> — die Ampel wird im Backend nach dieser
          Reihenfolge fuer <span className="font-mono">{order.material_article_number}</span> berechnet (ohne
          ERP-Einzelreihen).
        </span>
      </p>
      {order.order_id ? (
        <p className="hidden text-xs text-slate-600 sm:block">
          Technische Speicherreferenz (API): <span className="font-mono">{order.order_id}</span>
        </p>
      ) : null}

      <p className="text-sm text-slate-900">
        <span className="text-slate-600 sm:text-inherit">Material: </span>
        <span className="font-mono">{order.material_article_number}</span>
        {order.material_description ? <span className="text-slate-700"> — {order.material_description}</span> : null}
      </p>

      <div className="grid gap-2 rounded-md border border-emerald-100/90 bg-white/60 p-2.5 sm:border-0 sm:bg-transparent sm:p-0">
        <p className="text-sm leading-snug text-slate-800">
          <span className="font-medium text-slate-700">Bedarf: </span>
          <span className="tabular-nums">{order.required_m.toLocaleString("de-DE", { maximumFractionDigits: 3 })} m</span>
          <span className="block text-xs text-slate-600 sm:mt-0 sm:inline sm:text-sm">
            {" "}
            ({order.quantity}×{order.part_length_mm} mm, Kerf {order.kerf_mm} mm
            <span className="hidden sm:inline">
              {" "}
              · wie ERP-Sim <code className="text-xs">required_m</code>
            </span>
            )
          </span>
        </p>
        {order.disposition_available_before_m != null ? (
          <p className="text-sm leading-snug text-slate-800">
            <span className="font-medium text-slate-700">Verfuegbar vor diesem Auftrag: </span>
            <span className="tabular-nums">
              {order.disposition_available_before_m.toLocaleString("de-DE", {
                maximumFractionDigits: 3,
              })}{" "}
              m
            </span>
            <span className="hidden text-xs text-slate-500 sm:inline">
              {" "}
              — nur App-Reihenfolge; ERP-offene Auftraege als Pipeline aggregiert.
            </span>
          </p>
        ) : null}
      </div>

      <p className="text-xs text-slate-700 sm:text-sm">
        <span className="font-medium">Workflow-Status: </span>
        {appOrderStatusLabelDe(order.status)} <span className="text-slate-500">({order.status})</span>
      </p>

      {order.customer_name || order.due_date ? (
        <p className="text-[11px] text-slate-600 sm:text-xs">
          {order.customer_name ? <span>Kunde: {order.customer_name}</span> : null}
          {order.customer_name && order.due_date ? <span> · </span> : null}
          {order.due_date ? <span>Faellig: {order.due_date}</span> : null}
        </p>
      ) : null}

      {order.erp_order_number ? (
        <p className="text-xs text-slate-600">
          ERP-Referenz: <span className="font-mono">{order.erp_order_number}</span>
        </p>
      ) : null}
      <p className="text-[11px] text-slate-600 sm:text-xs">
        Reihenfolge am Material (niedrig = frueher):{" "}
        <span className="font-medium text-slate-800">{order.priority_order ?? "—"}</span>
        <span className="hidden sm:inline"> — Drag &amp; Drop aendert persistiert</span>
      </p>
    </div>
  );
}
