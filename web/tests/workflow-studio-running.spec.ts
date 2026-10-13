import {
  test,
  expect,
  type APIRequestContext,
  type Page,
} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
import { fakeAppURL } from "../test-runtime";
import type {
  Definition,
  Doc,
  Run,
} from "../src/components/workflows/studio/types";
import { configureStudioBlock } from "./studio-helpers";
const dir = "../artifacts/workflow-studio/ws-d/browser";
test.use({
  viewport: { width: 1440, height: 900 },
  isMobile: false,
  hasTouch: false,
  video: { mode: "on", size: { width: 1440, height: 900 } },
});
async function create(
  request: APIRequestContext,
  options: {
    name?: string;
    review?: boolean;
    prompt?: string;
    count?: number;
    pick?: boolean;
  } = {},
) {
  const c = (await (await request.get("/api/connections")).json())[0];
  const d: Definition = await (
    await request.post("/api/workflows/defs", {
      data: {
        name: options.name ?? "Synthetic running workflow",
        template_id: "brief_images",
        default_model: { connection_id: c.id, model_id: "fake-chat" },
      },
    })
  ).json();
  const doc = d.graph;
  if (options.review === false) {
    doc.nodes = doc.nodes.filter((n) => n.kind !== "review");
    doc.edges = doc.edges.filter(
      (e) => e.source !== "n_review" && e.target !== "n_review",
    );
    doc.edges.push({
      id: "e_direct",
      source: "n_draft",
      source_port: "out",
      target: "n_images",
      target_port: "in",
    });
    const images = doc.nodes.find((n) => n.kind === "generate_image")!;
    images.config.prompt = "{{draft.text}}";
    const save = doc.nodes.find((n) => n.kind === "output")!;
    save.config.include = save.config.include.map((item) => ({
      ...item,
      ref: item.ref.replace("review.value", "draft.text"),
    }));
  }
  const draft = doc.nodes.find((n) => n.kind === "generate")!;
  if (options.prompt) {
    draft.config.instructions = "";
    draft.config.prompt = options.prompt;
  }
  const images = doc.nodes.find((n) => n.kind === "generate_image")!;
  images.config.count = options.count ?? 1;
  images.config.seeds = Array.from(
    { length: images.config.count },
    (_, i) => 42 + i,
  );
  if (options.pick) {
    doc.nodes.push({
      id: "n_pick",
      key: "favorites",
      kind: "pick",
      title: "Pick favorites",
      disabled: false,
      position: { x: 320, y: 880 },
      config: { from: ["{{images.images}}"], type: "image_list", maximum: 1 },
    });
    const edge = doc.edges.find((e) => e.target === "n_save")!;
    edge.target = "n_pick";
    doc.edges.push({
      id: "e_pick_save",
      source: "n_pick",
      source_port: "out",
      target: "n_save",
      target_port: "in",
    });
    const save = doc.nodes.find((n) => n.kind === "output")!;
    save.config.include = [{ label: "Favorite", ref: "{{favorites.chosen}}" }];
  }
  return (
    await request.put(`/api/workflows/defs/${d.id}`, {
      data: {
        name: d.name,
        description: d.description,
        icon: d.icon,
        graph: doc,
        version: d.version,
      },
    })
  ).json() as Promise<Definition>;
}
async function start(
  request: APIRequestContext,
  d: Definition,
  extra: Record<string, unknown> = {},
) {
  const response = await request.post(`/api/workflows/defs/${d.id}/runs`, {
    data: {
      request_key: crypto.randomUUID(),
      inputs: { brief: "Synthetic blue shapes" },
      ...extra,
    },
  });
  expect(response.status()).toBe(202);
  return response.json() as Promise<Run>;
}
async function done(page: Page) {
  await expect(
    page.locator(".wf-run-card [role=status]").first(),
  ).toContainText("Ready for review");
}
async function shot(page: Page, name: string) {
  await settle(page);
  await mkdir(dir, { recursive: true });
  await page.screenshot({ path: `${dir}/${name}-fake.png`, fullPage: true });
}

