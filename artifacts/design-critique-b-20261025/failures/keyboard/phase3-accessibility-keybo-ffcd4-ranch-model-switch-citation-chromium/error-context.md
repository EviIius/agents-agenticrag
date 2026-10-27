# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: phase3-accessibility.spec.ts >> keyboard walkthrough send stop regenerate branch model switch citation
- Location: tests/phase3-accessibility.spec.ts:81:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('.meta').filter({ hasText: /stopped/i })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('.meta').filter({ hasText: /stopped/i }) with timeout 5000ms
  - waiting for locator('.meta').filter({ hasText: /stopped/i })

```

```yaml
- complementary:
  - button "Collapse sidebar"
  - text: Aether
  - link "New chat":
    - /url: /
  - navigation "Chat history":
    - textbox "Search history":
      - /placeholder: Search chats…
    - text: ⌘K
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
        - text: Workflows
        - img "A workflow is waiting for you"
      - link "Images":
        - /url: /images
    - region "Folders":
      - heading "Folders" [level=2]
      - button "New folder"
      - paragraph: No folders yet
    - paragraph: Today
    - 'link "#long:50 #slow:10"':
      - /url: /c/d8e26b61d6f649b986c7aeb013a43332
    - 'button "Actions for #long:50 #slow:10"'
    - link "Parameter payload 1440 chromium":
      - /url: /c/d18d8049b03c4ac3b85580fd5cce682f
    - button "Actions for Parameter payload 1440 chromium"
    - link "Parameter payload 390 chromium":
      - /url: /c/c383cd57f8b04c7b9916659e54c524de
    - button "Actions for Parameter payload 390 chromium"
    - link "Synthetic mobile request":
      - /url: /c/b3e51f8dccf641a2bfccb43819bd894e
    - button "Actions for Synthetic mobile request"
    - link "Context payload 1440 true chromium":
      - /url: /c/8be2ddf98c624651b4ff92b9fdc8c708
    - button "Actions for Context payload 1440 true chromium"
    - link "Context payload 1440 false chromium":
      - /url: /c/780946dcc1964952890f67e7362fbe37
    - button "Actions for Context payload 1440 false chromium"
    - link "Context payload 390 true chromium":
      - /url: /c/e8ffa4fb574345f9840896a64c06c832
    - button "Actions for Context payload 390 true chromium"
    - link "Context payload 390 false chromium":
      - /url: /c/00fd23fd8b6741f7b5676694df98f836
    - button "Actions for Context payload 390 false chromium"
    - link "#lib Synthetic empty scope":
      - /url: /c/1f7b5529f7f247378e8b73edd8423948
    - 'button "Actions for #lib Synthetic empty scope"'
    - link "#lib What does the invented handbook say?":
      - /url: /c/f4be8c196d5849cdac638ded14287629
    - 'button "Actions for #lib What does the invented handbook say?"'
    - link "#lib What does the invented handbook say?":
      - /url: /c/9e17d072985949ddb7b7ea1d6bab99a9
    - 'button "Actions for #lib What does the invented handbook say?"'
    - link "#lib What does the invented handbook say?":
      - /url: /c/b9aca9e450494f94bce23379c57f46e8
    - 'button "Actions for #lib What does the invented handbook say?"'
    - link "#lib What does the invented handbook say?":
      - /url: /c/0a838d217a984316ba3b0c2bbf9e2c43
    - 'button "Actions for #lib What does the invented handbook say?"'
    - 'link "Synthetic browser image #slow"':
      - /url: /c/a068b4130a5a4d14950574504a14e284
    - 'button "Actions for Synthetic browser image #slow"'
    - link "Synthetic mobile handoff request":
      - /url: /c/ae1654f580704e5a8dfc45bc77bb06b0
    - button "Actions for Synthetic mobile handoff request"
    - link "Who lost the 2021 NBA Finals? Show a table.":
      - /url: /c/33926244e8394b09a3a2e168b8482560
    - button "Actions for Who lost the 2021 NBA Finals? Show a table."
    - link "Synthetic handoff history 44":
      - /url: /c/ad0e454746354bdab66370e69be41057
    - button "Actions for Synthetic handoff history 44"
    - link "Synthetic handoff history 43":
      - /url: /c/8ebf362bca544a349c47f9ec07a34f53
    - button "Actions for Synthetic handoff history 43"
    - link "Synthetic handoff history 42":
      - /url: /c/3044444e18594cd6875d693a1a5d9d2e
    - button "Actions for Synthetic handoff history 42"
    - link "Synthetic handoff history 41":
      - /url: /c/96303c21f35541c2915f4e1bd93c8000
    - button "Actions for Synthetic handoff history 41"
    - link "Synthetic handoff history 40":
      - /url: /c/ee4d82cd088d4491ba54bfb151c9b614
    - button "Actions for Synthetic handoff history 40"
    - link "Synthetic handoff history 39":
      - /url: /c/2befd63ed14f45b893552dfc43ed673b
    - button "Actions for Synthetic handoff history 39"
    - link "Synthetic handoff history 38":
      - /url: /c/06aa793d47d14be988742bb08493faf2
    - button "Actions for Synthetic handoff history 38"
    - link "Synthetic handoff history 37":
      - /url: /c/675d2d481a9b4a39997978f6c0b450f1
    - button "Actions for Synthetic handoff history 37"
    - link "Synthetic handoff history 36":
      - /url: /c/13ba099a3bc94a288082b04e7ad83265
    - button "Actions for Synthetic handoff history 36"
    - link "Synthetic handoff history 35":
      - /url: /c/2ad88289e14c4e7280500ce84a8d3a41
    - button "Actions for Synthetic handoff history 35"
    - link "Synthetic handoff history 34":
      - /url: /c/d5c188cd41bb4358859ae0f83748dddc
    - button "Actions for Synthetic handoff history 34"
    - link "Synthetic handoff history 33":
      - /url: /c/8fa5a35daec7492baaeff1192d453e14
    - button "Actions for Synthetic handoff history 33"
    - link "Synthetic handoff history 32":
      - /url: /c/fb79e76fd1bd4c9db49da36a7729a8be
    - button "Actions for Synthetic handoff history 32"
    - link "Synthetic handoff history 31":
      - /url: /c/afc8ae6fbfe44a04ac06e3538e024fc0
    - button "Actions for Synthetic handoff history 31"
    - link "Synthetic handoff history 30":
      - /url: /c/c2228f9a3a414c49b9493150c9cf11e7
    - button "Actions for Synthetic handoff history 30"
    - link "Synthetic handoff history 29":
      - /url: /c/adfe5921d8404153ba6d74f9a54b9ce1
    - button "Actions for Synthetic handoff history 29"
    - link "Synthetic handoff history 28":
      - /url: /c/ac59a5a62b474122be42dbc86ab363c6
    - button "Actions for Synthetic handoff history 28"
    - link "Synthetic handoff history 27":
      - /url: /c/25f42367c2f1448faecb283d2514c0ec
    - button "Actions for Synthetic handoff history 27"
    - link "Synthetic handoff history 26":
      - /url: /c/03c61c644047477f92eb456081219835
    - button "Actions for Synthetic handoff history 26"
    - link "Synthetic handoff history 25":
      - /url: /c/9e18ba6eb7bc4d80ba3373afae54a16f
    - button "Actions for Synthetic handoff history 25"
    - link "Synthetic handoff history 24":
      - /url: /c/dfacb761042e4ae98346d4e307586da7
    - button "Actions for Synthetic handoff history 24"
    - link "Synthetic handoff history 23":
      - /url: /c/58eee34010934502a345d26baa9f43cd
    - button "Actions for Synthetic handoff history 23"
    - link "Synthetic handoff history 22":
      - /url: /c/ba1317d45d024ff2a27178bb414f7bcb
    - button "Actions for Synthetic handoff history 22"
    - link "Synthetic handoff history 21":
      - /url: /c/ab806e4820de42e88c75b984fdaa74fa
    - button "Actions for Synthetic handoff history 21"
    - link "Synthetic handoff history 20":
      - /url: /c/0ed50b529e5d43d8b4a144ea8165bced
    - button "Actions for Synthetic handoff history 20"
    - link "Synthetic handoff history 19":
      - /url: /c/a21f8669128848eda472591f038f50ff
    - button "Actions for Synthetic handoff history 19"
    - link "Synthetic handoff history 18":
      - /url: /c/c251aa17abaf452ba2cefab80c06b38e
    - button "Actions for Synthetic handoff history 18"
    - link "Synthetic handoff history 17":
      - /url: /c/b86a0bc7490f4f7daae289bcfc7524f3
    - button "Actions for Synthetic handoff history 17"
    - link "Synthetic handoff history 16":
      - /url: /c/bc87827ffb9f41d0bb801c13f896f80d
    - button "Actions for Synthetic handoff history 16"
    - link "Synthetic handoff history 15":
      - /url: /c/c65f7b4ea3154b9b82d366402cbc62e9
    - button "Actions for Synthetic handoff history 15"
    - link "Synthetic handoff history 14":
      - /url: /c/3be976abbe8449e29d601d44433a9095
    - button "Actions for Synthetic handoff history 14"
    - link "Synthetic handoff history 13":
      - /url: /c/7552773e9b3e44a7961759b4da26528f
    - button "Actions for Synthetic handoff history 13"
    - link "Synthetic handoff history 12":
      - /url: /c/94446fc335b042bbaa243e07bc81ae68
    - button "Actions for Synthetic handoff history 12"
    - link "Synthetic handoff history 11":
      - /url: /c/43592238d979479289337542f8ca9b72
    - button "Actions for Synthetic handoff history 11"
    - paragraph: Loading more chats…
  - button "Settings"
