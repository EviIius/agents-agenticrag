import { test, expect, type Page } from "@playwright/test";

// All API traffic is synthetic, so these checks can also inspect a published
// build without reading chats, writing preferences or calling a model.
async function syntheticChat(
  page: Page,
  state: "waiting" | "thinking" | "empty",
  motion: "system" | "always" = "system",
) {
  const now = new Date().toISOString();
  const model = {
    connection_id: "synthetic",
    model_id: "synthetic-chat",
    display_name: "Synthetic chat",
    chat_capable: true,
    loaded: true,
    hidden: false,
    embedding: false,
    params_defaults: {},
    context_length: 32768,
    context_limit: 32768,
  };
  const chat = {
    id: "synthetic-motion",
    title: "Synthetic motion check",
    connection_id: model.connection_id,
    model_id: model.model_id,
    params: {},
    web_enabled: false,
    library_enabled: false,
    pinned: false,
    created_at: now,
    updated_at: now,
    current_leaf_id: state === "empty" ? null : "synthetic-answer",
  };
  const settings = {
    "appearance.reduce_motion": motion,
    "appearance.theme": "dark",
    default_connection_id: model.connection_id,
    default_model_id: model.model_id,
    auto_title: false,
  };
  await page.route("**/api/**", async (route) => {
    const path = new URL(route.request().url()).pathname.slice(4);
    const respond = (body: unknown, status = 200) =>
      route.fulfill({ status, json: body });
    if (route.request().method() !== "GET") {
      if (path === `/chats/${chat.id}/messages`) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return respond(
          { error: { code: "validation_error", message: "Synthetic stop" } },
          422,
        );
      }
      throw new Error(`Unexpected synthetic mutation: ${path}`);
    }
    if (path === "/bootstrap")
      return respond({
        app_name: "Atelier",
        version: "synthetic",
        data_dir: "synthetic",
        settings,
        connections: [
          {
            id: model.connection_id,
            kind: "ollama",
            name: "Synthetic runtime",
            enabled: true,
            reachable: true,
            base_url: "http://127.0.0.1:1",
          },
        ],
        features: { library: false, web_search: false, transcription: false },
        attachment_extensions: { text: [".txt"], document: [".pdf"] },
      });
    if (path === "/models") return respond([model]);
    if (path === "/chats") return respond({ items: [chat] });
    if (path === `/chats/${chat.id}`)
      return respond({
        chat,
        messages:
          state === "empty"
            ? []
            : [
                {
                  id: "synthetic-answer",
                  chat_id: chat.id,
                  role: "assistant",
                  content: "",
                  reasoning:
                    state === "thinking"
                      ? "Synthetic reasoning: inspect motion over multiple frames."
                      : null,
                  status: "streaming",
                  model,
                  created_at: now,
                  attachments: [],
                },
              ],
        sources: {},
        reads: {},
      });
    if (path === `/chats/${chat.id}/context`)
      return respond({
        used_tokens: 30,
        context_length: 32768,
        dropped_message_count: 0,
      });
    if (path === "/transcription/status")
      return respond({ ready: false, audio_extensions: [] });
    if (path === "/images/status") return respond({ available: false });
    if (path === "/workflows/stream") return route.fulfill({ status: 204 });
    if (path === "/workflows/runs")
      return respond({ items: [], paused_count: 0 });
    if (
      ["/folders", "/presets", "/runs/active", "/attachments/pending"].includes(
        path,
      )
    )
      return respond([]);
    throw new Error(`Unexpected synthetic request: ${path}`);
  });
  await page.goto(`/c/${chat.id}`);
  await expect(page.locator("html")).toHaveAttribute(
    "data-reduce-motion",
    motion,
  );
  await expect(page.locator(".composer textarea")).toBeVisible();
}

async function sample(page: Page, selector: string, duration: number) {
  return page.locator(selector).evaluate(async (el, ms) => {
    const values: {
      time: number;
      transform: string;
      opacity: string;
      dash: string;
    }[] = [];
    const started = performance.now();
    do {
      await new Promise(requestAnimationFrame);
      const css = getComputedStyle(el);
      values.push({
        time: performance.now() - started,
        transform: css.transform,
        opacity: css.opacity,
        dash: css.strokeDasharray,
      });
    } while (performance.now() - started < ms);
    return values;
  }, duration);
}

