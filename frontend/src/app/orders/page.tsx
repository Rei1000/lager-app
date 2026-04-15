"use client";

import { useState } from "react";

import { PageShell } from "@/components/shared/page-shell";
import { cn } from "@/lib/utils";
import { NewOrderPlanningForm } from "@/features/orders/new-order-planning-form";
import { OrdersOpenOverview } from "@/features/orders/orders-open-overview";

type OrdersTab = "new" | "list";

export default function OrdersPage() {
  const [activeTab, setActiveTab] = useState<OrdersTab>("new");
  const [ordersListRefresh, setOrdersListRefresh] = useState(0);

  return (
    <PageShell title="Auftraege">
      <div className="grid gap-4">
        <div
          className="flex flex-wrap gap-2 border-b border-slate-200 pb-2"
          role="tablist"
          aria-label="Auftraege Bereiche"
        >
          <button
            type="button"
            id="orders-tab-new-trigger"
            role="tab"
            className={cn(
              "min-h-[44px] rounded-md border px-4 py-2.5 text-sm font-medium transition sm:min-h-11",
              activeTab === "new"
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-300 bg-white text-slate-800 hover:bg-slate-50"
            )}
            aria-selected={activeTab === "new"}
            aria-controls="orders-tab-new-panel"
            onClick={() => setActiveTab("new")}
          >
            Neuer Auftrag
          </button>
          <button
            type="button"
            id="orders-tab-list-trigger"
            role="tab"
            className={cn(
              "min-h-[44px] rounded-md border px-4 py-2.5 text-sm font-medium transition sm:min-h-11",
              activeTab === "list"
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-300 bg-white text-slate-800 hover:bg-slate-50"
            )}
            aria-selected={activeTab === "list"}
            aria-controls="orders-tab-list-panel"
            onClick={() => setActiveTab("list")}
          >
            Auftraege
          </button>
        </div>

        <div
          id="orders-tab-new-panel"
          role="tabpanel"
          aria-labelledby="orders-tab-new-trigger"
          className={activeTab === "new" ? "grid gap-4" : "hidden"}
        >
          <p className="rounded border border-slate-200 bg-slate-50 p-2 text-xs text-slate-800">
            Planung mit Backend-Vorschau. Unter F) wird der App-Auftrag per API in der Datenbank gespeichert.
          </p>
          <NewOrderPlanningForm onAppOrderSaved={() => setOrdersListRefresh((n) => n + 1)} />
        </div>

        <div
          id="orders-tab-list-panel"
          role="tabpanel"
          aria-labelledby="orders-tab-list-trigger"
          className={activeTab === "list" ? "grid gap-4" : "hidden"}
        >
          <OrdersOpenOverview listRefreshToken={ordersListRefresh} />
        </div>
      </div>
    </PageShell>
  );
}
