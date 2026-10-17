import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
import type { Definition } from "../src/components/workflows/studio/types";
import { blankDoc, remove } from "../src/components/workflows/studio/graph";
const dir = "../artifacts/workflow-studio/ws-c/browser";
test.use({
  viewport: { width: 1440, height: 900 },
  isMobile: false,
  hasTouch: false,
  video: { mode: "on", size: { width: 1440, height: 900 } },
});
async function create(
  request: APIRequestContext,
  template?: string,
): Promise<Definition> {
  const c = (await (await request.get("/api/connections")).json())[0];
  const r = await request.post("/api/workflows/defs", {
    data: {
      name: "Synthetic editor",
      ...(template ? { template_id: template } : { graph: blankDoc() }),
      default_model: { connection_id: c.id, model_id: "fake-chat" },
    },
  });
  expect(r.status()).toBe(201);
  return r.json();
}
async function block(page: Page, id: string) {
  await page.locator(`.react-flow__node[data-id='${id}']`).click();
}
async function saved(page: Page) {
  await expect(page.locator(".wf-save-status")).toHaveText("Saved");
}
async function def(
  request: APIRequestContext,
  id: string,
): Promise<Definition> {
  return (await request.get(`/api/workflows/defs/${id}`)).json();
}
test("Desktop native dragging adds blocks in space and inserts on a connection", async ({
  page,
  request,
}) => {
  const d = await create(request);
  await page.goto(`/workflows/${d.id}`);
  await expect(page.locator(".react-flow__node-block")).toHaveCount(2);
  const palette = page.getByRole("button", {
    name: "Generate text",
    exact: true,
  });
  const box = await page.locator(".wf-canvas").boundingBox();
  expect(box).toBeTruthy();
  await palette.dragTo(page.locator(".wf-canvas"), {
    targetPosition: { x: 140, y: 180 },
  });
  await expect(page.locator(".react-flow__node-block")).toHaveCount(3);
  await page
    .getByRole("button", { name: "Close Inspector", exact: true })
    .click();
  await saved(page);
  await settle(page);
  const edge = page.locator(".react-flow__edge-path").first();
  const at = await edge.evaluate((element: SVGPathElement) => {
    const p = element
      .getPointAtLength(element.getTotalLength() / 2)
      .matrixTransform(element.getScreenCTM()!);
    return { x: p.x, y: p.y };
  });
  const canvasBox = await page.locator(".wf-canvas").boundingBox();
  expect(canvasBox).toBeTruthy();
  await palette.dragTo(page.locator(".wf-canvas"), {
    targetPosition: { x: at.x - canvasBox!.x, y: at.y - canvasBox!.y },
  });
  await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  await saved(page);
  const current = await def(request, d.id);
  expect(current.graph.edges).toHaveLength(2);
  const inserted = current.graph.nodes.at(-1)!;
  expect(
    current.graph.edges.some(
      (e) => e.target === inserted.id && e.source === "n_start",
    ),
  ).toBe(true);
  expect(
    current.graph.edges.some(
      (e) => e.source === inserted.id && e.target === "n_save",
    ),
  ).toBe(true);
});
test("Keyboard adds, wires through Connections and runs a blank workflow", async ({
  page,
  request,
}) => {
  const d = await create(request);
  await page.goto(`/workflows/${d.id}`);
  const start = page.locator(".react-flow__node[data-id='n_start']");
  await start.focus();
  await page.keyboard.press("n");
  const quick = page.getByRole("dialog", { name: "Add a block" });
  await expect(quick).toBeVisible();
  await quick.getByRole("combobox").fill("Generate text");
  await page.keyboard.press("Enter");
  await page
    .getByRole("textbox", { name: "Prompt", exact: true })
    .fill("Synthetic keyboard workflow");
  await page.getByRole("combobox", { name: "Add an input connection" }).click();
  await page.getByRole("option", { name: "Start", exact: true }).click();
  await page
    .getByRole("combobox", { name: "Add an output connection" })
    .click();
  await page.getByRole("option", { name: "Save results", exact: true }).click();
  await saved(page);
  await page.getByRole("button", { name: "Run", exact: true }).click();
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  await expect(
    page
      .getByRole("article", { name: "Synthetic editor run" })
      .getByRole("status"),
  ).toContainText("Ready for review");
});
test("Delete heals a chain in one undo; redo keeps references as explicit problems", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  await page.goto(`/workflows/${d.id}`);
  await block(page, "n_review");
  await page.locator(".react-flow__node[data-id='n_review']").focus();
  await page.keyboard.press("Delete");
  await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  await saved(page);
  const healed = await def(request, d.id);
  expect(
    healed.graph.edges.some(
      (e) => e.source === "n_draft" && e.target === "n_images",
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Undo", exact: true }).click();
  await expect(page.locator(".react-flow__node-block")).toHaveCount(5);
  await saved(page);
  expect((await def(request, d.id)).graph.nodes).toEqual(d.graph.nodes);
  await page.getByRole("button", { name: "Redo", exact: true }).click();
  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Problems", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("A referenced output does not exist.").first(),
  ).toBeVisible();
});
test("Autosave survives reload and both stale-save conflict choices preserve intent", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  await page.goto(`/workflows/${d.id}`);
  await block(page, "n_draft");
  await page
    .getByRole("textbox", { name: "Block name", exact: true })
    .fill("Synthetic renamed draft");
  await saved(page);
  await page.reload();
  await expect(
    page
      .locator(".wf-block-title")
      .filter({ hasText: "Synthetic renamed draft" }),
  ).toBeVisible();
  const stale = await def(request, d.id);
  await request.put(`/api/workflows/defs/${d.id}`, {
    data: {
      ...stale,
      name: "Synthetic other device",
      version: stale.version,
      graph: stale.graph,
      id: undefined,
      graph_hash: undefined,
      template_id: undefined,
      archived_at: undefined,
      created_at: undefined,
      updated_at: undefined,
    },
  });
  await block(page, "n_draft");
  await page
    .getByRole("textbox", { name: "Block name", exact: true })
    .fill("Synthetic keep mine");
  await expect(
    page.getByText("This workflow changed on another device."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Keep mine", exact: true }).click();
  await saved(page);
  expect(
    (await def(request, d.id)).graph.nodes.find((n) => n.id === "n_draft")!
      .title,
  ).toBe("Synthetic keep mine");
  const next = await def(request, d.id);
  await request.put(`/api/workflows/defs/${d.id}`, {
    data: {
      name: "Synthetic latest",
      description: next.description,
      icon: next.icon,
      graph: next.graph,
      version: next.version,
    },
  });
  await page
    .getByRole("textbox", { name: "Block name", exact: true })
    .fill("Synthetic discarded draft");
  await expect(
    page.getByText("This workflow changed on another device."),
  ).toBeVisible();
  await page.getByRole("button", { name: "Load latest", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Synthetic latest", exact: true }),
  ).toBeVisible();
  expect(
    (await def(request, d.id)).graph.nodes.find((n) => n.id === "n_draft")!
      .title,
  ).toBe("Synthetic keep mine");
});
test("References, rename, notes, context actions and tidy persist without hidden prompts", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  await page.goto(`/workflows/${d.id}`);
  await block(page, "n_draft");
  await page.getByText("Advanced", { exact: true }).click();
  await page
    .getByRole("textbox", { name: "Reference name", exact: true })
    .fill("draft_new");
  await page
    .getByRole("textbox", { name: "Reference name", exact: true })
    .press("Enter");
  await saved(page);
  const renamed = await def(request, d.id);
  expect(
    renamed.graph.nodes.find((n) => n.kind === "review")?.config,
  ).toMatchObject({ show: "{{draft_new.text}}" });
  await page
    .getByRole("button", { name: "Insert a variable in Prompt", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: /Start.*start.brief/ }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Note", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Note text", exact: true })
    .fill("Synthetic annotation");
  await saved(page);
  await page
    .getByRole("button", { name: "Tidy up", exact: true })
    .first()
    .click();
  await saved(page);
  expect((await def(request, d.id)).graph.notes[0].text).toBe(
    "Synthetic annotation",
  );
});
test("New UI states match tokens and have no serious/critical axe findings in both themes", async ({
  page,
  request,
  browserName,
}) => {
  const d = await create(request, "meeting_pack");
  await mkdir(dir, { recursive: true });
  const results = [];
  for (const theme of ["light", "dark"]) {
    await request.patch("/api/settings", {
      data: { "appearance.theme": theme },
    });
    await page.addInitScript(
      (v) => localStorage.setItem("workbench-theme", v),
      theme,
    );
    const modelMetadata = page.waitForResponse(
      (response) =>
        new URL(response.url()).pathname === "/api/models" && response.ok(),
    );
    await page.goto(`/workflows/${d.id}`);
    await (await modelMetadata).finished();
    await expect(page.locator(".wf-studio")).toBeVisible();
    await expect(page.locator(".wf-save-status")).toHaveText("Saved");
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    await settle(page);
    await expect(page.locator(".app-main")).toHaveCSS("opacity", "1");
    for (const state of ["canvas", "selected", "problems"]) {
      if (state === "selected") await block(page, "n_pack");
      if (state === "problems") {
        await page
          .getByRole("button", { name: "Workflow menu", exact: true })
          .click();
        await page
          .getByRole("menuitem", { name: "Problems", exact: true })
          .click();
      }
      await settle(page);
      const scan = await new AxeBuilder({ page }).analyze();
      expect(
        scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
        state,
      ).toEqual([]);
      results.push({ theme, state, seriousCritical: 0 });
      await page.screenshot({
        path: `${dir}/${state}-1440-${theme}-${browserName}-fake.png`,
      });
    }
  }
  await writeFile(
    `${dir}/axe-editor-${browserName}.json`,
    JSON.stringify(results, null, 2),
  );
});
test("Both reduced-motion triggers remove Studio motion; dragging never gets a transform transition", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  await request.patch("/api/settings", {
    data: { "appearance.theme": "dark", "appearance.reduce_motion": "system" },
  });
  await page.addInitScript(() =>
    localStorage.setItem("workbench-theme", "light"),
  );
  const preferenceWrites: unknown[] = [];
  page.on("request", (r) => {
    if (r.method() === "PATCH" && new URL(r.url()).pathname === "/api/settings")
      preferenceWrites.push(r.postDataJSON());
  });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(`/workflows/${d.id}`);
  await block(page, "n_draft");
  expect(
    await page
      .locator(".wf-right")
      .evaluate((e) => getComputedStyle(e).animationName),
  ).toBe("none");
  await settle(page);
  expect(preferenceWrites).toEqual([]);
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const response = await request.patch("/api/settings", {
    data: { "appearance.reduce_motion": "always" },
  });
  expect(response.ok()).toBeTruthy();
  expect((await response.json())["appearance.reduce_motion"]).toBe("always");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute(
    "data-reduce-motion",
    "always",
  );
  await block(page, "n_draft");
  expect(
    await page
      .locator(".wf-right")
      .evaluate((e) => getComputedStyle(e).animationName),
  ).toBe("none");
  expect(
    await page
      .locator(".react-flow__node[data-id='n_draft']")
      .evaluate((e) => getComputedStyle(e).transitionDuration),
  ).toBe("0s");
  await request.patch("/api/settings", {
    data: { "appearance.reduce_motion": "system" },
  });
});
test.describe("Phone Outline", () => {
  test.use({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
  });
  test("Inserts and edits through the real bottom sheets at 390px", async ({
    page,
    request,
    browserName,
  }) => {
    const d = await create(request, "brief_images");
    await page.goto(`/workflows/${d.id}`);
    await page
      .getByRole("button", { name: "Insert after Start", exact: true })
      .tap();
    const quick = page.getByRole("dialog", { name: "Add a block" });
    await quick.getByRole("combobox").fill("Generate text");
    await quick.getByRole("option").filter({ hasText: "Generate text" }).tap();
    const inspector = page.getByRole("dialog");
    await inspector
      .getByRole("textbox", { name: "Block name", exact: true })
      .fill("Synthetic phone block");
    await inspector
      .getByRole("textbox", { name: "Prompt", exact: true })
      .fill("Synthetic phone prompt");
    await page
      .getByRole("button", { name: "Close Inspector", exact: true })
      .tap();
    await expect(
      page.getByRole("button", {
        name: "Configure Synthetic phone block",
        exact: true,
      }),
    ).toBeVisible();
    await saved(page);
    await page.reload();
    await page
      .getByRole("button", {
        name: "Configure Synthetic phone block",
        exact: true,
      })
      .tap();
    await settle(page);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
    const scan = await new AxeBuilder({ page }).analyze();
    expect(
      scan.violations.filter((v) =>
        ["serious", "critical"].includes(v.impact ?? ""),
      ),
    ).toEqual([]);
    await mkdir(dir, { recursive: true });
    await page.screenshot({
      path: `${dir}/phone-inspector-390-light-${browserName}-fake.png`,
    });
  });
  test("Outline reorders a chain, displays branch lanes and prevents structural edits to non-nestable graphs", async ({
    page,
    request,
    browserName,
  }) => {
    const d = await create(request, "brief_images");
    const chain = remove(d.graph, ["n_review"]);
    const put = async (graph: Definition["graph"]) => {
      const current = await def(request, d.id);
      const response = await request.put(`/api/workflows/defs/${d.id}`, {
        data: {
          name: current.name,
          description: current.description,
          icon: current.icon,
          version: current.version,
          graph,
        },
      });
      expect(response.ok()).toBeTruthy();
    };
    await put(chain);
    await page.goto(`/workflows/${d.id}`);
    await page
      .getByRole("button", { name: "Actions for Create images", exact: true })
      .tap();
    await page.getByRole("menuitem", { name: "Move up", exact: true }).tap();
    await saved(page);
    expect(
      (await def(request, d.id)).graph.edges.some(
        (e) => e.source === "n_start" && e.target === "n_images",
      ),
    ).toBe(true);
    await page
      .getByRole("button", { name: "Actions for Create images", exact: true })
      .tap();
    await page.getByRole("menuitem", { name: "Move down", exact: true }).tap();
    await saved(page);
    expect((await def(request, d.id)).graph.edges).toEqual(chain.edges);
    const branched = structuredClone(d.graph);
    branched.edges.push({
      id: "e_rejected_save",
      source: "n_review",
      source_port: "rejected",
      target: "n_save",
      target_port: "in",
    });
    await put(branched);
    await page.reload();
    await expect(page.locator(".wf-outline-lane")).toHaveCount(2);
    await expect(
      page.locator(".wf-lane-label").filter({ hasText: "Approved" }),
    ).toBeVisible();
    await expect(
      page.locator(".wf-lane-label").filter({ hasText: "Rejected" }),
    ).toBeVisible();
    await expect(page.getByText("Then", { exact: true })).toBeVisible();
    await mkdir(dir, { recursive: true });
    await page.screenshot({
      path: `${dir}/outline-branches-390-${browserName}-fake.png`,
    });
    const detached = structuredClone(
      branched.nodes.find((n) => n.kind === "generate")!,
    );
    detached.id = "n_detached";
    detached.key = "detached";
    detached.title = "Synthetic detached";
    branched.nodes.push(detached);
    await put(branched);
    await page.reload();
    await expect(
      page.getByText(
        "Part of this workflow is easier to change on a larger screen. Settings still open here.",
      ),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Insert after Start", exact: true }),
    ).toBeDisabled();
    await page
      .getByRole("button", {
        name: "Actions for Synthetic detached",
        exact: true,
      })
      .tap();
    await expect(
      page.getByRole("menuitem", { name: "Duplicate", exact: true }),
    ).toHaveAttribute("aria-disabled", "true");
    await expect(
      page.getByRole("menuitem", { name: "Delete", exact: true }),
    ).toHaveAttribute("aria-disabled", "true");
    await page.keyboard.press("Escape");
    await page
      .getByRole("button", {
        name: "Configure Synthetic detached",
        exact: true,
      })
      .tap();
    await page
      .getByRole("textbox", { name: "Block name", exact: true })
      .fill("Synthetic edited on phone");
    await page
      .getByRole("button", { name: "Close Inspector", exact: true })
      .tap();
    await saved(page);
    expect(
      (await def(request, d.id)).graph.nodes.find((n) => n.id === detached.id)!
        .title,
    ).toBe("Synthetic edited on phone");
  });
});

