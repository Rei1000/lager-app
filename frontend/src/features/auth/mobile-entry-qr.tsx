"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import QRCode from "qrcode";

import { resolveMobileAppUrl } from "@/lib/mobile-entry-url";

export function MobileEntryQr() {
  const targetUrl = resolveMobileAppUrl({
    envUrl: process.env.NEXT_PUBLIC_MOBILE_APP_URL,
  });
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [isFailed, setIsFailed] = useState(false);

  useEffect(() => {
    let isActive = true;
    void QRCode.toDataURL(targetUrl, {
      width: 180,
      margin: 1,
      errorCorrectionLevel: "M",
    })
      .then((value: string) => {
        if (!isActive) {
          return;
        }
        setQrDataUrl(value);
      })
      .catch(() => {
        if (!isActive) {
          return;
        }
        setIsFailed(true);
      });

    return () => {
      isActive = false;
    };
  }, [targetUrl]);

  return (
    <section className="rounded-md border border-dashed border-slate-300 p-3 text-sm text-slate-700">
      <p className="font-medium text-slate-800">Mobile Version oeffnen</p>
      <p className="pt-1 text-xs text-slate-600">Mit Smartphone scannen.</p>
      <div className="pt-3">
        {qrDataUrl && !isFailed ? (
          <img
            src={qrDataUrl}
            alt="QR-Code fuer mobilen Einstieg zur Login-Seite"
            className="h-[180px] w-[180px] rounded border border-slate-200 bg-white p-1"
          />
        ) : (
          <p className="text-xs text-slate-600">
            QR-Code aktuell nicht verfuegbar. Login kann normal fortgesetzt werden.
          </p>
        )}
      </div>
      <p className="pt-3 text-xs text-slate-500 break-all">
        Ziel-URL:{" "}
        <Link href={targetUrl} className="underline underline-offset-2">
          {targetUrl}
        </Link>
      </p>
    </section>
  );
}
