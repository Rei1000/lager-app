import { describe, expect, it } from "vitest";

import { getVisibleNavigationItems } from "@/components/shared/app-chrome";

describe("app chrome navigation", () => {
  it("shows all expected items for admin", () => {
    const items = getVisibleNavigationItems("admin").map((item) => item.label);
    expect(items).toEqual([
      "Dashboard",
      "Orders",
      "Inventur",
      "Scan",
      "ERP-Transfer",
      "Admin",
      "Simulator-Test",
    ]);
  });

  it("shows expected subset for leitung", () => {
    const items = getVisibleNavigationItems("leitung").map((item) => item.label);
    expect(items).toEqual(["Dashboard", "Orders", "Inventur", "ERP-Transfer"]);
  });

  it("shows operative subset for lager", () => {
    const items = getVisibleNavigationItems("lager").map((item) => item.label);
    expect(items).toEqual(["Scan", "Orders", "Inventur"]);
  });

  it("falls back to login for missing role", () => {
    const items = getVisibleNavigationItems(null).map((item) => item.label);
    expect(items).toEqual(["Login"]);
  });
});
