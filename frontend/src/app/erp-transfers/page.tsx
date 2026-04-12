import { PageShell } from "@/components/shared/page-shell";
import { ErpTransferPanel } from "@/features/erp-transfers/erp-transfer-panel";

export default function ErpTransfersPage() {
  return (
    <PageShell title="ERP-Transfer (vorbereitend)">
      <ErpTransferPanel />
    </PageShell>
  );
}
