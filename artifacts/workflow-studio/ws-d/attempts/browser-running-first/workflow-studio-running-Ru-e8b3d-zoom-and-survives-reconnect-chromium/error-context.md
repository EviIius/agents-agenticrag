# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect
- Location: tests/workflow-studio-running.spec.ts:129:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('.wf-block[data-run="paused"]')
Expected substring: "Waiting for you"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" locator('.wf-block[data-run="paused"]') with timeout 5000ms
  - waiting for locator('.wf-block[data-run="paused"]')

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
  - status: Saving…
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
      - img "Connection from Draft image prompt to Check the prompt"
    - img:
      - img "Connection from Start to Draft image prompt"
    - img:
      - img "Connection from Check the prompt to Create images"
    - img:
      - img "Connection from Create images to Save results"
    - group "Start block ‘Start’, 1 of 5":
      - text: Start Start
      - paragraph: Done in 0 s
      - text: start.brief
      - img "complete"
    - group "Generate text block ‘Draft image prompt’, 2 of 5":
      - text: Draft image prompt Generate text
      - paragraph: Writing · 190 characters
      - text: draft.text
    - group "Approve or edit block ‘Check the prompt’, 3 of 5":
      - text: Check the prompt Approve or edit
      - paragraph: Waiting
      - text: review.value
      - img "The rejected path ends here."
      - text: Approved Rejected
    - group "Create images block ‘Create images’, 4 of 5":
      - text: Create images Create images
      - paragraph: Waiting
      - text: images.images images.prompt
    - group "Save results block ‘Save results’, 5 of 5":
      - text: Save results Save results
      - paragraph: Waiting
    - img
    - img "Mini Map"
    - link "React Flow attribution":
      - /url: https://reactflow.dev/attribution
      - text: React Flow
  - button "Following run" [pressed]
  - button "Zoom out"
  - button "Zoom 100%": 84%
  - button "Zoom in"
  - button "Fit view"
  - button "Outline view"
  - button "Canvas actions"
  - complementary "run":
    - heading "Run" [level=2]
    - button "Close Run"
    - article "Synthetic running workflow run":
      - heading "Synthetic running workflow" [level=3]
      - time: 10/13/2026, 8:18:00 AM
      - status: Draft image prompt · running
      - list:
        - listitem:
          - button "View result for Start": Start Done in 0 s
        - listitem:
          - button "View result for Draft image prompt": Draft image prompt Writing · 190 characters
          - status
          - paragraph: token0 token1 token2 token3 token4 token5 token6 token7 token8 token9 token10 token11 token12 token13 token14 token15 token16 token17 token18 token19 token20 token21 token22 token23 token24
        - listitem:
          - button "View result for Check the prompt": Check the prompt Waiting
        - listitem:
          - button "View result for Create images": Create images Waiting
        - listitem:
          - button "View result for Save results": Save results Waiting
      - button "Cancel workflow"
      - button "Save outputs"
      - paragraph: Draft for review. Check it against the original.
  - button "Import workflow JSON"
- region "Notifications alt+T"
```

# Test source

```ts
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
  115 |   expect(response.status()).toBe(202);
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
  134 |   const d = await create(request, { prompt: "#long:30 #slow:4", review: true });
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
> 157 |   await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
      |                                                              ^ Error: expect(locator).toContainText(expected) failed
  158 |     "Waiting for you",
  159 |   );
  160 |   await expect(page.locator(".wf-stream-preview").first()).toContainText(
  161 |     "token29",
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
  216 |   expect(second.nodes.n_draft.attempt).toBe(0);
  217 |   await shot(page, `reused-${browserName}`);
  218 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  219 |   await configureStudioBlock(page, "Draft image prompt");
  220 |   await page
  221 |     .getByRole("textbox", { name: "Prompt", exact: true })
  222 |     .fill("Synthetic changed prompt");
  223 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  224 |   await configureStudioBlock(page, "Create images");
  225 |   await page
  226 |     .locator(".wf-inspector")
  227 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  228 |     .click();
  229 |   await expect(
  230 |     page.getByRole("menuitem", { name: "Run from here", exact: true }),
  231 |   ).toBeDisabled();
  232 |   await page.keyboard.press("Escape");
  233 |   await page
  234 |     .getByRole("button", { name: "Close Inspector", exact: true })
  235 |     .click();
  236 |   await page
  237 |     .getByRole("button", { name: "Workflow menu", exact: true })
  238 |     .click();
  239 |   await page.getByRole("menuitem", { name: "Versions", exact: true }).click();
  240 |   const version = page.locator(".wf-version").last();
  241 |   await version.getByRole("textbox").fill("Synthetic named version");
  242 |   await version.getByRole("button", { name: "Save name", exact: true }).click();
  243 |   await expect(version).toContainText("Synthetic named version");
  244 |   await version.getByRole("button", { name: "Restore", exact: true }).click();
  245 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  246 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  247 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  248 |   const restored = await (
  249 |     await request.get(`/api/workflows/defs/${d.id}`)
  250 |   ).json();
  251 |   expect(
  252 |     restored.graph.nodes.find((n: { kind: string }) => n.kind === "generate")
  253 |       .config.prompt,
  254 |   ).toBe("Synthetic changed prompt");
  255 | });
  256 | 
  257 | test("Single block tests use explicit samples and remain outside recent history after reload", async ({
```