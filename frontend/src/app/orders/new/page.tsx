import Link from "next/link";

import { PageShell } from "@/components/shared/page-shell";
import { NewOrderPlanningForm } from "@/features/orders/new-order-planning-form";

export default function NewOrderPage() {
  return (
    <PageShell title="Neuer Auftrag">
      <div className="mb-4">
        <Link href="/orders" className="text-sm text-slate-700 underline underline-offset-2 hover:text-slate-900">
          Zurück zur Auftragsübersicht
        </Link>
      </div>
      <p className="mb-4 rounded border border-amber-200 bg-amber-50/80 p-2 text-xs text-amber-950">
        Planung und Prüfung nur im Frontend. Es wird kein Auftrag gespeichert.
      </p>
      <NewOrderPlanningForm />
    </PageShell>
  );
}
