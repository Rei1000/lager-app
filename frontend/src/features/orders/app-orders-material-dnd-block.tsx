"use client";

import type { ReactNode } from "react";

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

import { cn } from "@/lib/utils";
import type { OrderDto } from "@/lib/types";

export type AppOrdersMaterialDndBlockProps = {
  materialArticleNumber: string;
  sequence: OrderDto[];
  /** Gesamte Sequenz gesperrt (z. B. globales Speichern). */
  reorderDisabled: boolean;
  /** Ob diese Zeile optisch abgeschwaecht ist (Filter trifft nicht zu). */
  isOrderDimmed: (order: OrderDto) => boolean;
  renderCard: (ctx: { order: OrderDto; positionLabel: string }) => ReactNode;
  onDragEndReorder: (orderedIds: string[]) => Promise<void>;
};

function SortableAppOrderItem({
  order,
  dimmed,
  reorderDisabled,
  children,
}: {
  order: OrderDto;
  dimmed: boolean;
  reorderDisabled: boolean;
  children: ReactNode;
}) {
  const id = order.order_id ?? "";
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
    disabled: !id || reorderDisabled,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const dragDisabled = !id || reorderDisabled;

  return (
    <li
      ref={setNodeRef}
      style={style}
      className={cn(
        "flex gap-3 rounded border border-emerald-200 bg-emerald-50/40 p-3 text-sm sm:p-4",
        "cursor-default",
        dimmed && "opacity-70",
        isDragging && "z-20 opacity-90 shadow-lg ring-2 ring-emerald-500/30",
        reorderDisabled && "opacity-90"
      )}
    >
      <button
        type="button"
        className={cn(
          "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded border border-emerald-300/70 bg-emerald-100/90 text-emerald-950 shadow-sm",
          "touch-none select-none",
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
      <div className="min-w-0 flex-1 cursor-default">{children}</div>
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
}: AppOrdersMaterialDndBlockProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const ids = sequence.map((o) => o.order_id).filter((id): id is string => Boolean(id));

  async function handleDragEnd(event: DragEndEvent) {
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
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={(e) => void handleDragEnd(e)}>
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <ul className="grid gap-2">
          {sequence.map((order, index) => {
            const posLabel = `${index + 1} von ${sequence.length}`;
            const oid = order.order_id ?? "";
            return (
              <SortableAppOrderItem
                key={oid || `${materialArticleNumber}-${index}`}
                order={order}
                dimmed={isOrderDimmed(order)}
                reorderDisabled={reorderDisabled}
              >
                {renderCard({
                  order,
                  positionLabel: posLabel,
                })}
              </SortableAppOrderItem>
            );
          })}
        </ul>
      </SortableContext>
    </DndContext>
  );
}
