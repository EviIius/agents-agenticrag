# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect
- Location: tests/workflow-studio-running.spec.ts:135:1

# Error details

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator: getByRole('button', { name: 'Following run', exact: true })
Expected: "true"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveAttribute" getByRole('button', { name: 'Following run', exact: true }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Following run', exact: true })

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
        - img "A workflow is waiting for you"
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
      - paragraph: Done in 5 s
      - text: draft.text
      - img "complete"
    - group "Approve or edit block ‘Check the prompt’, 3 of 5":
      - text: Check the prompt Approve or edit
      - paragraph: Waiting for you
      - text: review.value
      - img "paused"
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
  - button "Resume following run"
  - button "Zoom out"
  - button "Zoom 100%": 100%
  - button "Zoom in"
  - button "Fit view"
  - button "Outline view"
  - button "Canvas actions"
  - complementary "run":
    - heading "Run" [level=2]
    - button "Close Run"
    - article "Synthetic running workflow run":
      - heading "Synthetic running workflow" [level=3]
      - time: 10/13/2026, 9:12:04 AM
      - status: "Waiting for you: Check the prompt · paused"
      - list:
        - listitem:
          - button "View result for Start": Start Done in 0 s
        - listitem:
          - button "View result for Draft image prompt" [expanded]: Draft image prompt Done in 5 s
          - status
          - paragraph: token0 token1 token2 token3 token4 token5 token6 token7 token8 token9 token10 token11 token12 token13 token14 token15
        - listitem:
          - button "View result for Check the prompt": Check the prompt Waiting for you
        - listitem:
          - button "View result for Create images": Create images Waiting
        - listitem:
          - button "View result for Save results": Save results Waiting
      - text: Review Check the prompt
      - textbox "Review result": token0 token1 token2 token3 token4 token5 token6 token7 token8 token9 token10 token11 token12 token13 token14 token15
      - paragraph: Check the prompt before images are made.
      - button "Approve"
      - button "Reject"
      - button "Cancel workflow"
      - button "Save outputs"
      - paragraph: Draft for review. Check it against the original.
  - button "Import workflow JSON"
