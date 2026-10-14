# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflows.spec.ts >> Creative workflow review, reconnect, variants and cancellable saving
- Location: tests/workflows.spec.ts:110:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('article', { name: 'Brief to images run' }).first().getByRole('status')
Expected substring: "Ready for review"
Error: strict mode violation: getByRole('article', { name: 'Brief to images run' }).first().getByRole('status') resolved to 2 elements:
    1) <p role="status" class="my-3 text-sm text-fg-2">Ready for review · complete</p> aka getByText('Ready for review · complete')
    2) <span role="status" class="sr-only" aria-live="polite"></span> aka getByRole('region', { name: 'Workflow results' }).getByRole('status')

Call log:
  - Expect "toContainText" getByRole('article', { name: 'Brief to images run' }).first().getByRole('status') with timeout 15000ms
  - waiting for getByRole('article', { name: 'Brief to images run' }).first().getByRole('status')
    2 × locator resolved to <p role="status" class="my-3 text-sm text-fg-2">Waiting for you: Check the prompt · paused</p>
      - unexpected value "Waiting for you: Check the prompt · paused"
    3 × locator resolved to <p role="status" class="my-3 text-sm text-fg-2">Create images · running</p>
      - unexpected value "Create images · running"

```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - generic [ref=f1e3]:
    - complementary [ref=f1e4]:
      - generic [ref=f1e5]:
        - button "Expand sidebar" [ref=f1e7] [cursor=pointer]
        - link "New chat" [ref=f1e8] [cursor=pointer]:
          - /url: /
        - button "Search chats" [ref=f1e9] [cursor=pointer]
        - navigation "Chat history" [ref=f1e10]:
          - navigation "Workspace" [ref=f1e11]:
            - link "Workflows" [ref=f1e12] [cursor=pointer]:
              - /url: /workflows
              - img "A workflow is waiting for you" [ref=f1e13]
            - link "Images" [ref=f1e14] [cursor=pointer]:
              - /url: /images
        - button "Settings" [ref=f1e16] [cursor=pointer]
    - main [ref=f1e17]:
      - generic [ref=f1e18]:
        - generic [ref=f1e19]:
          - link "Back to Workflows" [ref=f1e20] [cursor=pointer]:
            - /url: /workflows
            - generic [ref=f1e23]: Workflows
          - generic [ref=f1e24]: /
          - button "Brief to images" [ref=f1e25] [cursor=pointer]
          - status [ref=f1e26]: Saved
          - button "Undo" [disabled]
          - button "Redo" [disabled]
          - button "Workflow menu" [ref=f1e28] [cursor=pointer]
          - button "Run" [ref=f1e29] [cursor=pointer]
        - generic [ref=f1e30]:
          - complementary "Blocks" [ref=f1e31]:
            - textbox "Search blocks" [ref=f1e36]
            - generic [ref=f1e37]:
              - group [ref=f1e38]:
                - generic "Inputs" [ref=f1e39] [cursor=pointer]
                - button "Start" [ref=f1e40] [cursor=pointer]
              - group [ref=f1e43]:
                - generic "AI" [ref=f1e44] [cursor=pointer]
                - button "Generate text" [ref=f1e45] [cursor=pointer]
                - button "Classify" [disabled] [ref=f1e48]
              - group [ref=f1e51]:
                - generic "Knowledge" [ref=f1e52] [cursor=pointer]
                - button "Search the web" [disabled] [ref=f1e53]
                - button "Search my files" [disabled] [ref=f1e56]
                - button "Read a document" [disabled] [ref=f1e59]
              - group [ref=f1e62]:
                - generic "Media" [ref=f1e63] [cursor=pointer]
                - button "Transcribe recording" [ref=f1e64] [cursor=pointer]
                - button "Clean up transcript" [ref=f1e67] [cursor=pointer]
                - button "Create images" [ref=f1e70] [cursor=pointer]
              - group [ref=f1e73]:
                - generic "Logic" [ref=f1e74] [cursor=pointer]
                - button "If / else" [disabled] [ref=f1e75]
                - button "Compose text" [disabled] [ref=f1e78]
              - group [ref=f1e81]:
                - generic "Review" [ref=f1e82] [cursor=pointer]
                - button "Approve or edit" [ref=f1e83] [cursor=pointer]
                - button "Pick favorites" [ref=f1e86] [cursor=pointer]
              - group [ref=f1e89]:
                - generic "Output" [ref=f1e90] [cursor=pointer]
                - button "Save results" [ref=f1e91] [cursor=pointer]
            - button "Note" [ref=f1e95] [cursor=pointer]
          - generic "Read-only workflow canvas" [ref=f1e98]:
            - application [ref=f1e99]:
              - generic [ref=f1e101]:
                - generic:
                  - generic:
                    - img:
                      - img "Connection from Draft image prompt to Check the prompt"
                    - img:
                      - img "Connection from Start to Draft image prompt"
                    - img:
                      - img "Connection from Check the prompt to Create images" [ref=f1e102] [cursor=pointer]
                    - img:
                      - img "Connection from Create images to Save results"
                  - generic:
                    - group "Start block ‘Start’, 1 of 5" [ref=f1e105] [cursor=pointer]:
                      - generic [ref=f1e108]:
                        - generic [ref=f1e113]:
                          - generic [ref=f1e114]: Start
                          - generic [ref=f1e115]: Start
                        - paragraph [ref=f1e116]: Done in 0 s
                        - generic [ref=f1e117]: start.brief
                        - img "complete" [ref=f1e119]
                    - group "Generate text block ‘Draft image prompt’, 2 of 5" [ref=f1e123] [cursor=pointer]:
                      - generic [ref=f1e127]:
                        - generic [ref=f1e133]:
                          - generic [ref=f1e134]: Draft image prompt
                          - generic [ref=f1e135]: Generate text
                        - paragraph [ref=f1e136]: Done in 0 s
                        - generic [ref=f1e137]: draft.text
                        - img "complete" [ref=f1e139]
                    - group "Approve or edit block ‘Check the prompt’, 3 of 5" [ref=f1e143] [cursor=pointer]:
                      - generic [ref=f1e144]:
                        - generic [ref=f1e147]:
                          - generic [ref=f1e154]:
                            - generic [ref=f1e155]: Check the prompt
                            - generic [ref=f1e156]: Approve or edit
                          - paragraph [ref=f1e157]: Done in 1 s
                          - generic [ref=f1e158]: review.value
                          - img "complete" [ref=f1e160]
                          - img "The rejected path ends here." [ref=f1e163]
                        - generic: Approved
                        - generic: Rejected
                    - group "Create images block ‘Create images’, 4 of 5" [ref=f1e168] [cursor=pointer]:
                      - generic [ref=f1e172]:
                        - generic [ref=f1e179]:
                          - generic [ref=f1e180]: Create images
                          - generic [ref=f1e181]: Create images
                        - paragraph [ref=f1e182]: Done in 0 s
                        - generic [ref=f1e183]:
                          - generic [ref=f1e184]: images.images
                          - generic [ref=f1e185]: images.prompt
                        - img "complete" [ref=f1e186]
                    - group "Save results block ‘Save results’, 5 of 5" [ref=f1e190] [cursor=pointer]:
                      - generic [ref=f1e194]:
                        - generic [ref=f1e201]:
                          - generic [ref=f1e202]: Save results
                          - generic [ref=f1e203]: Save results
                        - paragraph [ref=f1e204]: Done in 0 s
                        - img "complete" [ref=f1e205]
              - img "Mini Map" [ref=f1e209]
              - link "React Flow attribution" [ref=f1e216] [cursor=pointer]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - generic [ref=f1e217]:
              - button "Following run" [pressed] [ref=f1e218] [cursor=pointer]
              - button "Zoom out" [ref=f1e219] [cursor=pointer]
              - button "Zoom 100%" [ref=f1e220] [cursor=pointer]: 79%
              - button "Zoom in" [ref=f1e221] [cursor=pointer]
              - button "Fit view" [ref=f1e222] [cursor=pointer]
              - button "Outline view" [ref=f1e223] [cursor=pointer]
              - button "Canvas actions" [ref=f1e224] [cursor=pointer]
          - complementary "run" [ref=f1e225]:
            - generic [ref=f1e226]:
              - generic [ref=f1e227]:
                - heading "Run" [level=2] [ref=f1e228]
                - button "Close Run" [ref=f1e229] [cursor=pointer]
              - article "Brief to images run" [ref=f1e231]:
                - generic [ref=f1e232]:
                  - heading "Brief to images" [level=3] [ref=f1e233]
                  - time [ref=f1e234]: 10/13/2026, 9:45:06 AM
                - status [ref=f1e235]: Ready for review · complete
                - list [ref=f1e236]:
                  - listitem [ref=f1e237]:
                    - button "View result for Start" [ref=f1e238] [cursor=pointer]:
                      - generic [ref=f1e241]: Start
                      - generic [ref=f1e242]: Done in 0 s
                  - listitem [ref=f1e243]:
                    - button "View result for Draft image prompt" [ref=f1e244] [cursor=pointer]:
                      - generic [ref=f1e247]: Draft image prompt
                      - generic [ref=f1e248]: Done in 0 s
                  - listitem [ref=f1e249]:
                    - button "View result for Check the prompt" [ref=f1e250] [cursor=pointer]:
                      - generic [ref=f1e253]: Check the prompt
                      - generic [ref=f1e254]: Done in 1 s
                  - listitem [ref=f1e255]:
                    - button "View result for Create images" [ref=f1e256] [cursor=pointer]:
                      - generic [ref=f1e259]: Create images
                      - generic [ref=f1e260]: Done in 0 s
                  - listitem [ref=f1e261]:
                    - button "View result for Save results" [ref=f1e262] [cursor=pointer]:
                      - generic [ref=f1e265]: Save results
                      - generic [ref=f1e266]: Done in 0 s
                - region "Workflow results" [ref=f1e267]:
                  - heading "Results" [level=3] [ref=f1e268]
                  - generic [ref=f1e269]:
                    - heading "Save results" [level=4] [ref=f1e270]
                    - generic [ref=f1e271]:
                      - paragraph [ref=f1e272]: Prompt
                      - generic [ref=f1e273]:
                        - status [ref=f1e274]
                        - paragraph [ref=f1e276]: Synthetic blue circle
                    - generic [ref=f1e277]:
                      - paragraph [ref=f1e278]: Images
                      - generic [ref=f1e279]:
                        - button "Save result image 1" [ref=f1e280] [cursor=pointer]:
                          - img "Saved result 1" [ref=f1e281]
                        - button "Save result image 2" [ref=f1e282] [cursor=pointer]:
                          - img "Saved result 2" [ref=f1e283]
                - button "Save outputs" [ref=f1e285] [cursor=pointer]
                - paragraph [ref=f1e286]: Draft for review. Check it against the original.
        - button "Import workflow JSON" [ref=f1e287]
  - region "Notifications alt+T":
    - list:
      - listitem [ref=f1e288]:
        - button "Close toast" [ref=f1e289] [cursor=pointer]
        - generic [ref=f1e293]: Brief to images is waiting for you.
        - button "Open" [ref=f1e295] [cursor=pointer]
```

