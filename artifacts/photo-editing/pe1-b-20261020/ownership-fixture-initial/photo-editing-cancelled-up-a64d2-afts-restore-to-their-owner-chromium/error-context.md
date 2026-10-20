# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: photo-editing.spec.ts >> cancelled uploads cannot return into another chat; completed drafts restore to their owner
- Location: tests/photo-editing.spec.ts:165:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Open sidebar', exact: true })

```

# Page snapshot

```yaml
- generic [ref=f2e2]:
  - generic [ref=f2e3]:
    - complementary [ref=f2e4]:
      - generic [ref=f2e5]:
        - generic [ref=f2e6]:
          - button "Collapse sidebar" [ref=f2e7] [cursor=pointer]
          - generic [ref=f2e8]: Aether
          - link "New chat" [active] [ref=f2e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=f2e10]:
          - generic [ref=f2e11]:
            - textbox "Search history" [ref=f2e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=f2e13]:
            - link "Workflows" [ref=f2e15] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=f2e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=f2e27]:
            - generic [ref=f2e28]:
              - heading "Folders" [level=2] [ref=f2e29]
              - button "New folder" [ref=f2e30] [cursor=pointer]
            - paragraph [ref=f2e31]: No folders yet
          - generic [ref=f2e32]:
            - paragraph [ref=f2e33]: Today
            - generic [ref=f2e34]:
              - link "Earlier synthetic edit" [ref=f2e35] [cursor=pointer]:
                - /url: /c/7b10ba964f9743c3bf360b5300fe1b8e
              - button "Actions for Earlier synthetic edit" [ref=f2e36] [cursor=pointer]
        - button "Settings" [ref=f2e39] [cursor=pointer]
    - main [ref=f2e40]:
      - generic [ref=f2e41]:
        - button "Choose model" [ref=f2e43] [cursor=pointer]:
          - generic [aria-hidden] [ref=f2e44]: ●
          - generic [ref=f2e45]: fake-chat
          - generic [ref=f2e46]: Fake runtime
        - button "Chat controls" [ref=f2e47] [cursor=pointer]
      - generic [ref=f2e48]:
        - heading "Good morning" [level=1] [ref=f2e49]
        - form "Message" [ref=f2e50]:
          - textbox "Message fake-chat" [ref=f2e51]:
            - /placeholder: Message fake-chat…
          - generic [ref=f2e52]:
            - generic "Attach files · ⌘U" [ref=f2e53]:
              - button "Attach files" [ref=f2e54] [cursor=pointer]
            - button "Tools" [ref=f2e55] [cursor=pointer]
            - generic [ref=f2e57]:
              - img "0 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=f2e58]
              - generic [ref=f2e62]:
                - button "Send message" [disabled]
        - generic [ref=f2e63]:
          - button "Explain" [ref=f2e64] [cursor=pointer]
          - button "Write" [ref=f2e65] [cursor=pointer]
          - button "Code" [ref=f2e66] [cursor=pointer]
          - button "Search the web" [ref=f2e67] [cursor=pointer]
        - paragraph [ref=f2e68]: Your models. Your Mac.
  - region "Notifications alt+T"
