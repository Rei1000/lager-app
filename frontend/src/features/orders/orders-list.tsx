"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EntityComments } from "@/components/comments/entity-comments";
import {
  fetchErpMaterialStock,
  fetchErpOrderValidation,
  getMaterialByArticleNumber,
  linkErpOrder,
  recalculateOrders,
  reprioritizeOrders,
  reserveOrder,
} from "@/lib/api-client";
import { MaterialSummaryCard } from "@/features/materials/material-summary-card";
import type { ErpOrderValidationDto, MaterialLookupDto, OrderDto } from "@/lib/types";

type OrdersListProps = {
  initialOrders: OrderDto[];
  onRefresh: () => Promise<void> | void;
};

function trafficLightBadgeClass(light: string | null): string {
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

export function OrdersList({ initialOrders, onRefresh }: OrdersListProps) {
  const [orders, setOrders] = useState<OrderDto[]>(initialOrders);
  const [statusFilter, setStatusFilter] = useState("");
  const [materialFilter, setMaterialFilter] = useState("");
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [selectedMaterial, setSelectedMaterial] = useState<MaterialLookupDto | null>(null);
  const [recalculateMaterial, setRecalculateMaterial] = useState("ART-DEMO");
  const [reprioMaterial, setReprioMaterial] = useState("ART-DEMO");
  const [reprioIds, setReprioIds] = useState("");
  const [linkOrderId, setLinkOrderId] = useState("");
  const [erpNumber, setErpNumber] = useState("ERP-42");
  const [error, setError] = useState<string | null>(null);
  const [erpStockPayload, setErpStockPayload] = useState<Record<string, unknown> | null>(null);
  const [erpValidation, setErpValidation] = useState<ErpOrderValidationDto | null>(null);
  const [erpReadError, setErpReadError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    setOrders(initialOrders);
  }, [initialOrders]);

  const selectedOrder = useMemo(
    () => orders.find((order) => order.order_id === selectedOrderId) ?? null,
    [orders, selectedOrderId]
  );

  const visibleOrders = useMemo(() => {
    return [...orders]
      .filter((order) => (statusFilter ? order.status === statusFilter : true))
      .filter((order) =>
        materialFilter ? order.material_article_number.toLowerCase().includes(materialFilter.toLowerCase()) : true
      )
      .sort((a, b) => {
        const aPriority = a.priority_order ?? Number.MAX_SAFE_INTEGER;
        const bPriority = b.priority_order ?? Number.MAX_SAFE_INTEGER;
        return aPriority - bPriority;
      });
  }, [orders, statusFilter, materialFilter]);

  useEffect(() => {
    if (!selectedOrder?.material_article_number) {
      setSelectedMaterial(null);
      return;
    }
    void getMaterialByArticleNumber(selectedOrder.material_article_number)
      .then((material) => setSelectedMaterial(material))
      .catch(() => setSelectedMaterial(null));
  }, [selectedOrder?.material_article_number]);

  useEffect(() => {
    if (!selectedOrder?.material_article_number) {
      setErpStockPayload(null);
      setErpValidation(null);
      setErpReadError(null);
      return;
    }
    const currentOrder = selectedOrder;
    let active = true;

    async function loadErpContext() {
      try {
        setErpReadError(null);
        const stock = await fetchErpMaterialStock(currentOrder.material_article_number);
        if (!active) {
          return;
        }
        setErpStockPayload(stock);
      } catch {
        if (active) {
          setErpStockPayload(null);
          setErpReadError("ERP-Bestand ist fuer dieses Material derzeit nicht verfuegbar.");
        }
      }

      if (!currentOrder.erp_order_number) {
        setErpValidation(null);
        return;
      }

      try {
        const validation = await fetchErpOrderValidation(currentOrder.erp_order_number);
        if (active) {
          setErpValidation(validation);
        }
      } catch {
        if (active) {
          setErpValidation(null);
          setErpReadError("ERP-Referenz konnte derzeit nicht validiert werden.");
        }
      }
    }

    void loadErpContext();
    return () => {
      active = false;
    };
  }, [selectedOrder?.erp_order_number, selectedOrder?.material_article_number]);

  async function handleReserve(orderId: string) {
    setActionLoading(`reserve:${orderId}`);
    setError(null);
    try {
      const updated = await reserveOrder(orderId);
      setOrders((current) => current.map((order) => (order.order_id === orderId ? updated : order)));
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleRecalculate() {
    setActionLoading("recalculate");
    setError(null);
    try {
      const updated = await recalculateOrders({ material_article_number: recalculateMaterial });
      setOrders(updated);
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleReprioritize() {
    setActionLoading("reprioritize");
    setError(null);
    try {
      const ids = reprioIds
        .split(",")
        .map((value) => value.trim())
        .filter((value) => value.length > 0);
      const updated = await reprioritizeOrders({
        material_article_number: reprioMaterial,
        ordered_ids: ids,
      });
      setOrders(updated);
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleLinkErp() {
    setActionLoading("link-erp");
    setError(null);
    try {
      const updated = await linkErpOrder({ order_id: linkOrderId, erp_order_number: erpNumber });
      setOrders((current) =>
        current.map((order) => (order.order_id === linkOrderId ? updated : order))
      );
      await onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  return (
    <div className="grid gap-4">
      <h2 className="text-lg font-medium">Auftragsuebersicht</h2>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="grid gap-2 rounded border border-slate-200 p-3 sm:grid-cols-2">
        <Input
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          placeholder="Filter Status (z. B. reserved)"
        />
        <Input
          value={materialFilter}
          onChange={(event) => setMaterialFilter(event.target.value)}
          placeholder="Filter Materialartikel"
        />
      </div>

      <ul className="grid gap-2">
        {visibleOrders.length === 0 ? (
          <li className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
            Keine Auftraege vorhanden.
          </li>
        ) : null}
        {visibleOrders.map((order, index) => (
          <li
            key={order.order_id ?? `order-${index}`}
            className="rounded border border-slate-200 p-3 text-sm sm:p-4"
          >
            <div className="grid gap-2">
              <p className="font-medium">
                {order.material_article_number} | Status: {order.status}
              </p>
              <p className="text-slate-700">
                ID: {order.order_id ?? "-"} | Prioritaet: {order.priority_order ?? "-"}
              </p>
              <span className={`rounded px-2 py-0.5 text-xs ${trafficLightBadgeClass(order.traffic_light)}`}>
                {order.traffic_light ?? "-"}
              </span>
              <div className="grid gap-2 sm:flex">
                <Button className="w-full sm:w-auto" onClick={() => setSelectedOrderId(order.order_id ?? null)}>
                  Details
                </Button>
                <Button
                  className="w-full sm:w-auto"
                  disabled={actionLoading !== null}
                  onClick={() => order.order_id && handleReserve(order.order_id)}
                >
                  {actionLoading === `reserve:${order.order_id}` ? "Reserviere..." : "Reserve"}
                </Button>
              </div>
            </div>
          </li>
        ))}
      </ul>

      {selectedOrder ? (
        <div className="grid gap-3 rounded border border-slate-200 p-3 text-sm">
          <h3 className="text-base font-medium">Auftragsdetail</h3>
          <p>Order ID: {selectedOrder.order_id ?? "-"}</p>
          <p>Status: {selectedOrder.status}</p>
          <p>Prioritaet: {selectedOrder.priority_order ?? "-"}</p>
          <p>Material: {selectedOrder.material_article_number}</p>
          <p>Bedarf (mm): {selectedOrder.total_demand_mm}</p>
          <p>Reststuecknutzung: {selectedOrder.include_rest_stock ? "ja" : "nein"}</p>
          <p>ERP-Verknuepfung: {selectedOrder.erp_order_number ?? "-"}</p>
          {selectedMaterial ? <MaterialSummaryCard material={selectedMaterial} /> : null}
          <div className="grid gap-1 rounded border border-slate-200 p-3">
            <p className="font-medium">ERP-Read-Daten (Quelle: ERP)</p>
            {erpReadError ? <p className="text-red-600">{erpReadError}</p> : null}
            <p>
              ERP-Referenzstatus:{" "}
              {selectedOrder.erp_order_number
                ? erpValidation
                  ? erpValidation.is_valid
                    ? "gueltig"
                    : "ungueltig"
                  : "nicht verfuegbar"
                : "keine ERP-Referenz gesetzt"}
            </p>
            {erpStockPayload ? (
              <details className="rounded border border-slate-200 p-2">
                <summary className="cursor-pointer font-medium">ERP-Bestand fuer Material anzeigen</summary>
                <pre className="overflow-x-auto pt-2 text-xs">{JSON.stringify(erpStockPayload, null, 2)}</pre>
              </details>
            ) : (
              <p>ERP-Bestand: nicht verfuegbar</p>
            )}
          </div>
          {selectedOrder.order_id ? (
            <EntityComments
              entityType="order"
              entityId={selectedOrder.order_id}
              title="Kommentare zum Auftrag"
            />
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-2 rounded border border-slate-200 p-3 sm:p-4">
        <h3 className="font-medium">Recalculate</h3>
        <Input
          value={recalculateMaterial}
          onChange={(event) => setRecalculateMaterial(event.target.value)}
          placeholder="Materialartikel"
        />
        <Button className="w-full sm:w-auto" onClick={handleRecalculate}>
          {actionLoading === "recalculate" ? "Laeuft..." : "POST /orders/recalculate"}
        </Button>
      </div>

      <div className="grid gap-2 rounded border border-slate-200 p-3 sm:p-4">
        <h3 className="font-medium">Reprioritize</h3>
        <Input
          value={reprioMaterial}
          onChange={(event) => setReprioMaterial(event.target.value)}
          placeholder="Materialartikel"
        />
        <Input
          value={reprioIds}
          onChange={(event) => setReprioIds(event.target.value)}
          placeholder="Order IDs (kommagetrennt)"
        />
        <Button className="w-full sm:w-auto" onClick={handleReprioritize}>
          {actionLoading === "reprioritize" ? "Laeuft..." : "POST /orders/reprioritize"}
        </Button>
      </div>

      <div className="grid gap-2 rounded border border-slate-200 p-3 sm:p-4">
        <h3 className="font-medium">Link ERP</h3>
        <Input
          value={linkOrderId}
          onChange={(event) => setLinkOrderId(event.target.value)}
          placeholder="Order ID"
        />
        <Input
          value={erpNumber}
          onChange={(event) => setErpNumber(event.target.value)}
          placeholder="ERP-Nummer"
        />
        <Button className="w-full sm:w-auto" onClick={handleLinkErp}>
          {actionLoading === "link-erp" ? "Verknuepfe..." : "POST /orders/{'{id}'}/link-erp"}
        </Button>
      </div>
    </div>
  );
}