# Test source

```ts
  44  |         "cancelling",
  45  |         "cancelled",
  46  |         "interrupted",
  47  |         "meeting-running",
  48  |         "meeting-complete",
  49  |         "uploading",
  50  |         "upload-failed",
  51  |         "cleanup-failed",
  52  |       ]) {
  53  |         await page.getByRole("button", { name: state, exact: true }).click();
  54  |         await settle(page);
  55  |         expect(
  56  |           await page.evaluate(
  57  |             () => document.documentElement.scrollWidth <= innerWidth,
  58  |           ),
  59  |         ).toBeTruthy();
  60  |         const scan = await new AxeBuilder({ page }).analyze();
  61  |         expect(
  62  |           scan.violations.filter((v) =>
  63  |             ["serious", "critical"].includes(v.impact ?? ""),
  64  |           ),
  65  |           state,
  66  |         ).toEqual([]);
  67  |         results.push({ state, seriousCritical: 0 });
  68  |         await page.screenshot({
  69  |           path: `${dir}/${state}-${width}-${theme}-${browserName}-fake.png`,
  70  |           fullPage: true,
  71  |         });
  72  |       }
  73  |       await page
  74  |         .getByRole("button", { name: "View original transcript" })
  75  |         .click();
  76  |       await expect(
  77  |         page.getByRole("dialog", { name: "Original transcript" }),
  78  |       ).toContainText("Synthetic source");
  79  |       await page
  80  |         .getByText("Original source timestamps", { exact: true })
  81  |         .click();
  82  |       await expect(page.getByText("0.2s–2.8s", { exact: true })).toBeVisible();
  83  |       await page.screenshot({
  84  |         path: `${dir}/source-timeline-${width}-${theme}-${browserName}-fake.png`,
  85  |         fullPage: true,
  86  |       });
  87  |       await page.keyboard.press("Escape");
  88  |       await page.getByRole("button", { name: "Save outputs" }).click();
  89  |       const dialog = page.getByRole("dialog", {
  90  |         name: "Save workflow outputs",
  91  |       });
  92  |       await dialog
  93  |         .getByRole("button", { name: "Details and source (.json)" })
  94  |         .click();
  95  |       await expect(
  96  |         dialog.getByRole("button", { name: "Details and source (.json)" }),
  97  |       ).toHaveAttribute("aria-pressed", "true");
  98  |       await page.screenshot({
  99  |         path: `${dir}/save-json-${width}-${theme}-${browserName}-fake.png`,
  100 |         fullPage: true,
  101 |       });
  102 |       await page.keyboard.press("Escape");
  103 |       await writeFile(
  104 |         `${dir}/axe-${width}-${theme}-${browserName}.json`,
  105 |         JSON.stringify(results, null, 2),
  106 |       );
  107 |     });
  108 |   }
  109 | 
  110 | test("Creative workflow review, reconnect, variants and cancellable saving", async ({
  111 |   page,
  112 | }) => {
  113 |   await page.goto("/workflows/new?template=brief_images");
  114 |   await configureStudioBlock(page, "Draft image prompt");
  115 |   await chooseStudioModel(page);
  116 |   await configureStudioBlock(page, "Create images");
  117 |   await page.getByRole("button", { name: "2", exact: true }).click();
  118 |   await page.getByRole("button", { name: "Advanced", exact: true }).click();
  119 |   await page
  120 |     .getByRole("spinbutton", { name: "Seed 1", exact: true })
  121 |     .fill("901");
  122 |   await page
  123 |     .getByRole("spinbutton", { name: "Seed 2", exact: true })
  124 |     .fill("902");
  125 |   await openStudioRun(page);
  126 |   await page
  127 |     .getByRole("textbox", { name: "Image brief", exact: true })
  128 |     .fill("Synthetic browser workflow: one blue circle on a white background");
  129 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  130 |   const card = page
  131 |     .getByRole("article", { name: "Brief to images run" })
  132 |     .first();
  133 |   await expect(
  134 |     card.getByRole("textbox", { name: "Review result" }),
  135 |   ).toBeVisible();
  136 |   await page.reload();
  137 |   await expect(
  138 |     card.getByRole("textbox", { name: "Review result" }),
  139 |   ).toBeVisible();
  140 |   await card
  141 |     .getByRole("textbox", { name: "Review result" })
  142 |     .fill("Synthetic blue circle");
  143 |   await card.getByRole("button", { name: "Approve", exact: true }).click();
> 144 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
      |                                          ^ Error: expect(locator).toContainText(expected) failed
  145 |     timeout: 15000,
  146 |   });
  147 |   await expect(
  148 |     card.getByRole("img", { name: /Workflow generated image/ }),
  149 |   ).toHaveCount(2);
  150 |   let downloads = 0;
  151 |   page.on("download", () => downloads++);
  152 |   await card.getByRole("button", { name: "Save outputs" }).click();
  153 |   await page.getByRole("button", { name: "Close workflow save" }).click();
  154 |   expect(downloads).toBe(0);
  155 |   await page.reload();
  156 |   await expect(card.getByRole("status")).toContainText("Ready for review");
  157 | });
  158 | 
  159 | test("Recording workflow retains source and sends only explicit overrides", async ({
  160 |   page,
  161 |   request,
  162 | }) => {
  163 |   const upload = await request.post("/api/attachments", {
  164 |     multipart: {
  165 |       file: {
  166 |         name: "Synthetic-workflow.wav",
  167 |         mimeType: "audio/wav",
  168 |         buffer: Buffer.from("fake"),
  169 |       },
  170 |     },
  171 |   });
  172 |   expect(upload.status()).toBe(201);
  173 |   await page.goto("/workflows/new?template=meeting_pack");
  174 |   await configureStudioBlock(page, "Draft meeting pack");
  175 |   await chooseStudioModel(page);
  176 |   await page.getByText("Optional overrides", { exact: true }).click();
  177 |   await page
  178 |     .getByRole("spinbutton", { name: "Output limit", exact: true })
  179 |     .fill("900");
  180 |   await page
  181 |     .getByRole("spinbutton", { name: "Temperature", exact: true })
  182 |     .fill("0.4");
  183 |   await openStudioRun(page);
  184 |   await page
  185 |     .getByRole("combobox", { name: "Saved recording", exact: true })
  186 |     .click();
  187 |   await page
  188 |     .getByRole("option")
  189 |     .filter({ hasText: "Synthetic-workflow.wav" })
  190 |     .first()
  191 |     .click();
  192 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  193 |   const card = page
  194 |     .getByRole("article", { name: "Recording to meeting pack run" })
  195 |     .first();
  196 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
  197 |     timeout: 15000,
  198 |   });
  199 |   await card.getByRole("button", { name: "View original transcript" }).click();
  200 |   await expect(
  201 |     page.getByRole("dialog", { name: "Original transcript" }),
  202 |   ).toContainText("Fake transcript");
  203 |   await page.keyboard.press("Escape");
  204 |   const captures = await request.get("http://127.0.0.1:18080/tests/state");
  205 |   expect(captures.ok()).toBeTruthy();
  206 |   {
  207 |     const rows = (await captures.json()).captures;
  208 |     const body = rows.findLast(
  209 |       (r: { options?: { num_predict?: number } }) =>
  210 |         r.options?.num_predict === 900,
  211 |     );
  212 |     expect(body.options.temperature).toBe(0.4);
  213 |     expect(body.tools).toBeUndefined();
  214 |   }
  215 |   expect((await request.get(fakeAppURL + "/api/health")).status()).toBe(200);
  216 | });
  217 | 
```