"use client";

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";

import {
  AppOrdersMaterialDndBlock,
  type AppOrderRenderContext,
} from "@/features/orders/app-orders-material-dnd-block";
import { useNarrowViewport } from "@/lib/use-narrow-viewport";
import type { OrderDto } from "@/lib/types";
import type { ReactNode } from "react";

function orderSequenceByIds(sequence: OrderDto[], orderedIds: string[]): OrderDto[] {
  const map = new Map<string, OrderDto>();
  for (const o of sequence) {
    if (o.order_id) {
      map.set(o.order_id, o);
    }
  }
  const out: OrderDto[] = [];
  for (const id of orderedIds) {
    const o = map.get(id);
    if (o) {
      out.push(o);
    }
  }
  return out;
}

function idsEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  return a.every((id, i) => id === b[i]);
}

type MobileMaterialReorderSheetProps = {
  materialArticleNumber: string | null;
  sequence: OrderDto[];
  reorderDisabled: boolean;
  isOrderDimmed: (order: OrderDto) => boolean;
  onClose: () => void;
  /** Ein Aufruf mit vollstaendiger ordered_ids-Liste beim Tippen auf Fertig. */
  onCommitReorder: (orderedIds: string[]) => Promise<boolean>;
  onMaterialDragActiveChange?: (materialArticleNumber: string | null) => void;
  renderCard: (ctx: AppOrderRenderContext) => ReactNode;
};

export function MobileMaterialReorderSheet({
  materialArticleNumber,
  sequence,
  reorderDisabled,
  isOrderDimmed,
  onClose,
  onCommitReorder,
  onMaterialDragActiveChange,
  renderCard,
}: MobileMaterialReorderSheetProps) {
  const titleId = useId();
  const narrow = useNarrowViewport();
  const open = Boolean(materialArticleNumber && sequence.length > 1 && narrow);
  const sequenceRef = useRef(sequence);
  sequenceRef.current = sequence;

  const [localSequence, setLocalSequence] = useState<OrderDto[]>([]);
  const [baselineIds, setBaselineIds] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  useLayoutEffect(() => {
    if (!open || !materialArticleNumber) {
      return;
    }
    const s = sequenceRef.current;
    if (s.length < 2) {
      return;
    }
    setLocalSequence([...s]);
    setBaselineIds(s.map((o) => o.order_id).filter((id): id is string => Boolean(id)));
  }, [open, materialArticleNumber]);

  const displaySequence = localSequence.length > 0 ? localSequence : sequence;

  const currentIds = useMemo(
    () => displaySequence.map((o) => o.order_id).filter((id): id is string => Boolean(id)),
    [displaySequence]
  );

  const isDirty =
    baselineIds.length > 0 && currentIds.length > 0 && !idsEqual(currentIds, baselineIds);

  useEffect(() => {
    if (!open) {
      return;
    }
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!materialArticleNumber || sequence.length < 2 || !narrow) {
    return null;
  }

  async function handleFertig() {
    if (!isDirty || !materialArticleNumber || isSaving || reorderDisabled) {
      return;
    }
    setIsSaving(true);
    try {
      const ok = await onCommitReorder(currentIds);
      if (ok) {
        onClose();
      }
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[90] flex min-h-0 flex-col bg-white sm:hidden"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
    >
      <div className="flex shrink-0 items-start justify-between gap-2 border-b border-slate-100 px-2 py-2.5">
        <div className="min-w-0 pr-1">
          <h2 id={titleId} className="text-sm font-semibold text-slate-900">
            Reihenfolge aendern
          </h2>
          <p className="mt-0.5 text-[11px] leading-snug text-slate-600">
            Material <span className="break-all font-mono text-slate-800">{materialArticleNumber}</span> — per Griff
            sortieren, mit <strong>Fertig</strong> speichern.
          </p>
          {!isDirty && baselineIds.length > 0 ? (
            <p className="mt-1 text-[10px] text-slate-500">Noch keine Aenderung an der Reihenfolge.</p>
          ) : null}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          <button
            type="button"
            className="rounded-md px-2 py-1 text-xs font-medium text-slate-600 touch-manipulation hover:bg-slate-100"
            onClick={onClose}
          >
            Abbrechen
          </button>
          <button
            type="button"
            className="rounded-lg border border-emerald-700 bg-emerald-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm touch-manipulation hover:bg-emerald-700 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-200 disabled:text-slate-500 disabled:shadow-none"
            disabled={!isDirty || reorderDisabled || isSaving}
            onClick={() => void handleFertig()}
          >
            {isSaving ? "Speichern …" : "Fertig"}
          </button>
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-y-contain px-2 pb-3 touch-pan-y">
        <div className="mx-auto w-full max-w-[17.5rem]">
          <AppOrdersMaterialDndBlock
            materialArticleNumber={materialArticleNumber}
            sequence={displaySequence}
            reorderDisabled={reorderDisabled}
            isOrderDimmed={isOrderDimmed}
            renderCard={renderCard}
            onDragEndReorder={async (nextIds) => {
              setLocalSequence((prev) => orderSequenceByIds(prev.length > 0 ? prev : sequenceRef.current, nextIds));
            }}
            onMaterialDragActiveChange={onMaterialDragActiveChange}
            reorderUiMode="mobileSheet"
            listContainerClassName="min-h-0"
          />
        </div>
      </div>
    </div>
  );
}