test("Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect", async ({
  page,
  request,
  browserName,
}) => {
  const d = await create(request, { prompt: "#long:16 #slow:3", review: true });
  const run = await start(request, d);
  await page.goto(`/workflows/${d.id}?run=1`);
  await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  const text = page.locator(".wf-stream-preview").first();
  await expect(text).toContainText("token");
  const before = await text.innerText();
  await expect.poll(() => text.innerText()).not.toBe(before);
  await expect(
    page.getByRole("button", { name: "Following run", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Zoom out", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Resume following run", exact: true }),
  ).toHaveAttribute("aria-pressed", "false");
  await shot(page, `stream-${browserName}`);
  let detailReads = 0;
  page.on("request", (r) => {
    if (r.url().endsWith(`/runs/${run.id}/v2`)) detailReads++;
  });
  await page.context().setOffline(true);
  await page.waitForTimeout(350);
  await page.context().setOffline(false);
  await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
    "Waiting for you",
  );
  await expect(
    page.getByRole("button", { name: "Following run", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page
    .getByRole("button", {
      name: "View result for Draft image prompt",
      exact: true,
    })
    .click();
  await expect(page.locator(".wf-stream-preview").first()).toContainText(
    "token15",
  );
  expect(detailReads).toBeLessThanOrEqual(1);
  await page
    .getByRole("textbox", { name: "Review result" })
    .fill("Synthetic approved blue circle");
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await done(page);
  await expect(page.locator('.wf-block[data-run="complete"]')).toHaveCount(
    d.graph.nodes.length,
  );
  const snapshot = await (
    await request.get(`/api/workflows/runs/${run.id}/v2`)
  ).json();
  expect(snapshot.nodes.n_review.output.value).toBe(
    "Synthetic approved blue circle",
  );
  await shot(page, `complete-${browserName}`);
});

test("Run from here uses saved outputs, rejects changed settings, and versions restore with undo", async ({
  page,
  request,
  browserName,
}) => {
  const d = await create(request, { review: false });
  const first = await start(request, d);
  await page.goto(`/workflows/${d.id}?run=1`);
  await done(page);
  await page.getByRole("button", { name: "Close Run", exact: true }).click();
  await configureStudioBlock(page, "Create images");
  await page
    .locator(".wf-inspector")
    .getByRole("button", { name: "Actions for Create images", exact: true })
    .click();
  await page
    .getByRole("menuitem", { name: "Run from here", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Run from here", exact: true })
    .click();
  await done(page);
  await expect(page.locator('.wf-block[data-run="reused"]')).toContainText([
    "Start",
    "Draft image prompt",
  ]);
  const all = await (
    await request.get(`/api/workflows/runs?def_id=${d.id}`)
  ).json();
  const second = all.items[0];
  expect(second.id).not.toBe(first.id);
  expect(second.nodes.n_draft.reused_from).toBe(first.id);
  expect(second.nodes.n_draft.attempt).toBe(0);
  await shot(page, `reused-${browserName}`);
  await page.getByRole("button", { name: "Close Run", exact: true }).click();
  await configureStudioBlock(page, "Draft image prompt");
  await page
    .getByRole("textbox", { name: "Prompt", exact: true })
    .fill("Synthetic changed prompt");
  await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  await configureStudioBlock(page, "Create images");
  await page
    .locator(".wf-inspector")
    .getByRole("button", { name: "Actions for Create images", exact: true })
    .click();
  await expect(
    page.getByRole("menuitem", { name: "Run from here", exact: true }),
  ).toBeDisabled();
  await page.keyboard.press("Escape");
  await page
    .getByRole("button", { name: "Close Inspector", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Workflow menu", exact: true })
    .click();
  await page.getByRole("menuitem", { name: "Versions", exact: true }).click();
  const version = page.locator(".wf-version").last();
  await version.getByRole("textbox").fill("Synthetic named version");
  await version.getByRole("button", { name: "Save name", exact: true }).click();
  await expect(version).toContainText("Synthetic named version");
  await version.getByRole("button", { name: "Restore", exact: true }).click();
  await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Undo", exact: true }).click();
  await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  const restored = await (
    await request.get(`/api/workflows/defs/${d.id}`)
  ).json();
  expect(
    restored.graph.nodes.find((n: { kind: string }) => n.kind === "generate")
      .config.prompt,
  ).toBe("Synthetic changed prompt");
});

test("Single block tests use explicit samples and remain outside recent history after reload", async ({
  page,
  request,
}) => {
  const d = await create(request, { review: false });
  await page.goto(`/workflows/${d.id}`);
  await configureStudioBlock(page, "Draft image prompt");
  await page
    .locator(".wf-inspector")
    .getByRole("button", {
      name: "Actions for Draft image prompt",
      exact: true,
    })
    .click();
  await page
    .getByRole("menuitem", { name: "Test this block", exact: true })
    .click();
  await page
    .getByRole("textbox", { name: "Sample start.brief", exact: true })
    .fill("Synthetic test brief");
  await page.getByRole("button", { name: "Test block", exact: true }).click();
  await done(page);
  await page.reload();
  await done(page);
  await expect(page.locator(".wf-run-card")).toContainText(
    "Draft image prompt",
  );
  const list = await (
    await request.get(`/api/workflows/runs?def_id=${d.id}`)
  ).json();
  expect(list.items).toEqual([]);
  const tests = await (
    await request.get(`/api/workflows/defs/${d.id}/tests?node_id=n_draft`)
  ).json();
  expect(tests).toHaveLength(1);
  expect(tests[0].mode).toBe("test");
  expect(tests[0].nodes.n_images.attempt).toBe(0);
  await page.getByRole("button", { name: "Close Run", exact: true }).click();
  await configureStudioBlock(page, "Draft image prompt");
  await page.getByRole("tab", { name: "Output", exact: true }).click();
  await expect(page.locator(".wf-panel-body").last()).toContainText(
    "Block test",
  );
});

test("Favorites select actual image outputs and saved run uses an immutable canvas snapshot", async ({
  page,
  request,
  browserName,
}) => {
  const d = await create(request, { review: false, count: 2, pick: true });
  const run = await start(request, d);
  await page.goto(`/workflows/${d.id}?run=1`);
  await expect(
    page.getByRole("region", { name: "Pick favorites" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Pick result 2", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Keep favorites", exact: true })
    .click();
  await done(page);
  const completed = await (
    await request.get(`/api/workflows/runs/${run.id}/v2`)
  ).json();
  expect(completed.results[0].items[0].value[0].id).toBe(
    completed.nodes.n_images.output.images[1].id,
  );
  const changed: Doc = structuredClone(d.graph);
  changed.nodes[0].position.x += 300;
  await request.put(`/api/workflows/defs/${d.id}`, {
    data: {
      name: d.name,
      description: d.description,
      icon: d.icon,
      graph: changed,
      version: d.version,
    },
  });
  await page.goto(`/workflows/${d.id}/runs/${run.id}`);
  await expect(
    page.getByText("The current workflow has changed.", { exact: false }),
  ).toBeVisible();
  await expect(page.locator(".wf-canvas")).toHaveAttribute(
    "aria-label",
    "Read-only workflow canvas",
  );
  await expect(
    page.getByRole("region", { name: "Workflow results" }),
  ).toBeVisible();
  await shot(page, `run-view-${browserName}`);
});

test("Failed image block retries without repeating the finished text and shows paused notification", async ({
  page,
  request,
}) => {
  const d = await create(request, { review: false });
  const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  image.config.prompt = `Synthetic image ${d.id} #fail-once`;
  const saved = await (
    await request.put(`/api/workflows/defs/${d.id}`, {
      data: {
        name: d.name,
        description: d.description,
        icon: d.icon,
        graph: d.graph,
        version: d.version,
      },
    })
  ).json();
  await start(request, saved);
  await page.goto(`/workflows/${d.id}?run=1`);
  await expect(page.locator('.wf-block[data-run="failed"]')).toContainText(
    "Image could not be completed or validated",
  );
  await expect(
    page.getByRole("button", { name: "Retry block", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Retry block", exact: true }).click();
  await done(page);
  const recovered = await (
    await request.get(`/api/workflows/runs?def_id=${d.id}`)
  ).json();
  expect(recovered.items[0].nodes.n_draft.attempt).toBe(1);
  expect(recovered.items[0].nodes.n_images.attempt).toBe(2);
  const paused = await create(request, { review: true });
  await page.goto("/");
  await start(request, paused);
  await expect(
    page.getByRole("button", { name: "Open", exact: true }),
  ).toBeVisible();
  await expect(
    page.locator(
      'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
    ),
  ).toBeVisible();
  await page.getByRole("button", { name: "Open", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: "Review result", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reject", exact: true }).click();
  await done(page);
});

test("Palette selects the correct paused run when workflow names repeat", async ({
  page,
  request,
}) => {
  const name = `Synthetic repeated palette ${crypto.randomUUID()}`;
  const first = await create(request, { name });
  const second = await create(request, { name });
  const runs = [await start(request, first), await start(request, second)];
  const duplicateKeys: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error" && message.text().includes("same key"))
      duplicateKeys.push(message.text());
  });
  await page.goto("/");
  await expect(
    page.locator(
      'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
    ),
  ).toBeVisible();
  await page.keyboard.press("ControlOrMeta+k");
  await page
    .getByRole("combobox", { name: "Search chats and actions" })
    .fill(`Resume ${name}`);
  const options = page.getByRole("option", {
    name: `Resume ${name}`,
    exact: true,
  });
  await expect(options).toHaveCount(2);
  const values = await options.evaluateAll((items) =>
    items.map((item) => item.getAttribute("data-value")),
  );
  expect(new Set(values).size).toBe(2);
  const selected = values[1]!.slice("resume:".length);
  expect(runs.map((run) => run.id)).toContain(selected);
  await options.nth(1).click();
  await expect(page).toHaveURL(new RegExp(`/runs/${selected}$`));
  await expect(
    page.getByRole("textbox", { name: "Review result", exact: true }),
  ).toBeVisible();
  expect(duplicateKeys).toEqual([]);
});

test("Full application lifecycle restart preserves completed blocks and resumes unfinished work", async ({
  page,
  request,
  browserName,
}) => {
  const d = await create(request, { review: false });
  const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  image.config.prompt = "Synthetic restart image #restart";
  const saved = await (
    await request.put(`/api/workflows/defs/${d.id}`, {
      data: {
        name: d.name,
        description: d.description,
        icon: d.icon,
        graph: d.graph,
        version: d.version,
      },
    })
  ).json();
  const run = await start(request, saved);
  await page.goto(`/workflows/${d.id}?run=1`);
  await expect(page.locator('.wf-block[data-run="running"]')).toContainText(
    "Create images",
  );
  expect(
    (await request.post(`${fakeAppURL}/tests/restart-lifecycle`)).ok(),
  ).toBe(true);
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Retry unfinished steps", exact: true }),
  ).toBeVisible();
  const interrupted = await (
    await request.get(`/api/workflows/runs/${run.id}/v2`)
  ).json();
  expect(interrupted.state).toBe("interrupted");
  expect(interrupted.nodes.n_draft.state).toBe("complete");
  await page
    .getByRole("button", { name: "Retry unfinished steps", exact: true })
    .click();
  await done(page);
  const recovered = await (
    await request.get(`/api/workflows/runs/${run.id}/v2`)
  ).json();
  expect(recovered.nodes.n_draft.attempt).toBe(1);
  expect(recovered.nodes.n_draft.output).toEqual(
    interrupted.nodes.n_draft.output,
  );
  expect(recovered.nodes.n_images.attempt).toBe(2);
  await shot(page, `restart-recovered-${browserName}`);
});

for (const width of [390, 1440])
  for (const theme of ["dark", "light"])
    test(`Run design states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      const results = [];
      await page.setViewportSize({ width, height: 900 });
      for (const state of [
        "run-running",
        "run-paused",
        "run-complete",
        "run-failed",
        "run-interrupted",
        "run-reused",
        "run-skipped",
        "pick-paused",
        "block-test",
        "setup-pick",
        "run-view",
        "versions",
        "run-from-here",
        "test-inputs",
      ]) {
        await page.goto("/design?studio");
        await page.getByRole("button", { name: theme, exact: true }).click();
        await page.getByRole("button", { name: state, exact: true }).click();
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        expect(
          scan.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          `${state} ${width} ${theme}`,
        ).toEqual([]);
        results.push({ width, theme, state, seriousCritical: 0 });
        await shot(page, `${state}-${width}-${theme}-${browserName}`);
      }
      await mkdir(dir, { recursive: true });
      await writeFile(
        `${dir}/axe-states-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });
test("Run activity stops for system and Always reduced motion", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/design?studio&state=run-running");
  await settle(page);
  const block = page.locator('.wf-block[data-run="running"]');
  await expect(block).toBeVisible();
  expect(
    await block.evaluate(
      (el) => getComputedStyle(el, "::before").animationName,
    ),
  ).toBe("wf-sweep");
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(
    await block.evaluate(
      (el) => getComputedStyle(el, "::before").animationName,
    ),
  ).toBe("none");
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.evaluate(
    () => (document.documentElement.dataset.reduceMotion = "always"),
  );
  expect(
    await block.evaluate(
      (el) => getComputedStyle(el, "::before").animationName,
    ),
  ).toBe("none");
});

test.describe("Phone", () => {
  test.use({
    viewport: { width: 390, height: 844 },
    hasTouch: true,
    isMobile: true,
  });
  test("Outline opens review in a sheet and keeps edit and reject decisions", async ({
    page,
    request,
    browserName,
  }) => {
    const d = await create(request);
    const run = await start(request, d);
    await page.goto(`/workflows/${d.id}?run=1`);
    await expect(
      page.locator('.wf-outline-row[data-run="paused"]'),
    ).toContainText("Waiting for you");
    await page
      .getByRole("textbox", { name: "Review result", exact: true })
      .fill("Synthetic phone edit");
    await shot(page, `phone-paused-${browserName}`);
    await page.getByRole("button", { name: "Approve", exact: true }).click();
    await done(page);
    const result = await (
      await request.get(`/api/workflows/runs/${run.id}/v2`)
    ).json();
    expect(result.nodes.n_review.output.value).toBe("Synthetic phone edit");
    await start(request, d);
    await expect(
      page.locator('.wf-outline-row[data-run="paused"]'),
    ).toContainText("Waiting for you");
    await expect(
      page.getByRole("textbox", { name: "Review result", exact: true }),
    ).not.toHaveValue("Synthetic phone edit");
    await page.getByRole("button", { name: "Reject", exact: true }).click();
    await done(page);
    const rejected = await (
      await request.get(`/api/workflows/runs?def_id=${d.id}`)
    ).json();
    expect(rejected.items[0].nodes.n_review.port).toBe("rejected");
    expect(rejected.items[0].nodes.n_images.state).toBe("skipped");
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
});
