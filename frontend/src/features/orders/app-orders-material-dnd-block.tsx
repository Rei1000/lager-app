"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  type DragEndEvent,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import { useNarrowViewport } from "@/lib/use-narrow-viewport";
import { cn } from "@/lib/utils";
import type { OrderDto } from "@/lib/types";

export type AppOrderRenderContext = {
  order: OrderDto;
  positionLabel: string;
  /** Nur während Drag: andere Karten dieser Sequenz visuell kompakter (Mobile). */
  dragPeerCompact: boolean;
  /** Gezogenes Item auf schmalen Viewports / im Mobile-Sortier-Sheet: vereinfachte Drag-Darstellung. */
  dragActiveSimplified: boolean;
  /** Inline-Liste (Desktop) vs. fokussiertes Mobile-Sortier-Sheet. */
  reorderUiMode: "default" | "mobileSheet";
};

export type AppOrdersMaterialDndBlockProps = {
  materialArticleNumber: string;
  sequence: OrderDto[];
  /** Gesamte Sequenz gesperrt (z. B. globales Speichern). */
  reorderDisabled: boolean;
  /** Ob diese Zeile optisch abgeschwaecht ist (Filter trifft nicht zu). */
  isOrderDimmed: (order: OrderDto) => boolean;
  renderCard: (ctx: AppOrderRenderContext) => ReactNode;
  onDragEndReorder: (orderedIds: string[]) => Promise<void>;
  /** Während Drag: welches Material aktiv ist (null = kein Drag). */
  onMaterialDragActiveChange?: (materialArticleNumber: string | null) => void;
  /** Mobile-Sortier-Sheet: kompakte Zeilen und gleiche Drag-Darstellung wie schmaler Viewport. */
  reorderUiMode?: "default" | "mobileSheet";
  /** Optionaler Wrapper um die Liste (z. B. lokaler Scroll im Sheet). */
  listContainerClassName?: string;
};

function SortableAppOrderItem({
  order,
  dimmed,
  reorderDisabled,
  sessionActive,
  positionLabel,
  renderCard,
  reorderUiMode,
  dropFlash,
}: {
  order: OrderDto;
  dimmed: boolean;
  reorderDisabled: boolean;
  sessionActive: boolean;
  positionLabel: string;
  renderCard: (ctx: AppOrderRenderContext) => ReactNode;
  reorderUiMode: "default" | "mobileSheet";
  dropFlash: boolean;
}) {
  const id = order.order_id ?? "";
  const narrow = useNarrowViewport();
  const compactDragVisual = narrow || reorderUiMode === "mobileSheet";
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
    disabled: !id || reorderDisabled,
  });

  const dndTransform = CSS.Transform.toString(transform);
  /** dnd-kit setzt transform inline — Skalierung muss mit merged werden (Tailwind-scale greift sonst nicht). */
  const style = {
    transform: isDragging
      ? compactDragVisual
        ? `${dndTransform} scale(0.56)`
        : `${dndTransform} scale(0.98)`
      : dndTransform,
    transition,
    ...(isDragging && compactDragVisual ? ({ transformOrigin: "center top" } as const) : {}),
  };

  const dragDisabled = !id || reorderDisabled;
  const peerCompact = sessionActive && !isDragging;
  const dragActiveSimplified = Boolean(isDragging && compactDragVisual);
  const card = renderCard({
    order,
    positionLabel,
    dragPeerCompact: peerCompact,
    dragActiveSimplified,
    reorderUiMode,
  });

  return (
    <li
      ref={setNodeRef}
      style={style}
      className={cn(
        "flex rounded border border-emerald-200 bg-emerald-50/40 text-sm transition-[padding,opacity,gap,transform,box-shadow] duration-150",
        reorderUiMode === "mobileSheet"
          ? "gap-1.5 px-2 py-1.5 text-xs sm:gap-3 sm:p-4"
          : "gap-2 p-2.5 sm:gap-3 sm:p-4",
        "cursor-default",
        dimmed && "opacity-70",
        peerCompact &&
          (reorderUiMode === "mobileSheet"
            ? "gap-1.5 py-1 pl-1.5 pr-2 opacity-[0.88]"
            : "max-sm:gap-1.5 max-sm:py-1.5 max-sm:pl-2 max-sm:pr-2 max-sm:opacity-[0.88]"),
        isDragging &&
          cn(
            "z-40 shadow-2xl ring-2 ring-emerald-500/60",
            "opacity-90",
            reorderUiMode === "mobileSheet"
              ? "gap-1 p-1.5 opacity-[0.92]"
              : "max-sm:gap-1 max-sm:p-1.5 max-sm:opacity-[0.92]",
            "sm:opacity-95 sm:shadow-xl sm:ring-emerald-500/35"
          ),
        reorderUiMode === "mobileSheet" && !isDragging && "py-1.5",
        dropFlash && "ring-2 ring-emerald-500/55 transition-shadow duration-200",
        reorderDisabled && "opacity-90"
      )}
    >
      <button
        type="button"
        className={cn(
          "mt-0.5 flex shrink-0 items-center justify-center rounded-lg border text-emerald-950 shadow-sm transition-transform",
          reorderUiMode === "mobileSheet"
            ? "border-emerald-700/90 bg-emerald-200/95 ring-1 ring-emerald-800/20 h-9 w-9 min-h-10 min-w-10 sm:h-9 sm:w-9 sm:min-h-0 sm:min-w-0"
            : "border-emerald-300/70 bg-emerald-100/90 h-11 w-11 min-h-[44px] min-w-[44px] sm:h-9 sm:w-9 sm:min-h-0 sm:min-w-0",
          isDragging &&
            compactDragVisual &&
            "max-sm:mt-0 max-sm:h-8 max-sm:w-8 max-sm:min-h-[32px] max-sm:min-w-[32px]",
          reorderUiMode === "mobileSheet" && isDragging && "mt-0 h-8 w-8 min-h-[32px] min-w-[32px]",
          peerCompact &&
            (reorderUiMode === "mobileSheet"
              ? "h-10 w-10 min-h-[40px] min-w-[40px]"
              : "max-sm:h-10 max-sm:w-10 max-sm:min-h-[40px] max-sm:min-w-[40px]"),
          "touch-none select-none touch-manipulation",
          dragDisabled
            ? "cursor-not-allowed opacity-50"
            : "cursor-grab active:cursor-grabbing"
        )}
        aria-label="Reihenfolge per Ziehen aendern"
        disabled={dragDisabled}
        {...(dragDisabled ? {} : listeners)}
        {...(dragDisabled ? {} : attributes)}
      >
        <span
          aria-hidden
          className="grid grid-cols-2 gap-x-0.5 gap-y-px text-[5px] leading-none text-emerald-900"
        >
          <span className="block h-1 w-1 rounded-full bg-current" />
          <span className="block h-1 w-1 rounded-full bg-current" />
          <span className="block h-1 w-1 rounded-full bg-current" />
          <span className="block h-1 w-1 rounded-full bg-current" />
          <span className="block h-1 w-1 rounded-full bg-current" />
          <span className="block h-1 w-1 rounded-full bg-current" />
        </span>
      </button>
      <div className="min-w-0 flex-1 cursor-default">{card}</div>
    </li>
  );
}

