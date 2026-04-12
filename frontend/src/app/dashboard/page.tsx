import { PageShell } from "@/components/shared/page-shell";
import { DashboardOverview } from "@/features/dashboard/dashboard-overview";

export default function DashboardPage() {
  return (
    <PageShell title="Dashboard">
      <DashboardOverview />
    </PageShell>
  );
}
