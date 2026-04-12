import { PageShell } from "@/components/shared/page-shell";
import { InventoryPanel } from "@/features/inventory/inventory-panel";

export default function InventoryPage() {
  return (
    <PageShell title="Inventur">
      <InventoryPanel />
    </PageShell>
  );
}
