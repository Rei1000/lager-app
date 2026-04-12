"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EntityComments } from "@/components/comments/entity-comments";
import {
  cancelStockCorrection,
  compareInventory,
  confirmStockCorrection,
  createInventoryCount,
  createStockCorrection,
  fetchInventoryCounts,
  listPhotosForEntity,
  uploadPhoto,
} from "@/lib/api-client";
import { API_BASE_URL } from "@/lib/config";
import type { InventoryCountDto, InventoryDifferenceDto, PhotoDto, StockCorrectionDto } from "@/lib/types";

export function InventoryPanel() {
  const [error, setError] = useState<string | null>(null);
  const [counts, setCounts] = useState<InventoryCountDto[]>([]);
  const [difference, setDifference] = useState<InventoryDifferenceDto | null>(null);
  const [correction, setCorrection] = useState<StockCorrectionDto | null>(null);
  const [countPhotos, setCountPhotos] = useState<PhotoDto[]>([]);
  const [correctionPhotos, setCorrectionPhotos] = useState<PhotoDto[]>([]);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const [materialArticleNumber, setMaterialArticleNumber] = useState("ART-DEMO");
  const [countedStockMm, setCountedStockMm] = useState("10000");
  const [countedByUserId, setCountedByUserId] = useState("1");
  const [comment, setComment] = useState("");
  const [countPhotoFile, setCountPhotoFile] = useState<File | null>(null);
  const [correctionCountId, setCorrectionCountId] = useState("1");
  const [correctionUserId, setCorrectionUserId] = useState("1");
  const [correctionId, setCorrectionId] = useState("1");
  const [correctionPhotoFile, setCorrectionPhotoFile] = useState<File | null>(null);

  function handleError(err: unknown) {
    setError(err instanceof Error ? err.message : "Unbekannter Fehler");
  }

  async function loadCounts() {
    setActionLoading("load-counts");
    setError(null);
    try {
      setCounts(await fetchInventoryCounts());
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCreateCount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionLoading("create-count");
    setError(null);
    try {
      const created = await createInventoryCount({
        material_article_number: materialArticleNumber,
        counted_stock_mm: Number(countedStockMm),
        counted_by_user_id: Number(countedByUserId),
        comment: comment || null,
      });
      if (countPhotoFile) {
        await uploadPhoto({
          entity_type: "inventory_count",
          entity_id: String(created.id),
          file: countPhotoFile,
          comment: comment || null,
        });
      }
      setCounts((current) => [created, ...current]);
      setCorrectionCountId(String(created.id));
      setCountPhotoFile(null);
      setCountPhotos(
        await listPhotosForEntity({
          entity_type: "inventory_count",
          entity_id: String(created.id),
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCompare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionLoading("compare");
    setError(null);
    try {
      const result = await compareInventory({
        material_article_number: materialArticleNumber,
        counted_stock_mm: Number(countedStockMm),
      });
      setDifference(result);
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCreateCorrection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionLoading("create-correction");
    setError(null);
    try {
      const created = await createStockCorrection({
        inventory_count_id: Number(correctionCountId),
        requested_by_user_id: Number(correctionUserId),
        comment: comment || null,
      });
      if (correctionPhotoFile) {
        await uploadPhoto({
          entity_type: "stock_correction",
          entity_id: String(created.id),
          file: correctionPhotoFile,
          comment: comment || null,
        });
      }
      setCorrection(created);
      setCorrectionId(String(created.id));
      setCorrectionPhotoFile(null);
      setCorrectionPhotos(
        await listPhotosForEntity({
          entity_type: "stock_correction",
          entity_id: String(created.id),
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function loadInventoryPhotos() {
    setActionLoading("load-inventory-photos");
    setError(null);
    try {
      setCountPhotos(
        await listPhotosForEntity({
          entity_type: "inventory_count",
          entity_id: correctionCountId,
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function loadCorrectionPhotos() {
    setActionLoading("load-correction-photos");
    setError(null);
    try {
      setCorrectionPhotos(
        await listPhotosForEntity({
          entity_type: "stock_correction",
          entity_id: correctionId,
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleConfirmCorrection() {
    setActionLoading("confirm-correction");
    setError(null);
    try {
      setCorrection(
        await confirmStockCorrection({
          correction_id: Number(correctionId),
          acting_user_id: Number(correctionUserId),
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleCancelCorrection() {
    setActionLoading("cancel-correction");
    setError(null);
    try {
      setCorrection(
        await cancelStockCorrection({
          correction_id: Number(correctionId),
          acting_user_id: Number(correctionUserId),
        })
      );
    } catch (err) {
      handleError(err);
    } finally {
      setActionLoading(null);
    }
  }

  return (
    <div className="grid gap-4 sm:gap-6">
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <section className="grid gap-3 rounded border border-slate-200 p-3 sm:p-4">
        <h2 className="text-lg font-medium">Inventurzaehlungen</h2>
        <Button className="w-full sm:w-auto" onClick={loadCounts} disabled={actionLoading !== null}>
          {actionLoading === "load-counts" ? "Laedt..." : "Liste laden"}
        </Button>
        <ul className="grid gap-1 text-sm">
          {counts.length === 0 ? <li>Keine Inventurvorgaenge vorhanden.</li> : null}
          {counts.map((count) => (
            <li key={count.id}>
              #{count.id} - {count.material_article_number}: Ist {count.counted_stock_mm} / Ref{" "}
              {count.reference_stock_mm} (Diff {count.difference_mm}, {count.status})
            </li>
          ))}
        </ul>
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-3 sm:p-4">
        <h2 className="text-lg font-medium">Neue Zaehlung erfassen</h2>
        <form className="grid gap-2" onSubmit={handleCreateCount}>
          <Input
            value={materialArticleNumber}
            onChange={(event) => setMaterialArticleNumber(event.target.value)}
            placeholder="Materialartikel"
            required
          />
          <Input
            type="number"
            min={0}
            value={countedStockMm}
            onChange={(event) => setCountedStockMm(event.target.value)}
            required
          />
          <Input
            type="number"
            min={1}
            value={countedByUserId}
            onChange={(event) => setCountedByUserId(event.target.value)}
            required
          />
          <Input value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Kommentar" />
          <Input
            type="file"
            accept="image/*"
            onChange={(event) => setCountPhotoFile(event.target.files?.[0] ?? null)}
          />
          <Button className="w-full sm:w-auto" type="submit" disabled={actionLoading !== null}>
            {actionLoading === "create-count" ? "Speichert..." : "Inventur speichern"}
          </Button>
        </form>
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-3 sm:p-4">
        <h2 className="text-lg font-medium">Abweichung vergleichen</h2>
        <form className="grid gap-2" onSubmit={handleCompare}>
          <Button className="w-full sm:w-auto" type="submit" disabled={actionLoading !== null}>
            {actionLoading === "compare" ? "Vergleicht..." : "Bestand vergleichen"}
          </Button>
        </form>
        {difference ? (
          <p className="text-sm">
            Vergleich: {difference.material_article_number} - Diff {difference.difference_mm} (
            {difference.difference_type})
          </p>
        ) : null}
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-3 sm:p-4">
        <h2 className="text-lg font-medium">Korrekturvorgang</h2>
        <form className="grid gap-2" onSubmit={handleCreateCorrection}>
          <Input
            type="number"
            min={1}
            value={correctionCountId}
            onChange={(event) => setCorrectionCountId(event.target.value)}
            placeholder="Inventur-ID"
            required
          />
          <Input
            type="number"
            min={1}
            value={correctionUserId}
            onChange={(event) => setCorrectionUserId(event.target.value)}
            placeholder="User-ID"
            required
          />
          <Button className="w-full sm:w-auto" type="submit" disabled={actionLoading !== null}>
            {actionLoading === "create-correction" ? "Anlegen..." : "Korrektur anlegen"}
          </Button>
        </form>
        <Input
          type="file"
          accept="image/*"
          onChange={(event) => setCorrectionPhotoFile(event.target.files?.[0] ?? null)}
        />
        <div className="grid gap-2 sm:flex">
          <Input
            type="number"
            min={1}
            value={correctionId}
            onChange={(event) => setCorrectionId(event.target.value)}
            placeholder="Korrektur-ID"
            required
          />
          <Button className="w-full sm:w-auto" onClick={handleConfirmCorrection} disabled={actionLoading !== null}>
            {actionLoading === "confirm-correction" ? "Bestaetigt..." : "Korrektur bestaetigen"}
          </Button>
          <Button className="w-full sm:w-auto" onClick={handleCancelCorrection} disabled={actionLoading !== null}>
            {actionLoading === "cancel-correction" ? "Storniert..." : "Korrektur stornieren"}
          </Button>
        </div>
        {correction ? (
          <p className="text-sm">
            Korrektur #{correction.id}: {correction.correction_mm} mm - Status {correction.status}
          </p>
        ) : null}
      </section>

      <section className="grid gap-3 rounded border border-slate-200 p-3 sm:p-4">
        <h2 className="text-lg font-medium">Fotos zu Inventur und Korrektur</h2>
        <div className="flex flex-wrap gap-2">
          <Button className="w-full sm:w-auto" onClick={loadInventoryPhotos} disabled={actionLoading !== null}>
            {actionLoading === "load-inventory-photos" ? "Laedt..." : "Inventurfotos laden"}
          </Button>
          <Button className="w-full sm:w-auto" onClick={loadCorrectionPhotos} disabled={actionLoading !== null}>
            {actionLoading === "load-correction-photos" ? "Laedt..." : "Korrekturfotos laden"}
          </Button>
        </div>
        <div className="grid gap-2 text-sm">
          <p className="font-medium">Inventur-ID {correctionCountId}</p>
          {countPhotos.length === 0 ? <p>Keine Fotos vorhanden.</p> : null}
          {countPhotos.map((photo) => (
            <div key={`count-${photo.id}`} className="rounded border border-slate-200 p-2">
              <p>{photo.original_filename}</p>
              {photo.comment ? <p className="text-slate-600">{photo.comment}</p> : null}
              <img
                className="mt-2 max-h-44 w-full rounded border border-slate-200 object-contain"
                src={`${API_BASE_URL}${photo.file_url}`}
                alt={photo.original_filename}
                loading="lazy"
              />
            </div>
          ))}
        </div>
        <div className="grid gap-2 text-sm">
          <p className="font-medium">Korrektur-ID {correctionId}</p>
          {correctionPhotos.length === 0 ? <p>Keine Fotos vorhanden.</p> : null}
          {correctionPhotos.map((photo) => (
            <div key={`corr-${photo.id}`} className="rounded border border-slate-200 p-2">
              <p>{photo.original_filename}</p>
              {photo.comment ? <p className="text-slate-600">{photo.comment}</p> : null}
              <img
                className="mt-2 max-h-44 w-full rounded border border-slate-200 object-contain"
                src={`${API_BASE_URL}${photo.file_url}`}
                alt={photo.original_filename}
                loading="lazy"
              />
            </div>
          ))}
        </div>
      </section>

      <EntityComments
        entityType="inventory_count"
        entityId={correctionCountId}
        title={`Kommentare zur Inventur-ID ${correctionCountId}`}
      />
      <EntityComments
        entityType="stock_correction"
        entityId={correctionId}
        title={`Kommentare zur Korrektur-ID ${correctionId}`}
      />
    </div>
  );
}
