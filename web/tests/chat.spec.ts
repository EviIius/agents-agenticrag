import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
const dir = "../artifacts/phase-1";
async function send(page: import("@playwright/test").Page, text: string) {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  await page.locator(".composer textarea").fill(text);
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page).toHaveURL(/\/c\//);
}
for (const width of [320, 390, 768, 1440])
  for (const theme of ["light", "dark"])
    test(`live chat ${width} ${theme}`, async ({ page, request }) => {
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await send(page, "Hello from the browser");
      await expect(
        page.getByText("Fake runtime reply.", { exact: false }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Stop generating" }),
      ).not.toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      const thread = await page.getByTestId("thread").boundingBox(),
        composer = await page.getByTestId("composer-row").boundingBox();
      expect(thread!.y + thread!.height).toBeLessThanOrEqual(composer!.y + 1);
      await mkdir(dir, { recursive: true });
      await page.screenshot({
        path: `${dir}/chat-${width}-${theme}-fake-runtime.png`,
      });
      const result = await new AxeBuilder({ page }).analyze();
      expect(
        result.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.reload();
      await expect(
        page
          .getByRole("article", { name: "user message" })
          .getByText("Hello from the browser", { exact: true }),
      ).toBeVisible();
    });
test("Stop persists partial text and closes runtime connection", async ({
  page,
  request,
}) => {
  const before = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).disconnected;
  await send(page, "#long:500 #slow:50");
  await expect(page.getByText(/token0 token1/)).toBeVisible();
  await page.getByRole("button", { name: "Stop generating" }).click();
  await expect(
    page.locator(".meta").filter({ hasText: /stopped/i }),
  ).toBeVisible();
  await expect
    .poll(
      async () =>
        (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
          .disconnected,
    )
    .toBeGreaterThan(before);
  const text = await page.locator(".prose-answer").innerText();
  await page.reload();
  await expect(page.locator(".prose-answer")).toHaveText(text);
});
test("close tab and reopen after 20 seconds resumes exactly", async ({
  page,
  context,
  request,
}) => {
  test.setTimeout(65000);
  await send(page, "#long:350 #slow:10");
  await expect(page.getByText(/token0 token1/)).toBeVisible();
  const url = page.url();
  await page.close();
  await new Promise((resolve) => setTimeout(resolve, 20000));
  const reopened = await context.newPage();
  await reopened.goto(url);
  await expect(
    reopened.getByRole("button", { name: "Stop generating" }),
  ).toBeVisible();
  await expect(
    reopened.getByRole("button", { name: "Stop generating" }),
  ).not.toBeVisible({ timeout: 25000 });
  const data = await (
    await request.get("/api/chats/" + url.split("/").pop())
  ).json();
  expect(await reopened.locator(".prose-answer").innerText()).toBe(
    data.messages.findLast((m: { role: string }) => m.role === "assistant")
      .content,
  );
});
test("long answer completes beyond 90 seconds; idle timeout keeps partial", async ({
  page,
  request,
}) => {
  test.skip(
    test.info().project.name !== "chromium",
    "Run the real-time timeout gate once",
  );
  test.setTimeout(240000);
  await send(page, "#long:1500 #slow:10");
  await expect(page.getByText(/token1499/)).toBeVisible({ timeout: 180000 });
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).not.toBeVisible();
  const url = page.url();
  const data = await (
    await request.get("/api/chats/" + url.split("/").pop())
  ).json();
  expect(
    data.messages.findLast((m: { role: string }) => m.role === "assistant")
      .status,
  ).toBe("complete");
  expect(
    data.messages.findLast((m: { role: string }) => m.role === "assistant")
      .stats.total_ms,
  ).toBeGreaterThan(150000);
  await send(page, "#stall:70");
  await expect(
    page.getByText("The model stopped responding. The partial answer is kept."),
  ).toBeVisible({ timeout: 75000 });
  const id = page.url().split("/").pop();
  const error = await (await request.get("/api/chats/" + id)).json();
  expect(
    error.messages.findLast((m: { role: string }) => m.role === "assistant")
      .error.code,
  ).toBe("idle_timeout");
  expect(
    error.messages.findLast((m: { role: string }) => m.role === "assistant")
      .content.length,
  ).toBeGreaterThan(0);
});
test("100 tokens/s render frame trace", async ({ page }) => {
  const cdp =
    test.info().project.name === "chromium"
      ? await page.context().newCDPSession(page)
      : null;
  if (cdp)
    await cdp.send("Tracing.start", {
      categories: "devtools.timeline,blink.user_timing",
      transferMode: "ReturnAsStream",
    });
  await page.addInitScript(() => {
    const times: number[] = [];
    (window as unknown as { frames: number[] }).frames = times;
    let previous = performance.now();
    const frame = (now: number) => {
      times.push(now - previous);
      previous = now;
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  });
  await send(page, "#long:300 #slow:100");
  await expect(page.getByText(/token0 token1/)).toBeVisible();
  await page.evaluate(() => {
    (window as unknown as { frames: number[] }).frames.length = 0;
  });
  await expect(page.getByText(/token299/)).toBeVisible();
  const times = await page.evaluate(
    () => (window as unknown as { frames: number[] }).frames,
  );
  await mkdir(dir, { recursive: true });
  await writeFile(
    `${dir}/frames-${test.info().project.name}.json`,
    JSON.stringify(times),
  );
  if (cdp) {
    const finished = new Promise<string>((resolve, reject) =>
      cdp.once("Tracing.tracingComplete", (event) =>
        event.stream
          ? resolve(event.stream)
          : reject(new Error("Chrome trace stream missing")),
      ),
    );
    await cdp.send("Tracing.end");
    const handle = await finished;
    let trace = "";
    for (;;) {
      const part = await cdp.send("IO.read", { handle });
      trace += part.data;
      if (part.eof) break;
    }
    await cdp.send("IO.close", { handle });
    await writeFile(`${dir}/streaming-chromium-trace.json.gz`, gzipSync(trace));
  }
  const sorted = times.filter((n) => n < 100).sort((a, b) => a - b);
  expect(sorted[Math.floor(sorted.length * 0.5)]).toBeLessThan(20);
});

test("first-token render delay under 150ms", async ({ page, request }) => {
  await page.addInitScript(() => {
    const listener = new MutationObserver(() => {
      if (
        document
          .querySelector('[aria-label="assistant message"] .prose-answer')
          ?.textContent?.includes("Fake")
      ) {
        (window as unknown as { firstRendered: number }).firstRendered =
          performance.timeOrigin + performance.now();
        listener.disconnect();
      }
    });
    listener.observe(document, {
      subtree: true,
      childList: true,
      characterData: true,
    });
  });
  await send(page, "first-token-latency-check");
  await expect(
    page.getByText("Fake runtime reply.", { exact: false }),
  ).toBeVisible();
  const at = await page.evaluate(
    () => (window as unknown as { firstRendered: number }).firstRendered,
  );
  const state = await (
    await request.get("http://127.0.0.1:18080/tests/state")
  ).json();
  const first = state.first_tokens.findLast(
    (r: { prompt: string; at_ms: number }) =>
      r.prompt === "first-token-latency-check",
  );
  const delay = at - first.at_ms;
  expect(delay).toBeGreaterThanOrEqual(0);
  expect(delay).toBeLessThan(150);
  await writeFile(
    `${dir}/first-token-${test.info().project.name}.json`,
    JSON.stringify({
      runtime_first_ms: first.at_ms,
      ui_first_ms: at,
      delay_ms: delay,
    }),
  );
});

test("preferences and model defaults persist after reload", async ({
  page,
  request,
}) => {
  const initial = await (await request.get("/api/settings")).json();
  const models = await (await request.get("/api/models")).json();
  const model = models.find(
    (item: { model_id: string }) => item.model_id === "fake-chat",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  await page.keyboard.press("Control+,");
  const settings = page.getByRole("dialog", { name: "Settings" });
  await settings
    .getByRole("button", { name: "Appearance", exact: true })
    .click();
  await settings
    .getByPlaceholder("Your name (optional)")
    .fill("Preference test");
  await settings.getByRole("button", { name: "Sans · Geist" }).click();
  await expect
    .poll(
      async () => (await (await request.get("/api/settings")).json()).user_name,
    )
    .toBe("Preference test");
  await settings.getByRole("button", { name: "Models", exact: true }).click();
  await settings
    .getByRole("button", { name: "Parameters and context" })
    .first()
    .click();
  await settings
    .getByRole("switch", { name: "Use model default for Temperature" })
    .click();
  await settings
    .getByRole("spinbutton", { name: "Temperature", exact: true })
    .fill("0.35");
  await settings
    .getByRole("button", { name: "Save as model defaults" })
    .click();
  await expect
    .poll(async () => {
      const catalog = await (
        await request.get("/api/models?include_hidden=true")
      ).json();
      return catalog.find(
        (item: { model_id: string }) => item.model_id === "fake-chat",
      ).params_defaults.temperature;
    })
    .toBe(0.35);
  await settings.locator('section[aria-label="Models"]').evaluate((element) => {
    element.scrollTop = 0;
  });
  expect(
    await settings
      .locator('section[aria-label="Models"]')
      .evaluate((element) => element.scrollWidth <= element.clientWidth),
  ).toBeTruthy();
  await page.screenshot({
    path: `${dir}/settings-models-390-light-fake-runtime.png`,
  });
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Preference test/ }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.dataset.answerFont),
  ).toBe("sans");
  await page.locator(".composer textarea").fill("model-default-payload-check");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(
    page.getByText("Fake runtime reply.", { exact: false }),
  ).toBeVisible();
  const captures = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).captures;
  const payload = captures.findLast(
    (item: { messages?: { content: string }[] }) =>
      item.messages?.at(-1)?.content === "model-default-payload-check",
  );
  expect(payload.options.temperature).toBe(0.35);
  expect(payload.options).not.toHaveProperty("top_p");
  await request.put("/api/models/prefs", {
    data: {
      connection_id: model.connection_id,
      model_id: model.model_id,
      params: {},
    },
  });
  await request.patch("/api/settings", {
    data: {
      user_name: initial.user_name,
      "appearance.font": initial["appearance.font"] ?? "serif",
    },
  });
});
