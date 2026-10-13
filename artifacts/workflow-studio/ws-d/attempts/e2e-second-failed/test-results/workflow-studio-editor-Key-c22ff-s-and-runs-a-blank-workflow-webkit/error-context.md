# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-editor.spec.ts >> Keyboard adds, wires through Connections and runs a blank workflow
- Location: tests/workflow-studio-editor.spec.ts:96:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('article', { name: 'Synthetic editor run' }).getByRole('status')
Expected substring: "Ready for review"
Error: strict mode violation: getByRole('article', { name: 'Synthetic editor run' }).getByRole('status') resolved to 2 elements:
    1) <p role="status" class="my-3 text-sm text-fg-2">Generate text · running</p> aka getByText('Generate text · running')
    2) <span role="status" class="sr-only" aria-live="polite"></span> aka getByRole('status').filter({ hasText: /^$/ })

Call log:
  - Expect "toContainText" getByRole('article', { name: 'Synthetic editor run' }).getByRole('status') with timeout 5000ms
  - waiting for getByRole('article', { name: 'Synthetic editor run' }).getByRole('status')
    - locator resolved to <p role="status" class="my-3 text-sm text-fg-2">Generate text · running</p>
    - unexpected value "Generate text · running"

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - button "Expand sidebar" [ref=e7] [cursor=pointer]
        - link "New chat" [ref=e8]:
          - /url: /
        - button "Search chats" [ref=e9] [cursor=pointer]
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e12]:
              - /url: /workflows
              - img "A workflow is waiting for you" [ref=e13]
            - link "Images" [ref=e14]:
              - /url: /images
        - button "Settings" [ref=e16] [cursor=pointer]
    - main [ref=e17]:
      - generic [active] [ref=e18]:
        - generic [ref=e19]:
          - link "Back to Workflows" [ref=e20]:
            - /url: /workflows
            - generic [ref=e23]: Workflows
          - generic [ref=e24]: /
          - button "Synthetic editor" [ref=e25] [cursor=pointer]
          - status [ref=e26]: Saved
          - button "Undo" [ref=e28] [cursor=pointer]
          - button "Redo" [disabled]
          - button "Workflow menu" [ref=e29] [cursor=pointer]
          - button "Run" [ref=e30] [cursor=pointer]
        - generic [ref=e31]:
          - complementary "Blocks" [ref=e32]:
            - textbox "Search blocks" [ref=e37]
            - generic [ref=e38]:
              - group [ref=e39]:
                - generic "Inputs" [ref=e40] [cursor=pointer]
                - button "Start" [ref=e41] [cursor=pointer]
              - group [ref=e44]:
                - generic "AI" [ref=e45] [cursor=pointer]
                - button "Generate text" [ref=e46] [cursor=pointer]
                - button "Classify" [disabled] [ref=e49]
              - group [ref=e52]:
                - generic "Knowledge" [ref=e53] [cursor=pointer]
                - button "Search the web" [disabled] [ref=e54]
                - button "Search my files" [disabled] [ref=e57]
                - button "Read a document" [disabled] [ref=e60]
              - group [ref=e63]:
                - generic "Media" [ref=e64] [cursor=pointer]
                - button "Transcribe recording" [ref=e65] [cursor=pointer]
                - button "Clean up transcript" [ref=e68] [cursor=pointer]
                - button "Create images" [ref=e71] [cursor=pointer]
              - group [ref=e74]:
                - generic "Logic" [ref=e75] [cursor=pointer]
                - button "If / else" [disabled] [ref=e76]
                - button "Compose text" [disabled] [ref=e79]
              - group [ref=e82]:
                - generic "Review" [ref=e83] [cursor=pointer]
                - button "Approve or edit" [ref=e84] [cursor=pointer]
                - button "Pick favorites" [ref=e87] [cursor=pointer]
              - group [ref=e90]:
                - generic "Output" [ref=e91] [cursor=pointer]
                - button "Save results" [ref=e92] [cursor=pointer]
            - button "Note" [ref=e96] [cursor=pointer]
          - generic "Read-only workflow canvas" [ref=e99]:
            - application [ref=e100]:
              - generic [ref=e102]:
                - generic:
                  - generic:
                    - img:
                      - img "Connection from Start to Save results"
                    - img:
                      - img "Connection from Start to Generate text" [ref=e103] [cursor=pointer]
                    - img:
                      - img "Connection from Generate text to Save results" [ref=e106] [cursor=pointer]
                  - generic:
                    - group "Start block ‘Start’, 1 of 3" [ref=e109] [cursor=pointer]:
                      - generic [ref=e112]:
                        - generic [ref=e117]:
                          - generic [ref=e118]: Start
                          - generic [ref=e119]: Start
                        - paragraph [ref=e120]: Done in 0 s
                        - img "complete" [ref=e121]
                    - group "Save results block ‘Save results’, 2 of 3" [ref=e125] [cursor=pointer]:
                      - generic [ref=e129]:
                        - generic [ref=e136]:
                          - generic [ref=e137]: Save results
                          - generic [ref=e138]: Save results
                        - paragraph [ref=e139]: Waiting
                    - group "Generate text block ‘Generate text’, 3 of 3" [ref=e140] [cursor=pointer]:
                      - generic [ref=e144]:
                        - generic [ref=e150]:
                          - generic [ref=e151]: Generate text
                          - generic [ref=e152]: Generate text
                        - paragraph [ref=e153]: Writing · 143 characters
                        - generic [ref=e154]: generate.text
              - img "Mini Map" [ref=e158]
              - link "React Flow attribution" [ref=e163]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - generic [ref=e164]:
              - button "Following run" [pressed] [ref=e165] [cursor=pointer]
              - button "Zoom out" [ref=e166] [cursor=pointer]
              - button "Zoom 100%" [ref=e167] [cursor=pointer]: 155%
              - button "Zoom in" [ref=e168] [cursor=pointer]
              - button "Fit view" [ref=e169] [cursor=pointer]
              - button "Outline view" [ref=e170] [cursor=pointer]
              - button "Canvas actions" [ref=e171] [cursor=pointer]
          - complementary "run" [ref=e172]:
            - generic [ref=e173]:
              - generic [ref=e174]:
                - heading "Run" [level=2] [ref=e175]
                - button "Close Run" [ref=e176] [cursor=pointer]
              - article "Synthetic editor run" [ref=e178]:
                - generic [ref=e179]:
                  - heading "Synthetic editor" [level=3] [ref=e180]
                  - time [ref=e181]: 10/13/2026, 10:12:55 AM
                - status [ref=e182]: Generate text · running
                - list [ref=e183]:
                  - listitem [ref=e184]:
                    - button "View result for Start" [ref=e185] [cursor=pointer]:
                      - generic [ref=e188]: Start
                      - generic [ref=e189]: Done in 0 s
                  - listitem [ref=e190]:
                    - button "View result for Generate text" [expanded] [ref=e191] [cursor=pointer]:
                      - generic [ref=e194]: Generate text
                      - generic [ref=e195]: Writing · 143 characters
                    - generic [ref=e197]:
                      - status [ref=e198]
                      - generic [ref=e199]:
                        - paragraph [ref=e200]: Fake runtime reply.
                        - list [ref=e201]:
                          - listitem [ref=e202]: A clear first step
                          - listitem [ref=e203]: A useful second step
                        - generic [ref=e204]:
                          - generic [ref=e205]: python
                          - button "Copy Code" [disabled] [ref=e208]
                          - region "Code example" [ref=e211]:
                            - code [ref=e213]:
                              - generic [ref=e214]: print('Hello')
                        - region "Answer table" [ref=e215]:
                          - region "Answer table" [ref=e216]:
                            - table [ref=e217]:
                              - rowgroup [ref=e218]:
                                - row [ref=e219]:
                                  - columnheader "Item" [ref=e220]
                                  - columnheader "Value" [ref=e221]
                              - rowgroup [ref=e222]:
                                - row [ref=e223]:
                                  - cell "Example" [ref=e224]
                                  - cell "42" [ref=e225]
                  - listitem [ref=e226]:
                    - button "View result for Save results" [ref=e227] [cursor=pointer]:
                      - generic [ref=e230]: Save results
                      - generic [ref=e231]: Waiting
                - generic [ref=e232]:
                  - button "Cancel workflow" [ref=e233] [cursor=pointer]
                  - button "Save outputs" [ref=e234] [cursor=pointer]
                - paragraph [ref=e235]: Draft for review. Check it against the original.
        - button "Import workflow JSON" [ref=e236]
  - region "Notifications alt+T":
    - list:
      - listitem [ref=e237]:
        - button "Close toast" [ref=e238] [cursor=pointer]
        - generic [ref=e242]: Brief to images is waiting for you.
        - button "Open" [ref=e244] [cursor=pointer]
