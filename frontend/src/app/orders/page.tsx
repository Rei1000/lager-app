"use client";

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
        {error ? <p className="text-sm text-red-600">Fehler: {error}</p> : null}
        <CreateOrderForm onCreated={(_order) => void loadOrders()} />
        <OrdersList initialOrders={orders} onRefresh={loadOrders} />
      </div>
    </PageShell>
  );
}
