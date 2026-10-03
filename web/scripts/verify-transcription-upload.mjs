/** TAC3: synthetic 1 GiB browser upload; sample only the Workbench server's RSS. */
import { chromium, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { open, unlink, writeFile } from "node:fs/promises";
import { performance } from "node:perf_hooks";
const path = "/tmp/workbench-phase-t-synthetic/one-gib-synthetic.wav";
const file = await open(path, "w");
await file.write("#fake:slow 60\n");
await file.truncate(1024 ** 3);
await file.close();
const pid = execFileSync("lsof", ["-t", "-iTCP:8787", "-sTCP:LISTEN"], { encoding: "utf8" }).trim();
const rss = () => Number(execFileSync("ps", ["-p", pid, "-o", "rss="], { encoding: "utf8" }).trim()) / 1024;
const browser = await chromium.launch();
const context = await browser.newContext({ baseURL: "http://127.0.0.1:8787", viewport: { width: 1440, height: 900 } });
const page = await context.newPage();
await page.addInitScript(() => {
  window.syntheticUploadProgress = [];
  addEventListener("DOMContentLoaded", () => new MutationObserver(() => {
    const match = document.body.innerText.match(/Uploading (\d+)%/);
    if (match) window.syntheticUploadProgress.push(Number(match[1]));
  }).observe(document.body, { subtree: true, childList: true, characterData: true }));
});
let sampler;
try {
  await page.goto("http://127.0.0.1:8787/");
  await expect(page.getByRole("button", { name: "Choose model", exact: true })).toContainText("fake-chat");
  const baseline = rss();
  let peak = baseline, samples = 0;
  sampler = setInterval(() => { peak = Math.max(peak, rss()); samples++; }, 50);
  const cdp = await context.newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: 40 * 1024 ** 2 });
  const started = performance.now();
  const response = page.waitForResponse((response) => response.url().endsWith("/api/attachments") && response.request().method() === "POST", { timeout: 120000 });
  await page.locator('input[type="file"]').setInputFiles(path);
  const upload = await response;
  clearInterval(sampler);
  if (upload.status() !== 201) throw new Error(`Upload returned ${upload.status()}`);
  const item = await upload.json();
  const progress = await page.evaluate(() => [...new Set(window.syntheticUploadProgress)]);
  const result = {
    synthetic: true, bytes: 1024 ** 3, upload_seconds: (performance.now() - started) / 1000,
    measurement: "ps -p <uvicorn pid> -o rss= every 50 ms during Chromium XHR upload; network throttled to 40 MiB/s",
    baseline_rss_mib: baseline, peak_rss_mib: peak, growth_mib: peak - baseline,
    samples, observed_chip_percentages: progress,
    passed: peak - baseline < 100 && progress.some((value) => value > 0 && value < 100),
  };
  await writeFile("../artifacts/phase-t/upload-memory.json", JSON.stringify(result, null, 2) + "\n");
  await context.request.post(`/api/attachments/${item.id}/cancel`, { data: {} });
  await context.request.delete(`/api/attachments/${item.id}`);
  if (!result.passed) throw new Error("Upload memory or progress acceptance failed");
  console.log(JSON.stringify(result));
} finally {
  clearInterval(sampler);
  await browser.close();
  await unlink(path);
}
