# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Workflow count uses automatic seeds and repeats uncertain acceptance exactly
- Location: tests/composer-workflows.spec.ts:117:1

# Error details

```
TypeError: Cannot read properties of undefined (reading 'id')
```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - button "Expand sidebar" [ref=e7] [cursor=pointer]
        - link "New chat" [ref=e8] [cursor=pointer]:
          - /url: /
        - button "Search chats" [ref=e9] [cursor=pointer]
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e12] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e13] [cursor=pointer]:
              - /url: /images
        - button "Settings" [ref=e15] [cursor=pointer]
    - main [ref=e16]:
      - generic [ref=e17]:
        - generic [ref=e18]:
          - link "Back to Workflows" [ref=e19] [cursor=pointer]:
            - /url: /workflows
            - generic [ref=e22]: Workflows
          - generic [ref=e23]: /
          - button "Brief to images" [ref=e24] [cursor=pointer]
          - status [ref=e25]: Saved
          - button "Undo" [ref=e27] [cursor=pointer]
          - button "Redo" [disabled]
          - button "Workflow menu" [ref=e28] [cursor=pointer]
          - button "Run" [ref=e29] [cursor=pointer]
        - generic [ref=e30]:
          - complementary "Blocks" [ref=e31]:
            - textbox "Search blocks" [ref=e36]
            - generic [ref=e37]:
              - group [ref=e38]:
                - generic "Inputs" [ref=e39] [cursor=pointer]
                - button "Start" [ref=e40] [cursor=pointer]
              - group [ref=e43]:
                - generic "AI" [ref=e44] [cursor=pointer]
                - button "Generate text" [ref=e45] [cursor=pointer]
                - button "Classify" [disabled] [ref=e48]
              - group [ref=e51]:
                - generic "Knowledge" [ref=e52] [cursor=pointer]
                - button "Search the web" [disabled] [ref=e53]
                - button "Search my files" [disabled] [ref=e56]
                - button "Read a document" [disabled] [ref=e59]
              - group [ref=e62]:
                - generic "Media" [ref=e63] [cursor=pointer]
                - button "Transcribe recording" [ref=e64] [cursor=pointer]
                - button "Clean up transcript" [ref=e67] [cursor=pointer]
                - button "Create images" [ref=e70] [cursor=pointer]
              - group [ref=e73]:
                - generic "Logic" [ref=e74] [cursor=pointer]
                - button "If / else" [disabled] [ref=e75]
                - button "Compose text" [disabled] [ref=e78]
              - group [ref=e81]:
                - generic "Review" [ref=e82] [cursor=pointer]
                - button "Approve or edit" [ref=e83] [cursor=pointer]
                - button "Pick favorites" [disabled] [ref=e86]
              - group [ref=e89]:
                - generic "Output" [ref=e90] [cursor=pointer]
                - button "Save results" [ref=e91] [cursor=pointer]
            - button "Note" [ref=e95] [cursor=pointer]
          - generic "Workflow canvas" [ref=e98]:
            - application [ref=e99]:
              - generic [ref=e101]:
                - generic:
                  - generic:
                    - img:
                      - group "Connection from Draft image prompt to Check the prompt"
                    - img:
                      - group "Connection from Start to Draft image prompt"
                    - img:
                      - group "Connection from Check the prompt to Create images" [ref=e102] [cursor=pointer]
                    - img:
                      - group "Connection from Create images to Save results"
                  - generic:
                    - generic [ref=e105]:
                      - button "Insert on connection e_draft_review" [ref=e106] [cursor=pointer]
                      - button "Delete connection e_draft_review" [ref=e107] [cursor=pointer]
                    - generic [ref=e108]:
                      - button "Insert on connection e_start_draft" [ref=e109] [cursor=pointer]
                      - button "Delete connection e_start_draft" [ref=e110] [cursor=pointer]
                    - generic [ref=e111]:
                      - button "Insert on connection e_review_images" [ref=e112] [cursor=pointer]
                      - button "Delete connection e_review_images" [ref=e113] [cursor=pointer]
                    - generic [ref=e114]:
                      - button "Insert on connection e_images_save" [ref=e115] [cursor=pointer]
                      - button "Delete connection e_images_save" [ref=e116] [cursor=pointer]
                  - generic:
                    - group "Start block ‘Start’, 1 of 5" [ref=e117]:
                      - generic [ref=e120]:
                        - generic [ref=e121]:
                          - generic [ref=e125]:
                            - generic [ref=e126]: Start
                            - generic [ref=e127]: Start
                          - button "Actions for Start" [ref=e128] [cursor=pointer]
                        - paragraph [ref=e129]: "Inputs: Image brief"
                        - generic [ref=e130]: start.brief
                    - group "Generate text block ‘Draft image prompt’, 2 of 5" [ref=e133]:
                      - generic [ref=e137]:
                        - generic [ref=e138]:
                          - generic [ref=e143]:
                            - generic [ref=e144]: Draft image prompt
                            - generic [ref=e145]: Generate text
                          - button "Actions for Draft image prompt" [ref=e146] [cursor=pointer]
                        - paragraph [ref=e147]: fake-chat
                        - generic [ref=e148]: draft.text
                    - group "Approve or edit block ‘Check the prompt’, 3 of 5" [ref=e151]:
                      - generic [ref=e152]:
                        - generic [ref=e155]:
                          - generic [ref=e156]:
                            - generic [ref=e162]:
                              - generic [ref=e163]: Check the prompt
                              - generic [ref=e164]: Approve or edit
                            - button "Actions for Check the prompt" [ref=e165] [cursor=pointer]
                          - paragraph [ref=e166]: "Review {{draft.text}} · editable"
                          - generic [ref=e167]: review.value
                          - generic "The rejected path ends here." [ref=e169]
                        - generic: Approved
                        - generic: Rejected
                    - group "Create images block ‘Create images’, 4 of 5" [ref=e174]:
                      - generic [ref=e178]:
                        - generic [ref=e179]:
                          - generic [ref=e185]:
                            - generic [ref=e186]: Create images
                            - generic [ref=e187]: Create images
                          - button "Actions for Create images" [ref=e188] [cursor=pointer]
                        - paragraph [ref=e189]: 3 images · FLUX.2 klein
                        - generic [ref=e190]:
                          - generic [ref=e191]: images.images
                          - generic [ref=e192]: images.prompt
                    - group "Save results block ‘Save results’, 5 of 5" [ref=e194]:
                      - generic [ref=e198]:
                        - generic [ref=e199]:
                          - generic [ref=e205]:
                            - generic [ref=e206]: Save results
                            - generic [ref=e207]: Save results
                          - button "Actions for Save results" [ref=e208] [cursor=pointer]
                        - paragraph [ref=e209]: Markdown, JSON · 2 items
              - img "Mini Map" [ref=e211]
              - link "React Flow attribution" [ref=e218] [cursor=pointer]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - paragraph [ref=e219]: Drag blocks from the left, or hover a connection and press +
            - generic [ref=e220]:
              - button "Zoom out" [ref=e221] [cursor=pointer]
              - button "Zoom 100%" [ref=e222] [cursor=pointer]: 79%
              - button "Zoom in" [ref=e223] [cursor=pointer]
              - button "Fit view" [ref=e224] [cursor=pointer]
              - button "Tidy up" [ref=e225] [cursor=pointer]
              - button "Outline view" [ref=e226] [cursor=pointer]
              - button "Canvas actions" [ref=e227] [cursor=pointer]
          - complementary "run" [ref=e228]:
            - generic [ref=e229]:
              - generic [ref=e230]:
                - heading "Run" [level=2] [ref=e231]
                - button "Close Run" [ref=e232] [cursor=pointer]
              - generic [ref=e233]:
                - form "Run workflow inputs" [ref=e234]:
                  - heading "Run workflow" [level=2] [ref=e235]
                  - generic [ref=e236]:
                    - text: Image brief
                    - textbox "Image brief" [ref=e237]: Synthetic automatic variants
                  - button "Run workflow" [ref=e238] [cursor=pointer]
                  - paragraph [ref=e239]: Accepted runs keep going on your Mac. Text outputs are drafts for your review.
                - article "Brief to images run" [ref=e240]:
                  - generic [ref=e241]:
                    - heading "Brief to images" [level=3] [ref=e242]
                    - time [ref=e243]: 10/13/2026, 12:40:43 AM
                  - status [ref=e244]: Draft image prompt · running
                  - list [ref=e245]:
                    - listitem [ref=e246]:
                      - generic [ref=e247]:
                        - generic [ref=e248]: Start
                        - generic [ref=e249]: complete
                    - listitem [ref=e250]:
                      - generic [ref=e251]:
                        - generic [ref=e252]: Draft image prompt
                        - generic [ref=e253]: running
                      - generic [ref=e254]: Fake
                    - listitem [ref=e255]:
                      - generic [ref=e256]:
                        - generic [ref=e257]: Check the prompt
                        - generic [ref=e258]: pending
                    - listitem [ref=e259]:
                      - generic [ref=e260]:
                        - generic [ref=e261]: Create images
                        - generic [ref=e262]: pending
                    - listitem [ref=e263]:
                      - generic [ref=e264]:
                        - generic [ref=e265]: Save results
                        - generic [ref=e266]: pending
                  - generic [ref=e267]:
                    - button "Cancel workflow" [ref=e268] [cursor=pointer]
                    - button "Save outputs" [ref=e269] [cursor=pointer]
                  - paragraph [ref=e270]: Draft for review. Check it against the original.
        - button "Import workflow JSON" [ref=e271]
  - region "Notifications alt+T"
