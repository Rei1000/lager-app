import type { SimulatorMaterialSearchDto } from "@/lib/types";

export const MAIN_GROUP_OPTIONS = ["100", "200", "300", "400", "410", "420", "430", "440"] as const;
export const MATERIAL_OPTIONS = ["FE", "AL", "CU", "VA", "MS"] as const;
export const DIMENSION_OPTIONS = ["010", "012", "025", "050", "100"] as const;

export type SimulatorSearchFilters = {
  mainGroup: string;
  material: string;
  dimension: string;
};

/** Filtert Simulator-Suchtreffer nach Hauptgruppe / Werkstoff / Dimension (Schema CCC-MM-DDD). */
export function matchesSimulatorMaterialFilters(
  item: SimulatorMaterialSearchDto,
  filters: SimulatorSearchFilters
): boolean {
  const [groupCode, materialCode, dimensionCode] = item.material_no.split("-");
  if (filters.mainGroup && groupCode !== filters.mainGroup) {
    return false;
  }
  if (filters.material && materialCode !== filters.material) {
    return false;
  }
  if (filters.dimension && dimensionCode !== filters.dimension) {
    return false;
  }
  return true;
}

function syntheticSearchRow(materialNo: string): SimulatorMaterialSearchDto {
  return {
    material_no: materialNo,
    description: "",
    profile: null,
    shape: null,
    size_mm: null,
    material_group_code: null,
    material_group: null,
    material_code: null,
    material: null,
    dimension_code: null,
    dimension_mm: null,
    unit: null,
  };
}

/** Gleiche Hauptgruppe/Material/Dimension-Regeln wie bei der Simulator-Suche, angewandt auf eine Artikelnummer. */
export function matchesArticleNumberSimulatorFilters(
  materialArticleNumber: string,
  filters: SimulatorSearchFilters
): boolean {
  return matchesSimulatorMaterialFilters(syntheticSearchRow(materialArticleNumber), filters);
}
