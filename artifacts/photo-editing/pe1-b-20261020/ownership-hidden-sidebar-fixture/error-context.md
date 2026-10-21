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
  - waiting for locator('a[href="/c/6406fdd026014328852461d6c77b31e0"]').first()
    - locator resolved to <a data-discover="true" href="/c/6406fdd026014328852461d6c77b31e0" class="min-w-0 flex-1 truncate px-3 py-2 text-sm" aria-label="Synthetic history for photo draft navigation">…</a>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
      - waiting 100ms
    82 × waiting for element to be visible, enabled and stable
       - element is not visible
     - retrying click action
       - waiting 500ms

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
            - generic:
              - button:
                - generic [aria-hidden]: ●
                - generic: fake-chat
          - button
        - generic:
          - heading [level=1]: Good morning
          - form:
            - textbox:
              - /placeholder: Message fake-chat…
            - generic:
              - generic:
                - button [aria-hidden]
                - button
              - button
              - generic:
                - generic:
                  - button [disabled]
          - generic:
            - button: Explain
            - button: Write
            - button: Code
            - button: Search the web
          - paragraph: Your models. Your Mac.
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Chat history" [level=2] [ref=e3]
    - paragraph [ref=e4]: Your saved conversations
    - generic [ref=e5]:
      - banner [ref=e6]:
        - button "Collapse sidebar" [active] [ref=e7] [cursor=pointer]
        - generic [ref=e8]: Aether
        - link "New chat" [ref=e9]:
          - /url: /
      - navigation "Chat history" [ref=e10]:
        - generic [ref=e11]:
          - textbox "Search history" [ref=e12]:
            - /placeholder: Search chats…
          - generic: ⌘K
        - navigation "Workspace" [ref=e13]:
          - link "Workflows" [ref=e15]:
            - /url: /workflows
          - link "Images" [ref=e21]:
            - /url: /images
        - region "Folders" [ref=e27]:
          - generic [ref=e28]:
            - heading "Folders" [level=2] [ref=e29]
            - button "New folder" [ref=e30] [cursor=pointer]
          - paragraph [ref=e31]: No folders yet
        - generic [ref=e32]:
          - paragraph [ref=e33]: Today
          - generic [ref=e34]:
            - link "Synthetic history for photo draft navigation" [ref=e35]:
              - /url: /c/6406fdd026014328852461d6c77b31e0
            - button "Actions for Synthetic history for photo draft navigation" [ref=e36] [cursor=pointer]
        - generic [ref=e38]:
          - link "Earlier synthetic edit" [ref=e39]:
            - /url: /c/e67ad9e6fd1d446c80517ff452f69fb2
          - button "Actions for Earlier synthetic edit" [ref=e40] [cursor=pointer]
        - generic [ref=e42]:
          - link "Synthetic history for photo draft navigation" [ref=e43]:
            - /url: /c/9fa0d4789b9c4bbbb7039b9010b3b792
          - button "Actions for Synthetic history for photo draft navigation" [ref=e44] [cursor=pointer]
        - generic [ref=e46]:
          - link "Earlier synthetic edit" [ref=e47]:
            - /url: /c/aa67f0cffc514b56b7e8fc1ae17a1cd3
          - button "Actions for Earlier synthetic edit" [ref=e48] [cursor=pointer]
      - contentinfo [ref=e50]:
        - button "Settings" [ref=e51] [cursor=pointer]
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
  175 |   // Only chats with history appear in the sidebar. Seed a real fake-runtime
  176 |   // message before using its navigation link; an empty chat has no such link.
  177 |   const seeded = await request.post(`/api/chats/${first.id}/messages`, {
  178 |     data: {
  179 |       content: "Synthetic history for photo draft navigation",
  180 |       web: false,
  181 |       attachment_ids: [],
  182 |     },
  183 |   });
  184 |   expect(seeded.status()).toBe(202);
  185 |   await page.goto(`/c/${first.id}`);
  186 |   await choose(page);
  187 |   await page
  188 |     .getByRole("textbox", { name: "Photo edit instruction" })
  189 |     .fill("Retained photo instruction");
  190 |   const newLink = page.getByRole("link", { name: "New chat", exact: true });
  191 |   if (!(await newLink.isVisible()))
  192 |     await page
  193 |       .getByRole("button", { name: "Open sidebar", exact: true })
  194 |       .click();
  195 |   await newLink.click();
  196 |   await expect(
  197 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  198 |   ).toHaveCount(0);
  199 |   // Sidebar links are real SPA navigation, so no draft store reload occurs.
  200 |   const firstLink = page.locator(`a[href="/c/${first.id}"]`).first();
  201 |   if (!(await firstLink.isVisible()))
  202 |     await page
  203 |       .getByRole("button", { name: "Open sidebar", exact: true })
  204 |       .click();
