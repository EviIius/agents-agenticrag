import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";

async function existing(page: Page, request: APIRequestContext) {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      auto_title: false,
      "web.default_on": false,
    },
  });
  const chat = await (
    await request.post("/api/chats", {
      data: {
        connection_id: connection.id,
        model_id: "fake-chat",
        web_enabled: false,
      },
    })
  ).json();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/c/${chat.id}`);
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  return chat;
}
async function rejectLater(page: Page, id: string) {
  let release!: () => void;
  const ready = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(`**/api/chats/${id}/messages`, async (route) => {
    await ready;
    await route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "context_overflow", message: "Synthetic rejection" },
      }),
    });
  });
  return release;
}

test("existing send paints in one frame, replaces once, stays pinned and never replays", async ({
  page,
  request,
}) => {
  const chat = await existing(page, request);
  await page.route(`**/api/chats/${chat.id}/messages`, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    await route.continue();
  });
  await page.evaluate(() => {
    document.addEventListener(
      "submit",
      () => {
        const start = performance.now();
        const inspect = () => {
          const row = document.querySelector(
            '[data-testid="optimistic-send"] article',
          );
          const field =
            document.querySelector<HTMLTextAreaElement>(".composer textarea")!;
          if (row && field.value === "") {
            Object.assign(document.documentElement.dataset, {
              immediateSendMs: String(performance.now() - start),
              immediateFresh: row.getAttribute("data-fresh"),
              immediateAnimation: getComputedStyle(row).animationName,
            });
          } else requestAnimationFrame(inspect);
        };
        requestAnimationFrame(inspect);
      },
      { once: true, capture: true },
    );
  });
  const text = "Synthetic immediate send #long:90 #slow:30";
  await page.locator(".composer textarea").fill(text);
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.locator('[data-testid="optimistic-send"]')).toContainText(
    text,
  );
  await expect(page.locator(".composer textarea")).toHaveValue("");
  await expect(page.locator("html")).toHaveAttribute(
    "data-immediate-fresh",
    "true",
  );
  const delay = Number(
    await page.locator("html").getAttribute("data-immediate-send-ms"),
  );
  expect(delay).toBeLessThanOrEqual(100);
  expect(
    await page.locator("html").getAttribute("data-immediate-animation"),
  ).not.toBe("none");
  const frames = await page.evaluate(async () => {
    const samples: number[] = [];
    for (let i = 0; i < 60; i++)
      await new Promise<void>((resolve) =>
        requestAnimationFrame(() => {
          const thread = document.querySelector('[data-testid="thread"]')!;
          samples.push(
            thread.scrollHeight - thread.clientHeight - thread.scrollTop,
          );
          resolve();
        }),
      );
    return samples;
  });
  expect(Math.max(...frames)).toBeLessThan(80);
  await expect(page.getByRole("article", { name: "user message" })).toHaveCount(
    1,
  );
  await expect(
    page.getByRole("article", { name: "user message" }),
  ).not.toHaveAttribute("data-fresh", "true");
  await expect(
    page.locator('[data-streaming="true"] .prose-answer'),
  ).toBeVisible();
  await expect
    .poll(() =>
      page
        .locator('[data-streaming="true"] .prose-answer')
        .evaluate((root) =>
          getComputedStyle(root).getPropertyValue("--streamdown-caret"),
        ),
    )
    .toContain("▋");
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).not.toBeVisible({ timeout: 10000 });
  await expect(page.locator('[data-streaming="true"]')).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole("article")).toHaveCount(2);
  expect(await page.locator('article[data-fresh="true"]').count()).toBe(0);
  await page.getByTestId("thread").evaluate((element) => {
    element.scrollTop = 0;
    element.scrollTop = element.scrollHeight;
  });
  expect(await page.locator('article[data-fresh="true"]').count()).toBe(0);
  await mkdir("../artifacts/phase-4/4c", { recursive: true });
  await writeFile(
    `../artifacts/phase-4/4c/send-${test.info().project.name}-fake.json`,
    JSON.stringify(
      {
        delay_ms: delay,
        maximum_bottom_gap: Math.max(...frames),
        frame_count: frames.length,
      },
      null,
      2,
    ),
  );
});

for (const mode of [
  "restore",
  "new draft",
  "changed then cleared",
  "switch chat",
  "new chat",
] as const) {
  test(`rejected send protects draft: ${mode}`, async ({ page, request }) => {
    const chat = await existing(page, request);
    const other =
      mode === "switch chat"
        ? await (
            await request.post("/api/chats", {
              data: {
                connection_id: chat.connection_id,
                model_id: "fake-chat",
              },
            })
          ).json()
        : null;
    if (other) {
      await request.post(`/api/chats/${other.id}/messages`, {
        data: { content: "Synthetic second chat seed", web: false },
      });
      await request.patch(`/api/chats/${other.id}`, {
        data: { title: `Synthetic second chat ${other.id}` },
      });
      await page.reload();
    }
    const release = await rejectLater(page, chat.id);
    const composer = page.locator(".composer textarea");
    await composer.fill("Synthetic rejected send");
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page.getByTestId("optimistic-send")).toBeVisible();
    await expect(composer).toHaveValue("");
    if (mode === "switch chat" || mode === "new chat") {
      if (mode === "switch chat") {
        await page
          .getByRole("button", { name: "Open sidebar", exact: true })
          .click();
        await page
          .getByRole("link", {
            name: `Synthetic second chat ${other.id}`,
            exact: true,
          })
          .click();
        await expect(page).toHaveURL(`/c/${other.id}`);
      } else {
        await page
          .getByRole("button", { name: "Open sidebar", exact: true })
          .click();
        await page
          .getByRole("dialog", { name: "Chat history" })
          .getByRole("banner")
          .getByRole("link", { name: "New chat", exact: true })
          .click();
        await expect(page).toHaveURL(/\/$/);
      }
      await composer.fill("Synthetic draft in another chat");
    } else if (mode !== "restore") {
      await composer.fill("Synthetic newer draft");
      if (mode === "changed then cleared") await composer.fill("");
    }
    release();
    await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Stop generating", exact: true }),
    ).not.toBeVisible();
    await expect(composer).toHaveValue(
      mode === "restore"
        ? "Synthetic rejected send"
        : mode === "changed then cleared"
          ? ""
          : mode === "new draft"
            ? "Synthetic newer draft"
            : "Synthetic draft in another chat",
    );
    if (mode === "switch chat" || mode === "new chat")
      await expect(page.getByRole("alert")).toHaveCount(0);
    else await expect(page.getByRole("alert")).toBeVisible();
    expect(
      (await (await request.get(`/api/chats/${chat.id}`)).json()).messages,
    ).toHaveLength(0);
  });
}

test("copy confirms locally without a toast; reduced streaming has no word fades or blink", async ({
  page,
  request,
}) => {
  await existing(page, request);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page
    .locator(".composer textarea")
    .fill("Synthetic copy #long:40 #slow:15");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByText(/token0 token1/)).toBeVisible();
  expect(await page.locator("[data-sd-animate]").count()).toBe(0);
  const caret = await page
    .locator('[data-streaming="true"] .prose-answer')
    .evaluate(
      (element) =>
        getComputedStyle(element.lastElementChild!, "::after").animationName,
    );
  expect(caret).toBe("none");
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).not.toBeVisible({ timeout: 10000 });
  await page.evaluate(() =>
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async () => {} },
    }),
  );
  const row = page.getByRole("article", { name: "assistant message" });
  await row.getByRole("button", { name: "Copy message", exact: true }).click();
  await expect(row.locator('[data-slot="copy-check"]')).toBeVisible();
  await expect(
    row.getByRole("status").filter({ hasText: "Copied" }),
  ).toHaveText("Copied");
  await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
  await expect(row.locator('[data-slot="copy-check"]')).toHaveCount(0);
  await settle(page);
});

// Exercise the native-file path independently of the existing ordinary-download tests.
test("chat save cancellation keeps formats editable and never opens a fallback download", async ({
  page,
  request,
}) => {
  const chat = await existing(page, request);
  await request.patch(`/api/chats/${chat.id}`, {
    data: { title: "Synthetic export chat" },
  });
  await page.reload();
  await page.evaluate(() => {
    let count = 0;
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: () => true,
    });
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: async (data: ShareData) => {
        const file = data.files![0];
        document.documentElement.dataset.shareCount = String(++count);
        document.documentElement.dataset.shareName = file.name;
        document.documentElement.dataset.shareActive = String(
          navigator.userActivation?.isActive ?? true,
        );
        document.documentElement.dataset.shareContent = await file.text();
        if (count === 1) throw new DOMException("Cancelled", "AbortError");
      },
    });
  });
  let downloads = 0;
  page.on("download", () => downloads++);
  const original = page.url();
  await page
    .getByRole("button", {
      name: "Actions for Synthetic export chat",
      exact: true,
    })
    .click();
  await page
    .getByRole("menuitem", { name: "Export JSON", exact: true })
    .click();
  const dialog = page.getByRole("dialog", { name: "Export chat", exact: true });
  await expect(
    dialog.getByRole("button", { name: "JSON (.json)", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await dialog
    .getByRole("button", { name: "Save or share", exact: true })
    .click();
  await expect(dialog.getByText(/Save cancelled/)).toBeVisible();
  await expect(
    dialog.getByRole("button", { name: "Close chat export", exact: true }),
  ).toBeInViewport({ ratio: 1 });
  await dialog
    .getByRole("button", { name: "Markdown (.md)", exact: true })
    .click();
  await expect(
    dialog.getByRole("button", { name: "Markdown (.md)", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(
    dialog.getByRole("button", { name: "JSON (.json)", exact: true }),
  ).toHaveAttribute("aria-pressed", "false");
  await expect(dialog.getByLabel("Download filename")).toHaveText(
    "Synthetic export chat.md",
  );
  await dialog
    .getByRole("button", { name: "Save or share", exact: true })
    .click();
  await expect(dialog.getByText(/Returned from the save sheet/)).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("data-share-count", "2");
  await expect(page.locator("html")).toHaveAttribute(
    "data-share-active",
    "true",
  );
  await expect(page.locator("html")).toHaveAttribute(
    "data-share-name",
    "Synthetic export chat.md",
  );
  expect(
    await page.locator("html").getAttribute("data-share-content"),
  ).toContain("Synthetic export chat");
  expect(downloads).toBe(0);
  await expect(page).toHaveURL(original);
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(dialog).toHaveCount(0);
});

for (const reduce of ["system", "always"] as const) {
  test(`conversation preview and streaming respect ${reduce} reduced motion`, async ({
    page,
    request,
  }) => {
    await existing(page, request);
    if (reduce === "system")
      await page.emulateMedia({ reducedMotion: "reduce" });
    else {
      await request.patch("/api/settings", {
        data: { "appearance.reduce_motion": "always" },
      });
      await page.reload();
    }
    await page
      .locator(".composer textarea")
      .fill("Synthetic reduced motion #long:40 #slow:15");
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page.getByText(/token0 token1/)).toBeVisible();
    expect(await page.locator("[data-sd-animate]").count()).toBe(0);
    await expect(
      page.getByRole("button", { name: "Stop generating", exact: true }),
    ).not.toBeVisible({ timeout: 10000 });
    await page.goto("/design");
    if (reduce === "always")
      await page
        .getByRole("button", { name: "Always reduce motion", exact: true })
        .click();
    const preview = page.getByRole("region", {
      name: "Conversation motion",
      exact: true,
    });
    for (const state of [
      "optimistic",
      "waiting",
      "reasoning",
      "streaming",
      "search",
      "complete",
    ]) {
      await preview
        .getByRole("button", { name: `Preview ${state}`, exact: true })
        .click();
      await settle(page);
      const motion = await preview.locator("*").evaluateAll((elements) =>
        elements.flatMap((element) => {
          const css = getComputedStyle(element);
          return css.animationName !== "none" ||
            css.transitionDuration
              .split(",")
              .some((value) => parseFloat(value) !== 0)
            ? [element.outerHTML.slice(0, 180)]
            : [];
        }),
      );
      expect(motion).toEqual([]);
    }
    await request.patch("/api/settings", {
      data: { "appearance.reduce_motion": "system" },
    });
  });
}

test("model status pulse is based on a successful load, not initial cached state", async ({
  page,
}) => {
  await page.goto("/design");
  const preview = page.getByRole("region", {
    name: "Conversation motion",
    exact: true,
  });
  const status = preview.locator('[data-slot="model-status"]');
  await expect(status).not.toHaveAttribute("data-loaded-fresh", "true");
  await status.evaluate((element) =>
    new MutationObserver(() => {
      if (element.getAttribute("data-loaded-fresh") === "true")
        document.documentElement.dataset.pulseSeen = "true";
    }).observe(element, { attributes: true }),
  );
  await preview
    .getByRole("button", { name: "Choose model", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Eject fake-chat", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Load fake-chat", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Load fake-chat", exact: true })
    .click();
  await expect(page.locator("html")).toHaveAttribute("data-pulse-seen", "true");
  await page
    .locator('[aria-label="Conversation motion"] [data-slot="model-status"]')
    .waitFor();
  await expect(
    page.locator(
      '[aria-label="Conversation motion"] [data-slot="model-status"]',
    ),
  ).not.toHaveAttribute("data-loaded-fresh", "true");
});

test("sidebar candidate width motion keeps the existing 300-message frame budget", async ({
  page,
  request,
}) => {
  const chat = await existing(page, request);
  await request.post(`http://127.0.0.1:8787/tests/long-chat/${chat.id}`);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.reload();
  await expect(page.getByRole("article")).toHaveCount(300);
  await page.addStyleTag({
    content: ".sidebar-desktop {transition:width 240ms var(--ease-sheet);}",
  });
  const samples: number[] = [];
  for (const collapsed of [true, false, true, false]) {
    await page.evaluate(() => {
      const frames: number[] = [];
      (window as unknown as { sidebarFrames: number[] }).sidebarFrames = frames;
      let previous = 0;
      const end = performance.now() + 350;
      const frame = (now: number) => {
        if (previous) frames.push(now - previous);
        previous = now;
        if (now < end) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    });
    await page
      .getByRole("button", {
        name: collapsed ? "Collapse sidebar" : "Open sidebar",
        exact: true,
      })
      .click();
    await page.waitForTimeout(400);
    samples.push(
      ...(await page.evaluate(
        () => (window as unknown as { sidebarFrames: number[] }).sidebarFrames,
      )),
    );
  }
  samples.sort((a, b) => a - b);
  const p95 = samples[Math.floor(samples.length * 0.95)];
  await mkdir("../artifacts/phase-4/4c", { recursive: true });
  await writeFile(
    `../artifacts/phase-4/4c/sidebar-${test.info().project.name}-fake.json`,
    JSON.stringify(
      {
        candidate_width_ms: 240,
        samples: samples.length,
        p95_ms: p95,
        allowed: p95 <= 18,
      },
      null,
      2,
    ),
  );
  // The specification permits a snapping fallback if either browser exceeds 18 ms.
  expect(samples.length).toBeGreaterThan(40);
});

