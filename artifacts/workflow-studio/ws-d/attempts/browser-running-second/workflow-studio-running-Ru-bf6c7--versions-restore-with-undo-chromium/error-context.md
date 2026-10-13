# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Run from here uses saved outputs, rejects changed settings, and versions restore with undo
- Location: tests/workflow-studio-running.spec.ts:184:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 202
Received: 422
```

# Test source

```ts
  15  | import { configureStudioBlock } from "./studio-helpers";
  16  | const dir = "../artifacts/workflow-studio/ws-d/browser";
  17  | test.use({
  18  |   viewport: { width: 1440, height: 900 },
  19  |   isMobile: false,
  20  |   hasTouch: false,
  21  |   video: { mode: "on", size: { width: 1440, height: 900 } },
  22  | });
  23  | async function create(
  24  |   request: APIRequestContext,
  25  |   options: {
  26  |     review?: boolean;
  27  |     prompt?: string;
  28  |     count?: number;
  29  |     pick?: boolean;
  30  |   } = {},
  31  | ) {
  32  |   const c = (await (await request.get("/api/connections")).json())[0];
  33  |   const d: Definition = await (
  34  |     await request.post("/api/workflows/defs", {
  35  |       data: {
  36  |         name: "Synthetic running workflow",
  37  |         template_id: "brief_images",
  38  |         default_model: { connection_id: c.id, model_id: "fake-chat" },
  39  |       },
  40  |     })
  41  |   ).json();
  42  |   const doc = d.graph;
  43  |   if (options.review === false) {
  44  |     doc.nodes = doc.nodes.filter((n) => n.kind !== "review");
  45  |     doc.edges = doc.edges.filter(
  46  |       (e) => e.source !== "n_review" && e.target !== "n_review",
  47  |     );
  48  |     doc.edges.push({
  49  |       id: "e_direct",
  50  |       source: "n_draft",
  51  |       source_port: "out",
  52  |       target: "n_images",
  53  |       target_port: "in",
  54  |     });
  55  |     const images = doc.nodes.find((n) => n.kind === "generate_image")!;
  56  |     images.config.prompt = "{{draft.text}}";
  57  |   }
  58  |   const draft = doc.nodes.find((n) => n.kind === "generate")!;
  59  |   if (options.prompt) {
  60  |     draft.config.instructions = "";
  61  |     draft.config.prompt = options.prompt;
  62  |   }
  63  |   const images = doc.nodes.find((n) => n.kind === "generate_image")!;
  64  |   images.config.count = options.count ?? 1;
  65  |   images.config.seeds = Array.from(
  66  |     { length: images.config.count },
  67  |     (_, i) => 42 + i,
  68  |   );
  69  |   if (options.pick) {
  70  |     doc.nodes.push({
  71  |       id: "n_pick",
  72  |       key: "favorites",
  73  |       kind: "pick",
  74  |       title: "Pick favorites",
  75  |       disabled: false,
  76  |       position: { x: 320, y: 880 },
  77  |       config: { from: ["{{images.images}}"], type: "image_list", maximum: 1 },
  78  |     });
  79  |     const edge = doc.edges.find((e) => e.target === "n_save")!;
  80  |     edge.target = "n_pick";
  81  |     doc.edges.push({
  82  |       id: "e_pick_save",
  83  |       source: "n_pick",
  84  |       source_port: "out",
  85  |       target: "n_save",
  86  |       target_port: "in",
  87  |     });
  88  |     const save = doc.nodes.find((n) => n.kind === "output")!;
  89  |     save.config.include = [{ label: "Favorite", ref: "{{favorites.chosen}}" }];
  90  |   }
  91  |   return (
  92  |     await request.put(`/api/workflows/defs/${d.id}`, {
  93  |       data: {
  94  |         name: d.name,
  95  |         description: d.description,
  96  |         icon: d.icon,
  97  |         graph: doc,
  98  |         version: d.version,
  99  |       },
  100 |     })
  101 |   ).json() as Promise<Definition>;
  102 | }
  103 | async function start(
  104 |   request: APIRequestContext,
  105 |   d: Definition,
  106 |   extra: Record<string, unknown> = {},
  107 | ) {
  108 |   const response = await request.post(`/api/workflows/defs/${d.id}/runs`, {
  109 |     data: {
  110 |       request_key: crypto.randomUUID(),
  111 |       inputs: { brief: "Synthetic blue shapes" },
  112 |       ...extra,
  113 |     },
  114 |   });
> 115 |   expect(response.status()).toBe(202);
      |                             ^ Error: expect(received).toBe(expected) // Object.is equality
  116 |   return response.json() as Promise<Run>;
  117 | }
  118 | async function done(page: Page) {
  119 |   await expect(
  120 |     page.locator(".wf-run-card [role=status]").first(),
  121 |   ).toContainText("Ready for review");
  122 | }
  123 | async function shot(page: Page, name: string) {
  124 |   await settle(page);
  125 |   await mkdir(dir, { recursive: true });
  126 |   await page.screenshot({ path: `${dir}/${name}-fake.png`, fullPage: true });
  127 | }
  128 | 
  129 | test("Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect", async ({
  130 |   page,
  131 |   request,
  132 |   browserName,
  133 | }) => {
  134 |   const d = await create(request, { prompt: "#long:16 #slow:3", review: true });
  135 |   const run = await start(request, d);
  136 |   await page.goto(`/workflows/${d.id}?run=1`);
  137 |   await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  138 |   const text = page.locator(".wf-stream-preview").first();
  139 |   await expect(text).toContainText("token");
  140 |   const before = await text.innerText();
  141 |   await expect.poll(() => text.innerText()).not.toBe(before);
  142 |   await expect(
  143 |     page.getByRole("button", { name: "Following run", exact: true }),
  144 |   ).toHaveAttribute("aria-pressed", "true");
  145 |   await page.getByRole("button", { name: "Zoom out", exact: true }).click();
  146 |   await expect(
  147 |     page.getByRole("button", { name: "Resume following run", exact: true }),
  148 |   ).toHaveAttribute("aria-pressed", "false");
  149 |   await shot(page, `stream-${browserName}`);
  150 |   let detailReads = 0;
  151 |   page.on("request", (r) => {
  152 |     if (r.url().endsWith(`/runs/${run.id}/v2`)) detailReads++;
  153 |   });
  154 |   await page.context().setOffline(true);
  155 |   await page.waitForTimeout(350);
  156 |   await page.context().setOffline(false);
  157 |   await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
  158 |     "Waiting for you",
  159 |   );
  160 |   await expect(page.locator(".wf-stream-preview").first()).toContainText(
  161 |     "token15",
  162 |   );
  163 |   expect(detailReads).toBeLessThanOrEqual(1);
  164 |   await expect(
  165 |     page.getByRole("button", { name: "Following run", exact: true }),
  166 |   ).toHaveAttribute("aria-pressed", "true");
  167 |   await page
  168 |     .getByRole("textbox", { name: "Review result" })
  169 |     .fill("Synthetic approved blue circle");
  170 |   await page.getByRole("button", { name: "Approve", exact: true }).click();
  171 |   await done(page);
  172 |   await expect(page.locator('.wf-block[data-run="complete"]')).toHaveCount(
  173 |     d.graph.nodes.length,
  174 |   );
  175 |   const snapshot = await (
  176 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  177 |   ).json();
  178 |   expect(snapshot.nodes.n_review.output.value).toBe(
  179 |     "Synthetic approved blue circle",
  180 |   );
  181 |   await shot(page, `complete-${browserName}`);
  182 | });
  183 | 
  184 | test("Run from here uses saved outputs, rejects changed settings, and versions restore with undo", async ({
  185 |   page,
  186 |   request,
  187 |   browserName,
  188 | }) => {
  189 |   const d = await create(request, { review: false });
  190 |   const first = await start(request, d);
  191 |   await page.goto(`/workflows/${d.id}?run=1`);
  192 |   await done(page);
  193 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  194 |   await configureStudioBlock(page, "Create images");
  195 |   await page
  196 |     .locator(".wf-inspector")
  197 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  198 |     .click();
  199 |   await page
  200 |     .getByRole("menuitem", { name: "Run from here", exact: true })
  201 |     .click();
  202 |   await page
  203 |     .getByRole("button", { name: "Run from here", exact: true })
  204 |     .click();
  205 |   await done(page);
  206 |   await expect(page.locator('.wf-block[data-run="reused"]')).toContainText([
  207 |     "Start",
  208 |     "Draft image prompt",
  209 |   ]);
  210 |   const all = await (
  211 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  212 |   ).json();
  213 |   const second = all.items[0];
  214 |   expect(second.id).not.toBe(first.id);
  215 |   expect(second.nodes.n_draft.reused_from).toBe(first.id);
```