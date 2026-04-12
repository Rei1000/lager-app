import { describe, expect, it } from "vitest";

import { canUseBrowserScanner, getFirstDetectedCode } from "@/features/scan/scanner-utils";

describe("scanner utils", () => {
  it("extracts first non-empty detected code", () => {
    const value = getFirstDetectedCode([
      { rawValue: "" },
      { rawValue: "  " },
      { rawValue: "QR-123" },
    ]);
    expect(value).toBe("QR-123");
  });

  it("returns null when no detected code exists", () => {
    expect(getFirstDetectedCode([])).toBeNull();
    expect(getFirstDetectedCode([{ rawValue: " " }])).toBeNull();
  });

  it("supports scanner only with mediaDevices and detector", () => {
    const mediaDevices = {
      getUserMedia: async () => new MediaStream(),
    } as MediaDevices;

    expect(canUseBrowserScanner(mediaDevices, class {})).toBe(true);
    expect(canUseBrowserScanner(undefined, class {})).toBe(false);
    expect(canUseBrowserScanner(mediaDevices, null)).toBe(false);
  });
});