test("Design catalogue exposes every editing panel and Quick add in both themes and sizes", async ({
  page,
  request,
  browserName,
}) => {
  test.setTimeout(240000);
  await request.patch("/api/settings", {
    data: { "appearance.reduce_motion": "system" },
  });
  const states = [
    "empty",
    "selected",
    "problems",
    "conflict",
    "outline",
    "non-nestable",
    "settings",
    "run-inputs",
    "cards",
    "home-cards",
    "quick-add",
    ...[
      "start",
      "generate",
      "transcribe",
      "clean_transcript",
      "generate_image",
      "review",
      "output",
    ].map((k) => "setup-" + k),
  ];
  const results = [];
  await mkdir(dir, { recursive: true });
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const theme of ["light", "dark"]) {
      for (const state of states) {
        await page.goto(`/design?studio&state=${state}`);
        await expect(
          page.getByText("Workflow Studio · fake runtime states"),
        ).toBeVisible();
        await page.evaluate(
          (v) => (document.documentElement.dataset.theme = v),
          theme,
        );
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        expect(
          scan.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          `${width}/${theme}/${state}`,
        ).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          `${width}/${theme}/${state} overflow`,
        ).toBe(true);
        results.push({ width, theme, state, seriousCritical: 0 });
        await page.screenshot({
          path: `${dir}/design-${state}-${width}-${theme}-${browserName}-fake.png`,
        });
      }
    }
  }
  await writeFile(
    `${dir}/axe-design-${browserName}.json`,
    JSON.stringify(results, null, 2),
  );
});

