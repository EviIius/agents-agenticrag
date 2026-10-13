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
    - locator resolved to <p role="status" class="my-3 text-sm text-fg-2">Waiting for you: Check the prompt · paused</p>
    - unexpected value "Waiting for you: Check the prompt · paused"
    4 × locator resolved to <p role="status" class="my-3 text-sm text-fg-2">Create images · running</p>
      - unexpected value "Create images · running"

```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - main:
        - generic:
          - generic:
            - button
            - link:
              - /url: /workflows
            - button: Brief to images
            - button
            - button: Run
          - generic:
            - generic:
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Start
                      - generic: Done in 0 s
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Draft image prompt
                      - generic: Done in 0 s
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Check the prompt
                      - generic: Done in 1 s
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Create images
                      - generic: Done in 0 s
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Save results
                      - generic: Done in 0 s
          - button
    - region "Notifications alt+T":
      - list:
        - listitem [ref=f1e1]:
          - button "Close toast" [ref=f1e2] [cursor=pointer]
          - generic [ref=f1e6]: Brief to images is waiting for you.
          - button "Open" [ref=f1e8] [cursor=pointer]
  - dialog [active] [ref=f1e10]:
    - heading "run" [level=2] [ref=f1e12]
    - paragraph [ref=f1e13]: Edit this workflow's settings.
    - generic [ref=f1e14]:
      - banner [ref=f1e15]:
        - heading "Run" [level=2] [ref=f1e16]
        - button "Close Run" [ref=f1e17] [cursor=pointer]
      - article "Brief to images run" [ref=f1e19]:
        - generic [ref=f1e20]:
          - heading "Brief to images" [level=3] [ref=f1e21]
          - time [ref=f1e22]: 10/13/2026, 10:12:25 AM
        - status [ref=f1e23]: Ready for review · complete
        - list [ref=f1e24]:
          - listitem [ref=f1e25]:
            - button "View result for Start" [ref=f1e26] [cursor=pointer]:
              - generic [ref=f1e29]: Start
              - generic [ref=f1e30]: Done in 0 s
          - listitem [ref=f1e31]:
            - button "View result for Draft image prompt" [ref=f1e32] [cursor=pointer]:
              - generic [ref=f1e35]: Draft image prompt
              - generic [ref=f1e36]: Done in 0 s
          - listitem [ref=f1e37]:
            - button "View result for Check the prompt" [ref=f1e38] [cursor=pointer]:
              - generic [ref=f1e41]: Check the prompt
              - generic [ref=f1e42]: Done in 1 s
          - listitem [ref=f1e43]:
            - button "View result for Create images" [ref=f1e44] [cursor=pointer]:
              - generic [ref=f1e47]: Create images
              - generic [ref=f1e48]: Done in 0 s
          - listitem [ref=f1e49]:
            - button "View result for Save results" [ref=f1e50] [cursor=pointer]:
              - generic [ref=f1e53]: Save results
              - generic [ref=f1e54]: Done in 0 s
        - region "Workflow results" [ref=f1e55]:
          - heading "Results" [level=3] [ref=f1e56]
          - generic [ref=f1e57]:
            - heading "Save results" [level=4] [ref=f1e58]
            - generic [ref=f1e59]:
              - paragraph [ref=f1e60]: Prompt
              - generic [ref=f1e61]:
                - status [ref=f1e62]
                - paragraph [ref=f1e64]: Synthetic blue circle
            - generic [ref=f1e65]:
              - paragraph [ref=f1e66]: Images
              - generic [ref=f1e67]:
                - button "Save result image 1" [ref=f1e68] [cursor=pointer]:
                  - img "Saved result 1" [ref=f1e69]
                - button "Save result image 2" [ref=f1e70] [cursor=pointer]:
                  - img "Saved result 2" [ref=f1e71]
        - button "Save outputs" [ref=f1e73] [cursor=pointer]
        - paragraph [ref=f1e74]: Draft for review. Check it against the original.
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