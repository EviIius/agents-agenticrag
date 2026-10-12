# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflows.spec.ts >> Creative workflow review, reconnect, variants and cancellable saving
- Location: tests/workflows.spec.ts:93:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('article', { name: 'Brief to images run' }).first().getByRole('textbox', { name: 'Review image prompt' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('article', { name: 'Brief to images run' }).first().getByRole('textbox', { name: 'Review image prompt' }) with timeout 5000ms
  - waiting for getByRole('article', { name: 'Brief to images run' }).first().getByRole('textbox', { name: 'Review image prompt' })

```

```yaml
- main:
  - link "Back to chat":
    - /url: /
  - heading "Workflows" [level=1]
  - status: Connected
  - status: The request contains invalid values.
  - heading "New workflow" [level=2]
  - button "Brief to images" [pressed]
  - button "Recording to meeting pack"
  - text: Image brief
  - textbox "Image brief":
    - /placeholder: Describe the image you want…
    - text: "Synthetic browser workflow: one blue circle on a white background"
  - paragraph: Your text model drafts one prompt. FLUX.2 klein 4B generates the images.
  - paragraph: Choose a model marked “tested with images” for an uninterrupted run. Other loaded combinations can stop the image step; your draft stays saved.
  - text: Prompt draft model
  - combobox "Prompt draft model": fake-chat · 16K context
  - group: Optional model overrides
  - text: Image seeds · one to three variants
  - textbox "Image variant seeds": 901,902
  - checkbox "Pause to review the prompt before generating" [checked]
  - text: Pause to review the prompt before generating
  - button "Start workflow"
  - paragraph: Accepted steps continue on your Mac when you close the app. The latest 50 runs are shown below.
  - heading "Saved runs" [level=2]
  - paragraph: No workflows yet. Choose a template and model to begin.
- region "Notifications alt+T"
```

# Test source

```ts
  13  |       model_id: "fake-chat",
  14  |       display_name: "fake-chat",
  15  |       params: {},
  16  |       context_length: 16384,
  17  |     },
  18  |   });
  19  | });
  20  | 
  21  | for (const width of [390, 1440])
  22  |   for (const theme of ["light", "dark"]) {
  23  |     test(`Workflow synthetic states ${width} ${theme}`, async ({
  24  |       page,
  25  |       browserName,
  26  |     }) => {
  27  |       await page.setViewportSize({ width, height: 900 });
  28  |       await page.goto("/design?workflows");
  29  |       await page.getByRole("button", { name: theme, exact: true }).click();
  30  |       await mkdir(dir, { recursive: true });
  31  |       const results = [];
  32  |       for (const state of [
  33  |         "empty",
  34  |         "queued",
  35  |         "running",
  36  |         "paused",
  37  |         "complete",
  38  |         "failed",
  39  |         "cancelling",
  40  |         "cancelled",
  41  |         "interrupted",
  42  |         "cleanup-failed",
  43  |       ]) {
  44  |         await page.getByRole("button", { name: state, exact: true }).click();
  45  |         await settle(page);
  46  |         expect(
  47  |           await page.evaluate(
  48  |             () => document.documentElement.scrollWidth <= innerWidth,
  49  |           ),
  50  |         ).toBeTruthy();
  51  |         const scan = await new AxeBuilder({ page }).analyze();
  52  |         expect(
  53  |           scan.violations.filter((v) =>
  54  |             ["serious", "critical"].includes(v.impact ?? ""),
  55  |           ),
  56  |           state,
  57  |         ).toEqual([]);
  58  |         results.push({ state, seriousCritical: 0 });
  59  |         await page.screenshot({
  60  |           path: `${dir}/${state}-${width}-${theme}-${browserName}-fake.png`,
  61  |           fullPage: true,
  62  |         });
  63  |       }
  64  |       await page
  65  |         .getByRole("button", { name: "View original transcript" })
  66  |         .click();
  67  |       await expect(
  68  |         page.getByRole("dialog", { name: "Original transcript" }),
  69  |       ).toContainText("Synthetic source");
  70  |       await page.keyboard.press("Escape");
  71  |       await page.getByRole("button", { name: "Save outputs" }).click();
  72  |       const dialog = page.getByRole("dialog", {
  73  |         name: "Save workflow outputs",
  74  |       });
  75  |       await dialog
  76  |         .getByRole("button", { name: "Details and source (.json)" })
  77  |         .click();
  78  |       await expect(
  79  |         dialog.getByRole("button", { name: "Details and source (.json)" }),
  80  |       ).toHaveAttribute("aria-pressed", "true");
  81  |       await page.screenshot({
  82  |         path: `${dir}/save-json-${width}-${theme}-${browserName}-fake.png`,
  83  |         fullPage: true,
  84  |       });
  85  |       await page.keyboard.press("Escape");
  86  |       await writeFile(
  87  |         `${dir}/axe-${width}-${theme}-${browserName}.json`,
  88  |         JSON.stringify(results, null, 2),
  89  |       );
  90  |     });
  91  |   }
  92  | 
  93  | test("Creative workflow review, reconnect, variants and cancellable saving", async ({
  94  |   page,
  95  | }) => {
  96  |   await page.goto("/workflows");
  97  |   await page
  98  |     .getByRole("textbox", { name: "Image brief" })
  99  |     .fill("Synthetic browser workflow: one blue circle on a white background");
  100 |   await page.getByRole("combobox", { name: "Prompt draft model" }).click();
  101 |   await page.getByRole("option").filter({ hasText: "fake-chat" }).click();
  102 |   await page
  103 |     .getByRole("textbox", { name: "Image variant seeds" })
  104 |     .fill("901,902");
  105 |   await page
  106 |     .getByRole("button", { name: "Start workflow", exact: true })
  107 |     .click();
  108 |   const card = page
  109 |     .getByRole("article", { name: "Brief to images run" })
  110 |     .first();
  111 |   await expect(
  112 |     card.getByRole("textbox", { name: "Review image prompt" }),
> 113 |   ).toBeVisible();
      |     ^ Error: expect(locator).toBeVisible() failed
  114 |   await page.reload();
  115 |   await expect(
  116 |     card.getByRole("textbox", { name: "Review image prompt" }),
  117 |   ).toBeVisible();
  118 |   await card
  119 |     .getByRole("textbox", { name: "Review image prompt" })
  120 |     .fill("Synthetic blue circle");
  121 |   await card
  122 |     .getByRole("button", { name: "Approve prompt and generate" })
  123 |     .click();
  124 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
  125 |     timeout: 15000,
  126 |   });
  127 |   await expect(
  128 |     card.getByRole("img", { name: "Workflow generated image" }),
  129 |   ).toHaveCount(2);
  130 |   let downloads = 0;
  131 |   page.on("download", () => downloads++);
  132 |   await card.getByRole("button", { name: "Save outputs" }).click();
  133 |   await page.getByRole("button", { name: "Close workflow save" }).click();
  134 |   expect(downloads).toBe(0);
  135 |   await page.reload();
  136 |   await expect(card.getByRole("status")).toContainText("Ready for review");
  137 | });
  138 | 
  139 | test("Recording workflow retains source and sends only explicit overrides", async ({
  140 |   page,
  141 |   request,
  142 | }) => {
  143 |   const upload = await request.post("/api/attachments", {
  144 |     multipart: {
  145 |       file: {
  146 |         name: "Synthetic-workflow.wav",
  147 |         mimeType: "audio/wav",
  148 |         buffer: Buffer.from("fake"),
  149 |       },
  150 |     },
  151 |   });
  152 |   expect(upload.status()).toBe(201);
  153 |   await page.goto("/workflows");
  154 |   await page
  155 |     .getByRole("button", { name: "Recording to meeting pack", exact: true })
  156 |     .click();
  157 |   await page.getByRole("combobox", { name: "Saved recording" }).click();
  158 |   await page
  159 |     .getByRole("option")
  160 |     .filter({ hasText: "Synthetic-workflow.wav" })
  161 |     .first()
  162 |     .click();
  163 |   await page.getByRole("combobox", { name: "Meeting-pack model" }).click();
  164 |   await page.getByRole("option").filter({ hasText: "fake-chat" }).click();
  165 |   await page.getByText("Optional model overrides", { exact: true }).click();
  166 |   await page
  167 |     .getByRole("spinbutton", { name: "Workflow output token limit" })
  168 |     .fill("900");
  169 |   await page
  170 |     .getByRole("spinbutton", { name: "Workflow temperature" })
  171 |     .fill("0.4");
  172 |   await page
  173 |     .getByRole("button", { name: "Start workflow", exact: true })
  174 |     .click();
  175 |   const card = page
  176 |     .getByRole("article", { name: "Recording to meeting pack run" })
  177 |     .first();
  178 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
  179 |     timeout: 15000,
  180 |   });
  181 |   await card.getByRole("button", { name: "View original transcript" }).click();
  182 |   await expect(
  183 |     page.getByRole("dialog", { name: "Original transcript" }),
  184 |   ).toContainText("Fake transcript");
  185 |   await page.keyboard.press("Escape");
  186 |   const captures = await request.get("http://127.0.0.1:18080/tests/state");
  187 |   expect(captures.ok()).toBeTruthy();
  188 |   {
  189 |     const rows = (await captures.json()).captures;
  190 |     const body = rows.findLast(
  191 |       (r: { options?: { num_predict?: number } }) =>
  192 |         r.options?.num_predict === 900,
  193 |     );
  194 |     expect(body.options.temperature).toBe(0.4);
  195 |     expect(body.tools).toBeUndefined();
  196 |   }
  197 |   expect((await request.get(fakeAppURL + "/api/health")).status()).toBe(200);
  198 | });
  199 | 
```