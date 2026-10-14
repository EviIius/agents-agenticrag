# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-images.spec.ts >> image command, independent drafts, cancellation, removed outputs and failed load retry
- Location: tests/chat-images.spec.ts:148:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator: locator('[data-slot="image-turn"]').last().getByRole('status')
Expected: "Cancelled"
Error: strict mode violation: locator('[data-slot="image-turn"]').last().getByRole('status') resolved to 2 elements:
    1) <div role="status" class="mt-3 flex min-h-8 items-center gap-2 text-sm text-fg-2">…</div> aka getByRole('status').filter({ hasText: 'Waiting for your Mac · after' })
    2) <span role="status" class="sr-only" aria-live="polite"></span> aka getByRole('button', { name: 'Copy prompt' })

Call log:
  - Expect "toHaveText" locator('[data-slot="image-turn"]').last().getByRole('status') with timeout 5000ms
  - waiting for locator('[data-slot="image-turn"]').last().getByRole('status')

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - button "Collapse sidebar" [ref=e7] [cursor=pointer]
          - generic [ref=e8]: Atelier
          - link "New chat" [ref=e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=e10]:
          - generic [ref=e11]:
            - textbox "Search history" [ref=e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=e13]:
            - link "Workflows" [ref=e15] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e27]:
            - generic [ref=e28]:
              - heading "Folders" [level=2] [ref=e29]
              - button "New folder" [ref=e30] [cursor=pointer]
            - paragraph [ref=e31]: No folders yet
          - generic [ref=e32]:
            - paragraph [ref=e33]: Today
            - generic [ref=e34]:
              - 'link "Synthetic cancel circle #slow" [ref=e35] [cursor=pointer]':
                - /url: /c/6b6c2fcf6b554d2cb5d49eb902f60c5e
              - 'button "Actions for Synthetic cancel circle #slow" [ref=e36] [cursor=pointer]'
          - generic [ref=e38]:
            - 'link "Synthetic paused lanterns #pause-step" [ref=e39] [cursor=pointer]':
              - /url: /c/8e2bc0e0c72045ad9a21d8b0ca36c7ad
            - 'button "Actions for Synthetic paused lanterns #pause-step" [ref=e40] [cursor=pointer]'
          - generic [ref=e42]:
            - 'link "Synthetic saved cobalt circle #slow" [ref=e43] [cursor=pointer]':
              - /url: /c/78f912f1e52d4ecb9832fff3e435fe68
            - 'button "Actions for Synthetic saved cobalt circle #slow" [ref=e44] [cursor=pointer]'
        - button "Settings" [ref=e47] [cursor=pointer]
    - main [ref=e48]:
      - generic [ref=e49]:
        - button "Choose model" [ref=e51] [cursor=pointer]:
          - generic [aria-hidden] [ref=e52]: ●
          - generic [ref=e53]: fake-chat
          - generic [ref=e54]: Fake runtime
        - generic "Double-click to rename" [ref=e55]: "Synthetic cancel circle #slow"
        - button "Chat controls" [ref=e56] [cursor=pointer]
        - 'button "Actions for Synthetic cancel circle #slow" [ref=e57] [cursor=pointer]'
      - status [ref=e58]
      - log "Conversation" [ref=e59]:
        - generic [ref=e60]:
          - article "user message" [ref=e61]:
            - heading "You said" [level=2] [ref=e62]
            - generic [ref=e63]:
              - paragraph [ref=e64]: Image
              - paragraph [ref=e69]: "Synthetic cancel circle #slow"
          - article "assistant message" [ref=e70]:
            - heading "Assistant replied" [level=2] [ref=e71]
            - generic [ref=e72]:
              - paragraph [ref=e73]: FLUX.2 klein 4B
              - generic [ref=e77]:
                - generic [ref=e78]: Cancelled
                - button "Retry" [ref=e79] [cursor=pointer]
              - status [ref=e80]:
                - generic [ref=e81]: Cancelled
              - generic [ref=e82]:
                - button "Try again" [active] [ref=e83] [cursor=pointer]
                - button "Copy prompt" [ref=e84] [cursor=pointer]:
                  - status [ref=e85]
                  - text: Copy prompt
      - generic [ref=e86]:
        - button [aria-hidden] [ref=e87] [cursor=pointer]
        - form "Message" [ref=e88]:
          - textbox "Image prompt" [ref=e89]:
            - /placeholder: Describe an image…
          - generic [ref=e90]:
            - button "Leave image mode" [pressed] [ref=e91] [cursor=pointer]:
              - generic [ref=e92]: Image
            - button "Image count" [ref=e93] [cursor=pointer]: 1 image
            - button "Image options" [ref=e94] [cursor=pointer]
            - generic [ref=e95]:
              - generic [ref=e96]: FLUX.2 klein 4B · 1024²
              - generic [ref=e97]:
                - button "Create image" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
  66  |     .locator("[data-job-id]")
  67  |     .getAttribute("data-job-id");
  68  |   await page.reload();
  69  |   await expect(turn(page).locator("img")).toBeVisible();
  70  |   await expect(turn(page).locator("img")).not.toHaveAttribute(
  71  |     "data-reveal",
  72  |     "true",
  73  |   );
  74  |   await page.goto("/images");
  75  |   const gallery = page.locator(`[data-job-id="${id}"]`);
  76  |   await gallery.getByRole("link", { name: /^From / }).click();
  77  |   await expect(page).toHaveURL(/#m-/);
  78  |   await expect(turn(page)).toBeVisible();
  79  | });
  80  | 
  81  | test("real paused worker progress, next frames, SSE reconnection and sibling retry", async ({
  82  |   page,
  83  |   request,
  84  | }) => {
  85  |   await request.post("/tests/images/pause");
  86  |   await enter(page);
  87  |   await page.getByRole("button", { name: "Image count" }).click();
  88  |   await page.getByRole("menuitem", { name: "3 images", exact: true }).click();
  89  |   await prompt(page).fill("Synthetic paused lanterns #pause-step");
  90  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  91  |   await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
  92  |     "aria-valuenow",
  93  |     "2",
  94  |   );
  95  |   await expect(turn(page).getByText("Next", { exact: true })).toHaveCount(2);
  96  |   const jobIds = await turn(page)
  97  |     .locator("[data-job-id]")
  98  |     .evaluateAll((nodes) => nodes.map((n) => (n as HTMLElement).dataset.jobId));
  99  |   await page.waitForTimeout(900);
  100 |   await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
  101 |     "aria-valuenow",
  102 |     "2",
  103 |   );
  104 |   await page.reload();
  105 |   await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
  106 |     "aria-valuenow",
  107 |     "2",
  108 |   );
  109 |   const gets: string[] = [];
  110 |   page.on("request", (r) => {
  111 |     if (r.method() === "GET" && /\/images\/(jobs|events)/.test(r.url()))
  112 |       gets.push(r.url());
  113 |   });
  114 |   await request.post("/tests/images/release");
  115 |   await expect(turn(page).locator("img")).toHaveCount(3);
  116 |   await expect(turn(page).getByRole("status")).toContainText("3 images");
  117 |   await expect(
  118 |     turn(page).getByRole("button", { name: "Try again", exact: true }),
  119 |   ).toBeVisible();
  120 |   expect(gets.filter((url) => /\/images\/jobs[^/]*$/.test(url))).toHaveLength(
  121 |     0,
  122 |   );
  123 |   const old = await request
  124 |     .get(`/api/images/jobs/${jobIds[0]}`)
  125 |     .then((r) => r.json());
  126 |   await turn(page)
  127 |     .getByRole("button", { name: "Try again", exact: true })
  128 |     .click();
  129 |   await expect(
  130 |     turn(page).getByRole("button", { name: "Previous branch" }),
  131 |   ).toBeEnabled();
  132 |   await expect(turn(page).locator("img")).toHaveCount(3);
  133 |   const retryIds = await turn(page)
  134 |     .locator("[data-job-id]")
  135 |     .evaluateAll((nodes) => nodes.map((n) => (n as HTMLElement).dataset.jobId));
  136 |   expect(retryIds).not.toEqual(jobIds);
  137 |   const retried = await request
  138 |     .get(`/api/images/jobs/${retryIds[0]}`)
  139 |     .then((r) => r.json());
  140 |   expect(retried.seed).not.toBe(old.seed);
  141 |   await turn(page).getByRole("button", { name: "Previous branch" }).click();
  142 |   await expect(turn(page).locator("[data-job-id]").first()).toHaveAttribute(
  143 |     "data-job-id",
  144 |     jobIds[0]!,
  145 |   );
  146 | });
  147 | 
  148 | test("image command, independent drafts, cancellation, removed outputs and failed load retry", async ({
  149 |   page,
  150 |   request,
  151 | }) => {
  152 |   await page.goto("/");
  153 |   await expect(
  154 |     page.getByRole("button", { name: "Create image", exact: true }),
  155 |   ).toBeEnabled();
  156 |   await page
  157 |     .locator(".composer textarea")
  158 |     .fill("/image Synthetic cancel circle #slow");
  159 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  160 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  161 |   await page.locator(".composer textarea").fill("Synthetic separate text");
  162 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  163 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  164 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  165 |   await turn(page).getByRole("button", { name: "Cancel", exact: true }).click();
> 166 |   await expect(turn(page).getByRole("status")).toHaveText("Cancelled");
      |                                                ^ Error: expect(locator).toHaveText(expected) failed
  167 |   await turn(page)
  168 |     .getByRole("button", { name: "Try again", exact: true })
  169 |     .click();
  170 |   await expect(turn(page).locator("img")).toBeVisible();
  171 |   await page.route("**/api/images/jobs/*/output/png", (route) =>
  172 |     route.fulfill({ status: 404, body: "Synthetic load failure" }),
  173 |   );
  174 |   await page.reload();
  175 |   await expect(turn(page)).toContainText("Couldn't load the image");
  176 |   await page.unroute("**/api/images/jobs/*/output/png");
  177 |   await turn(page).getByRole("button", { name: "Retry", exact: true }).click();
  178 |   await expect(turn(page).locator("img.is-loaded")).toBeVisible();
  179 |   await turn(page).getByRole("button", { name: "More image actions" }).click();
  180 |   await page
  181 |     .getByRole("menuitem", { name: "Remove image", exact: true })
  182 |     .click();
  183 |   await page
  184 |     .getByRole("dialog")
  185 |     .getByRole("button", { name: "Remove", exact: true })
  186 |     .click();
  187 |   await expect(turn(page)).toContainText("Image removed");
  188 |   const chatId = new URL(page.url()).pathname.split("/").at(-1);
  189 |   await request.delete(`/api/chats/${chatId}`);
  190 |   await page.goto("/images");
  191 |   await expect(page.getByText("From a deleted chat").first()).toBeVisible();
  192 | });
  193 | 
  194 | for (const width of [390, 1440])
  195 |   for (const theme of ["light", "dark"])
  196 |     test(`chat image frame states, counts and axe ${width} ${theme}`, async ({
  197 |       page,
  198 |       browserName,
  199 |     }) => {
  200 |       await page.setViewportSize({ width, height: 900 });
  201 |       await page.goto("/design?chat-images");
  202 |       await page.getByRole("button", { name: theme, exact: true }).click();
  203 |       await mkdir(dir, { recursive: true });
  204 |       const results = [];
  205 |       for (const state of [
  206 |         "queued",
  207 |         "preparing",
  208 |         "step 0",
  209 |         "step 1",
  210 |         "step 2",
  211 |         "step 3",
  212 |         "step 4",
  213 |         "decoding",
  214 |         "complete",
  215 |         "cancelling",
  216 |         "cancelled",
  217 |         "failed",
  218 |         "interrupted",
  219 |         "removed",
  220 |       ]) {
  221 |         await page
  222 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  223 |           .click();
  224 |         for (const count of [1, 2, 3]) {
  225 |           await page
  226 |             .getByRole("button", {
  227 |               name: `Preview ${count} image${count > 1 ? "s" : ""}`,
  228 |               exact: true,
  229 |             })
  230 |             .click();
  231 |           await expect(page.locator(".image-frame")).toHaveCount(count);
  232 |         }
  233 |         await settle(page);
  234 |         expect(
  235 |           await page.evaluate(
  236 |             () => document.documentElement.scrollWidth <= innerWidth,
  237 |           ),
  238 |         ).toBe(true);
  239 |         const scan = await new AxeBuilder({ page }).analyze();
  240 |         const violations = scan.violations.filter((v) =>
  241 |           ["critical", "serious"].includes(v.impact ?? ""),
  242 |         );
  243 |         expect(violations).toEqual([]);
  244 |         results.push({ state, count: 3, violations });
  245 |         await page.screenshot({
  246 |           path: `${dir}/${state.replace(" ", "-")}-${width}-${theme}-${browserName}-fake.png`,
  247 |           fullPage: true,
  248 |         });
  249 |       }
  250 |       await writeFile(
  251 |         `${dir}/axe-${width}-${theme}-${browserName}.json`,
  252 |         JSON.stringify(results, null, 2),
  253 |       );
  254 |     });
  255 | 
  256 | for (const mode of ["always", "system"] as const)
  257 |   test(`image develop and progress motion respects ${mode}`, async ({
  258 |     page,
  259 |   }) => {
  260 |     await page.emulateMedia({
  261 |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  262 |     });
  263 |     await page.goto("/design?chat-images");
  264 |     if (mode === "always")
  265 |       await page.getByRole("button", { name: "Reduce motion" }).click();
  266 |     await expect(page.locator(".image-progress")).toHaveCount(2);
```