import { PageShell } from "@/components/shared/page-shell";
import { AdminPanel } from "@/features/admin/admin-panel";

export default function AdminPage() {
  return (
    <PageShell title="Admin">
      <AdminPanel />
    </PageShell>
  );
}
