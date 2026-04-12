"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EntityComments } from "@/components/comments/entity-comments";
import {
  approveErpTransfer,
  createErpTransfer,
  fetchCurrentUser,
  fetchErpTransfers,
  markErpTransferFailed,
  markErpTransferReady,
  markErpTransferSent,
} from "@/lib/api-client";
import type { ErpTransferRequestDto } from "@/lib/types";

export function ErpTransferPanel() {
  const [transfers, setTransfers] = useState<ErpTransferRequestDto[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [roleCode, setRoleCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const [orderId, setOrderId] = useState("demo-order-1");
  const [materialArticleNumber, setMaterialArticleNumber] = useState("ART-DEMO");
  const [requestedByUserId, setRequestedByUserId] = useState("1");
  const [payloadRaw, setPayloadRaw] = useState('{"source":"manual","note":"vorbereitung"}');

  const [actingUserId, setActingUserId] = useState("1");
  const [failureReason, setFailureReason] = useState("ERP nicht erreichbar");

  async function loadTransfers() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchErpTransfers();
      setTransfers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTransfers();
    void fetchCurrentUser()
      .then((user) => setRoleCode(user.role_code))
      .catch(() => setRoleCode(null));
  }, []);

  const canLeitungPlus = roleCode === "leitung" || roleCode === "admin";
  const canAdmin = roleCode === "admin";

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionLoading("create");
    setError(null);
    try {
      let payload: Record<string, unknown> | null = null;
      const normalized = payloadRaw.trim();
      if (normalized) {
        const parsed = JSON.parse(normalized) as Record<string, unknown>;
        payload = parsed;
      }
      await createErpTransfer({
        order_id: orderId,
        material_article_number: materialArticleNumber,
        requested_by_user_id: Number(requestedByUserId),
        payload,
      });
      await loadTransfers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleMarkReady(transferId: number) {
    setActionLoading(`ready:${transferId}`);
    setError(null);
    try {
      await markErpTransferReady({
        transfer_id: transferId,
        acting_user_id: Number(actingUserId),
      });
      await loadTransfers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleMarkSent(transferId: number) {
    setActionLoading(`sent:${transferId}`);
    setError(null);
    try {
      await markErpTransferSent({
        transfer_id: transferId,
        acting_user_id: Number(actingUserId),
      });
      await loadTransfers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleApprove(transferId: number) {
    setActionLoading(`approve:${transferId}`);
    setError(null);
    try {
      await approveErpTransfer({
        transfer_id: transferId,
        acting_user_id: Number(actingUserId),
      });
      await loadTransfers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleMarkFailed(transferId: number) {
    setActionLoading(`failed:${transferId}`);
    setError(null);
    try {
      await markErpTransferFailed({
        transfer_id: transferId,
        acting_user_id: Number(actingUserId),
        failure_reason: failureReason || null,
      });
      await loadTransfers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setActionLoading(null);
    }
  }

  return (
    <div className="grid gap-4">
      <p className="text-sm text-slate-700">
        Kontrollierter ERP-Write-Flow: Vorbereitung, Freigabe und simuliertes Senden ohne echte ERP-Buchung.
      </p>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <section className="grid gap-2 rounded border border-slate-200 p-3">
        <h2 className="text-base font-medium">Transfer anlegen</h2>
        <form className="grid gap-2" onSubmit={handleCreate}>
          <Input value={orderId} onChange={(event) => setOrderId(event.target.value)} required />
          <Input
            value={materialArticleNumber}
            onChange={(event) => setMaterialArticleNumber(event.target.value)}
            required
          />
          <Input
            type="number"
            min={1}
            value={requestedByUserId}
            onChange={(event) => setRequestedByUserId(event.target.value)}
            required
          />
          <Input
            value={payloadRaw}
            onChange={(event) => setPayloadRaw(event.target.value)}
            placeholder='{"key":"value"}'
          />
          <Button type="submit" disabled={!canLeitungPlus || actionLoading !== null}>
            {actionLoading === "create" ? "Erstelle..." : "Transfer erstellen"}
          </Button>
          {!canLeitungPlus ? (
            <p className="text-xs text-slate-600">Erstellen erfordert Rolle Leitung oder Admin.</p>
          ) : null}
        </form>
      </section>

      <section className="grid gap-2 rounded border border-slate-200 p-3">
        <h2 className="text-base font-medium">Statusaktionen</h2>
        <Input
          type="number"
          min={1}
          value={actingUserId}
          onChange={(event) => setActingUserId(event.target.value)}
          placeholder="acting_user_id"
          required
        />
        <Input
          value={failureReason}
          onChange={(event) => setFailureReason(event.target.value)}
          placeholder="Fehlergrund fuer fail"
        />
      </section>

      <section className="grid gap-2">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-medium">ERP-Transfer-Requests</h2>
          <Button onClick={() => void loadTransfers()} disabled={loading || actionLoading !== null}>
            {loading ? "Laedt..." : "Liste aktualisieren"}
          </Button>
        </div>
        {loading ? <p className="text-sm text-slate-600">Transfers werden geladen...</p> : null}
        <ul className="grid gap-2">
          {!loading && transfers.length === 0 ? (
            <li className="rounded border border-dashed border-slate-300 p-3 text-sm text-slate-600">
              Keine ERP-Transfer-Vorgaenge vorhanden.
            </li>
          ) : null}
          {transfers.map((transfer) => (
            <li key={transfer.id} className="grid gap-1 rounded border border-slate-200 p-3 text-sm">
              <p className="font-medium">
                #{transfer.id} | Status: {transfer.status}
              </p>
              <p>Auftrag: {transfer.order_id}</p>
              <p>Material: {transfer.material_article_number}</p>
              <p>Angelegt von User: {transfer.requested_by_user_id}</p>
              <p>Angelegt am: {transfer.created_at}</p>
              <p>Ready am: {transfer.ready_at ?? "-"}</p>
              <p>Approved am: {transfer.approved_at ?? "-"}</p>
              <p>Sent am: {transfer.sent_at ?? "-"}</p>
              <p>Failed am: {transfer.failed_at ?? "-"}</p>
              <p>Fehlergrund: {transfer.failure_reason ?? "-"}</p>
              <p>Approved von User: {transfer.approved_by_user_id ?? "-"}</p>
              <div className="flex flex-wrap gap-2 pt-1">
                <Button
                  disabled={!canLeitungPlus || actionLoading !== null}
                  onClick={() => void handleMarkReady(transfer.id)}
                >
                  {actionLoading === `ready:${transfer.id}` ? "Laeuft..." : "Als ready markieren"}
                </Button>
                <Button
                  disabled={!canLeitungPlus || actionLoading !== null}
                  onClick={() => void handleApprove(transfer.id)}
                >
                  {actionLoading === `approve:${transfer.id}` ? "Laeuft..." : "Freigeben"}
                </Button>
                <Button disabled={!canAdmin || actionLoading !== null} onClick={() => void handleMarkSent(transfer.id)}>
                  {actionLoading === `sent:${transfer.id}` ? "Laeuft..." : "Send simulieren"}
                </Button>
                <Button
                  disabled={!canLeitungPlus || actionLoading !== null}
                  onClick={() => void handleMarkFailed(transfer.id)}
                >
                  {actionLoading === `failed:${transfer.id}` ? "Laeuft..." : "Als failed markieren"}
                </Button>
              </div>
              <EntityComments
                entityType="erp_transfer"
                entityId={String(transfer.id)}
                title={`Kommentare zu Transfer #${transfer.id}`}
              />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
