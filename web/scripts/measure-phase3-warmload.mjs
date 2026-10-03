// Timing only: never capture screenshots, page text, private responses or console content.
import { chromium, webkit, devices } from "@playwright/test";
import { writeFile } from "node:fs/promises";
const url = "https://jakes-mac-mini.tailc4d343.ts.net/";
const measurements = [];
for (const [name, type, options] of [
  ["chromium", chromium, { viewport: { width: 390, height: 844 } }],
  ["webkit", webkit, devices["iPhone 13"]],
]) {
  const browser = await type.launch();
  try {
    for (let i = 0; i < 3; i++) {
      const context = await browser.newContext(options);
      try {
        const page = await context.newPage();
        await page.goto(url);
        await page.waitForFunction(
          () =>
            performance.getEntriesByName("workbench:time-to-interactive")
              .length > 0,
        );
        const duration = await page.evaluate(
          () =>
            performance.getEntriesByName("workbench:time-to-interactive")[0]
              .duration,
        );
        measurements.push({
          browser: name,
          sample: i + 1,
          interactive_ms: duration,
        });
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
}
await writeFile(
  "../artifacts/phase-3/tailscale-headless-warmload.json",
  JSON.stringify(
    {
      method:
        "fresh browser contexts over actual Tailscale HTTPS, warm server, application readiness mark after bootstrap/models; headless host only",
      physical_iphone_evidence: false,
      target_ms: 1500,
      measurements,
    },
    null,
    2,
  ),
);
