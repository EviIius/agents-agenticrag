# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: phase5a.spec.ts >> 5A retained edits, validation and unified settings Save 390
- Location: tests/phase5a.spec.ts:119:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: 'Chat controls', exact: true }).locator('.bg-brand')
Expected: visible
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: 'Chat controls', exact: true }).locator('.bg-brand') with timeout 5000ms
  - waiting for getByRole('button', { name: 'Chat controls', exact: true }).locator('.bg-brand')
  - Target page, context or browser has been closed

```

```yaml
- region "Notifications alt+T"
- dialog "Chat controls":
  - button "Close chat controls"
  - heading "Chat controls" [level=2]
  - paragraph: Sampling and context for this conversation
  - region "Chat controls":
    - group:
      - paragraph: fake-chat
      - heading "This chat" [level=3]
      - text: Preset
      - combobox "Preset": None
      - heading "System prompt" [level=3]
      - switch "Use default system prompt" [checked]
      - text: Use default system prompt
      - textbox "System prompt" [disabled]
      - heading "Sampling" [level=3]
      - group "Temperature 3":
        - text: Temperature 3
        - switch "Use model default for Temperature"
        - text: Use model default
        - slider "Temperature slider"
        - spinbutton "Temperature" [invalid]: "3"
        - paragraph: Choose a value from 0 to 2.
      - group "Top P Model default":
        - text: Top P Model default
        - switch "Use model default for Top P" [checked]
        - text: Use model default
      - group "Top K Model default":
        - text: Top K Model default
        - switch "Use model default for Top K" [checked]
        - text: Use model default
      - group "Max output tokens Model default":
        - text: Max output tokens Model default
        - switch "Use model default for Max output tokens" [checked]
        - text: Use model default
      - group "Seed Model default":
        - text: Seed Model default
        - switch "Use model default for Seed" [checked]
        - text: Use model default
      - group: Every chat with this model
      - group "Context length":
        - text: Context length
        - paragraph: Applies to fake-chat in every chat.
        - spinbutton "Context length": "16384"
        - paragraph: "Configured limit: 16K tokens."
        - button "4K"
        - button "8K"
        - button "16K" [pressed]
      - status: Unsaved changes
      - button "Save settings" [disabled]
      - button "Reset to model defaults"
