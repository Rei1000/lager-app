import { PageShell } from "@/components/shared/page-shell";
import { AdminSimulatorTestPanel } from "@/features/admin/admin-simulator-test-panel";

export default function AdminSimulatorTestPage() {
  return (
    <PageShell title="Admin Simulator Test - Suche">
      <AdminSimulatorTestPanel />
    </PageShell>
  );
}
