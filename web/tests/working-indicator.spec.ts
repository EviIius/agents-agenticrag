import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";

const dir = "../artifacts/chat-images/ci-a/browser";
test.use({ video: { mode: "on" } });
const line = (page: Page) =>
  page.locator('[data-slot="working-line"][data-state="open"]');
const word = (page: Page) => line(page).locator(".word-in");
async function preview(page: Page) {
  await page.goto("/design?indicator");
  await expect(
    page.getByRole("heading", { name: "Working indicator" }),
  ).toBeVisible();
}

test("seeded words change at 2.4 seconds while phase announcements stay quiet; Plain persists", async ({
  page,
}) => {
  await page.clock.install();
  await preview(page);
  await page.getByRole("button", { name: "Restart clock" }).click();
  const first = await word(page).textContent();
  await page.clock.runFor(2200);
  await expect(word(page)).toHaveText(first!);
  await page.clock.runFor(400);
  await expect(word(page)).not.toHaveText(first!);
  await expect(line(page).getByRole("status")).toHaveText("Working");
  await page.getByRole("button", { name: "Plain status" }).click();
  await expect(word(page)).toHaveText("Working");
  await page.clock.runFor(5000);
  await expect(word(page)).toHaveText("Working");
  await page.reload();
  await expect(word(page)).toHaveText("Working");
  await page
    .getByRole("button", { name: "Preview Queued", exact: true })
    .click();
  await expect(word(page)).toHaveText(
    "Waiting for Fake runtime · fake-chat · #2 in line",
  );
});

