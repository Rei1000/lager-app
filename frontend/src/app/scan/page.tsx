import { PageShell } from "@/components/shared/page-shell";
import { ScanLookupPanel } from "@/features/scan/scan-lookup-panel";

export default function ScanPage() {
  return (
    <PageShell title="Scan / Materialsuche">
      <ScanLookupPanel />
    </PageShell>
  );
}
