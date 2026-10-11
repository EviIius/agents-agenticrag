// Read-only installed-app measurements. No screenshots, text or model calls.
const { chromium, webkit } = require("../../web/node_modules/@playwright/test");
const fs = require("node:fs");
const crypto = require("node:crypto");

(async () => {
  const result = {
    started_epoch_ms: Date.now(),
    source_sha256: crypto.createHash("sha256").update(fs.readFileSync(__filename)).digest("hex"),
    results: [],
    physical_iphone: false,
  };
  for (const [name, engine, width] of [["chromium", chromium, 1440], ["webkit", webkit, 390]]) {
    const browser = await engine.launch({ headless: true });
    try {
      const page = await browser.newPage({ viewport: { width, height: 844 } });
      let blockedMutationCount = 0;
      await page.route("**/api/**", async (route) => {
        if (!["GET", "HEAD", "OPTIONS"].includes(route.request().method())) {
          blockedMutationCount += 1;
          await route.abort();
        } else {
          await route.continue();
        }
      });
      const start = performance.now();
      const response = await page.goto("http://127.0.0.1:8787/", { waitUntil: "domcontentloaded" });
      const field = page.locator("textarea").first();
      await field.waitFor({ state: "visible", timeout: 10000 });
      const usable_ms = performance.now() - start;
      const focusStarted = performance.now();
      await field.focus();
      const focused = await field.evaluate((el) => document.activeElement === el);
      const focus_ms = performance.now() - focusStarted;
      const frame_deltas_ms = await page.evaluate(() => new Promise((resolve) => {
        const frames = [];
        function frame(t) {
          frames.push(t);
          if (frames.length < 61) requestAnimationFrame(frame);
          else resolve(frames.slice(1).map((value, index) => value - frames[index]));
        }
        requestAnimationFrame(frame);
      }));
      result.results.push({ engine: name, width, http_status: response.status(),
        usable_ms, focused, focus_ms, frame_deltas_ms, blocked_mutation_count: blockedMutationCount });
    } finally {
      await browser.close();
    }
  }
  result.finished_epoch_ms = Date.now();
  fs.writeFileSync("artifacts/image-trial/i1-0/browser-during-trial.json", JSON.stringify(result, null, 2) + "\n", { flag: "wx" });
  if (result.results.some((row) => row.http_status !== 200 || !row.focused || row.blocked_mutation_count))
    throw new Error("Read-only browser qualification failed");
  console.log(JSON.stringify(result.results.map(({ engine, usable_ms, focused }) => ({ engine, usable_ms, focused }))));
})().catch((error) => { console.error(error); process.exitCode = 1; });