> 205 |   await firstLink.click();
      |                   ^ Error: locator.click: Test timeout of 45000ms exceeded.
  206 |   await expect(
  207 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  208 |   ).toHaveValue("Retained photo instruction");
  209 |   let release!: () => void;
  210 |   const gate = new Promise<void>((resolve) => {
  211 |     release = resolve;
  212 |   });
  213 |   await page.route("**/api/chats/*/image-references", async (route) => {
  214 |     await gate;
  215 |     await route.continue().catch(() => {});
  216 |   });
  217 |   const chooser = page.waitForEvent("filechooser");
  218 |   await page
  219 |     .getByRole("button", { name: "Replace photo", exact: true })
  220 |     .click();
  221 |   await (await chooser).setFiles(file);
  222 |   await page
  223 |     .getByRole("button", { name: "Cancel photo upload", exact: true })
  224 |     .click();
  225 |   release();
  226 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  227 |     "Choose one",
  228 |   );
  229 |   await expect(
  230 |     page.getByRole("button", { name: "Edit photo", exact: true }),
  231 |   ).toBeDisabled();
  232 |   await expect(
  233 |     page.getByRole("textbox", { name: "Photo edit instruction" }),
  234 |   ).toHaveValue("Retained photo instruction");
  235 | });
  236 | 
  237 | test("editing a generated output explicitly binds pixels; Refine keeps generation semantics", async ({
  238 |   page,
  239 | }) => {
  240 |   await ready(page);
  241 |   await page
  242 |     .getByRole("textbox", { name: "Photo edit instruction" })
  243 |     .fill("Synthetic first edit");
  244 |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  245 |   await expect(
  246 |     page.getByRole("button", { name: "Open image 1", exact: true }),
  247 |   ).toBeVisible();
  248 |   const copy = page.waitForResponse((r) =>
  249 |     r.url().endsWith("/image-references/from-job"),
  250 |   );
  251 |   await page
  252 |     .getByRole("button", { name: "More image actions", exact: true })
  253 |     .click();
  254 |   await page.getByRole("menuitem", { name: "Edit image", exact: true }).click();
  255 |   const result = await copy;
  256 |   expect(result.request().postDataJSON().source_job_id).toMatch(
  257 |     /^[a-f0-9]{32}$/,
  258 |   );
  259 |   await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
  260 |     "Ready",
  261 |   );
  262 |   await page.getByRole("button", { name: "Refine image", exact: true }).click();
  263 |   await expect(
  264 |     page.getByRole("textbox", { name: "Image prompt", exact: true }),
  265 |   ).toBeVisible();
  266 |   await expect(
  267 |     page.getByRole("button", { name: "Image count", exact: true }),
  268 |   ).toBeVisible();
  269 |   await expect(page.locator('[data-slot="photo-reference"]')).toHaveCount(0);
  270 | });
  271 | 
  272 | for (const width of [390, 1440])
  273 |   for (const theme of ["light", "dark"]) {
  274 |     test(`photo edit states, comparison, tokens and reduced motion ${width} ${theme}`, async ({
  275 |       page,
  276 |       browserName,
  277 |     }) => {
  278 |       await page.setViewportSize({ width, height: 1000 });
  279 |       await page.goto("/design?photo-edit");
  280 |       await page.getByRole("button", { name: theme, exact: true }).click();
  281 |       await mkdir(directory, { recursive: true });
  282 |       const reports = [];
  283 |       for (const state of photoStates) {
  284 |         await page
  285 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  286 |           .click();
  287 |         await settle(page);
  288 |         const violations = (
  289 |           await new AxeBuilder({ page }).analyze()
  290 |         ).violations.filter((v) =>
  291 |           ["serious", "critical"].includes(v.impact ?? ""),
  292 |         );
  293 |         reports.push({ state, violations });
  294 |         expect(violations).toEqual([]);
  295 |         expect(
  296 |           await page.evaluate(
  297 |             () => document.documentElement.scrollWidth <= innerWidth,
  298 |           ),
  299 |         ).toBe(true);
  300 |         await page.screenshot({
  301 |           path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
  302 |           fullPage: true,
  303 |         });
  304 |       }
  305 |       await page
```