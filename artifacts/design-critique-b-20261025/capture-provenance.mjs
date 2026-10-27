import { createRequire } from "node:module";
import { mkdir, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
const { chromium, webkit } = createRequire(new URL("../../web/package.json", import.meta.url))("playwright");
const out = new URL("./browser/", import.meta.url);
await mkdir(out, { recursive: true });
const results = [];
for (const [engine, launcher] of Object.entries({ chromium, webkit })) {
  const browser = await launcher.launch();
  for (const width of [390, 1440]) for (const theme of ["light", "dark"]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("**/api/images/jobs/*/output/png", route => route.fulfill({ contentType: "image/png", body: readFileSync(new URL("../../web/public/icons/apple-touch-icon.png", import.meta.url)) }));
    await page.goto("http://127.0.0.1:5173/design?chat-state");
    await page.getByRole("button", { name: theme, exact: true }).click();
    await page.getByRole("button", { name: "Aero", exact: true }).click();
    const thread = page.getByTestId("thread");
    await thread.waitFor();
    for (const [state, title] of [["thread", "source"], ["cleared", "source-cleared"]]) {
      await page.getByRole("button", { name: state, exact: true }).click();
      await thread.evaluate((node) => { node.scrollTop = 0; });
      await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const source = page.locator('[data-slot="image-prompt-source"]').first();
      if (state === "thread") {
        await source.getByRole("img").evaluate((node) => node.decode());
        if (!(await source.textContent()).includes("Edit photo")) throw new Error("Edit label missing");
      } else if (!(await source.textContent()).includes("Source photo unavailable")) throw new Error("Unavailable source label missing");
      await page.screenshot({ path: new URL(`${title}-${width}-${theme}-${engine}-fake.png`, out).pathname, fullPage: true });
      results.push({ state, width, theme, engine, pageErrors: errors.length });
    }
    if (errors.length) throw new Error(errors.join("; "));
    await page.close();
  }
  await browser.close();
}
await writeFile(new URL("./provenance-captures.json", import.meta.url), JSON.stringify({ passed: true, cases: results, native_model_calls: 0 }, null, 2) + "\n");
console.log(JSON.stringify({ passed: true, captures: results.length }));