```

# Test source

```ts
  67  |     .fill("Synthetic composer circle");
  68  |   await page.getByRole("button", { name: "Generate one image" }).click();
  69  |   await expect(
  70  |     page
  71  |       .getByRole("status")
  72  |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  73  |   ).toBeVisible();
  74  |   await page.getByRole("button", { name: "Generate one image" }).click();
  75  |   await expect.poll(() => bodies.length).toBe(2);
  76  |   expect(bodies[1]).toEqual(bodies[0]);
  77  |   expect(Number.isInteger(bodies[0].seed)).toBe(true);
  78  |   expect(bodies[0].seed as number).toBeGreaterThanOrEqual(0);
  79  |   expect(bodies[0].seed as number).toBeLessThanOrEqual(4294967295);
  80  |   const job = page
  81  |     .getByRole("article")
  82  |     .filter({ hasText: "Synthetic composer circle" })
  83  |     .first();
  84  |   await expect(
  85  |     job.getByRole("button", { name: "Save", exact: true }),
  86  |   ).toBeVisible();
  87  |   const scan = await new AxeBuilder({ page }).analyze();
  88  |   expect(
  89  |     scan.violations.filter((v) =>
  90  |       ["critical", "serious"].includes(v.impact ?? ""),
  91  |     ),
  92  |   ).toEqual([]);
  93  |   await job.getByRole("button", { name: "Save", exact: true }).click();
  94  |   await expect(
  95  |     page.getByRole("dialog", { name: "Save image", exact: true }),
  96  |   ).toBeVisible();
  97  |   await page
  98  |     .getByRole("button", { name: "Close image save", exact: true })
  99  |     .click();
  100 |   await page.getByRole("button", { name: "Message", exact: true }).click();
  101 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  102 |   await expect(message).toBeFocused();
  103 |   expect(chatCalls).toBe(0);
  104 |   await workspaceLink(page, "Workflows");
  105 |   await page
  106 |     .getByRole("button", { name: "Use Brief to images template", exact: true })
  107 |     .click();
  108 |   await configureStudioBlock(page, "Draft image prompt");
  109 |   await expect(
  110 |     page.getByRole("combobox", { name: "Model", exact: true }),
  111 |   ).toContainText("fake-chat");
  112 |   await page.goBack();
  113 |   await page.goBack();
  114 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  115 | });
  116 | 
  117 | test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  118 |   page,
  119 | }) => {
  120 |   await page.goto("/workflows/new?template=brief_images");
  121 |   await configureStudioBlock(page, "Draft image prompt");
  122 |   await chooseStudioModel(page);
  123 |   await configureStudioBlock(page, "Create images");
  124 |   await expect(
  125 |     page.getByRole("spinbutton", { name: "Seed 1", exact: true }),
  126 |   ).not.toBeVisible();
  127 |   await page.getByRole("button", { name: "3", exact: true }).click();
  128 |   await openStudioRun(page);
  129 |   await page
  130 |     .getByRole("textbox", { name: "Image brief", exact: true })
  131 |     .fill("Synthetic automatic variants");
  132 |   const bodies: { request_key: string; inputs: Record<string, unknown> }[] = [];
  133 |   const accepted: {
  134 |     id: string;
  135 |     graph: {
  136 |       nodes: {
  137 |         kind: string;
  138 |         config: {
  139 |           count?: number;
  140 |           seeds?: number[];
  141 |           params?: Record<string, unknown>;
  142 |         };
  143 |       }[];
  144 |     };
  145 |   }[] = [];
  146 |   await page.route("**/api/workflows/defs/*/runs", async (route) => {
  147 |     bodies.push(route.request().postDataJSON());
  148 |     if (bodies.length === 1) {
  149 |       const response = await route.fetch();
  150 |       accepted.push(await response.json());
  151 |       await route.abort("failed");
  152 |     } else {
  153 |       const response = await route.fetch();
  154 |       accepted.push(await response.json());
  155 |       await route.fulfill({ response });
  156 |     }
  157 |   });
  158 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  159 |   await expect(
  160 |     page
  161 |       .getByRole("alert")
  162 |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  163 |   ).toBeVisible();
  164 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  165 |   await expect.poll(() => bodies.length).toBe(2);
  166 |   expect(bodies[1]).toEqual(bodies[0]);
> 167 |   expect(accepted[1].id).toBe(accepted[0].id);
      |                      ^ TypeError: Cannot read properties of undefined (reading 'id')
  168 |   const images = accepted[0].graph.nodes.find(
  169 |     (n) => n.kind === "generate_image",
  170 |   )!;
  171 |   expect(images.config.seeds).toHaveLength(3);
  172 |   expect(
  173 |     accepted[1].graph.nodes.find((n) => n.kind === "generate_image")!.config
  174 |       .seeds,
  175 |   ).toEqual(images.config.seeds);
  176 |   for (const seed of images.config.seeds!) {
  177 |     expect(Number.isInteger(seed)).toBe(true);
  178 |     expect(seed).toBeGreaterThanOrEqual(0);
  179 |     expect(seed).toBeLessThanOrEqual(4294967295);
  180 |   }
  181 |   const params = accepted[0].graph.nodes.find((n) => n.kind === "generate")!
  182 |     .config.params!;
  183 |   expect(Object.values(params).every((v) => v == null)).toBe(true);
  184 |   await expect(
  185 |     page
  186 |       .getByRole("article", { name: "Brief to images run" })
  187 |       .first()
  188 |       .getByRole("textbox", { name: "Review result" }),
  189 |   ).toBeVisible();
  190 | });
  191 | 
  192 | test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  193 |   page,
  194 |   request,
  195 |   browserName,
  196 | }) => {
  197 |   const connection = (await (await request.get("/api/connections")).json())[0];
  198 |   const response = await request.post("/api/chats", {
  199 |     data: { connection_id: connection.id, model_id: "fake-chat" },
  200 |   });
  201 |   const chat = await response.json();
  202 |   await page.goto(`/c/${chat.id}`);
  203 |   const message = page.getByRole("textbox", {
  204 |     name: "Message fake-chat",
  205 |     exact: true,
  206 |   });
  207 |   await message.fill("Synthetic saved-chat draft");
  208 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  209 |   await page
  210 |     .getByRole("textbox", { name: "Prompt", exact: true })
  211 |     .fill("Synthetic cancellable composer #slow");
  212 |   await page.getByRole("button", { name: "Generate one image" }).click();
  213 |   const job = page
  214 |     .getByRole("article")
  215 |     .filter({ hasText: "Synthetic cancellable composer #slow" })
  216 |     .first();
  217 |   await job.getByRole("button", { name: "Cancel", exact: true }).click();
  218 |   await expect(
  219 |     job.getByText("cancelled", { exact: true }).first(),
  220 |   ).toBeVisible();
  221 |   await settle(page);
  222 |   const dir = "../artifacts/composer-workflows/browser/composer";
  223 |   await mkdir(dir, { recursive: true });
  224 |   await page.screenshot({
  225 |     path: `${dir}/cancel-${browserName}-fake.png`,
  226 |     fullPage: true,
  227 |   });
  228 |   await page.getByRole("button", { name: "Message", exact: true }).click();
  229 |   await workspaceLink(page, "Workflows");
  230 |   await page.goBack();
  231 |   await expect(page).toHaveURL(new RegExp(`/c/${chat.id}$`));
  232 |   await expect(message).toHaveValue("Synthetic saved-chat draft");
  233 | });
  234 | 
  235 | test("Visual builder reflows and every node opens its settings with keyboard", async ({
  236 |   page,
  237 |   browserName,
  238 | }) => {
  239 |   const dir = "../artifacts/composer-workflows/browser/builder";
  240 |   await mkdir(dir, { recursive: true });
  241 |   for (const width of [320, 390, 1440]) {
  242 |     await page.setViewportSize({ width, height: 900 });
  243 |     await page.goto("/design?studio");
  244 |     for (const theme of ["light", "dark"]) {
  245 |       await page.getByRole("button", { name: theme, exact: true }).click();
  246 |       await configureStudioBlock(page, "Draft image prompt");
  247 |       await expect(
  248 |         page.getByRole("combobox", { name: "Model", exact: true }),
  249 |       ).toBeVisible();
  250 |       if (width < 768)
  251 |         await expect(
  252 |           page.locator(".wf-outline-row[data-selected=true]"),
  253 |         ).toContainText("Draft image prompt");
  254 |       else
  255 |         await expect(
  256 |           page.locator(".wf-block[data-selected=true]"),
  257 |         ).toContainText("Draft image prompt");
  258 |       await settle(page);
  259 |       expect(
  260 |         await page.evaluate(
  261 |           () => document.documentElement.scrollWidth <= innerWidth,
  262 |         ),
  263 |       ).toBe(true);
  264 |       const scan = await new AxeBuilder({ page }).analyze();
  265 |       expect(
  266 |         scan.violations.filter((v) =>
  267 |           ["critical", "serious"].includes(v.impact ?? ""),
```