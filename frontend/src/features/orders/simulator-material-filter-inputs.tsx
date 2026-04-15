"use client";

import { Input } from "@/components/ui/input";

import {
  DIMENSION_OPTIONS,
  MAIN_GROUP_OPTIONS,
  MATERIAL_OPTIONS,
} from "@/features/orders/simulator-material-search-constants";

export type SimulatorMaterialFilterValues = {
  textQuery: string;
  mainGroup: string;
  material: string;
  dimension: string;
};

type SimulatorMaterialFilterInputsProps = {
  values: SimulatorMaterialFilterValues;
  onChange: (next: SimulatorMaterialFilterValues) => void;
  /** z. B. „Volltext“ vs. kein Label-Unterschied */
  textQueryLabel?: string;
  textQueryPlaceholder?: string;
};

export function SimulatorMaterialFilterInputs({
  values,
  onChange,
  textQueryLabel = "Volltext (Artikelnummer oder Beschreibung)",
  textQueryPlaceholder = "z. B. stahl, profil oder 420",
}: SimulatorMaterialFilterInputsProps) {
  function patch(partial: Partial<SimulatorMaterialFilterValues>) {
    onChange({ ...values, ...partial });
  }

  return (
    <div className="grid gap-2">
      <label className="grid gap-1">
        {textQueryLabel}
        <Input
          value={values.textQuery}
          onChange={(e) => patch({ textQuery: e.target.value })}
          placeholder={textQueryPlaceholder}
        />
      </label>
      <div className="grid gap-2 sm:grid-cols-3">
        <label className="grid gap-1" title="Materialgruppe, z. B. 400 = Profilmaterial">
          Hauptgruppe
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={values.mainGroup}
            onChange={(e) => patch({ mainGroup: e.target.value })}
          >
            <option value="">Alle</option>
            {MAIN_GROUP_OPTIONS.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1" title="Werkstoff, z. B. FE = Stahl, AL = Aluminium">
          Material
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={values.material}
            onChange={(e) => patch({ material: e.target.value })}
          >
            <option value="">Alle</option>
            {MATERIAL_OPTIONS.map((materialCode) => (
              <option key={materialCode} value={materialCode}>
                {materialCode}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1" title="Maß in mm, z. B. 025 = 25 mm">
          Dimension
          <select
            className="h-10 rounded-md border border-slate-300 px-3 text-sm"
            value={values.dimension}
            onChange={(e) => patch({ dimension: e.target.value })}
          >
            <option value="">Alle</option>
            {DIMENSION_OPTIONS.map((dimensionCode) => (
              <option key={dimensionCode} value={dimensionCode}>
                {dimensionCode}
              </option>
            ))}
          </select>
        </label>
      </div>
    </div>
  );
}