- main:
  - button "Choose model": fake-chat Fake runtime
  - text: "#long:50 #slow:10"
  - button "Chat controls"
  - 'button "Actions for #long:50 #slow:10"'
  - status: Response stopped
  - log "Conversation":
    - article "user message":
      - heading "You said" [level=2]
      - paragraph: "#long:50 #slow:10"
      - button "Copy message":
        - status
      - button "Edit message"
    - article "assistant message":
      - heading "fake-chat replied" [level=2]
      - paragraph: fake-chat
      - status
      - paragraph: token0 token1 token2
      - status: Stopped
      - button "Continue"
      - button "Retry"
      - button "Copy message":
        - status
      - button "Regenerate with another model"
      - button "Message info"
      - paragraph: fake-chat · ≈29.3 tok/s · 6 tokens · 0.0s to first token
  - form "Message":
    - textbox "Message fake-chat":
      - /placeholder: Message…
    - button "Attach files"
    - button "Tools"
    - img "17 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin"
    - button "Send message" [disabled]
- region "Notifications alt+T"
```

# Test source

```ts
  12  |       await page.addInitScript(
  13  |         (value) => localStorage.setItem("workbench-theme", value),
  14  |         theme,
  15  |       );
  16  |       await page.goto("/design");
  17  |       const region = page.getByRole("region", { name: "Phase 3 previews" });
  18  |       await expect(region).toBeVisible();
  19  |       await mkdir("../artifacts/phase-3", { recursive: true });
  20  |       const audit = async (name: string) => {
  21  |         await settle(page);
  22  |         await page.screenshot({
  23  |           animations: "disabled",
  24  |           path: `../artifacts/phase-3/${name}-${width}-${theme}-${test.info().project.name}-fake.png`,
  25  |         });
  26  |         await settle(page);
  27  |         expect(
  28  |           (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
  29  |             ["serious", "critical"].includes(v.impact ?? ""),
  30  |           ),
  31  |         ).toEqual([]);
  32  |       };
  33  |       for (const state of ["ready", "empty", "loading", "error"]) {
  34  |         await region
  35  |           .getByRole("button", {
  36  |             name: `Preview palette ${state}`,
  37  |             exact: true,
  38  |           })
  39  |           .click();
  40  |         await expect(
  41  |           page.getByRole("dialog", { name: "Command palette" }),
  42  |         ).toBeVisible();
  43  |         if (state === "empty")
  44  |           await expect(
  45  |             page.getByText("No chats or actions found"),
  46  |           ).toBeVisible();
  47  |         await audit(`palette-${state}`);
  48  |         await page.keyboard.press("Escape");
  49  |       }
  50  |       for (const state of [
  51  |         "ready",
  52  |         "loading",
  53  |         "missing",
  54  |         "status-error",
  55  |         "importing",
  56  |         "failed",
  57  |       ]) {
  58  |         await region
  59  |           .getByRole("button", { name: `Import preview ${state}`, exact: true })
  60  |           .click();
  61  |         if (["ready", "importing", "failed"].includes(state)) {
  62  |           await region
  63  |             .getByRole("button", { name: "Import old chats", exact: true })
  64  |             .click();
  65  |           await expect(
  66  |             page.getByRole("alertdialog", { name: "Import old chats?" }),
  67  |           ).toBeVisible();
  68  |           await audit(`legacy-import-${state}`);
  69  |           await page.keyboard.press("Escape");
  70  |         } else await audit(`legacy-import-${state}`);
  71  |       }
  72  |       await region
  73  |         .getByRole("button", { name: "Preview app update", exact: true })
  74  |         .click();
  75  |       await expect(
  76  |         page.getByRole("button", { name: "Reload", exact: true }),
  77  |       ).toBeVisible();
  78  |       await audit("update-toast");
  79  |     });
  80  |   }
  81  | test("keyboard walkthrough send stop regenerate branch model switch citation", async ({
  82  |   page,
  83  |   request,
  84  | }) => {
  85  |   await request.patch("/api/settings", {
  86  |     data: {
  87  |       default_model_id: "fake-chat",
  88  |       "web.default_on": false,
  89  |       "transcription.block_web": true,
  90  |     },
  91  |   });
  92  |   await page.goto("/");
  93  |   const composer = page.locator(".composer textarea");
  94  |   await expect(
  95  |     page.getByRole("button", { name: "Choose model" }),
  96  |   ).toContainText("fake-chat");
  97  |   await composer.focus();
  98  |   await composer.fill("#long:50 #slow:10");
  99  |   await page.keyboard.press("Control+Enter");
  100 |   await expect(
  101 |     page.getByRole("button", { name: "Stop generating" }),
  102 |   ).toBeVisible();
  103 |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  104 |   await composer.focus();
  105 |   await page.keyboard.press("Escape");
  106 |   await expect(
  107 |     page.getByRole("button", { name: "Stop generating" }),
  108 |   ).toHaveCount(0);
  109 |   await expect(composer).toBeFocused();
  110 |   await expect(
  111 |     page.locator(".meta").filter({ hasText: /stopped/i }),
> 112 |   ).toBeVisible();
      |     ^ Error: expect(locator).toBeVisible() failed
  113 |   await page
  114 |     .getByRole("button", { name: "Regenerate answer", exact: true })
  115 |     .last()
  116 |     .focus();
  117 |   await page.keyboard.press("Enter");
  118 |   await expect(page.getByText(/token49/)).toBeVisible({ timeout: 15000 });
  119 |   await expect(
  120 |     page.getByRole("button", { name: "Stop generating" }),
  121 |   ).toHaveCount(0);
  122 |   await page
  123 |     .getByRole("button", { name: "Previous branch", exact: true })
  124 |     .last()
  125 |     .focus();
  126 |   await page.keyboard.press("Enter");
  127 |   await expect(
  128 |     page.getByRole("button", { name: "Next branch", exact: true }).last(),
  129 |   ).toBeEnabled();
  130 |   await page
  131 |     .getByRole("button", { name: "Next branch", exact: true })
  132 |     .last()
  133 |     .focus();
  134 |   await page.keyboard.press("Enter");
  135 |   await page.keyboard.press("Control+k");
  136 |   const dialog = page.getByRole("dialog", { name: "Command palette" });
  137 |   await dialog.getByRole("combobox").fill("switch model");
  138 |   await expect(
  139 |     dialog.getByRole("option", { name: "Switch model…", exact: true }),
  140 |   ).toHaveAttribute("data-selected", "true");
  141 |   await page.keyboard.press("Enter");
  142 |   await page
  143 |     .getByRole("combobox", { name: "Search models" })
  144 |     .fill("fake-reasoning");
  145 |   const model = page.getByRole("gridcell", { name: /fake-reasoning/ });
  146 |   await expect(model).toHaveAttribute("data-selected", "true");
  147 |   await page.keyboard.press("Enter");
  148 |   await expect(
  149 |     page.getByRole("button", { name: "Choose model" }),
  150 |   ).toContainText("fake-reasoning");
  151 |   await page.keyboard.press("Escape");
  152 |   await page.keyboard.press("Control+Shift+o");
  153 |   await expect(page).toHaveURL("http://127.0.0.1:5173/");
  154 |   await expect(page.getByRole("heading", { name: /Good / })).toBeVisible();
  155 |   await settle(page);
  156 |   const toggle = await webTool(page);
  157 |   await expect(toggle).toBeVisible();
  158 |   await toggle.focus();
  159 |   await expect(toggle).toBeFocused();
  160 |   await page.keyboard.press("Enter");
  161 |   await expect(await webTool(page)).toHaveAttribute("aria-checked", "true");
  162 |   await composer.focus();
  163 |   await composer.fill("Who lost the 2021 NBA Finals? Show a table.");
  164 |   await page.keyboard.press("Control+Enter");
  165 |   await expect(
  166 |     page.getByText("Synthetic web answer", { exact: false }),
  167 |   ).toBeVisible();
  168 |   await expect(
  169 |     page.getByRole("button", { name: "Stop generating" }),
  170 |   ).toHaveCount(0);
  171 |   const pill = page
  172 |     .getByRole("button", { name: /View source: Synthetic NBA Finals/ })
  173 |     .first();
  174 |   await pill.focus();
  175 |   await page.keyboard.press("Enter");
  176 |   await expect(
  177 |     page.getByRole("dialog", { name: "Citation sources" }),
  178 |   ).toBeVisible();
  179 |   await expect(
  180 |     page.getByRole("button", { name: "Close citation", exact: true }),
  181 |   ).toBeFocused();
  182 |   await page.keyboard.press("Escape");
  183 |   await expect(
  184 |     page.getByRole("dialog", { name: "Citation sources" }),
  185 |   ).not.toBeVisible();
  186 |   await expect(pill).toBeFocused();
  187 |   await mkdir("../artifacts/phase-3", { recursive: true });
  188 |   await writeFile(
  189 |     `../artifacts/phase-3/keyboard-${test.info().project.name}.json`,
  190 |     JSON.stringify(
  191 |       {
  192 |         method:
  193 |           "automated keyboard activation, focused controls; no mouse click",
  194 |         send: true,
  195 |         stop_focus: true,
  196 |         regenerate: true,
  197 |         branch: true,
  198 |         model_switch: true,
  199 |         citation: true,
  200 |         citation_focus_restored: true,
  201 |       },
  202 |       null,
  203 |       2,
  204 |     ),
  205 |   );
  206 | });
  207 | 
  208 | test("Escape stops a send before the run response arrives", async ({
  209 |   page,
  210 |   request,
  211 | }) => {
  212 |   await request.patch("/api/settings", {
```