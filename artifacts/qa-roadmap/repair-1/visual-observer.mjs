import { chromium, webkit, devices } from "../../../web/node_modules/@playwright/test/index.mjs";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
const base = fileURLToPath(new URL("./", import.meta.url));
await mkdir(base + "browser", { recursive: true });
const observations = [];
for (const [engine, width] of [[chromium, 1440], [webkit, 390]]) {
  const browser = await engine.launch();
  try {
    const context = await browser.newContext(width === 390
      ? { ...devices["iPhone 13"], viewport: { width, height: 844 } }
      : { viewport: { width, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    let blockedWrites = 0;
    page.on("pageerror", error => errors.push(String(error)));
    await page.route("**/api/**", async route => {
      if (route.request().method() !== "GET") {
        blockedWrites++;
        return route.fulfill({ json: {} });
      }
      return route.continue();
    });
    await page.goto("http://127.0.0.1:5173/design?indicator");
    await page.getByRole("button", { name: "Preview Long thinking", exact: true }).click();
    const warning = page.getByTestId("long-thinking");
    await warning.waitFor({ state: "visible" });
    await warning.scrollIntoViewIfNeeded();
    await warning.screenshot({ path: `${base}browser/long-thinking-detail-${engine.name()}-${width}-synthetic.png`, scale: "css" });
    const bounds = await warning.boundingBox();
    const button = await warning.getByRole("button", { name: "Stop reply", exact: true }).boundingBox();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    // Mobile targets are 44 px via globals.css; the desktop primitive is 36 px.
    const minimum = width === 390 ? 44 : 36;
    observations.push({ engine: engine.name(), width, bounds, stop_button: button,
      minimum_button_height: minimum, overflow, errors, blocked_writes: blockedWrites,
      native_inference_calls: 0 });
    await writeFile(base + "visual-observer.json", JSON.stringify(observations, null, 2) + "\n");
    if (errors.length || overflow || !button || button.height < minimum)
      throw new Error("Visual observer failed: " + JSON.stringify(observations.at(-1)));
  } finally {
    await browser.close();
  }
}
process.stdout.write(JSON.stringify(observations));