```

# Test source

```ts
  25  |     data: {
  26  |       name: "Synthetic editor",
  27  |       ...(template ? { template_id: template } : { graph: blankDoc() }),
  28  |       default_model: { connection_id: c.id, model_id: "fake-chat" },
  29  |     },
  30  |   });
  31  |   expect(r.status()).toBe(201);
  32  |   return r.json();
  33  | }
  34  | async function block(page: Page, id: string) {
  35  |   await page.locator(`.react-flow__node[data-id='${id}']`).click();
  36  | }
  37  | async function saved(page: Page) {
  38  |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  39  | }
  40  | async function def(
  41  |   request: APIRequestContext,
  42  |   id: string,
  43  | ): Promise<Definition> {
  44  |   return (await request.get(`/api/workflows/defs/${id}`)).json();
  45  | }
  46  | test("Desktop native dragging adds blocks in space and inserts on a connection", async ({
  47  |   page,
  48  |   request,
  49  | }) => {
  50  |   const d = await create(request);
  51  |   await page.goto(`/workflows/${d.id}`);
  52  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(2);
  53  |   const palette = page.getByRole("button", {
  54  |     name: "Generate text",
  55  |     exact: true,
  56  |   });
  57  |   const box = await page.locator(".wf-canvas").boundingBox();
  58  |   expect(box).toBeTruthy();
  59  |   await palette.dragTo(page.locator(".wf-canvas"), {
  60  |     targetPosition: { x: 140, y: 180 },
  61  |   });
  62  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(3);
  63  |   await page
  64  |     .getByRole("button", { name: "Close Inspector", exact: true })
  65  |     .click();
  66  |   await saved(page);
  67  |   await settle(page);
  68  |   const edge = page.locator(".react-flow__edge-path").first();
  69  |   const at = await edge.evaluate((element: SVGPathElement) => {
  70  |     const p = element
  71  |       .getPointAtLength(element.getTotalLength() / 2)
  72  |       .matrixTransform(element.getScreenCTM()!);
  73  |     return { x: p.x, y: p.y };
  74  |   });
  75  |   const canvasBox = await page.locator(".wf-canvas").boundingBox();
  76  |   expect(canvasBox).toBeTruthy();
  77  |   await palette.dragTo(page.locator(".wf-canvas"), {
  78  |     targetPosition: { x: at.x - canvasBox!.x, y: at.y - canvasBox!.y },
  79  |   });
  80  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  81  |   await saved(page);
  82  |   const current = await def(request, d.id);
  83  |   expect(current.graph.edges).toHaveLength(2);
  84  |   const inserted = current.graph.nodes.at(-1)!;
  85  |   expect(
  86  |     current.graph.edges.some(
  87  |       (e) => e.target === inserted.id && e.source === "n_start",
  88  |     ),
  89  |   ).toBe(true);
  90  |   expect(
  91  |     current.graph.edges.some(
  92  |       (e) => e.source === inserted.id && e.target === "n_save",
  93  |     ),
  94  |   ).toBe(true);
  95  | });
  96  | test("Keyboard adds, wires through Connections and runs a blank workflow", async ({
  97  |   page,
  98  |   request,
  99  | }) => {
  100 |   const d = await create(request);
  101 |   await page.goto(`/workflows/${d.id}`);
  102 |   const start = page.locator(".react-flow__node[data-id='n_start']");
  103 |   await start.focus();
  104 |   await page.keyboard.press("n");
  105 |   const quick = page.getByRole("dialog", { name: "Add a block" });
  106 |   await expect(quick).toBeVisible();
  107 |   await quick.getByRole("combobox").fill("Generate text");
  108 |   await page.keyboard.press("Enter");
  109 |   await page
  110 |     .getByRole("textbox", { name: "Prompt", exact: true })
  111 |     .fill("Synthetic keyboard workflow");
  112 |   await page.getByRole("combobox", { name: "Add an input connection" }).click();
  113 |   await page.getByRole("option", { name: "Start", exact: true }).click();
  114 |   await page
  115 |     .getByRole("combobox", { name: "Add an output connection" })
  116 |     .click();
  117 |   await page.getByRole("option", { name: "Save results", exact: true }).click();
  118 |   await saved(page);
  119 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  120 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  121 |   await expect(
  122 |     page
  123 |       .getByRole("article", { name: "Synthetic editor run" })
  124 |       .getByRole("status"),
> 125 |   ).toContainText("Ready for review");
      |     ^ Error: expect(locator).toContainText(expected) failed
  126 | });
  127 | test("Delete heals a chain in one undo; redo keeps references as explicit problems", async ({
  128 |   page,
  129 |   request,
  130 | }) => {
  131 |   const d = await create(request, "brief_images");
  132 |   await page.goto(`/workflows/${d.id}`);
  133 |   await block(page, "n_review");
  134 |   await page.locator(".react-flow__node[data-id='n_review']").focus();
  135 |   await page.keyboard.press("Delete");
  136 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  137 |   await saved(page);
  138 |   const healed = await def(request, d.id);
  139 |   expect(
  140 |     healed.graph.edges.some(
  141 |       (e) => e.source === "n_draft" && e.target === "n_images",
  142 |     ),
  143 |   ).toBe(true);
  144 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  145 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(5);
  146 |   await saved(page);
  147 |   expect((await def(request, d.id)).graph.nodes).toEqual(d.graph.nodes);
  148 |   await page.getByRole("button", { name: "Redo", exact: true }).click();
  149 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  150 |   await expect(
  151 |     page.getByRole("heading", { name: "Problems", exact: true }),
  152 |   ).toBeVisible();
  153 |   await expect(
  154 |     page.getByText("A referenced output does not exist.").first(),
  155 |   ).toBeVisible();
  156 | });
  157 | test("Autosave survives reload and both stale-save conflict choices preserve intent", async ({
  158 |   page,
  159 |   request,
  160 | }) => {
  161 |   const d = await create(request, "brief_images");
  162 |   await page.goto(`/workflows/${d.id}`);
  163 |   await block(page, "n_draft");
  164 |   await page
  165 |     .getByRole("textbox", { name: "Block name", exact: true })
  166 |     .fill("Synthetic renamed draft");
  167 |   await saved(page);
  168 |   await page.reload();
  169 |   await expect(
  170 |     page
  171 |       .locator(".wf-block-title")
  172 |       .filter({ hasText: "Synthetic renamed draft" }),
  173 |   ).toBeVisible();
  174 |   const stale = await def(request, d.id);
  175 |   await request.put(`/api/workflows/defs/${d.id}`, {
  176 |     data: {
  177 |       ...stale,
  178 |       name: "Synthetic other device",
  179 |       version: stale.version,
  180 |       graph: stale.graph,
  181 |       id: undefined,
  182 |       graph_hash: undefined,
  183 |       template_id: undefined,
  184 |       archived_at: undefined,
  185 |       created_at: undefined,
  186 |       updated_at: undefined,
  187 |     },
  188 |   });
  189 |   await block(page, "n_draft");
  190 |   await page
  191 |     .getByRole("textbox", { name: "Block name", exact: true })
  192 |     .fill("Synthetic keep mine");
  193 |   await expect(
  194 |     page.getByText("This workflow changed on another device."),
  195 |   ).toBeVisible();
  196 |   await page.getByRole("button", { name: "Keep mine", exact: true }).click();
  197 |   await saved(page);
  198 |   expect(
  199 |     (await def(request, d.id)).graph.nodes.find((n) => n.id === "n_draft")!
  200 |       .title,
  201 |   ).toBe("Synthetic keep mine");
  202 |   const next = await def(request, d.id);
  203 |   await request.put(`/api/workflows/defs/${d.id}`, {
  204 |     data: {
  205 |       name: "Synthetic latest",
  206 |       description: next.description,
  207 |       icon: next.icon,
  208 |       graph: next.graph,
  209 |       version: next.version,
  210 |     },
  211 |   });
  212 |   await page
  213 |     .getByRole("textbox", { name: "Block name", exact: true })
  214 |     .fill("Synthetic discarded draft");
  215 |   await expect(
  216 |     page.getByText("This workflow changed on another device."),
  217 |   ).toBeVisible();
  218 |   await page.getByRole("button", { name: "Load latest", exact: true }).click();
  219 |   await expect(
  220 |     page.getByRole("button", { name: "Synthetic latest", exact: true }),
  221 |   ).toBeVisible();
  222 |   expect(
  223 |     (await def(request, d.id)).graph.nodes.find((n) => n.id === "n_draft")!
  224 |       .title,
  225 |   ).toBe("Synthetic keep mine");
```