```

# Test source

```ts
  105 |     .getByRole("button", { name: "Remove files", exact: true })
  106 |     .click();
  107 |   await page.goto(chat);
  108 |   await expect(
  109 |     page.getByRole("button", { name: "Try again", exact: true }),
  110 |   ).toBeDisabled();
  111 |   await expect(
  112 |     page.getByRole("button", { name: "Open image 1", exact: true }),
  113 |   ).toBeVisible();
  114 | });
  115 | 
  116 | test("new typing survives an in-flight photo send and the new chat adoption", async ({
  117 |   page,
  118 | }) => {
  119 |   await ready(page);
  120 |   const instruction = page.getByRole("textbox", {
  121 |     name: "Photo edit instruction",
  122 |   });
  123 |   await instruction.fill("Earlier synthetic edit");
  124 |   let release!: () => void;
  125 |   const gate = new Promise<void>((resolve) => {
  126 |     release = resolve;
  127 |   });
  128 |   await page.route("**/api/chats/*/images", async (route) => {
  129 |     await gate;
  130 |     await route.continue();
  131 |   });
  132 |   const response = page.waitForResponse(
  133 |     (r) => r.url().endsWith("/images") && r.request().method() === "POST",
  134 |   );
  135 |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  136 |   await instruction.fill("Newer synthetic edit draft");
  137 |   let releasePhoto!: () => void;
  138 |   const photoGate = new Promise<void>((resolve) => {
  139 |     releasePhoto = resolve;
  140 |   });
  141 |   await page.route("**/api/chats/*/image-references", async (route) => {
  142 |     await photoGate;
  143 |     await route.continue();
  144 |   });
  145 |   const replacement = page.waitForEvent("filechooser");
  146 |   await page
  147 |     .getByRole("button", { name: "Replace photo", exact: true })
  148 |     .click();
  149 |   await (await replacement).setFiles(file);
  150 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  151 |     "Preparing photo",
  152 |   );
  153 |   release();
  154 |   expect((await response).request().postDataJSON().prompt).toBe(
  155 |     "Earlier synthetic edit",
  156 |   );
  157 |   await expect(page).toHaveURL(/\/c\//);
  158 |   await expect(instruction).toHaveValue("Newer synthetic edit draft");
  159 |   releasePhoto();
  160 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  161 |     "Ready",
  162 |   );
  163 | });
  164 | 
  165 | test("cancelled uploads cannot return into another chat; completed drafts restore to their owner", async ({
  166 |   page,
  167 |   request,
  168 | }) => {
  169 |   const connection = (await (await request.get("/api/connections")).json())[0];
  170 |   const first = await (
  171 |     await request.post("/api/chats", {
  172 |       data: { connection_id: connection.id, model_id: "fake-chat" },
  173 |     })
  174 |   ).json();
  175 |   const other = await (
  176 |     await request.post("/api/chats", {
  177 |       data: { connection_id: connection.id, model_id: "fake-chat" },
  178 |     })
  179 |   ).json();
  180 |   await page.goto(`/c/${first.id}`);
  181 |   await choose(page);
  182 |   await page
  183 |     .getByRole("textbox", { name: "Photo edit instruction" })
  184 |     .fill("Owner's synthetic instruction");
  185 |   await page.goto(`/c/${other.id}`);
  186 |   await expect(
  187 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  188 |   ).toHaveCount(0);
  189 |   await page.goto(`/c/${first.id}`);
  190 |   // Full document navigation intentionally discards in-memory unsent drafts.
  191 |   // Use the real app links below to verify route switching preserves them.
  192 |   await choose(page);
  193 |   await page
  194 |     .getByRole("textbox", { name: "Photo edit instruction" })
  195 |     .fill("Retained photo instruction");
  196 |   await page.getByRole("link", { name: "New chat", exact: true }).click();
  197 |   await expect(
  198 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  199 |   ).toHaveCount(0);
  200 |   // Sidebar links are real SPA navigation, so no draft store reload occurs.
  201 |   const firstLink = page.locator(`a[href="/c/${first.id}"]`).first();
  202 |   if (!(await firstLink.isVisible()))
  203 |     await page
  204 |       .getByRole("button", { name: "Open sidebar", exact: true })
> 205 |       .click();
      |        ^ Error: locator.click: Test timeout of 45000ms exceeded.
  206 |   await firstLink.click();
  207 |   await expect(
  208 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  209 |   ).toHaveValue("Retained photo instruction");
  210 |   let release!: () => void;
  211 |   const gate = new Promise<void>((resolve) => {
  212 |     release = resolve;
  213 |   });
  214 |   await page.route("**/api/chats/*/image-references", async (route) => {
  215 |     await gate;
  216 |     await route.continue().catch(() => {});
  217 |   });
  218 |   const chooser = page.waitForEvent("filechooser");
  219 |   await page
  220 |     .getByRole("button", { name: "Replace photo", exact: true })
  221 |     .click();
  222 |   await (await chooser).setFiles(file);
  223 |   await page
  224 |     .getByRole("button", { name: "Cancel photo upload", exact: true })
  225 |     .click();
  226 |   release();
  227 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  228 |     "Choose one",
  229 |   );
  230 |   await expect(
  231 |     page.getByRole("button", { name: "Edit photo", exact: true }),
  232 |   ).toBeDisabled();
  233 |   await expect(
  234 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  235 |   ).toHaveValue("Retained photo instruction");
  236 | });
  237 | 
  238 | test("editing a generated output explicitly binds pixels; Refine keeps generation semantics", async ({
  239 |   page,
  240 | }) => {
  241 |   await ready(page);
  242 |   await page
  243 |     .getByRole("textbox", { name: "Photo edit instruction" })
  244 |     .fill("Synthetic first edit");
  245 |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  246 |   await expect(
  247 |     page.getByRole("button", { name: "Open image 1", exact: true }),
  248 |   ).toBeVisible();
  249 |   const copy = page.waitForResponse((r) =>
  250 |     r.url().endsWith("/image-references/from-job"),
  251 |   );
  252 |   await page
  253 |     .getByRole("button", { name: "More image actions", exact: true })
  254 |     .click();
  255 |   await page.getByRole("menuitem", { name: "Edit image", exact: true }).click();
  256 |   const result = await copy;
  257 |   expect(result.request().postDataJSON().source_job_id).toMatch(
  258 |     /^[a-f0-9]{32}$/,
  259 |   );
  260 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  261 |     "Ready",
  262 |   );
  263 |   await page.getByRole("button", { name: "Refine image", exact: true }).click();
  264 |   await expect(
  265 |     page.getByRole("textbox", { name: "Image prompt", exact: true }),
  266 |   ).toBeVisible();
  267 |   await expect(
  268 |     page.getByRole("button", { name: "Image count", exact: true }),
  269 |   ).toBeVisible();
  270 |   await expect(page.locator('[data-slot="photo-reference"]')).toHaveCount(0);
  271 | });
  272 | 
  273 | for (const width of [390, 1440])
  274 |   for (const theme of ["light", "dark"]) {
  275 |     test(`photo edit states, comparison, tokens and reduced motion ${width} ${theme}`, async ({
  276 |       page,
  277 |       browserName,
  278 |     }) => {
  279 |       await page.setViewportSize({ width, height: 1000 });
  280 |       await page.goto("/design?photo-edit");
  281 |       await page.getByRole("button", { name: theme, exact: true }).click();
  282 |       await mkdir(directory, { recursive: true });
  283 |       const reports = [];
  284 |       for (const state of photoStates) {
  285 |         await page
  286 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  287 |           .click();
  288 |         await settle(page);
  289 |         const violations = (
  290 |           await new AxeBuilder({ page }).analyze()
  291 |         ).violations.filter((v) =>
  292 |           ["serious", "critical"].includes(v.impact ?? ""),
  293 |         );
  294 |         reports.push({ state, violations });
  295 |         expect(violations).toEqual([]);
  296 |         expect(
  297 |           await page.evaluate(
  298 |             () => document.documentElement.scrollWidth <= innerWidth,
  299 |           ),
  300 |         ).toBe(true);
  301 |         await page.screenshot({
  302 |           path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
  303 |           fullPage: true,
  304 |         });
  305 |       }
```