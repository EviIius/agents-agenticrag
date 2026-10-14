# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-images.spec.ts >> real paused worker progress, next frames, SSE reconnection and sibling retry
- Location: tests/chat-images.spec.ts:81:1

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  locator('[data-slot="image-turn"]').last().locator('img')
Expected: 3
Received: 0
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" locator('[data-slot="image-turn"]').last().locator('img') with timeout 5000ms
  - waiting for locator('[data-slot="image-turn"]').last().locator('img')
    14 × locator resolved to 0 elements
       - unexpected value "0"

```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - generic [ref=f1e3]:
    - complementary [ref=f1e4]:
      - generic [ref=f1e5]:
        - generic [ref=f1e6]:
          - button "Collapse sidebar" [ref=f1e7] [cursor=pointer]
          - generic [ref=f1e8]: Atelier
          - link "New chat" [ref=f1e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=f1e10]:
          - generic [ref=f1e11]:
            - textbox "Search history" [ref=f1e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=f1e13]:
            - link "Workflows" [ref=f1e15] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=f1e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=f1e27]:
            - generic [ref=f1e28]:
              - heading "Folders" [level=2] [ref=f1e29]
              - button "New folder" [ref=f1e30] [cursor=pointer]
            - paragraph [ref=f1e31]: No folders yet
          - generic [ref=f1e32]:
            - paragraph [ref=f1e33]: Today
            - generic [ref=f1e34]:
              - 'link "Synthetic paused lanterns #pause-step" [ref=f1e35] [cursor=pointer]':
                - /url: /c/8e2bc0e0c72045ad9a21d8b0ca36c7ad
              - 'button "Actions for Synthetic paused lanterns #pause-step" [ref=f1e36] [cursor=pointer]'
          - generic [ref=f1e38]:
            - 'link "Synthetic saved cobalt circle #slow" [ref=f1e39] [cursor=pointer]':
              - /url: /c/78f912f1e52d4ecb9832fff3e435fe68
            - 'button "Actions for Synthetic saved cobalt circle #slow" [ref=f1e40] [cursor=pointer]'
        - button "Settings" [ref=f1e43] [cursor=pointer]
    - main [ref=f1e44]:
      - generic [ref=f1e45]:
        - button "Choose model" [ref=f1e47] [cursor=pointer]:
          - generic [aria-hidden] [ref=f1e48]: ●
          - generic [ref=f1e49]: fake-chat
          - generic [ref=f1e50]: Fake runtime
        - generic "Double-click to rename" [ref=f1e51]: "Synthetic paused lanterns #pause-step"
        - button "Chat controls" [ref=f1e52] [cursor=pointer]
        - 'button "Actions for Synthetic paused lanterns #pause-step" [ref=f1e53] [cursor=pointer]'
      - status [ref=f1e54]
      - log "Conversation" [ref=f1e55]:
        - generic [ref=f1e56]:
          - article "user message" [ref=f1e57]:
            - heading "You said" [level=2] [ref=f1e58]
            - generic [ref=f1e59]:
              - paragraph [ref=f1e60]: Image · 3 images
              - paragraph [ref=f1e65]: "Synthetic paused lanterns #pause-step"
          - article "assistant message" [ref=f1e66]:
            - heading "Assistant replied" [level=2] [ref=f1e67]
            - generic [ref=f1e68]:
              - paragraph [ref=f1e69]: FLUX.2 klein 4B
              - generic [ref=f1e70]:
                - progressbar "Image denoising steps" [ref=f1e77]
                - generic [ref=f1e84]: Next
                - generic [ref=f1e88]: Next
              - status [ref=f1e92]:
                - generic [ref=f1e98]: Creating image 1 of 3 · step 3 of 4
              - generic [ref=f1e99]:
                - button "Cancel" [ref=f1e100] [cursor=pointer]
                - button "Copy prompt" [ref=f1e101] [cursor=pointer]:
                  - status [ref=f1e102]
                  - text: Copy prompt
      - generic [ref=f1e103]:
        - button [aria-hidden] [ref=f1e104] [cursor=pointer]
        - form "Message" [ref=f1e105]:
          - textbox "Image prompt" [ref=f1e106]:
            - /placeholder: Describe an image…
          - generic [ref=f1e107]:
            - button "Leave image mode" [pressed] [ref=f1e108] [cursor=pointer]:
              - generic [ref=f1e109]: Image
            - button "Image count" [ref=f1e110] [cursor=pointer]: 1 image
            - button "Image options" [ref=f1e111] [cursor=pointer]
            - generic [ref=f1e112]:
              - generic [ref=f1e113]: FLUX.2 klein 4B · 1024²
              - generic [ref=f1e114]:
                - button "Create image" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
  15  |   ).toBeEnabled();
  16  | }
  17  | 
  18  | test("saved image turn handles a lost response, automatic seeds, drafts, saving and reload", async ({
  19  |   page,
  20  | }) => {
  21  |   await page.goto("/");
  22  |   const text = page.locator(".composer textarea");
  23  |   await text.fill("Synthetic unsent text draft");
  24  |   await expect(
  25  |     page.getByRole("button", { name: "Create image", exact: true }),
  26  |   ).toBeEnabled();
  27  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  28  |   await prompt(page).fill("Synthetic saved cobalt circle #slow");
  29  |   const bodies: Record<string, unknown>[] = [];
  30  |   await page.route("**/api/chats/*/images", async (route) => {
  31  |     bodies.push(route.request().postDataJSON());
  32  |     if (bodies.length === 1) {
  33  |       await route.fetch();
  34  |       await route.abort("failed");
  35  |     } else await route.continue();
  36  |   });
  37  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  38  |   await expect(page.getByRole("alert")).toBeVisible();
  39  |   await expect(prompt(page)).toHaveValue("Synthetic saved cobalt circle #slow");
  40  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  41  |   await expect(page).toHaveURL(/\/c\//);
  42  |   expect(bodies).toHaveLength(2);
  43  |   expect(bodies[1]).toEqual(bodies[0]);
  44  |   expect(bodies[0].seeds).toHaveLength(1);
  45  |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(1);
  46  |   await expect(turn(page).locator("img")).toBeVisible();
  47  |   await turn(page)
  48  |     .getByRole("button", { name: "Save image", exact: true })
  49  |     .click();
  50  |   const save = page.getByRole("dialog", { name: "Save image", exact: true });
  51  |   await save
  52  |     .getByRole("button", { name: "Details (.json)", exact: true })
  53  |     .click();
  54  |   await expect(
  55  |     save.getByRole("button", { name: "Details (.json)", exact: true }),
  56  |   ).toHaveAttribute("aria-pressed", "true");
  57  |   let downloads = 0;
  58  |   page.on("download", () => downloads++);
  59  |   await save
  60  |     .getByRole("button", { name: "Close image save", exact: true })
  61  |     .click();
  62  |   expect(downloads).toBe(0);
  63  |   await page.getByRole("button", { name: "Leave image mode" }).click();
  64  |   await expect(text).toHaveValue("Synthetic unsent text draft");
  65  |   const id = await turn(page)
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
> 115 |   await expect(turn(page).locator("img")).toHaveCount(3);
      |                                           ^ Error: expect(locator).toHaveCount(expected) failed
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
  166 |   await expect(turn(page).getByRole("status")).toHaveText("Cancelled");
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
```