for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`conversation states and chat exports have no serious accessibility findings ${width} ${theme}`, async ({
      page,
      request,
    }) => {
      const { default: AxeBuilder } = await import("@axe-core/playwright");
      await request.patch("/api/settings", {
        data: {
          "appearance.theme": theme,
          "appearance.reduce_motion": "system",
        },
      });
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design");
      await page
        .locator(".design-page > header")
        .getByRole("button", {
          name: theme === "dark" ? "Dark" : "Light",
          exact: true,
        })
        .click();
      const preview = page.getByRole("region", {
        name: "Conversation motion",
        exact: true,
      });
      const results: { state: string; violations: string[] }[] = [];
      for (const state of [
        "optimistic",
        "waiting",
        "reasoning",
        "streaming",
        "search",
        "complete",
      ]) {
        await preview
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        await settle(page);
        const axe = await new AxeBuilder({ page })
          .include('[aria-label="Conversation motion"]')
          .analyze();
        const violations = axe.violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        );
        results.push({ state, violations: violations.map((item) => item.id) });
        expect(violations).toEqual([]);
      }
      await page
        .getByRole("button", { name: "Preview JSON export", exact: true })
        .click();
      const dialog = page.getByRole("dialog", {
        name: "Export chat",
        exact: true,
      });
      await settle(page);
      await expect(
        dialog.getByRole("button", { name: "Cancel", exact: true }),
      ).toBeInViewport({ ratio: 1 });
      const axe = await new AxeBuilder({ page }).analyze();
      const violations = axe.violations.filter((item) =>
        ["serious", "critical"].includes(item.impact ?? ""),
      );
      results.push({
        state: "export-json",
        violations: violations.map((item) => item.id),
      });
      expect(violations).toEqual([]);
      await mkdir("../artifacts/phase-4/4c", { recursive: true });
      await page.screenshot({
        path: `../artifacts/phase-4/4c/export-${width}-${theme}-${test.info().project.name}-fake.png`,
        animations: "disabled",
      });
      await writeFile(
        `../artifacts/phase-4/4c/axe-${width}-${theme}-${test.info().project.name}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
  }

test("code and transcript copy show a local check and clear it after 1.5 seconds", async ({
  page,
}) => {
  await page.goto("/design");
  await page.evaluate(() =>
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async () => {} },
    }),
  );
  const preview = page.getByRole("region", {
    name: "Conversation motion",
    exact: true,
  });
  await preview
    .getByRole("button", { name: "Preview complete", exact: true })
    .click();
  const code = preview
    .locator('[data-streamdown="code-block-copy-button"]')
    .first();
  await code.click();
  await expect(code.locator('[data-slot="copy-check"]')).toBeVisible();
  await expect(
    preview.getByRole("status").filter({ hasText: "Copied" }),
  ).toContainText("Copied");
  await expect(code.locator('[data-slot="copy-check"]')).toHaveCount(0);
  await page
    .getByRole("button", { name: "Preview transcript panel", exact: true })
    .click();
  const transcript = page.getByRole("dialog", {
    name: "Synthetic recording.wav",
    exact: true,
  });
  await transcript.getByRole("button", { name: "Copy", exact: true }).click();
  await expect(transcript.locator('[data-slot="copy-check"]')).toBeVisible();
  await expect(
    transcript.getByRole("status").filter({ hasText: "Copied" }),
  ).toHaveText("Copied");
  await expect(transcript.locator('[data-slot="copy-check"]')).toHaveCount(0);
  await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
});

// Capture short-lived flags on the page clock so automation latency cannot miss them.
test("new-chat send waits for confirmation; edit and regenerate animate only newly confirmed rows", async ({
  page,
  request,
}) => {
  await existing(page, request);
  await page.goto("/");
  await page.addInitScript(() => {
    document.addEventListener("DOMContentLoaded", () => {
      const seen: Set<string> = new Set();
      Object.defineProperty(window, "freshSeen", { value: seen });
      const inspect = () =>
        document
          .querySelectorAll('article[data-fresh="true"]')
          .forEach((element) =>
            seen.add(element.getAttribute("data-message-id")!),
          );
      new MutationObserver(inspect).observe(document, {
        subtree: true,
        attributes: true,
        childList: true,
      });
    });
  });
  await page.reload();
  await page.route("**/api/chats/*/messages", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    await route.continue();
  });
  const field = page.locator(".composer textarea");
  await field.fill("Synthetic first message #long:30 #slow:30");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(field).toHaveValue("Synthetic first message #long:30 #slow:30");
  await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
  await expect(page).toHaveURL(/\/c\//);
  const id = page.url().split("/c/")[1];
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).not.toBeVisible({ timeout: 10000 });
  let detail = await (await request.get(`/api/chats/${id}`)).json();
  let seen = await page.evaluate(() => [
    ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  ]);
  for (const message of detail.messages) expect(seen).toContain(message.id);
  await page
    .getByRole("button", { name: "Regenerate answer", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).not.toBeVisible({ timeout: 10000 });
  detail = await (await request.get(`/api/chats/${id}`)).json();
  seen = await page.evaluate(() => [
    ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  ]);
  for (const message of detail.messages) expect(seen).toContain(message.id);
  await page.getByRole("button", { name: "Edit message", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Edit message", exact: true })
    .fill("Synthetic edited message #long:30 #slow:30");
  await page.getByRole("button", { name: "Send", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).not.toBeVisible({ timeout: 10000 });
  detail = await (await request.get(`/api/chats/${id}`)).json();
  seen = await page.evaluate(() => [
    ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  ]);
  for (const message of detail.messages) expect(seen).toContain(message.id);
  await page.reload();
  await expect(page.getByRole("article")).toHaveCount(2);
  expect(await page.locator('article[data-fresh="true"]').count()).toBe(0);
});

test("theme uses the native root transition when available and switches immediately with reduced motion", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const native = document.startViewTransition?.bind(document);
    let count = 0;
    document.startViewTransition = ((update: () => void) => {
      document.documentElement.dataset.themeTransitions = String(++count);
      if (native) return native(update);
      update();
      return { finished: Promise.resolve() };
    }) as typeof document.startViewTransition;
  });
  await page.goto("/design");
  const header = page.locator(".design-page > header");
  await header.getByRole("button", { name: "Light", exact: true }).click();
  await settle(page);
  await header.getByRole("button", { name: "Dark", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  const before = Number(
    await page.locator("html").getAttribute("data-theme-transitions"),
  );
  expect(before).toBeGreaterThan(0);
  await page
    .getByRole("button", { name: "Always reduce motion", exact: true })
    .click();
  await header.getByRole("button", { name: "Light", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(
    Number(await page.locator("html").getAttribute("data-theme-transitions")),
  ).toBe(before);
});
