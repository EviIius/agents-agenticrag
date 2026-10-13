# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Single block tests use explicit samples and remain outside recent history after reload
- Location: tests/workflow-studio-running.spec.ts:262:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('.wf-run-card [role=status]').first()
Expected substring: "Ready for review"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" locator('.wf-run-card [role=status]').first() with timeout 5000ms
  - waiting for locator('.wf-run-card [role=status]').first()

```

```yaml
- complementary:
  - button "Expand sidebar"
  - link "New chat":
    - /url: /
  - button "Search chats"
  - navigation "Chat history":
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
      - link "Images":
        - /url: /images
  - button "Settings"
- main:
  - link "Back to Workflows":
    - /url: /workflows
    - text: Workflows
  - text: /
  - button "Synthetic running workflow"
  - status: Saved
  - button "Undo" [disabled]
  - button "Redo" [disabled]
  - button "Workflow menu"
  - button "Run"
  - complementary "Blocks":
    - textbox "Search blocks"
    - group:
      - text: Inputs
      - button "Start"
    - group:
      - text: AI
      - button "Generate text"
      - button "Classify" [disabled]
    - group:
      - text: Knowledge
      - button "Search the web" [disabled]
      - button "Search my files" [disabled]
      - button "Read a document" [disabled]
    - group:
      - text: Media
      - button "Transcribe recording"
      - button "Clean up transcript"
      - button "Create images"
    - group:
      - text: Logic
      - button "If / else" [disabled]
      - button "Compose text" [disabled]
    - group:
      - text: Review
      - button "Approve or edit"
      - button "Pick favorites"
    - group:
      - text: Output
      - button "Save results"
    - button "Note"
  - application:
    - img:
      - group "Connection from Start to Draft image prompt"
    - img:
      - group "Connection from Create images to Save results"
    - img:
      - group "Connection from Draft image prompt to Create images"
    - button "Insert on connection e_start_draft"
    - button "Delete connection e_start_draft"
    - button "Insert on connection e_images_save"
    - button "Delete connection e_images_save"
    - button "Insert on connection e_direct"
    - button "Delete connection e_direct"
    - group "Start block ‘Start’, 1 of 4":
      - text: Start Start
      - button "Actions for Start"
      - paragraph: "Inputs: Image brief"
      - text: start.brief
    - group "Generate text block ‘Draft image prompt’, 2 of 4":
      - text: Draft image prompt Generate text
      - button "Actions for Draft image prompt"
      - paragraph: fake-chat
      - text: draft.text
    - group "Create images block ‘Create images’, 3 of 4":
      - text: Create images Create images
      - button "Actions for Create images"
      - paragraph: 1 image · FLUX.2 klein
      - text: images.images images.prompt
    - group "Save results block ‘Save results’, 4 of 4":
      - text: Save results Save results
      - button "Actions for Save results"
      - paragraph: Markdown, JSON · 2 items
    - img
    - img "Mini Map"
    - link "React Flow attribution":
      - /url: https://reactflow.dev/attribution
      - text: React Flow
  - paragraph: Drag blocks from the left, or hover a connection and press +
  - button "Zoom out"
  - button "Zoom 100%": 100%
  - button "Zoom in"
  - button "Fit view"
  - button "Tidy up"
  - button "Outline view"
  - button "Canvas actions"
  - complementary "run":
    - heading "Run" [level=2]
    - button "Close Run"
    - form "Run workflow inputs":
      - heading "Run workflow" [level=2]
      - text: Image brief
      - textbox "Image brief"
      - paragraph: Add Image brief to start.
      - button "Run workflow" [disabled]
      - paragraph: Accepted runs keep going on your Mac. Text outputs are drafts for your review.
  - button "Import workflow JSON"