- region "Notifications alt+T"
```

# Test source

```ts
  78  |       key: "favorites",
  79  |       kind: "pick",
  80  |       title: "Pick favorites",
  81  |       disabled: false,
  82  |       position: { x: 320, y: 880 },
  83  |       config: { from: ["{{images.images}}"], type: "image_list", maximum: 1 },
  84  |     });
  85  |     const edge = doc.edges.find((e) => e.target === "n_save")!;
  86  |     edge.target = "n_pick";
  87  |     doc.edges.push({
  88  |       id: "e_pick_save",
  89  |       source: "n_pick",
  90  |       source_port: "out",
  91  |       target: "n_save",
  92  |       target_port: "in",
  93  |     });
  94  |     const save = doc.nodes.find((n) => n.kind === "output")!;
  95  |     save.config.include = [{ label: "Favorite", ref: "{{favorites.chosen}}" }];
  96  |   }
  97  |   return (
  98  |     await request.put(`/api/workflows/defs/${d.id}`, {
  99  |       data: {
  100 |         name: d.name,
  101 |         description: d.description,
  102 |         icon: d.icon,
  103 |         graph: doc,
  104 |         version: d.version,
  105 |       },
  106 |     })
  107 |   ).json() as Promise<Definition>;
  108 | }
  109 | async function start(
  110 |   request: APIRequestContext,
  111 |   d: Definition,
  112 |   extra: Record<string, unknown> = {},
  113 | ) {
  114 |   const response = await request.post(`/api/workflows/defs/${d.id}/runs`, {
  115 |     data: {
  116 |       request_key: crypto.randomUUID(),
  117 |       inputs: { brief: "Synthetic blue shapes" },
  118 |       ...extra,
  119 |     },
  120 |   });
  121 |   expect(response.status()).toBe(202);
  122 |   return response.json() as Promise<Run>;
  123 | }
  124 | async function done(page: Page) {
  125 |   await expect(
  126 |     page.locator(".wf-run-card [role=status]").first(),
  127 |   ).toContainText("Ready for review");
  128 | }
  129 | async function shot(page: Page, name: string) {
  130 |   await settle(page);
  131 |   await mkdir(dir, { recursive: true });
  132 |   await page.screenshot({ path: `${dir}/${name}-fake.png`, fullPage: true });
  133 | }
  134 | 
  135 | test("Run canvas streams truthful text, follows and yields to manual zoom, and survives reconnect", async ({
  136 |   page,
  137 |   request,
  138 |   browserName,
  139 | }) => {
  140 |   const d = await create(request, { prompt: "#long:16 #slow:3", review: true });
  141 |   const run = await start(request, d);
  142 |   await page.goto(`/workflows/${d.id}?run=1`);
  143 |   await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  144 |   const text = page.locator(".wf-stream-preview").first();
  145 |   await expect(text).toContainText("token");
  146 |   const before = await text.innerText();
  147 |   await expect.poll(() => text.innerText()).not.toBe(before);
  148 |   await expect(
  149 |     page.getByRole("button", { name: "Following run", exact: true }),
  150 |   ).toHaveAttribute("aria-pressed", "true");
  151 |   await page.getByRole("button", { name: "Zoom out", exact: true }).click();
  152 |   await expect(
  153 |     page.getByRole("button", { name: "Resume following run", exact: true }),
  154 |   ).toHaveAttribute("aria-pressed", "false");
  155 |   await shot(page, `stream-${browserName}`);
  156 |   let detailReads = 0;
  157 |   page.on("request", (r) => {
  158 |     if (r.url().endsWith(`/runs/${run.id}/v2`)) detailReads++;
  159 |   });
  160 |   await page.context().setOffline(true);
  161 |   await page.waitForTimeout(350);
  162 |   await page.context().setOffline(false);
  163 |   await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
  164 |     "Waiting for you",
  165 |   );
  166 |   await page
  167 |     .getByRole("button", {
  168 |       name: "View result for Draft image prompt",
  169 |       exact: true,
  170 |     })
  171 |     .click();
  172 |   await expect(page.locator(".wf-stream-preview").first()).toContainText(
  173 |     "token15",
  174 |   );
  175 |   expect(detailReads).toBeLessThanOrEqual(1);
  176 |   await expect(
  177 |     page.getByRole("button", { name: "Following run", exact: true }),
> 178 |   ).toHaveAttribute("aria-pressed", "true");
      |     ^ Error: expect(locator).toHaveAttribute(expected) failed
  179 |   await page
  180 |     .getByRole("textbox", { name: "Review result" })
  181 |     .fill("Synthetic approved blue circle");
  182 |   await page.getByRole("button", { name: "Approve", exact: true }).click();
  183 |   await done(page);
  184 |   await expect(page.locator('.wf-block[data-run="complete"]')).toHaveCount(
  185 |     d.graph.nodes.length,
  186 |   );
  187 |   const snapshot = await (
  188 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  189 |   ).json();
  190 |   expect(snapshot.nodes.n_review.output.value).toBe(
  191 |     "Synthetic approved blue circle",
  192 |   );
  193 |   await shot(page, `complete-${browserName}`);
  194 | });
  195 | 
  196 | test("Run from here uses saved outputs, rejects changed settings, and versions restore with undo", async ({
  197 |   page,
  198 |   request,
  199 |   browserName,
  200 | }) => {
  201 |   const d = await create(request, { review: false });
  202 |   const first = await start(request, d);
  203 |   await page.goto(`/workflows/${d.id}?run=1`);
  204 |   await done(page);
  205 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  206 |   await configureStudioBlock(page, "Create images");
  207 |   await page
  208 |     .locator(".wf-inspector")
  209 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  210 |     .click();
  211 |   await page
  212 |     .getByRole("menuitem", { name: "Run from here", exact: true })
  213 |     .click();
  214 |   await page
  215 |     .getByRole("button", { name: "Run from here", exact: true })
  216 |     .click();
  217 |   await done(page);
  218 |   await expect(page.locator('.wf-block[data-run="reused"]')).toContainText([
  219 |     "Start",
  220 |     "Draft image prompt",
  221 |   ]);
  222 |   const all = await (
  223 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  224 |   ).json();
  225 |   const second = all.items[0];
  226 |   expect(second.id).not.toBe(first.id);
  227 |   expect(second.nodes.n_draft.reused_from).toBe(first.id);
  228 |   expect(second.nodes.n_draft.attempt).toBe(0);
  229 |   await shot(page, `reused-${browserName}`);
  230 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  231 |   await configureStudioBlock(page, "Draft image prompt");
  232 |   await page
  233 |     .getByRole("textbox", { name: "Prompt", exact: true })
  234 |     .fill("Synthetic changed prompt");
  235 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  236 |   await configureStudioBlock(page, "Create images");
  237 |   await page
  238 |     .locator(".wf-inspector")
  239 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  240 |     .click();
  241 |   await expect(
  242 |     page.getByRole("menuitem", { name: "Run from here", exact: true }),
  243 |   ).toBeDisabled();
  244 |   await page.keyboard.press("Escape");
  245 |   await page
  246 |     .getByRole("button", { name: "Close Inspector", exact: true })
  247 |     .click();
  248 |   await page
  249 |     .getByRole("button", { name: "Workflow menu", exact: true })
  250 |     .click();
  251 |   await page.getByRole("menuitem", { name: "Versions", exact: true }).click();
  252 |   const version = page.locator(".wf-version").last();
  253 |   await version.getByRole("textbox").fill("Synthetic named version");
  254 |   await version.getByRole("button", { name: "Save name", exact: true }).click();
  255 |   await expect(version).toContainText("Synthetic named version");
  256 |   await version.getByRole("button", { name: "Restore", exact: true }).click();
  257 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  258 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  259 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  260 |   const restored = await (
  261 |     await request.get(`/api/workflows/defs/${d.id}`)
  262 |   ).json();
  263 |   expect(
  264 |     restored.graph.nodes.find((n: { kind: string }) => n.kind === "generate")
  265 |       .config.prompt,
  266 |   ).toBe("Synthetic changed prompt");
  267 | });
  268 | 
  269 | test("Single block tests use explicit samples and remain outside recent history after reload", async ({
  270 |   page,
  271 |   request,
  272 | }) => {
  273 |   const d = await create(request, { review: false });
  274 |   await page.goto(`/workflows/${d.id}`);
  275 |   await configureStudioBlock(page, "Draft image prompt");
  276 |   await page
  277 |     .locator(".wf-inspector")
  278 |     .getByRole("button", {
```