test.use({ video: "on", serviceWorkers: "block" });

test.beforeEach(async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
});

for (const state of ["waiting", "thinking"] as const)
  test(`${state} visibly animates through repeated cycles`, async ({
    page,
  }, info) => {
    await syntheticChat(page, state);
    const selector = state === "waiting" ? ".mark-a" : ".mark-dot";
    await expect(page.locator(selector)).toBeVisible();
    const firstWord = await page.locator(".word-in").textContent();
    const values = await sample(page, selector, 3800);
    const property = state === "waiting" ? "dash" : "transform";
    expect(new Set(values.map((v) => v[property])).size).toBeGreaterThan(10);
    // Check each half independently: a one-time entrance is insufficient.
    for (const half of [
      values.filter((v) => v.time < 1900),
      values.filter((v) => v.time >= 1900),
    ])
      expect(new Set(half.map((v) => v[property])).size).toBeGreaterThan(5);
    if (state === "thinking") {
      await expect(page.locator(".thought-ticker")).toContainText(
        "Synthetic reasoning",
      );
      await expect(
        page.getByRole("button", { name: "Show thinking", exact: true }),
      ).toHaveAttribute("aria-expanded", "false");
    } else await expect(page.locator(".word-in")).not.toHaveText(firstWord!);
    await info.attach(`${state}-synthetic-screen`, {
      body: await page.screenshot({ animations: "allow" }),
      contentType: "image/png",
    });
    await info.attach(`${state}-frames`, {
      body: JSON.stringify(values),
      contentType: "application/json",
    });
  });

for (const mode of ["always", "system"] as const)
  test(`${mode} reduced motion stays static across frames`, async ({
    page,
  }) => {
    if (mode === "system") await page.emulateMedia({ reducedMotion: "reduce" });
    await syntheticChat(page, "thinking", mode);
    const values = await sample(page, ".mark-dot", 1400);
    expect(new Set(values.map((v) => v.transform))).toEqual(new Set(["none"]));
    expect(new Set(values.map((v) => v.opacity))).toEqual(new Set(["1"]));
  });

test("sending a chat actually fades and moves the new bubble", async ({
  page,
}, info) => {
  await syntheticChat(page, "empty");
  await page.evaluate(() => {
    const frames: { time: number; opacity: number; transform: string }[] = [];
    Object.assign(window, { syntheticSendFrames: frames });
    document.addEventListener(
      "submit",
      () => {
        const started = performance.now();
        const inspect = () => {
          const row = document.querySelector(
            '[data-testid="optimistic-send"] article',
          );
          if (row) {
            const css = getComputedStyle(row);
            frames.push({
              time: performance.now() - started,
              opacity: Number(css.opacity),
              transform: css.transform,
            });
          }
          if (performance.now() - started < 450) requestAnimationFrame(inspect);
        };
        requestAnimationFrame(inspect);
      },
      { once: true, capture: true },
    );
  });
  await page.locator(".composer textarea").fill("Synthetic motion sample");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          (
            window as unknown as {
              syntheticSendFrames: { time: number }[];
            }
          ).syntheticSendFrames.at(-1)?.time ?? 0,
      ),
    )
    .toBeGreaterThan(350);
  const values = await page.evaluate(
    () =>
      (
        window as unknown as {
          syntheticSendFrames: {
            time: number;
            opacity: number;
            transform: string;
          }[];
        }
      ).syntheticSendFrames,
  );
  expect(Math.min(...values.map((v) => v.opacity))).toBeLessThan(0.95);
  expect(values.at(-1)!.opacity).toBe(1);
  expect(new Set(values.map((v) => v.transform)).size).toBeGreaterThan(3);
  await info.attach("send-frames", {
    body: JSON.stringify(values),
    contentType: "application/json",
  });
});
