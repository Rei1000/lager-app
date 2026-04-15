"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PageShell } from "@/components/shared/page-shell";
import { CreateOrderForm } from "@/features/orders/create-order-form";
import { OrdersList } from "@/features/orders/orders-list";
import { fetchOrders } from "@/lib/api-client";
import type { OrderDto } from "@/lib/types";

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderDto[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadOrders() {
    try {
      const loaded = await fetchOrders();
      setOrders(loaded);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    }
  }

  useEffect(() => {
    void loadOrders();
  }, []);

  return (
    <PageShell title="Auftraege">
      <div className="grid gap-6">
        <p>
          <Link
            href="/orders/new"
            className="text-sm font-medium text-slate-800 underline underline-offset-2 hover:text-slate-600"
          >
            Neuer Auftrag (Planung, ohne Speichern)
          </Link>
        </p>
        {error ? <p className="text-sm text-red-600">Fehler: {error}</p> : null}
        <CreateOrderForm onCreated={(_order) => void loadOrders()} />
        <OrdersList initialOrders={orders} onRefresh={loadOrders} />
      </div>
    </PageShell>
  );
}
