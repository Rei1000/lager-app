"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EntityComments } from "@/components/comments/entity-comments";
import {
  fetchErpMaterial,
  fetchErpMaterialStock,
  getMaterialByArticleNumber,
  listPhotosForEntity,
  searchMaterials,
  uploadPhoto,
} from "@/lib/api-client";
import { API_BASE_URL } from "@/lib/config";
import { canUseBrowserScanner, getFirstDetectedCode } from "@/features/scan/scanner-utils";
import type { MaterialLookupDto, PhotoDto } from "@/lib/types";

type BarcodeDetectorInstance = {
  detect(source: ImageBitmapSource): Promise<Array<{ rawValue?: string | null }>>;
};

type BarcodeDetectorCtor = new (options?: {
  formats?: string[];
}) => BarcodeDetectorInstance;

export function ScanLookupPanel() {
  const [scanValue, setScanValue] = useState("");
  const [results, setResults] = useState<MaterialLookupDto[]>([]);
  const [selected, setSelected] = useState<MaterialLookupDto | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [erpMaterialPayload, setErpMaterialPayload] = useState<Record<string, unknown> | null>(null);
  const [erpStockPayload, setErpStockPayload] = useState<Record<string, unknown> | null>(null);
  const [erpReadError, setErpReadError] = useState<string | null>(null);
  const [materialPhotos, setMaterialPhotos] = useState<PhotoDto[]>([]);
  const [materialPhotoFile, setMaterialPhotoFile] = useState<File | null>(null);
  const [materialPhotoComment, setMaterialPhotoComment] = useState("");
  const [scannerError, setScannerError] = useState<string | null>(null);
  const [scannerStatus, setScannerStatus] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isScannerSupported, setIsScannerSupported] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const scannerStreamRef = useRef<MediaStream | null>(null);
  const scannerIntervalRef = useRef<number | null>(null);
  const barcodeDetectorRef = useRef<BarcodeDetectorInstance | null>(null);

  function getBarcodeDetectorCtor(): BarcodeDetectorCtor | null {
    if (typeof window === "undefined") {
      return null;
    }
    const ctor = (window as Window & { BarcodeDetector?: BarcodeDetectorCtor }).BarcodeDetector;
    return ctor ?? null;
  }

  useEffect(() => {
    const detectorCtor = getBarcodeDetectorCtor();
    setIsScannerSupported(canUseBrowserScanner(navigator.mediaDevices, detectorCtor));
  }, []);

  function stopScanner(reason: "stopped" | "no_code" | "completed" = "stopped") {
    if (scannerIntervalRef.current !== null) {
      window.clearInterval(scannerIntervalRef.current);
      scannerIntervalRef.current = null;
    }
    if (scannerStreamRef.current) {
      for (const track of scannerStreamRef.current.getTracks()) {
        track.stop();
      }
      scannerStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsScanning(false);
    if (reason === "completed") {
      return;
    }
    if (reason === "no_code") {
      setScannerStatus("Kein Code erkannt. Scan erneut versuchen.");
      return;
    }
    setScannerStatus("Scan gestoppt. Scan erneut versuchen.");
  }

  useEffect(() => () => stopScanner(), []);

  async function executeLookup(rawInput: string) {
    const normalized = rawInput.trim();
    if (!normalized) {
      setMessage("Bitte einen Scan-Wert oder eine Artikelnummer eingeben.");
      setResults([]);
      setSelected(null);
      setError(null);
      setErpReadError(null);
      return;
    }

    setScanValue(normalized);
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const matches = await searchMaterials(normalized);
      setResults(matches);
      if (matches.length === 0) {
        setSelected(null);
        setMessage("Kein Material gefunden.");
      } else if (matches.length === 1) {
        const detailed = await getMaterialByArticleNumber(matches[0].article_number);
        setSelected(detailed);
      } else {
        setSelected(null);
        setMessage("Mehrere Treffer gefunden. Bitte passenden Artikel auswaehlen.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
      setResults([]);
      setSelected(null);
      setErpMaterialPayload(null);
      setErpStockPayload(null);
      setErpReadError(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await executeLookup(scanValue);
  }

  async function handleSelect(articleNumber: string) {
    setError(null);
    setMessage(null);
    try {
      const detailed = await getMaterialByArticleNumber(articleNumber);
      setSelected(detailed);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler");
    }
  }

  useEffect(() => {
    if (!selected?.article_number) {
      setErpMaterialPayload(null);
      setErpStockPayload(null);
      setErpReadError(null);
      setMaterialPhotos([]);
      return;
    }
    const articleNumber = selected.article_number;
    let active = true;
    async function loadErp() {
      try {
        setErpReadError(null);
        const [materialPayload, stockPayload, photos] = await Promise.all([
          fetchErpMaterial(articleNumber),
          fetchErpMaterialStock(articleNumber),
          listPhotosForEntity({ entity_type: "material", entity_id: articleNumber }),
        ]);
        if (!active) {
          return;
        }
        setErpMaterialPayload(materialPayload);
        setErpStockPayload(stockPayload);
        setMaterialPhotos(photos);
      } catch {
        if (active) {
          setErpMaterialPayload(null);
          setErpStockPayload(null);
          setErpReadError("ERP-Read-Daten sind derzeit nicht verfuegbar.");
          setMaterialPhotos([]);
        }
      }
    }
    void loadErp();
    return () => {
      active = false;
    };
  }, [selected?.article_number]);

  async function handleUploadMaterialPhoto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || !materialPhotoFile) {
      return;
    }
    setError(null);
    try {
      await uploadPhoto({
        entity_type: "material",
        entity_id: selected.article_number,
        file: materialPhotoFile,
        comment: materialPhotoComment || null,
      });
      setMaterialPhotoFile(null);
      setMaterialPhotoComment("");
      setMaterialPhotos(
        await listPhotosForEntity({
          entity_type: "material",
          entity_id: selected.article_number,
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Foto konnte nicht hochgeladen werden");
    }
  }

  async function startScanner() {
    setScannerError(null);
    setScannerStatus(null);
    const detectorCtor = getBarcodeDetectorCtor();
    if (!canUseBrowserScanner(navigator.mediaDevices, detectorCtor) || !detectorCtor) {
      setScannerError("Scanner im Browser nicht verfuegbar. Bitte manuell eingeben.");
      setScannerStatus("Scan erneut versuchen oder manuell eingeben.");
      return;
    }
    if (!videoRef.current) {
      setScannerError("Scanner-Vorschau nicht bereit.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      scannerStreamRef.current = stream;
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      barcodeDetectorRef.current = new detectorCtor({
        formats: ["qr_code", "code_128", "ean_13", "ean_8"],
      });
      setIsScanning(true);
      setMessage("Scanner gestartet. Code vor die Kamera halten.");
      setScannerStatus("Scanne...");

      scannerIntervalRef.current = window.setInterval(async () => {
        if (!videoRef.current || !barcodeDetectorRef.current) {
          return;
        }
        try {
          const detections = await barcodeDetectorRef.current.detect(videoRef.current);
          const detected = getFirstDetectedCode(detections);
          if (!detected) {
            return;
          }
          stopScanner("completed");
          setMessage(`Scan erkannt: ${detected}`);
          await executeLookup(detected);
        } catch {
          stopScanner();
          setScannerError("Scan konnte nicht gelesen werden. Bitte erneut versuchen.");
          setScannerStatus("Scan erneut versuchen.");
        }
      }, 700);
    } catch {
      stopScanner();
      setScannerError("Kamerazugriff fehlgeschlagen. Bitte manuell eingeben.");
      setScannerStatus("Scan erneut versuchen oder manuell eingeben.");
    }
  }

  return (
    <div className="grid gap-4">
      <section className="grid gap-2 rounded border border-slate-200 p-3 text-sm sm:p-4">
        <h2 className="text-base font-medium">Barcode-/QR-Scan</h2>
        <p>
          Optionaler Kamera-Scan. Falls nicht verfuegbar, funktioniert die manuelle Eingabe
          unveraendert.
        </p>
        <div className="grid gap-2 sm:flex">
          <Button className="w-full sm:w-auto" onClick={startScanner} disabled={isScanning || !isScannerSupported}>
            Scan starten
          </Button>
          <Button
            className="w-full sm:w-auto"
            onClick={() => stopScanner(isScanning ? "no_code" : "stopped")}
            disabled={!isScanning}
          >
            Scan stoppen
          </Button>
        </div>
        {scannerStatus ? <p className="text-slate-700">{scannerStatus}</p> : null}
        {!isScannerSupported ? (
          <p className="text-slate-600">
            Browser-Scanner nicht unterstuetzt. Bitte manuelle Eingabe verwenden.
          </p>
        ) : null}
        {scannerError ? <p className="text-red-600">{scannerError}</p> : null}
        <video
          ref={videoRef}
          className={`max-h-72 w-full rounded border border-slate-200 bg-black ${isScanning ? "block" : "hidden"}`}
          muted
          playsInline
        />
      </section>

      <form className="grid gap-2" onSubmit={handleLookup}>
        <label className="grid gap-1 text-sm">
          Scan-Wert / Artikelnummer
          <Input
            value={scanValue}
            onChange={(event) => setScanValue(event.target.value)}
            placeholder="z. B. ART-001"
            required
          />
        </label>
        <Button className="w-full sm:w-auto" type="submit" disabled={loading}>
          {loading ? "Suche..." : "Material suchen"}
        </Button>
      </form>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-slate-700">{message}</p> : null}

      {results.length > 1 ? (
        <ul className="grid gap-2 rounded border border-slate-200 p-3 text-sm">
          {results.map((item) => (
            <li key={item.article_number} className="flex items-center justify-between gap-2">
              <span>
                {item.article_number} - {item.name}
              </span>
              <Button onClick={() => handleSelect(item.article_number)}>Details</Button>
            </li>
          ))}
        </ul>
      ) : null}

      {selected ? (
        <section className="grid gap-1 rounded border border-slate-200 p-3 text-sm sm:p-4">
          <h2 className="text-base font-medium">Material gefunden</h2>
          <p className="pt-1 font-medium">App-Daten</p>
          <p>Artikelnummer: {selected.article_number}</p>
          <p>Name: {selected.name}</p>
          <p>Profil: {selected.profile ?? "-"}</p>
          <p>Synchronisierter ERP-Bestand (m): {selected.erp_stock_m ?? "-"}</p>
          <p>App-Restbestand (m): {selected.rest_stock_m ?? "-"}</p>
          <p className="pt-2 font-medium">ERP-Read-Daten (Quelle: ERP)</p>
          {erpReadError ? <p className="text-red-600">{erpReadError}</p> : null}
          {erpMaterialPayload ? (
            <details className="rounded border border-slate-200 p-2">
              <summary className="cursor-pointer font-medium">ERP-Materialdaten anzeigen</summary>
              <pre className="overflow-x-auto pt-2 text-xs">{JSON.stringify(erpMaterialPayload, null, 2)}</pre>
            </details>
          ) : (
            <p>ERP-Materialdaten: nicht verfuegbar</p>
          )}
          {erpStockPayload ? (
            <details className="rounded border border-slate-200 p-2">
              <summary className="cursor-pointer font-medium">ERP-Bestand anzeigen</summary>
              <pre className="overflow-x-auto pt-2 text-xs">{JSON.stringify(erpStockPayload, null, 2)}</pre>
            </details>
          ) : (
            <p>ERP-Bestand: nicht verfuegbar</p>
          )}
          <p className="pt-2">
            Weiterverwendung im Workflow:{" "}
            <Link className="text-blue-700 underline" href="/orders">
              zur Auftragsanlage
            </Link>
          </p>
          <div className="mt-3 grid gap-2 rounded border border-slate-200 p-2">
            <p className="font-medium">Materialfotos</p>
            <form className="grid gap-2" onSubmit={handleUploadMaterialPhoto}>
              <Input
                type="file"
                accept="image/*"
                onChange={(event) => setMaterialPhotoFile(event.target.files?.[0] ?? null)}
              />
              <Input
                value={materialPhotoComment}
                onChange={(event) => setMaterialPhotoComment(event.target.value)}
                placeholder="Kommentar (optional)"
              />
              <Button type="submit" disabled={!materialPhotoFile}>
                Foto hochladen
              </Button>
            </form>
            {materialPhotos.length === 0 ? <p>Keine Fotos vorhanden.</p> : null}
            {materialPhotos.map((photo) => (
              <div key={photo.id} className="rounded border border-slate-200 p-2">
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
          <EntityComments
            entityType="material"
            entityId={selected.article_number}
            title="Kommentare zum Material"
          />
        </section>
      ) : null}
    </div>
  );
}
