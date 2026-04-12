import type { MaterialLookupDto } from "@/lib/types";

type MaterialSummaryCardProps = {
  material: MaterialLookupDto;
};

export function MaterialSummaryCard({ material }: MaterialSummaryCardProps) {
  return (
    <div className="grid gap-1 rounded border border-slate-200 p-3 text-sm">
      <h3 className="font-medium">Material</h3>
      <p className="pt-1 font-medium">App-Daten</p>
      <p>Artikelnummer: {material.article_number}</p>
      <p>Name: {material.name}</p>
      <p>Profil: {material.profile ?? "-"}</p>
      <p className="pt-1 font-medium">Bestandskontext</p>
      <p>Synchronisierter ERP-Bestand (m): {material.erp_stock_m ?? "-"}</p>
      <p>App-Restbestand (m): {material.rest_stock_m ?? "-"}</p>
    </div>
  );
}
