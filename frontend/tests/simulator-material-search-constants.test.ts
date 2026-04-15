import { describe, expect, it } from "vitest";

import {
  matchesArticleNumberSimulatorFilters,
  matchesSimulatorMaterialFilters,
} from "@/features/orders/simulator-material-search-constants";
import type { SimulatorMaterialSearchDto } from "@/lib/types";

function row(material_no: string, description = "x"): SimulatorMaterialSearchDto {
  return {
    material_no,
    description,
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

describe("matchesSimulatorMaterialFilters", () => {
  it("laesst alle Treffer zu, wenn keine Filter gesetzt sind", () => {
    const item = row("100-FE-010");
    expect(
      matchesSimulatorMaterialFilters(item, { mainGroup: "", material: "", dimension: "" })
    ).toBe(true);
  });

  it("filtert nach Hauptgruppe", () => {
    const item = row("200-AL-025");
    expect(
      matchesSimulatorMaterialFilters(item, { mainGroup: "200", material: "", dimension: "" })
    ).toBe(true);
    expect(
      matchesSimulatorMaterialFilters(item, { mainGroup: "100", material: "", dimension: "" })
    ).toBe(false);
  });

  it("filtert nach Werkstoff und Dimension", () => {
    const item = row("300-CU-050");
    expect(
      matchesSimulatorMaterialFilters(item, {
        mainGroup: "",
        material: "CU",
        dimension: "050",
      })
    ).toBe(true);
    expect(
      matchesSimulatorMaterialFilters(item, {
        mainGroup: "",
        material: "FE",
        dimension: "050",
      })
    ).toBe(false);
  });
});

describe("matchesArticleNumberSimulatorFilters", () => {
  it("verhaelt sich wie matchesSimulatorMaterialFilters fuer dieselbe Nummer", () => {
    const filters = { mainGroup: "400", material: "FE", dimension: "" };
    expect(matchesArticleNumberSimulatorFilters("400-FE-025", filters)).toBe(true);
    expect(matchesArticleNumberSimulatorFilters("100-FE-025", filters)).toBe(false);
  });
});
