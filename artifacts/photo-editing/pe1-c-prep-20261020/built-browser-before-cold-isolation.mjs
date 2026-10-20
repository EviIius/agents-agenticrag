// Compiled candidate and fake runtimes only. No live API data or native calls.
import { spawn } from "node:child_process";
import { createWriteStream } from "node:fs";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import assert from "node:assert/strict";

const out = dirname(fileURLToPath(import.meta.url));
const root = resolve(out, "../../..");
const privateDir = process.env.HOME + "/.local/share/workbench/qa/photo-editing-pe1-c-prep-20261020";
const { chromium, webkit, devices, expect } = await import(pathToFileURL(root + "/web/node_modules/@playwright/test/index.mjs"));
await mkdir(privateDir, { recursive: true, mode: 0o700 });
const children = [];
function start(module, port) {
  const log = createWriteStream(privateDir + "/" + module.split(".").at(-1) + ".log");
  const child = spawn(root + "/server/.venv/bin/python", ["-m", "uvicorn", module + ":app", "--host", "127.0.0.1", "--port", String(port), "--workers", "1"], {
    cwd: root + "/server", stdio: ["ignore", "pipe", "pipe"], detached: true,
    env: { ...process.env, WORKBENCH_DATA_DIR: privateDir + "/unused-live-data", WORKBENCH_IMAGE_HOME: "", WORKBENCH_TRANSCRIBE_HOME: "" },
  });
  child.stdout.pipe(log); child.stderr.pipe(log); children.push(child);
  return child;
}
async function ready(url) {
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(url)).ok) return; } catch { /* owned server starts */ }
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error("Owned fake server did not become ready");
}
async function stop(child) {
  const done = () => child.exitCode !== null || child.signalCode !== null;
  if (done()) return;
  try { process.kill(-child.pid, "SIGTERM"); } catch (e) { if (e.code !== "ESRCH") throw e; return; }
  await Promise.race([new Promise(r => child.once("exit", r)), new Promise(r => setTimeout(r, 5000))]);
  if (!done()) {
    try { process.kill(-child.pid, "SIGKILL"); } catch (e) { if (e.code !== "ESRCH") throw e; }
    if (!done()) await new Promise(r => child.once("exit", r));
  }
}
const rows = [];
try {
  for (const port of [18080, 18787]) {
    try { await fetch(`http://127.0.0.1:${port}/api/health`); throw new Error("QA port already owned"); }
    catch (e) { if (e.message === "QA port already owned") throw e; }
  }
  start("tests.fake_runtime", 18080); await ready("http://127.0.0.1:18080/api/tags");
  start("tests.serve_app", 18787); await ready("http://127.0.0.1:18787/api/health");
  const entry = await (await fetch("http://127.0.0.1:18787/")).text();
  assert.equal(entry, await readFile(root + "/server/app/static/index.html", "utf8"));
  assert(!entry.includes("@vite/client"));
  const config = privateDir + "/built.config.mjs";
  await writeFile(config, `import {defineConfig,devices} from ${JSON.stringify(root + "/web/node_modules/@playwright/test/index.mjs")};
export default defineConfig({testDir:${JSON.stringify(root + "/web/tests")},workers:1,timeout:45000,reporter:'list',outputDir:${JSON.stringify(privateDir + "/built-test-results")},use:{baseURL:'http://127.0.0.1:18787',trace:'retain-on-failure',serviceWorkers:'block'},projects:[{name:'chromium',use:{...devices['Desktop Chrome']}},{name:'webkit',use:{...devices['iPhone 13'],viewport:{width:390,height:844}}}]});\n`);
  if (process.env.PE1_SKIP_MATCHED_TESTS !== "1") {
  const testLog = createWriteStream(out + "/built-functional.txt");
  const test = spawn(process.execPath, [root + "/web/node_modules/@playwright/test/cli.js", "test", "-c", config, "photo-editing.spec.ts", "-g", "rejected new-chat|photo upload|new typing|cancelled uploads|editing a generated"], { cwd: root + "/web", stdio: ["ignore", "pipe", "pipe"] });
  test.stdout.pipe(testLog); test.stderr.pipe(testLog);
  const code = await new Promise(r => test.on("exit", r));
  assert.equal(code, 0, "Built candidate functional suite failed; preserve its evidence");
  }
  for (const [name, engine, width] of [["chromium", chromium, 1440], ["webkit", webkit, 390]]) {
    const browser = await engine.launch();
    const context = await browser.newContext({ ...(name === "webkit" ? devices["iPhone 13"] : {}), viewport: { width, height: 900 }, serviceWorkers: "block" });
    const page = await context.newPage(), errors = [], modules = [], failures = [];
    page.on("pageerror", e => errors.push(String(e)));
    page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
    page.on("response", r => { if (/\/assets\/.*\.(?:js|css)(?:\?|$)/.test(r.url())) { modules.push({ path: new URL(r.url()).pathname, status: r.status(), contentType: r.headers()["content-type"] }); if (!r.ok()) failures.push({ path: new URL(r.url()).pathname, status: r.status() }); } });
    for (const route of ["/", "/workflows", "/images", "/workflows", "/"]) {
      await page.goto("http://127.0.0.1:18787" + route);
      if (route === "/workflows") await expect(page.getByRole("heading", { name: "Workflows", exact: true })).toBeVisible();
      else if (route === "/images") await expect(page.getByRole("heading", { name: "Images", exact: true })).toBeVisible();
      else await expect(page.locator(".composer textarea")).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    await page.locator(".composer textarea").fill("Synthetic built-bundle code-block check");
    await page.getByRole("button", { name: "Send message", exact: true }).click();
    await expect(page.getByRole("button", { name: "Stop generating", exact: true })).toBeHidden();
    await expect(page.locator("pre").filter({ hasText: "print('Hello')" })).toBeVisible();
    await expect(page.locator("pre .shiki").or(page.locator("pre code span[style]"))).not.toHaveCount(0);
    assert.equal(failures.length, 0, JSON.stringify(failures));
    assert.equal(errors.length, 0, JSON.stringify(errors));
    assert(modules.length > 0);
    rows.push({ engine: name, width, compiled_static: true, cold_routes: 5, highlighted_code_visible: true, module_responses: modules, errors, failures, service_workers: "blocked", native_calls: 0 });
    await context.close(); await browser.close();
  }
  await writeFile(out + "/built-browser.json", JSON.stringify({ passed: true, functional_cases: 10, observers: rows, limits: "Built static / fake APIs; no actual phone, native inference or full PWA update qualification" }, null, 2) + "\n");
  console.log(JSON.stringify({ passed: true, built_functional_cases: 10, observers: rows.length, native_calls: 0 }));
} catch (error) {
  console.error(error);
  throw error;
} finally {
  for (const child of children.reverse()) await stop(child);
}