- region "Notifications alt+T"
```

# Test source

```ts
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
  57  |     const save = doc.nodes.find((n) => n.kind === "output")!;
  58  |     save.config.include = save.config.include.map((item) => ({
  59  |       ...item,
  60  |       ref: item.ref.replace("review.value", "draft.text"),
  61  |     }));
  62  |   }
  63  |   const draft = doc.nodes.find((n) => n.kind === "generate")!;
  64  |   if (options.prompt) {
  65  |     draft.config.instructions = "";
  66  |     draft.config.prompt = options.prompt;
  67  |   }
  68  |   const images = doc.nodes.find((n) => n.kind === "generate_image")!;
  69  |   images.config.count = options.count ?? 1;
  70  |   images.config.seeds = Array.from(
  71  |     { length: images.config.count },
  72  |     (_, i) => 42 + i,
  73  |   );
  74  |   if (options.pick) {
  75  |     doc.nodes.push({
  76  |       id: "n_pick",
  77  |       key: "favorites",
  78  |       kind: "pick",
  79  |       title: "Pick favorites",
  80  |       disabled: false,
  81  |       position: { x: 320, y: 880 },
  82  |       config: { from: ["{{images.images}}"], type: "image_list", maximum: 1 },
  83  |     });
  84  |     const edge = doc.edges.find((e) => e.target === "n_save")!;
  85  |     edge.target = "n_pick";
  86  |     doc.edges.push({
  87  |       id: "e_pick_save",
  88  |       source: "n_pick",
  89  |       source_port: "out",
  90  |       target: "n_save",
  91  |       target_port: "in",
  92  |     });
  93  |     const save = doc.nodes.find((n) => n.kind === "output")!;
  94  |     save.config.include = [{ label: "Favorite", ref: "{{favorites.chosen}}" }];
  95  |   }
  96  |   return (
  97  |     await request.put(`/api/workflows/defs/${d.id}`, {
  98  |       data: {
  99  |         name: d.name,
  100 |         description: d.description,
  101 |         icon: d.icon,
  102 |         graph: doc,
  103 |         version: d.version,
  104 |       },
  105 |     })
  106 |   ).json() as Promise<Definition>;
  107 | }
  108 | async function start(
  109 |   request: APIRequestContext,
  110 |   d: Definition,
  111 |   extra: Record<string, unknown> = {},
  112 | ) {
  113 |   const response = await request.post(`/api/workflows/defs/${d.id}/runs`, {
  114 |     data: {
  115 |       request_key: crypto.randomUUID(),
  116 |       inputs: { brief: "Synthetic blue shapes" },
  117 |       ...extra,
  118 |     },
  119 |   });
  120 |   expect(response.status()).toBe(202);
  121 |   return response.json() as Promise<Run>;
  122 | }
  123 | async function done(page: Page) {
  124 |   await expect(
  125 |     page.locator(".wf-run-card [role=status]").first(),
> 126 |   ).toContainText("Ready for review");
      |     ^ Error: expect(locator).toContainText(expected) failed
  127 | }
  128 | async function shot(page: Page, name: string) {
  129 |   await settle(page);
  130 |   await mkdir(dir, { recursive: true });
  131 |   await page.screenshot({ path: `${dir}/${name}-fake.png`, fullPage: true });
  132 | }
  133 | 
  134 | test("Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect", async ({
  135 |   page,
  136 |   request,
  137 |   browserName,
  138 | }) => {
  139 |   const d = await create(request, { prompt: "#long:16 #slow:3", review: true });
  140 |   const run = await start(request, d);
  141 |   await page.goto(`/workflows/${d.id}?run=1`);
  142 |   await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  143 |   const text = page.locator(".wf-stream-preview").first();
  144 |   await expect(text).toContainText("token");
  145 |   const before = await text.innerText();
  146 |   await expect.poll(() => text.innerText()).not.toBe(before);
  147 |   await expect(
  148 |     page.getByRole("button", { name: "Following run", exact: true }),
  149 |   ).toHaveAttribute("aria-pressed", "true");
  150 |   await page.getByRole("button", { name: "Zoom out", exact: true }).click();
  151 |   await expect(
  152 |     page.getByRole("button", { name: "Resume following run", exact: true }),
  153 |   ).toHaveAttribute("aria-pressed", "false");
  154 |   await shot(page, `stream-${browserName}`);
  155 |   let detailReads = 0;
  156 |   page.on("request", (r) => {
  157 |     if (r.url().endsWith(`/runs/${run.id}/v2`)) detailReads++;
  158 |   });
  159 |   await page.context().setOffline(true);
  160 |   await page.waitForTimeout(350);
  161 |   await page.context().setOffline(false);
  162 |   await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
  163 |     "Waiting for you",
  164 |   );
  165 |   await expect(page.locator(".wf-stream-preview").first()).toContainText(
  166 |     "token15",
  167 |   );
  168 |   expect(detailReads).toBeLessThanOrEqual(1);
  169 |   await expect(
  170 |     page.getByRole("button", { name: "Following run", exact: true }),
  171 |   ).toHaveAttribute("aria-pressed", "true");
  172 |   await page
  173 |     .getByRole("textbox", { name: "Review result" })
  174 |     .fill("Synthetic approved blue circle");
  175 |   await page.getByRole("button", { name: "Approve", exact: true }).click();
  176 |   await done(page);
  177 |   await expect(page.locator('.wf-block[data-run="complete"]')).toHaveCount(
  178 |     d.graph.nodes.length,
  179 |   );
  180 |   const snapshot = await (
  181 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  182 |   ).json();
  183 |   expect(snapshot.nodes.n_review.output.value).toBe(
  184 |     "Synthetic approved blue circle",
  185 |   );
  186 |   await shot(page, `complete-${browserName}`);
  187 | });
  188 | 
  189 | test("Run from here uses saved outputs, rejects changed settings, and versions restore with undo", async ({
  190 |   page,
  191 |   request,
  192 |   browserName,
  193 | }) => {
  194 |   const d = await create(request, { review: false });
  195 |   const first = await start(request, d);
  196 |   await page.goto(`/workflows/${d.id}?run=1`);
  197 |   await done(page);
  198 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  199 |   await configureStudioBlock(page, "Create images");
  200 |   await page
  201 |     .locator(".wf-inspector")
  202 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  203 |     .click();
  204 |   await page
  205 |     .getByRole("menuitem", { name: "Run from here", exact: true })
  206 |     .click();
  207 |   await page
  208 |     .getByRole("button", { name: "Run from here", exact: true })
  209 |     .click();
  210 |   await done(page);
  211 |   await expect(page.locator('.wf-block[data-run="reused"]')).toContainText([
  212 |     "Start",
  213 |     "Draft image prompt",
  214 |   ]);
  215 |   const all = await (
  216 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  217 |   ).json();
  218 |   const second = all.items[0];
  219 |   expect(second.id).not.toBe(first.id);
  220 |   expect(second.nodes.n_draft.reused_from).toBe(first.id);
  221 |   expect(second.nodes.n_draft.attempt).toBe(0);
  222 |   await shot(page, `reused-${browserName}`);
  223 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  224 |   await configureStudioBlock(page, "Draft image prompt");
  225 |   await page
  226 |     .getByRole("textbox", { name: "Prompt", exact: true })
```