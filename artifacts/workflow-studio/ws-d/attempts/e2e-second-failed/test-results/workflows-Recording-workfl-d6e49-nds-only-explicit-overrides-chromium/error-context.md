# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflows.spec.ts >> Recording workflow retains source and sends only explicit overrides
- Location: tests/workflows.spec.ts:159:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('article', { name: 'Recording to meeting pack run' }).first().getByRole('status')
Expected substring: "Ready for review"
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" getByRole('article', { name: 'Recording to meeting pack run' }).first().getByRole('status') with timeout 15000ms
  - waiting for getByRole('article', { name: 'Recording to meeting pack run' }).first().getByRole('status')

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
  - button "Recording to meeting pack"
  - status: Saved
  - button "Undo"
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
      - group "Connection from Start to Transcribe recording"
    - img:
      - group "Connection from Transcribe recording to Clean up transcript"
    - img:
      - group "Connection from Clean up transcript to Draft meeting pack"
    - img:
      - group "Connection from Transcribe recording to Draft meeting pack"
    - img:
      - group "Connection from Draft meeting pack to Save results"
    - button "Insert on connection e_start_transcript"
    - button "Delete connection e_start_transcript"
    - button "Insert on connection e_transcript_clean"
    - button "Delete connection e_transcript_clean"
    - button "Insert on connection e_clean_pack"
    - button "Delete connection e_clean_pack"
    - button "Insert on connection e_transcript_pack"
    - button "Delete connection e_transcript_pack"
    - button "Insert on connection e_pack_save"
    - button "Delete connection e_pack_save"
    - group "Start block ‘Start’, 1 of 5":
      - text: Start Start
      - button "Actions for Start"
      - paragraph: "Inputs: Recording"
      - text: start.recording
    - group "Transcribe recording block ‘Transcribe recording’, 2 of 5":
      - text: Transcribe recording Transcribe recording
      - button "Actions for Transcribe recording"
      - paragraph: "{{start.recording}}"
      - text: transcript.transcript transcript.text +3
    - group "Clean up transcript block ‘Clean up transcript’, 3 of 5":
      - text: Clean up transcript Clean up transcript
      - button "Actions for Clean up transcript"
      - paragraph: Disabled · skipped when the workflow runs
      - text: clean.text
    - group "Generate text block ‘Draft meeting pack’, 4 of 5":
      - text: Draft meeting pack Generate text
      - button "Actions for Draft meeting pack"
      - paragraph: fake-chat · temperature 0.4 · Markdown
      - text: pack.text
    - group "Save results block ‘Save results’, 5 of 5":
      - text: Save results Save results
      - button "Actions for Save results"
      - paragraph: Markdown, JSON · 1 items
    - img
    - img "Mini Map"
    - link "React Flow attribution":
      - /url: https://reactflow.dev/attribution
      - text: React Flow
  - paragraph: Drag blocks from the left, or hover a connection and press +
  - button "Zoom out"
  - button "Zoom 100%": 79%
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
      - text: Recording * Saved recording
      - combobox "Saved recording": Synthetic-workflow.wav
      - text: Upload Recording
      - button "Upload Recording"
      - status: File ready.
      - alert: Choose a workflow default model or a model for this block.
      - button "Run workflow"
      - paragraph: Accepted runs keep going on your Mac. Text outputs are drafts for your review.
  - button "Import workflow JSON"
- region "Notifications alt+T"
```

# Test source

```ts
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
  144 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
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
> 196 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
      |                                          ^ Error: expect(locator).toContainText(expected) failed
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