test("Runtime availability errors are server-owned and lead to workflow settings", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  d.graph.settings.default_model = null;
  await request.put(`/api/workflows/defs/${d.id}`, {
    data: {
      name: d.name,
      description: d.description,
      icon: d.icon,
      graph: d.graph,
      version: d.version,
    },
  });
  const validation = await (
    await request.post(`/api/workflows/defs/${d.id}/validate`, {
      data: { graph: d.graph },
    })
  ).json();
  const issue = validation.issues.find(
    (i: { severity: string }) => i.severity === "error",
  );
  expect(issue).toBeTruthy();
  await page.goto(`/workflows/${d.id}`);
  await page
    .getByRole("button", { name: "Workflow menu", exact: true })
    .click();
  await page.getByRole("menuitem", { name: "Problems", exact: true }).click();
  await page.getByRole("button", { name: issue.message, exact: true }).click();
  await expect(
    page.getByRole("combobox", { name: "Default text model", exact: true }),
  ).toBeVisible();
});

test("Opening and fitting a template does not create an unsaved edit; explicit zoom still persists", async ({
  page,
  request,
}) => {
  const d = await create(request, "brief_images");
  await page.goto("/workflows");
  await page.goto(`/workflows/${d.id}`);
  await expect(page.locator(".react-flow__node-block")).toHaveCount(5);
  await settle(page);
  await saved(page);
  expect((await def(request, d.id)).version).toBe(1);
  expect((await def(request, d.id)).graph.viewport).toBeNull();
  await page.goBack();
  await expect(
    page.getByRole("heading", { name: "Workflows", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("dialog", { name: "Leave with unsaved changes?" }),
  ).not.toBeVisible();
  await page.goto(`/workflows/${d.id}`);
  await page.getByRole("button", { name: "Zoom in", exact: true }).click();
  await saved(page);
  await expect
    .poll(async () => (await def(request, d.id)).graph.viewport)
    .not.toBeNull();
});
