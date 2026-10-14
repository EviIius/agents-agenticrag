# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-editor.spec.ts >> Desktop native dragging adds blocks in space and inserts on a connection
- Location: tests/workflow-studio-editor.spec.ts:45:1

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  locator('.react-flow__node-block')
Expected: 4
Received: 3
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" locator('.react-flow__node-block') with timeout 5000ms
  - waiting for locator('.react-flow__node-block')
    14 × locator resolved to 3 elements
       - unexpected value "3"

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
            - link "Images" [ref=e13]:
              - /url: /images
        - button "Settings" [ref=e15] [cursor=pointer]
    - main [ref=e16]:
      - generic [active] [ref=e17]:
        - generic [ref=e18]:
          - link "Back to Workflows" [ref=e19]:
            - /url: /workflows
            - generic [ref=e22]: Workflows
          - generic [ref=e23]: /
          - button "Synthetic editor" [ref=e24] [cursor=pointer]
          - status [ref=e25]: Saved
          - button "2 workflow problems" [ref=e27] [cursor=pointer]: "2"
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
                - button "Pick favorites" [disabled] [ref=e87]
              - group [ref=e90]:
                - generic "Output" [ref=e91] [cursor=pointer]
                - button "Save results" [ref=e92] [cursor=pointer]
            - button "Note" [ref=e96] [cursor=pointer]
          - generic "Workflow canvas" [ref=e99]:
            - application [ref=e100]:
              - generic [ref=e102]:
                - generic:
                  - generic:
                    - img:
                      - group "Connection from Start to Save results"
                  - generic [ref=e103]:
                    - button "Insert on connection e_start_save" [ref=e104] [cursor=pointer]
                    - button "Delete connection e_start_save" [ref=e105] [cursor=pointer]
                  - generic:
                    - group "Start block ‘Start’, 1 of 3" [ref=e106]:
                      - generic [ref=e109]:
                        - generic [ref=e110]:
                          - generic [ref=e114]:
                            - generic [ref=e115]: Start
                            - generic [ref=e116]: Start
                          - button "Actions for Start" [ref=e117] [cursor=pointer]
                        - paragraph [ref=e118]: No inputs
                    - group "Save results block ‘Save results’, 2 of 3" [ref=e120]:
                      - generic [ref=e124]:
                        - generic [ref=e125]:
                          - generic [ref=e131]:
                            - generic [ref=e132]: Save results
                            - generic [ref=e133]: Save results
                          - button "Actions for Save results" [ref=e134] [cursor=pointer]
                        - paragraph [ref=e135]: Markdown, JSON · 0 items
                    - group "Generate text block ‘Generate text’, 3 of 3" [ref=e136]:
                      - generic [ref=e140]:
                        - generic [ref=e141]:
                          - generic [ref=e146]:
                            - generic [ref=e147]: Generate text
                            - generic [ref=e148]: Generate text
                          - button "Actions for Generate text" [ref=e149] [cursor=pointer]
                        - paragraph [ref=e150]: fake-chat
                        - generic [ref=e151]: generate.text
                        - generic "Connect this block to Start." [ref=e153]
              - img "Mini Map" [ref=e156]
              - link "React Flow attribution" [ref=e161]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - generic [ref=e162]:
              - button "Zoom out" [ref=e163] [cursor=pointer]
              - button "Zoom 100%" [ref=e164] [cursor=pointer]: 175%
              - button "Zoom in" [ref=e165] [cursor=pointer]
              - button "Fit view" [ref=e166] [cursor=pointer]
              - button "Tidy up" [ref=e167] [cursor=pointer]
              - button "Outline view" [ref=e168] [cursor=pointer]
              - button "Canvas actions" [ref=e169] [cursor=pointer]
        - button "Import workflow JSON" [ref=e170]
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import {
  2   |   test,
  3   |   expect,
  4   |   type Page,
  5   |   type APIRequestContext,
  6   | } from "@playwright/test";
  7   | import AxeBuilder from "@axe-core/playwright";
  8   | import { mkdir, writeFile } from "node:fs/promises";
  9   | import { settle } from "./helpers";
  10  | import type { Definition } from "../src/components/workflows/studio/types";
  11  | import { blankDoc } from "../src/components/workflows/studio/graph";
  12  | const dir = "../artifacts/workflow-studio/ws-c/browser";
  13  | test.use({
  14  |   viewport: { width: 1440, height: 900 },
  15  |   isMobile: false,
  16  |   hasTouch: false,
  17  | });
  18  | async function create(
  19  |   request: APIRequestContext,
  20  |   template?: string,
  21  | ): Promise<Definition> {
  22  |   const c = (await (await request.get("/api/connections")).json())[0];
  23  |   const r = await request.post("/api/workflows/defs", {
  24  |     data: {
  25  |       name: "Synthetic editor",
  26  |       ...(template ? { template_id: template } : { graph: blankDoc() }),
  27  |       default_model: { connection_id: c.id, model_id: "fake-chat" },
  28  |     },
  29  |   });
  30  |   expect(r.status()).toBe(201);
  31  |   return r.json();
  32  | }
  33  | async function block(page: Page, id: string) {
  34  |   await page.locator(`.react-flow__node[data-id='${id}']`).click();
  35  | }
  36  | async function saved(page: Page) {
  37  |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  38  | }
  39  | async function def(
  40  |   request: APIRequestContext,
  41  |   id: string,
  42  | ): Promise<Definition> {
  43  |   return (await request.get(`/api/workflows/defs/${id}`)).json();
  44  | }
  45  | test("Desktop native dragging adds blocks in space and inserts on a connection", async ({
  46  |   page,
  47  |   request,
  48  | }) => {
  49  |   const d = await create(request);
  50  |   await page.goto(`/workflows/${d.id}`);
  51  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(2);
  52  |   const palette = page.getByRole("button", {
  53  |     name: "Generate text",
  54  |     exact: true,
  55  |   });
  56  |   const box = await page.locator(".wf-canvas").boundingBox();
  57  |   expect(box).toBeTruthy();
  58  |   await palette.dragTo(page.locator(".wf-canvas"), {
  59  |     targetPosition: { x: 140, y: 180 },
  60  |   });
  61  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(3);
  62  |   await page
  63  |     .getByRole("button", { name: "Close Inspector", exact: true })
  64  |     .click();
  65  |   await saved(page);
  66  |   await settle(page);
  67  |   const edge = page.locator(".react-flow__edge-path").first();
  68  |   const at = await edge.evaluate((element: SVGPathElement) => {
  69  |     const p = element
  70  |       .getPointAtLength(element.getTotalLength() / 2)
  71  |       .matrixTransform(element.getScreenCTM()!);
  72  |     return { x: p.x, y: p.y };
  73  |   });
  74  |   const origin = await palette.boundingBox();
  75  |   expect(origin).toBeTruthy();
  76  |   await page.mouse.move(origin!.x + 30, origin!.y + 20);
  77  |   await page.mouse.down();
  78  |   await page.mouse.move(origin!.x + 35, origin!.y + 25);
  79  |   await page.mouse.move(at.x, at.y, { steps: 20 });
  80  |   await page.mouse.move(at.x + 1, at.y + 1);
  81  |   await page.mouse.up();
> 82  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
      |                                                         ^ Error: expect(locator).toHaveCount(expected) failed
  83  |   await saved(page);
  84  |   const current = await def(request, d.id);
  85  |   expect(current.graph.edges).toHaveLength(2);
  86  |   const inserted = current.graph.nodes.at(-1)!;
  87  |   expect(
  88  |     current.graph.edges.some(
  89  |       (e) => e.target === inserted.id && e.source === "n_start",
  90  |     ),
  91  |   ).toBe(true);
  92  |   expect(
  93  |     current.graph.edges.some(
  94  |       (e) => e.source === inserted.id && e.target === "n_save",
  95  |     ),
  96  |   ).toBe(true);
  97  | });
  98  | test("Keyboard adds, wires through Connections and runs a blank workflow", async ({
  99  |   page,
  100 |   request,
  101 | }) => {
  102 |   const d = await create(request);
  103 |   await page.goto(`/workflows/${d.id}`);
  104 |   const start = page.locator(".react-flow__node[data-id='n_start']");
  105 |   await start.focus();
  106 |   await page.keyboard.press("n");
  107 |   const quick = page.getByRole("dialog", { name: "Add a block" });
  108 |   await expect(quick).toBeVisible();
  109 |   await quick.getByRole("combobox").fill("Generate text");
  110 |   await page.keyboard.press("Enter");
  111 |   await page
  112 |     .getByRole("textbox", { name: "Prompt", exact: true })
  113 |     .fill("Synthetic keyboard workflow");
  114 |   await page.getByRole("combobox", { name: "Add an input connection" }).click();
  115 |   await page.getByRole("option", { name: "Start", exact: true }).click();
  116 |   await page
  117 |     .getByRole("combobox", { name: "Add an output connection" })
  118 |     .click();
  119 |   await page.getByRole("option", { name: "Save results", exact: true }).click();
  120 |   await saved(page);
  121 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  122 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  123 |   await expect(
  124 |     page
  125 |       .getByRole("article", { name: "Synthetic editor run" })
  126 |       .getByRole("status"),
  127 |   ).toContainText("Ready for review");
  128 | });
  129 | test("Delete heals a chain in one undo; redo keeps references as explicit problems", async ({
  130 |   page,
  131 |   request,
  132 | }) => {
  133 |   const d = await create(request, "brief_images");
  134 |   await page.goto(`/workflows/${d.id}`);
  135 |   await block(page, "n_review");
  136 |   await page.locator(".react-flow__node[data-id='n_review']").focus();
  137 |   await page.keyboard.press("Delete");
  138 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  139 |   await saved(page);
  140 |   const healed = await def(request, d.id);
  141 |   expect(
  142 |     healed.graph.edges.some(
  143 |       (e) => e.source === "n_draft" && e.target === "n_images",
  144 |     ),
  145 |   ).toBe(true);
  146 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  147 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(5);
  148 |   await saved(page);
  149 |   expect((await def(request, d.id)).graph.nodes).toEqual(d.graph.nodes);
  150 |   await page.getByRole("button", { name: "Redo", exact: true }).click();
  151 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  152 |   await expect(
  153 |     page.getByRole("heading", { name: "Problems", exact: true }),
  154 |   ).toBeVisible();
  155 |   await expect(
  156 |     page.getByText("A referenced output does not exist.").first(),
  157 |   ).toBeVisible();
  158 | });
  159 | test("Autosave survives reload and both stale-save conflict choices preserve intent", async ({
  160 |   page,
  161 |   request,
  162 | }) => {
  163 |   const d = await create(request, "brief_images");
  164 |   await page.goto(`/workflows/${d.id}`);
  165 |   await block(page, "n_draft");
  166 |   await page
  167 |     .getByRole("textbox", { name: "Block name", exact: true })
  168 |     .fill("Synthetic renamed draft");
  169 |   await saved(page);
  170 |   await page.reload();
  171 |   await expect(
  172 |     page
  173 |       .locator(".wf-block-title")
  174 |       .filter({ hasText: "Synthetic renamed draft" }),
  175 |   ).toBeVisible();
  176 |   const stale = await def(request, d.id);
  177 |   await request.put(`/api/workflows/defs/${d.id}`, {
  178 |     data: {
  179 |       ...stale,
  180 |       name: "Synthetic other device",
  181 |       version: stale.version,
  182 |       graph: stale.graph,
```