import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { TrafficLightIndicator } from "@/components/shared/traffic-light-indicator";

describe("TrafficLightIndicator", () => {
  it("maps green to Machbar without raw API token in markup", () => {
    const html = renderToStaticMarkup(createElement(TrafficLightIndicator, { trafficLight: "green" }));
    expect(html).toContain("Machbar");
    expect(html).not.toContain("green");
  });

  it("maps yellow to Eingeschraenkt label", () => {
    const html = renderToStaticMarkup(createElement(TrafficLightIndicator, { trafficLight: "yellow" }));
    expect(html).toContain("Eingeschränkt");
  });

  it("includes tooltip title for red", () => {
    const html = renderToStaticMarkup(createElement(TrafficLightIndicator, { trafficLight: "red" }));
    expect(html).toContain("title=");
    expect(html).toContain("Nicht machbar");
  });
});
