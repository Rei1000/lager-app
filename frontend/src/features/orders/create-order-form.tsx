"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createOrder } from "@/lib/api-client";
import type { OrderDto } from "@/lib/types";

type CreateOrderFormProps = {
  onCreated: (order: OrderDto) => void | Promise<void>;
};

export function CreateOrderForm({ onCreated }: CreateOrderFormProps) {
  const [orderId, setOrderId] = useState("demo-order-1");
  const [materialArticleNumber, setMaterialArticleNumber] = useState("ART-DEMO");
  const [quantity, setQuantity] = useState("1");
  const [partLengthMm, setPartLengthMm] = useState("1000");
  const [kerfMm, setKerfMm] = useState("0");
  const [includeRestStock, setIncludeRestStock] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const created = await createOrder({
        order_id: orderId,
        material_article_number: materialArticleNumber,
        quantity: Number(quantity),
        part_length_mm: Number(partLengthMm),
        kerf_mm: Number(kerfMm),
        include_rest_stock: includeRestStock,
      });
      onCreated(created);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unbekannter Fehler";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="grid gap-3" onSubmit={onSubmit}>
      <h2 className="text-lg font-medium">Auftrag erstellen</h2>
      <label className="grid gap-1 text-sm">
        Order ID
        <Input value={orderId} onChange={(event) => setOrderId(event.target.value)} required />
      </label>
      <label className="grid gap-1 text-sm">
        Material
        <Input
          value={materialArticleNumber}
          onChange={(event) => setMaterialArticleNumber(event.target.value)}
          required
        />
      </label>
      <label className="grid gap-1 text-sm">
        Menge
        <Input
          type="number"
          min={1}
          value={quantity}
          onChange={(event) => setQuantity(event.target.value)}
          required
        />
      </label>
      <label className="grid gap-1 text-sm">
        Laenge (mm)
        <Input
          type="number"
          min={1}
          value={partLengthMm}
          onChange={(event) => setPartLengthMm(event.target.value)}
          required
        />
      </label>
      <label className="grid gap-1 text-sm">
        Kerf (mm)
        <Input
          type="number"
          min={0}
          value={kerfMm}
          onChange={(event) => setKerfMm(event.target.value)}
          required
        />
      </label>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={includeRestStock}
          onChange={(event) => setIncludeRestStock(event.target.checked)}
        />
        Reststuecke beruecksichtigen
      </label>
      <Button type="submit" disabled={submitting}>
        {submitting ? "Speichere..." : "Auftrag senden"}
      </Button>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </form>
  );
}