test("ticker keeps geometry, expands the original text, follows until manual scrolling and closes on answer", async ({
  page,
}) => {
  await preview(page);
  await page
    .getByRole("button", { name: "Preview Thinking", exact: true })
    .click();
  const toggle = page.getByRole("button", { name: "Show thinking" });
  await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await expect(
    page.getByRole("region", { name: "Model reasoning" }),
  ).toHaveCount(0);
  const ticker = page.locator(".thought-ticker");
  await settle(page);
  const before = await ticker.boundingBox();
  await page.getByRole("button", { name: "Append thought" }).click();
  await expect(ticker).toContainText("Newest synthetic reasoning");
  expect((await ticker.textContent())!.length).toBeLessThanOrEqual(161);
  const after = await ticker.boundingBox();
  expect(after!.height).toBe(before!.height);
  expect(after!.y).toBe(before!.y);
  await toggle.click();
  const full = page.getByRole("region", { name: "Model reasoning" });
  await expect(full).toBeVisible();
  await settle(page);
  await expect
    .poll(() =>
      full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
    )
    .toBeLessThan(3);
  await full.evaluate((el) => {
    el.scrollTop = 0;
    el.dispatchEvent(new Event("scroll", { bubbles: true }));
  });
  await page.getByRole("button", { name: "Append thought" }).click();
  expect(await full.evaluate((el) => el.scrollTop)).toBe(0);
  await page.getByRole("button", { name: "Hide thinking" }).click();
  await page.getByRole("button", { name: "Show thinking" }).click();
  await settle(page);
  await expect
    .poll(() =>
      full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
    )
    .toBeLessThan(3);
  await page
    .getByRole("button", { name: "Preview Answer", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Thought for 12 s" }),
  ).toHaveAttribute("data-state", "closed");
  await expect(line(page)).toHaveCount(0);
  await expect(
    page.getByRole("region", { name: "Model reasoning" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Thought for 12 s" }).click();
  await expect(full).toContainText("Synthetic reasoning line 1:");
  await expect(full).toContainText("Newest synthetic reasoning");
});

for (const mode of ["always", "system"] as const)
  test(`indicator motion is static for ${mode}, while words still change`, async ({
    page,
  }) => {
    await page.clock.install();
    await page.emulateMedia({
      reducedMotion: mode === "system" ? "reduce" : "no-preference",
    });
    await preview(page);
    if (mode === "always")
      await page.getByRole("button", { name: "Reduce motion" }).click();
    const first = await word(page).textContent();
    await page.clock.runFor(2800);
    await expect(word(page)).not.toHaveText(first!);
    const styles = await line(page).evaluate((el) => {
      const mark = el.querySelector(".mark-a")!,
        dot = el.querySelector(".mark-dot")!,
        text = el.querySelector(".word-in")!;
      return [mark, dot, text].map((node) => ({
        animation: getComputedStyle(node).animationName,
        opacity: getComputedStyle(node).opacity,
        transform: getComputedStyle(node).transform,
      }));
    });
    for (const style of styles)
      expect(style).toMatchObject({
        animation: "none",
        opacity: "1",
        transform: "none",
      });
    await page
      .getByRole("button", { name: "Preview Thinking", exact: true })
      .click();
    expect(
      await page
        .locator(".mark-dot")
        .evaluate((el) => getComputedStyle(el).animationName),
    ).toBe("none");
  });

for (const width of [390, 1440])
  for (const theme of ["dark", "light"])
    test(`indicator production states ${width} ${theme}`, async ({ page }) => {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await preview(page);
      await mkdir(dir, { recursive: true });
      const checks: unknown[] = [];
      for (const state of [
        "Waiting",
        "Queued",
        "Loading",
        "Web search",
        "Reading pages",
        "Unreadable pages",
        "Library search",
        "Thinking",
        "Answer",
        "Complete",
        "Stopped",
        "Error",
      ]) {
        await page
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        await settle(page);
        if (state === "Reading pages")
          await expect(word(page)).toHaveText("Reading 4 pages");
        if (state === "Unreadable pages")
          await expect(word(page)).toHaveText("Pages couldn't be read");
        if (state === "Library search")
          await expect(word(page)).toHaveText("Searching your files");
        if (["Stopped", "Error"].includes(state))
          await expect(line(page)).toHaveCount(0);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        const result = await new AxeBuilder({ page }).analyze();
        const failures = result.violations.filter(
          (v) => v.impact === "serious" || v.impact === "critical",
        );
        expect(failures).toEqual([]);
        checks.push({ state, serious_or_critical: failures });
        await page.screenshot({
          path: `${dir}/${state.toLowerCase().replaceAll(" ", "-")}-${width}-${theme}-${test.info().project.name}-fake.png`,
          animations: "disabled",
          fullPage: true,
        });
      }
      await page
        .getByRole("button", { name: "Preview Thinking", exact: true })
        .click();
      await page.getByRole("button", { name: "Show thinking" }).click();
      await settle(page);
      const expanded = await new AxeBuilder({ page }).analyze();
      const failures = expanded.violations.filter(
        (v) => v.impact === "serious" || v.impact === "critical",
      );
      expect(failures).toEqual([]);
      checks.push({
        state: "Thinking expanded",
        serious_or_critical: failures,
      });
      await page.screenshot({
        path: `${dir}/thinking-expanded-${width}-${theme}-${test.info().project.name}-fake.png`,
        animations: "disabled",
        fullPage: true,
      });
      await page
        .getByRole("button", { name: "Preview Waiting", exact: true })
        .click();
      await page.getByRole("button", { name: "Plain status" }).click();
      await expect(word(page)).toHaveText("Working");
      await settle(page);
      const plain = await new AxeBuilder({ page }).analyze();
      const plainFailures = plain.violations.filter(
        (v) => v.impact === "serious" || v.impact === "critical",
      );
      expect(plainFailures).toEqual([]);
      checks.push({
        state: "Plain waiting",
        serious_or_critical: plainFailures,
      });
      await page.screenshot({
        path: `${dir}/plain-waiting-${width}-${theme}-${test.info().project.name}-fake.png`,
        animations: "disabled",
        fullPage: true,
      });
      await writeFile(
        `${dir}/axe-${width}-${theme}-${test.info().project.name}.json`,
        JSON.stringify(checks, null, 2),
      );
    });

// Feed controlled synthetic events through the unchanged production EventSource
// listeners and rAF batching. The actual fake request is cancelled in finally.
test("actual chat stream prioritizes stages, batches reasoning, collapses on text and retains settings payload", async ({
  page,
  request,
}) => {
  const [connection] = await (await request.get("/api/connections")).json();
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: connection.id, model_id: "fake-reasoning" },
    })
  ).json();
  await request.patch("/api/settings", {
    data: {
      "appearance.reduce_motion": "system",
      auto_title: false,
      "web.default_on": false,
    },
  });
  await page.addInitScript(() => {
    const Native = window.EventSource;
    const sources: EventTarget[] = [];
    window.EventSource = class extends EventTarget {
      constructor(url: string | URL, options?: EventSourceInit) {
        super();
        if (!/^\/api\/runs\/[^/]+\/events$/.test(String(url)))
          return new Native(url, options);
        sources.push(this);
      }
      close() {}
    } as unknown as typeof EventSource;
    Object.assign(window, {
      syntheticRunEvent: (type: string, data: unknown) =>
        sources
          .at(-1)
          ?.dispatchEvent(
            new MessageEvent(type, { data: JSON.stringify(data) }),
          ),
    });
    const renderRecords: { id: string; actualDuration: number }[] = [];
    Object.assign(window, { indicatorRenderRecords: renderRecords });
    window.addEventListener("workbench:message-render", (event) =>
      renderRecords.push((event as CustomEvent).detail),
    );
  });
  const emit = async (type: string, data: unknown) =>
    page.evaluate(
      ({ type, data }) =>
        (
          window as unknown as {
            syntheticRunEvent: (type: string, data: unknown) => void;
          }
        ).syntheticRunEvent(type, data),
      { type, data },
    );
  let runId: string | undefined;
  try {
    await page.goto(`/c/${chat.id}`);
    await page
      .locator(".composer textarea")
      .fill("#think #long:100 #slow:1 #stall:30 Synthetic ticker check");
    const accepted = page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        r.url().endsWith(`/api/chats/${chat.id}/messages`),
    );
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    const response = await accepted;
    expect(response.ok()).toBe(true);
    runId = (await response.json()).run_id;
    await expect(line(page)).toHaveCount(1);
    await emit("run.queued", { position: 2 });
    await expect(word(page)).toContainText("#2 in line");
    await emit("run.started", { model_loaded: false });
    await expect(word(page)).toContainText("Loading");
    await emit("search.reading", {
      url: "https://example.org/one",
      title: "Synthetic source",
    });
    await expect(word(page)).toHaveText("Reading 1 page");
    await emit("search.done", { sources: [], timings: {} });
    await emit("reasoning.delta", { text: "An original synthetic thought.\n" });
    await emit("reasoning.delta", {
      text: "Newest reasoning stays literal <tag>.",
    });
    await expect(page.locator(".thought-ticker")).toHaveText(
      "…An original synthetic thought. Newest reasoning stays literal <tag>.",
    );
    await expect(
      page.getByRole("button", { name: "Show thinking" }),
    ).toBeVisible();
    const performance = await page.evaluate(async () => {
      const target = window as unknown as {
        syntheticRunEvent: (type: string, data: unknown) => void;
        indicatorRenderRecords: { id: string; actualDuration: number }[];
      };
      target.indicatorRenderRecords.length = 0;
      await new Promise<void>((resolve) => {
        let i = 0;
        const timer = setInterval(() => {
          target.syntheticRunEvent("reasoning.delta", { text: ` delta${i++}` });
          if (i === 100) {
            clearInterval(timer);
            requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
          }
        }, 10);
      });
      const records = target.indicatorRenderRecords;
      const durations = records
        .map((row) => row.actualDuration)
        .sort((a, b) => a - b);
      return {
        synthetic_deltas_per_second: 100,
        render_samples: records.length,
        rows: [...new Set(records.map((row) => row.id))],
        render_p95_ms: durations[Math.floor(durations.length * 0.95)],
      };
    });
    expect(performance.render_samples).toBeGreaterThan(30);
    expect(performance.rows).toHaveLength(1);
    expect(performance.render_p95_ms).toBeLessThanOrEqual(8);
    await mkdir(dir, { recursive: true });
    await writeFile(
      `${dir}/ticker-performance-${test.info().project.name}.json`,
      JSON.stringify(performance, null, 2),
    );
    await expect(page.locator(".thought-ticker")).toContainText("delta99");
    await emit("text.delta", { text: "Synthetic streamed answer" });
    await expect(
      page.getByText("Synthetic streamed answer", { exact: true }),
    ).toBeVisible();
    await expect(line(page)).toHaveCount(0);
    const done = page.getByRole("button", { name: /Thought for/ });
    await done.click();
    await expect(
      page.getByRole("region", { name: "Model reasoning" }),
    ).toHaveText(
      "An original synthetic thought.\nNewest reasoning stays literal <tag>." +
        Array.from({ length: 100 }, (_, i) => ` delta${i}`).join(""),
    );
    const writes: unknown[] = [];
    page.on("request", (r) => {
      if (r.method() === "PATCH" && r.url().endsWith("/api/settings"))
        writes.push(r.postDataJSON());
    });
    await page
      .getByRole("button", { name: "Choose model", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Manage models…", exact: true })
      .click();
    const settings = page.getByRole("dialog", {
      name: "Settings",
      exact: true,
    });
    await settings
      .getByRole("button", { name: "Appearance", exact: true })
      .click();
    await settings.getByRole("button", { name: "Plain", exact: true }).click();
    await expect(
      settings.getByRole("button", { name: "Plain", exact: true }),
    ).toHaveAttribute("aria-pressed", "true");
    await page.waitForTimeout(500);
    expect(writes).toEqual([]);
    expect(
      await page.evaluate(() => localStorage.getItem("workbench-status-words")),
    ).toBe("plain");
    await settings
      .getByRole("button", { name: "Sans · Geist", exact: true })
      .click();
    await expect.poll(() => writes.length).toBe(1);
    expect(writes[0]).toMatchObject({ "appearance.font": "sans" });
    expect(Object.keys(writes[0] as object)).not.toContain(
      "appearance.status_words",
    );
    await mkdir(dir, { recursive: true });
    await writeFile(
      `${dir}/settings-payload-${test.info().project.name}.json`,
      JSON.stringify(writes, null, 2),
    );
  } finally {
    if (runId) await request.post(`/api/runs/${runId}/cancel`);
    await request.delete(`/api/chats/${chat.id}`);
    await request.patch("/api/settings", {
      data: { "appearance.font": "serif" },
    });
  }
});
