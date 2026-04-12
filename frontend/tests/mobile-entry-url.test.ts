import { describe, expect, it } from "vitest";

import { resolveMobileAppUrl } from "@/lib/mobile-entry-url";

describe("resolveMobileAppUrl", () => {
  it("uses environment URL when provided", () => {
    const url = resolveMobileAppUrl({
      envUrl: "https://mobile.example.com/login",
    });
    expect(url).toBe("https://mobile.example.com/login");
  });

  it("appends login path when env URL only contains origin", () => {
    const url = resolveMobileAppUrl({
      envUrl: "https://mobile.example.com/",
    });
    expect(url).toBe("https://mobile.example.com/login");
  });

  it("falls back to default when env URL is invalid", () => {
    const url = resolveMobileAppUrl({
      envUrl: "not-a-url",
    });
    expect(url).toBe("http://localhost:3001/login");
  });

  it("falls back to local default when everything else is missing", () => {
    const url = resolveMobileAppUrl({
      envUrl: "",
    });
    expect(url).toBe("http://localhost:3001/login");
  });
});