export function AppOrdersMaterialDndBlock({
  materialArticleNumber,
  sequence,
  reorderDisabled,
  isOrderDimmed,
  renderCard,
  onDragEndReorder,
  onMaterialDragActiveChange,
  reorderUiMode = "default",
  listContainerClassName,
}: AppOrdersMaterialDndBlockProps) {
  const [sessionActive, setSessionActive] = useState(false);
  const [dropFlashId, setDropFlashId] = useState<string | null>(null);
  const dropFlashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (dropFlashTimerRef.current) {
        clearTimeout(dropFlashTimerRef.current);
      }
    };
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const ids = sequence.map((o) => o.order_id).filter((id): id is string => Boolean(id));

  function notifyDragEnd() {
    setSessionActive(false);
    onMaterialDragActiveChange?.(null);
  }

  async function handleDragEnd(event: DragEndEvent) {
    notifyDragEnd();
    const { active, over } = event;
    if (!over || active.id === over.id) {
      return;
    }
    const oldIndex = ids.indexOf(String(active.id));
    const newIndex = ids.indexOf(String(over.id));
    if (oldIndex < 0 || newIndex < 0) {
      return;
    }
    const nextIds = arrayMove(ids, oldIndex, newIndex);
    await onDragEndReorder(nextIds);
    if (reorderUiMode === "mobileSheet") {
      const movedId = String(active.id);
      if (dropFlashTimerRef.current) {
        clearTimeout(dropFlashTimerRef.current);
      }
      setDropFlashId(movedId);
      dropFlashTimerRef.current = setTimeout(() => {
        setDropFlashId(null);
        dropFlashTimerRef.current = null;
      }, 280);
    }
  }

  const dndTree = (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      autoScroll={{
        acceleration: 14,
        interval: 4,
        threshold: { x: 0.2, y: 0.18 },
      }}
      onDragStart={() => {
        setSessionActive(true);
        onMaterialDragActiveChange?.(materialArticleNumber);
      }}
      onDragEnd={(e) => void handleDragEnd(e)}
      onDragCancel={() => {
        notifyDragEnd();
      }}
    >
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <ul
          className={cn(
            "grid transition-[gap] duration-150",
            sessionActive
              ? reorderUiMode === "mobileSheet"
                ? "gap-1.5"
                : "max-sm:gap-1 sm:gap-2"
              : "gap-2"
          )}
        >
          {sequence.map((order, index) => {
            const posLabel = `${index + 1} von ${sequence.length}`;
            const oid = order.order_id ?? "";
            return (
              <SortableAppOrderItem
                key={oid || `${materialArticleNumber}-${index}`}
                order={order}
                dimmed={isOrderDimmed(order)}
                reorderDisabled={reorderDisabled}
                sessionActive={sessionActive}
                positionLabel={posLabel}
                renderCard={renderCard}
                reorderUiMode={reorderUiMode}
                dropFlash={reorderUiMode === "mobileSheet" && dropFlashId === oid}
              />
            );
          })}
        </ul>
      </SortableContext>
    </DndContext>
  );

  if (listContainerClassName) {
    return <div className={listContainerClassName}>{dndTree}</div>;
  }
  return dndTree;
}
