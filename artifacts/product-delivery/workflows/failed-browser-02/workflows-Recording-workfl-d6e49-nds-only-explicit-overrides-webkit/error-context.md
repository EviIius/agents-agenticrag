# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflows.spec.ts >> Recording workflow retains source and sends only explicit overrides
- Location: tests/workflows.spec.ts:139:1

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
- main:
  - link "Back to chat":
    - /url: /
  - heading "Workflows" [level=1]
  - status: Connected
  - status: The request contains invalid values.
  - heading "New workflow" [level=2]
  - button "Brief to images"
  - button "Recording to meeting pack" [pressed]
  - text: Upload a recording
  - button "Upload workflow recording"
  - text: Or use a saved recording
  - combobox "Saved recording": Synthetic-workflow.wav · ready
  - paragraph: The original transcript is saved. Successful audio follows your existing retention setting.
  - text: Meeting-pack model
  - combobox "Meeting-pack model": fake-chat · 16K context
  - group:
    - text: Optional model overrides
    - paragraph: Empty fields use your saved model defaults, then runtime defaults.
    - text: Output token limit
    - spinbutton "Workflow output token limit": "900"
    - text: Temperature
    - spinbutton "Workflow temperature": "0.4"
  - checkbox "Run guarded transcript clean-up first"
  - text: Run guarded transcript clean-up first
  - paragraph: The meeting pack is a draft. Check decisions, owners and dates against the saved source.
  - button "Start workflow"
  - paragraph: Accepted steps continue on your Mac when you close the app. The latest 50 runs are shown below.
  - heading "Saved runs" [level=2]
  - paragraph: No workflows yet. Choose a template and model to begin.
- region "Notifications alt+T"
```

# Test source

```ts
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
  113 |   ).toBeVisible();
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
> 178 |   await expect(card.getByRole("status")).toContainText("Ready for review", {
      |                                          ^ Error: expect(locator).toContainText(expected) failed
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