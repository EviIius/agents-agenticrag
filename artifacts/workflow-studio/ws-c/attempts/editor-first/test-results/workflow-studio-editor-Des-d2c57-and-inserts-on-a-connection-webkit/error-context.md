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
  65  |   const edge = page.locator(".react-flow__edge-path").first();
  66  |   const at = await edge.evaluate((element: SVGPathElement) => {
  67  |     const p = element
  68  |       .getPointAtLength(element.getTotalLength() / 2)
  69  |       .matrixTransform(element.getScreenCTM()!);
  70  |     return { x: p.x, y: p.y };
  71  |   });
  72  |   const origin = await palette.boundingBox();
  73  |   expect(origin).toBeTruthy();
  74  |   await page.mouse.move(origin!.x + 30, origin!.y + 20);
  75  |   await page.mouse.down();
  76  |   await page.mouse.move(origin!.x + 35, origin!.y + 25);
  77  |   await page.mouse.move(at.x, at.y, { steps: 20 });
  78  |   await page.mouse.up();
> 79  |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
      |                                                         ^ Error: expect(locator).toHaveCount(expected) failed
  80  |   await saved(page);
  81  |   const current = await def(request, d.id);
  82  |   expect(current.graph.edges).toHaveLength(2);
  83  |   const inserted = current.graph.nodes.at(-1)!;
  84  |   expect(
  85  |     current.graph.edges.some(
  86  |       (e) => e.target === inserted.id && e.source === "n_start",
  87  |     ),
  88  |   ).toBe(true);
  89  |   expect(
  90  |     current.graph.edges.some(
  91  |       (e) => e.source === inserted.id && e.target === "n_save",
  92  |     ),
  93  |   ).toBe(true);
  94  | });
  95  | test("Keyboard adds, wires through Connections and runs a blank workflow", async ({
  96  |   page,
  97  |   request,
  98  | }) => {
  99  |   const d = await create(request);
  100 |   await page.goto(`/workflows/${d.id}`);
  101 |   const start = page.locator(".react-flow__node[data-id='n_start']");
  102 |   await start.focus();
  103 |   await page.keyboard.press("n");
  104 |   const quick = page.getByRole("dialog", { name: "Add a block" });
  105 |   await expect(quick).toBeVisible();
  106 |   await quick.getByRole("combobox").fill("Generate text");
  107 |   await page.keyboard.press("Enter");
  108 |   await page
  109 |     .getByRole("textbox", { name: "Prompt", exact: true })
  110 |     .fill("Synthetic keyboard workflow");
  111 |   await page.getByRole("combobox", { name: "Add an input connection" }).click();
  112 |   await page.getByRole("option", { name: "Start", exact: true }).click();
  113 |   await page
  114 |     .getByRole("combobox", { name: "Add an output connection" })
  115 |     .click();
  116 |   await page.getByRole("option", { name: "Save results", exact: true }).click();
  117 |   await saved(page);
  118 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  119 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  120 |   await expect(
  121 |     page
  122 |       .getByRole("article", { name: "Synthetic editor run" })
  123 |       .getByRole("status"),
  124 |   ).toContainText("Ready for review");
  125 | });
  126 | test("Delete heals a chain in one undo; redo keeps references as explicit problems", async ({
  127 |   page,
  128 |   request,
  129 | }) => {
  130 |   const d = await create(request, "brief_images");
  131 |   await page.goto(`/workflows/${d.id}`);
  132 |   await block(page, "n_review");
  133 |   await page.locator(".react-flow__node[data-id='n_review']").focus();
  134 |   await page.keyboard.press("Delete");
  135 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(4);
  136 |   await saved(page);
  137 |   const healed = await def(request, d.id);
  138 |   expect(
  139 |     healed.graph.edges.some(
  140 |       (e) => e.source === "n_draft" && e.target === "n_images",
  141 |     ),
  142 |   ).toBe(true);
  143 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  144 |   await expect(page.locator(".react-flow__node-block")).toHaveCount(5);
  145 |   await saved(page);
  146 |   expect((await def(request, d.id)).graph.nodes).toEqual(d.graph.nodes);
  147 |   await page.getByRole("button", { name: "Redo", exact: true }).click();
  148 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  149 |   await expect(
  150 |     page.getByRole("heading", { name: "Problems", exact: true }),
  151 |   ).toBeVisible();
  152 |   await expect(
  153 |     page.getByText("A referenced output does not exist.").first(),
  154 |   ).toBeVisible();
  155 | });
  156 | test("Autosave survives reload and both stale-save conflict choices preserve intent", async ({
  157 |   page,
  158 |   request,
  159 | }) => {
  160 |   const d = await create(request, "brief_images");
  161 |   await page.goto(`/workflows/${d.id}`);
  162 |   await block(page, "n_draft");
  163 |   await page
  164 |     .getByRole("textbox", { name: "Block name", exact: true })
  165 |     .fill("Synthetic renamed draft");
  166 |   await saved(page);
  167 |   await page.reload();
  168 |   await expect(
  169 |     page
  170 |       .locator(".wf-block-title")
  171 |       .filter({ hasText: "Synthetic renamed draft" }),
  172 |   ).toBeVisible();
  173 |   const stale = await def(request, d.id);
  174 |   await request.put(`/api/workflows/defs/${d.id}`, {
  175 |     data: {
  176 |       ...stale,
  177 |       name: "Synthetic other device",
  178 |       version: stale.version,
  179 |       graph: stale.graph,
```