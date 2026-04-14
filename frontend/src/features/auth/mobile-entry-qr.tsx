"use client";

import Link from "next/link";
import { useMemo } from "react";
import QRCode from "qrcode";

import { resolveMobileAppUrl } from "@/lib/mobile-entry-url";

function buildQrSvgDataUrl(targetUrl: string): string {
  const margin = 1;
  const qr = QRCode.create(targetUrl, { errorCorrectionLevel: "M" });
  const moduleCount = qr.modules.size;
  const viewBoxSize = moduleCount + margin * 2;

  let path = "";
  for (let row = 0; row < moduleCount; row += 1) {
    for (let col = 0; col < moduleCount; col += 1) {
      if (!qr.modules.get(row, col)) {
        continue;
      }
      path += `M${col + margin} ${row + margin}h1v1H${col + margin}z`;
    }
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${viewBoxSize} ${viewBoxSize}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="white"/><path fill="black" d="${path}"/></svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

export function MobileEntryQr() {
  const targetUrl = resolveMobileAppUrl({
    envUrl: process.env.NEXT_PUBLIC_MOBILE_APP_URL,
  });
  const qrDataUrl = useMemo(() => {
    try {
      return buildQrSvgDataUrl(targetUrl);
    } catch {
      return null;
    }
  }, [targetUrl]);

  return (
    <section className="rounded-md border border-dashed border-slate-300 p-3 text-sm text-slate-700">
      <p className="font-medium text-slate-800">Mobile Version oeffnen</p>
      <p className="pt-1 text-xs text-slate-600">Mit Smartphone scannen.</p>
      <div className="pt-3">
        {qrDataUrl ? (
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
