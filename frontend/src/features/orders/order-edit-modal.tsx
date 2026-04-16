"use client";

import { useCallback, useEffect, useId, useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiClientError, updateOrder } from "@/lib/api-client";
import type { OrderDto } from "@/lib/types";

type OrderEditModalProps = {
  order: OrderDto | null;
  onClose: () => void;
  onSaved: () => void;
};

export function OrderEditModal({ order, onClose, onSaved }: OrderEditModalProps) {
  const titleId = useId();
  const [quantity, setQuantity] = useState(1);
  const [partLengthMm, setPartLengthMm] = useState(1000);
  const [kerfMm, setKerfMm] = useState(0);
  const [customerName, setCustomerName] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!order) {
      return;
    }
    setQuantity(order.quantity);
    setPartLengthMm(order.part_length_mm);
    setKerfMm(order.kerf_mm);
    setCustomerName(order.customer_name?.trim() ?? "");
    setDueDate(order.due_date ?? "");
    setError(null);
  }, [order]);

  useEffect(() => {
    if (!order) {
      return;
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [order, onClose]);

  const submit = useCallback(async () => {
    if (!order?.order_id) {
      return;
    }
    if (quantity <= 0 || partLengthMm <= 0 || kerfMm < 0) {
      setError("Menge und Laenge muessen groesser 0 sein, Kerf nicht negativ.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await updateOrder(order.order_id, {
        quantity,
        part_length_mm: partLengthMm,
        kerf_mm: kerfMm,
        customer_name: customerName.trim() || null,
        due_date: dueDate.trim() || null,
      });
      onSaved();
      onClose();
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : e instanceof Error ? e.message : "Speichern fehlgeschlagen");
    } finally {
      setBusy(false);
    }
  }, [order, quantity, partLengthMm, kerfMm, customerName, dueDate, onClose, onSaved]);

  if (!order) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end justify-center bg-black/40 p-0 sm:items-center sm:p-4"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-t-lg border border-slate-200 bg-white shadow-xl sm:rounded-lg"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="border-b border-slate-100 px-4 py-3">
          <h2 id={titleId} className="text-base font-semibold text-slate-900">
            Auftrag bearbeiten
          </h2>
          <p className="mt-1 text-xs text-slate-600">
            {order.display_order_code?.trim() || order.order_id} ·{" "}
            <span className="font-mono">{order.material_article_number}</span>
          </p>
        </div>
        <div className="grid gap-3 px-4 py-4">
          {error ? (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          ) : null}
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-slate-800">Menge (Stueck)</span>
            <input
              type="number"
              min={1}
              step={1}
              className="h-10 rounded-md border border-slate-300 px-3"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-slate-800">Teillaenge (mm)</span>
            <input
              type="number"
              min={1}
              step={1}
              className="h-10 rounded-md border border-slate-300 px-3"
              value={partLengthMm}
              onChange={(e) => setPartLengthMm(Number(e.target.value))}
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-slate-800">Kerf (mm)</span>
            <input
              type="number"
              min={0}
              step={1}
              className="h-10 rounded-md border border-slate-300 px-3"
              value={kerfMm}
              onChange={(e) => setKerfMm(Number(e.target.value))}
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-slate-800">Kunde (optional)</span>
            <input
              type="text"
              className="h-10 rounded-md border border-slate-300 px-3"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              maxLength={255}
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-slate-800">Faellig (optional)</span>
            <input
              type="date"
              className="h-10 rounded-md border border-slate-300 px-3"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
          </label>
          <p className="text-xs text-slate-500">
            Material, Reihenfolge, Ampel und ERP-Referenz werden hier nicht geaendert.
          </p>
        </div>
        <div className="flex flex-wrap justify-end gap-2 border-t border-slate-100 px-4 py-3">
          <Button
            type="button"
            className="min-h-10 border border-slate-300 bg-white text-slate-900 hover:bg-slate-50"
            disabled={busy}
            onClick={onClose}
          >
            Abbrechen
          </Button>
          <Button type="button" className="min-h-10 min-w-[7rem]" disabled={busy} onClick={() => void submit()}>
            {busy ? "Speichern …" : "Speichern"}
          </Button>
        </div>
      </div>
    </div>
  );
}