```

# Test source

```ts
  41  |     page,
  42  |     request,
  43  |     browserName,
  44  |   }) => {
  45  |     await setup(page, request, width);
  46  |     await open(page);
  47  |     const panel = controls(page);
  48  |     await expect(
  49  |       panel.getByRole("button", { name: "Save settings", exact: true }),
  50  |     ).toBeDisabled();
  51  |     await panel
  52  |       .getByRole("switch", { name: "Use model default for Temperature" })
  53  |       .click();
  54  |     await panel
  55  |       .getByRole("spinbutton", { name: "Temperature", exact: true })
  56  |       .fill(".65");
  57  |     await panel
  58  |       .getByRole("switch", { name: "Use default system prompt" })
  59  |       .click();
  60  |     await panel
  61  |       .getByRole("textbox", { name: "System prompt", exact: true })
  62  |       .fill("Synthetic preset instruction.");
  63  |     await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
  64  |     await page
  65  |       .getByRole("option", { name: "Save as preset…", exact: true })
  66  |       .click();
  67  |     const editor = page.getByRole("dialog", {
  68  |         name: "Save as preset",
  69  |         exact: true,
  70  |       }),
  71  |       name = `Synthetic ${width} ${browserName}`;
  72  |     await editor.getByRole("textbox", { name: "Preset name" }).fill(name);
  73  |     await editor
  74  |       .getByRole("button", { name: "Save preset", exact: true })
  75  |       .click();
  76  |     await expect(editor).not.toBeVisible();
  77  |     await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
  78  |     await page.getByRole("option", { name, exact: true }).click();
  79  |     await panel
  80  |       .getByRole("button", { name: "Save settings", exact: true })
  81  |       .click();
  82  |     await expect(
  83  |       panel.getByRole("button", { name: "Save settings", exact: true }),
  84  |     ).toContainText("Saved");
  85  |     await close(page);
  86  |     const question = `Synthetic preset request ${width} ${browserName}`;
  87  |     await page.locator(".composer textarea").fill(question);
  88  |     await page.getByRole("button", { name: "Send message" }).click();
  89  |     await expect(page).toHaveURL(/\/c\//);
  90  |     const id = page.url().split("/c/")[1];
  91  |     const detail = async () =>
  92  |       await (await request.get(`/api/chats/${id}`)).json();
  93  |     await expect
  94  |       .poll(async () => (await detail()).messages.at(-1).status)
  95  |       .toBe("complete");
  96  |     const captures = (
  97  |       await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  98  |     ).captures;
  99  |     const sent = captures.findLast(
  100 |       (r: { messages?: { content: string }[] }) =>
  101 |         r.messages?.at(-1)?.content === question,
  102 |     );
  103 |     expect(sent.options).toEqual({ temperature: 0.65, num_ctx: 16384 });
  104 |     expect(sent.messages[0].content).toContain("Synthetic preset instruction.");
  105 |     const before = (await detail()).chat;
  106 |     const preset = (await (await request.get("/api/presets")).json()).find(
  107 |       (p: { name: string }) => p.name === name,
  108 |     );
  109 |     await request.patch(`/api/presets/${preset.id}`, {
  110 |       data: {
  111 |         params: { top_k: 19 },
  112 |         system_prompt: "A different synthetic instruction.",
  113 |       },
  114 |     });
  115 |     expect((await detail()).chat).toEqual(before);
  116 |     await request.delete(`/api/presets/${preset.id}`);
  117 |     expect((await detail()).chat).toEqual(before);
  118 |   });
  119 |   test(`5A retained edits, validation and unified settings Save ${width}`, async ({
  120 |     page,
  121 |     request,
  122 |   }) => {
  123 |     await setup(page, request, width);
  124 |     await open(page);
  125 |     const panel = controls(page),
  126 |       save = panel.getByRole("button", { name: "Save settings", exact: true });
  127 |     await expect(save).toBeDisabled();
  128 |     await panel
  129 |       .getByRole("switch", { name: "Use model default for Temperature" })
  130 |       .click();
  131 |     await panel
  132 |       .getByRole("spinbutton", { name: "Temperature", exact: true })
  133 |       .fill("3");
  134 |     await expect(save).toBeDisabled();
  135 |     await expect(panel.getByText("Choose a value from 0 to 2.")).toBeVisible();
  136 |     await close(page);
  137 |     await expect(
  138 |       page
  139 |         .getByRole("button", { name: "Chat controls", exact: true })
  140 |         .locator(".bg-brand"),
> 141 |     ).toBeVisible();
      |       ^ Error: expect(locator).toBeVisible() failed
  142 |     await open(page);
  143 |     await expect(
  144 |       panel.getByRole("spinbutton", { name: "Temperature", exact: true }),
  145 |     ).toHaveValue("3");
  146 |     await panel
  147 |       .getByRole("spinbutton", { name: "Temperature", exact: true })
  148 |       .fill(".55");
  149 |     const chatPatches: string[] = [];
  150 |     page.on("request", (r) => {
  151 |       if (
  152 |         r.method() === "PATCH" &&
  153 |         new URL(r.url()).pathname.startsWith("/api/chats/")
  154 |       )
  155 |         chatPatches.push(r.url());
  156 |     });
  157 |     await panel
  158 |       .getByRole("spinbutton", { name: "Context length" })
  159 |       .fill("8192");
  160 |     await panel.getByRole("button", { name: "Save settings" }).click();
  161 |     await expect(
  162 |       panel.getByRole("button", { name: "Save settings" }),
  163 |     ).toBeDisabled();
  164 |     expect(chatPatches).toEqual([]); // New-chat sampling stays in the local draft until Send.
  165 |     const updatedModels = await (await request.get("/api/models")).json();
  166 |     expect(
  167 |       updatedModels.find(
  168 |         (m: { model_id: string }) => m.model_id === "fake-chat",
  169 |       ).context_length,
  170 |     ).toBe(8192);
  171 |     await expect(save).toBeDisabled();
  172 |     await expect(save).toContainText("Saved");
  173 |     await close(page);
  174 |     await expect(
  175 |       page
  176 |         .getByRole("button", { name: "Chat controls", exact: true })
  177 |         .locator(".bg-brand"),
  178 |     ).toHaveCount(0);
  179 |     await open(page);
  180 |     await expect(
  181 |       panel.getByRole("spinbutton", { name: "Temperature", exact: true }),
  182 |     ).toHaveValue("0.55");
  183 |     await expect(save).toBeDisabled();
  184 |     await close(page);
  185 |   });
  186 | }
  187 | test("5A default preset can be explicitly cleared before first send", async ({
  188 |   page,
  189 |   request,
  190 | }) => {
  191 |   const conn = await setup(page, request);
  192 |   const preset = await (
  193 |     await request.post("/api/presets", {
  194 |       data: {
  195 |         name: "Synthetic Default",
  196 |         params: { top_k: 31 },
  197 |         system_prompt: "Synthetic default prompt.",
  198 |       },
  199 |     })
  200 |   ).json();
  201 |   await request.patch("/api/settings", {
  202 |     data: { default_preset_id: preset.id },
  203 |   });
  204 |   await page.reload();
  205 |   await open(page);
  206 |   const panel = controls(page);
  207 |   await expect(
  208 |     panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  209 |   ).toHaveValue("31");
  210 |   await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
  211 |   await page.getByRole("option", { name: "None", exact: true }).click();
  212 |   await panel
  213 |     .getByRole("button", { name: "Save settings", exact: true })
  214 |     .click();
  215 |   await close(page);
  216 |   await page.locator(".composer textarea").fill("Synthetic explicit None");
  217 |   await page.getByRole("button", { name: "Send message" }).click();
  218 |   await expect(page).toHaveURL(/\/c\//);
  219 |   const chat = (
  220 |     await (await request.get("/api/chats/" + page.url().split("/c/")[1])).json()
  221 |   ).chat;
  222 |   expect(chat.params).toEqual({});
  223 |   expect(chat.system_prompt).toBeNull();
  224 |   expect(chat.connection_id).toBe(conn.id);
  225 |   await request.delete(`/api/presets/${preset.id}`);
  226 | });
  227 | test("5A model name dialog, dual-name picker search and reset", async ({
  228 |   page,
  229 |   request,
  230 | }) => {
  231 |   await setup(page, request);
  232 |   await page.keyboard.press("Control+,");
  233 |   const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  234 |   await settings.getByRole("button", { name: "Models", exact: true }).click();
  235 |   await settings
  236 |     .getByRole("button", { name: "Rename fake-chat", exact: true })
  237 |     .click();
  238 |   let editor = page.getByRole("dialog", { name: "Rename model", exact: true });
  239 |   await editor
  240 |     .getByRole("textbox", { name: "Display name for fake-chat", exact: true })
  241 |     .fill("Synthetic Display");
```