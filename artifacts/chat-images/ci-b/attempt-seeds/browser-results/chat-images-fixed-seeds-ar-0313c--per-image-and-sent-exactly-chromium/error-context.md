# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-images.spec.ts >> fixed seeds are optional, validated per image and sent exactly
- Location: tests/chat-images.spec.ts:217:1

# Error details

```
Error: expect(locator).toBeDisabled() failed

Locator: getByRole('button', { name: 'Create image', exact: true })
Expected: disabled
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeDisabled" getByRole('button', { name: 'Create image', exact: true }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Create image', exact: true })

```

```yaml
- region "Notifications alt+T"
- menu "Image options":
  - paragraph: Seed · Fixed
  - paragraph: Leave every field empty for a new result. To repeat an image, set one seed for each image.
  - text: Seed 1
  - textbox "Seed 1":
    - /placeholder: Automatic
    - text: "4294967296"
  - text: Seed 2
  - textbox "Seed 2":
    - /placeholder: Automatic
  - alert: Use 0–4,294,967,295 for every image, or leave all seeds empty.
```

# Test source

```ts
  131 |   page.on("request", (r) => {
  132 |     if (r.method() === "GET" && /\/images\/(jobs|events)/.test(r.url()))
  133 |       gets.push(r.url());
  134 |   });
  135 |   await request.post(`${fakeAppURL}/tests/images/release`);
  136 |   await expect(turn(page).locator("img")).toHaveCount(3);
  137 |   await expect(turn(page).locator("div[role=status]")).toContainText(
  138 |     "3 images",
  139 |   );
  140 |   await expect(
  141 |     turn(page).getByRole("button", { name: "Try again", exact: true }),
  142 |   ).toBeVisible();
  143 |   expect(gets.filter((url) => /\/images\/jobs[^/]*$/.test(url))).toHaveLength(
  144 |     0,
  145 |   );
  146 |   const old = await request
  147 |     .get(`/api/images/jobs/${jobIds[0]}`)
  148 |     .then((r) => r.json());
  149 |   await turn(page)
  150 |     .getByRole("button", { name: "Try again", exact: true })
  151 |     .click();
  152 |   await expect(
  153 |     turn(page).getByRole("button", { name: "Previous branch" }),
  154 |   ).toBeEnabled();
  155 |   await expect(turn(page).locator("img")).toHaveCount(3);
  156 |   const retryIds = await turn(page)
  157 |     .locator("[data-job-id]")
  158 |     .evaluateAll((nodes) => nodes.map((n) => (n as HTMLElement).dataset.jobId));
  159 |   expect(retryIds).not.toEqual(jobIds);
  160 |   const retried = await request
  161 |     .get(`/api/images/jobs/${retryIds[0]}`)
  162 |     .then((r) => r.json());
  163 |   expect(retried.seed).not.toBe(old.seed);
  164 |   await turn(page).getByRole("button", { name: "Previous branch" }).click();
  165 |   await expect(turn(page).locator("[data-job-id]").first()).toHaveAttribute(
  166 |     "data-job-id",
  167 |     jobIds[0]!,
  168 |   );
  169 | });
  170 | 
  171 | test("image command, independent drafts, cancellation, removed outputs and failed load retry", async ({
  172 |   page,
  173 |   request,
  174 | }) => {
  175 |   await page.goto("/");
  176 |   await expect(
  177 |     page.getByRole("button", { name: "Create image", exact: true }),
  178 |   ).toBeEnabled();
  179 |   await page
  180 |     .locator(".composer textarea")
  181 |     .fill("/image Synthetic cancel circle #slow");
  182 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  183 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  184 |   await page.locator(".composer textarea").fill("Synthetic separate text");
  185 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  186 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  187 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  188 |   await turn(page).getByRole("button", { name: "Cancel", exact: true }).click();
  189 |   await expect(turn(page).locator("div[role=status]")).toHaveText("Cancelled");
  190 |   await turn(page)
  191 |     .getByRole("button", { name: "Try again", exact: true })
  192 |     .click();
  193 |   await expect(turn(page).locator("img")).toBeVisible();
  194 |   await page.route("**/api/images/jobs/*/output/png", (route) =>
  195 |     route.fulfill({ status: 404, body: "Synthetic load failure" }),
  196 |   );
  197 |   await page.reload();
  198 |   await expect(turn(page)).toContainText("Couldn't load the image");
  199 |   await page.unroute("**/api/images/jobs/*/output/png");
  200 |   await turn(page).getByRole("button", { name: "Retry", exact: true }).click();
  201 |   await expect(turn(page).locator("img.is-loaded")).toBeVisible();
  202 |   await turn(page).getByRole("button", { name: "More image actions" }).click();
  203 |   await page
  204 |     .getByRole("menuitem", { name: "Remove image", exact: true })
  205 |     .click();
  206 |   await page
  207 |     .getByRole("dialog")
  208 |     .getByRole("button", { name: "Remove", exact: true })
  209 |     .click();
  210 |   await expect(turn(page)).toContainText("Image removed");
  211 |   const chatId = new URL(page.url()).pathname.split("/").at(-1);
  212 |   await request.delete(`/api/chats/${chatId}`);
  213 |   await page.goto("/images");
  214 |   await expect(page.getByText("From a deleted chat").first()).toBeVisible();
  215 | });
  216 | 
  217 | test("fixed seeds are optional, validated per image and sent exactly", async ({
  218 |   page,
  219 | }) => {
  220 |   await enter(page);
  221 |   await prompt(page).fill("Synthetic fixed-seed circles");
  222 |   await page.getByRole("button", { name: "Image count" }).click();
  223 |   await page.getByRole("menuitem", { name: "2 images", exact: true }).click();
  224 |   await page.getByRole("button", { name: "Image options" }).click();
  225 |   await page
  226 |     .getByRole("textbox", { name: "Seed 1", exact: true })
  227 |     .fill("4294967296");
  228 |   await expect(page.getByRole("alert")).toContainText("4,294,967,295");
  229 |   await expect(
  230 |     page.getByRole("button", { name: "Create image", exact: true }),
> 231 |   ).toBeDisabled();
      |     ^ Error: expect(locator).toBeDisabled() failed
  232 |   await page.getByRole("textbox", { name: "Seed 1", exact: true }).fill("1337");
  233 |   await page.getByRole("textbox", { name: "Seed 2", exact: true }).fill("42");
  234 |   await page.keyboard.press("Escape");
  235 |   await expect(prompt(page)).toBeFocused();
  236 |   const accepted = page.waitForRequest(
  237 |     (r) =>
  238 |       r.method() === "POST" &&
  239 |       /\/api\/chats\/[^/]+\/images$/.test(new URL(r.url()).pathname),
  240 |   );
  241 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  242 |   expect((await accepted).postDataJSON().seeds).toEqual([1337, 42]);
  243 |   await expect(turn(page).locator("img")).toHaveCount(2);
  244 | });
  245 | 
  246 | for (const width of [390, 1440])
  247 |   for (const theme of ["light", "dark"])
  248 |     test(`chat image frame states, counts and axe ${width} ${theme}`, async ({
  249 |       page,
  250 |       browserName,
  251 |     }) => {
  252 |       await page.setViewportSize({ width, height: 900 });
  253 |       await page.goto("/design?chat-images");
  254 |       await page.getByRole("button", { name: theme, exact: true }).click();
  255 |       await mkdir(dir, { recursive: true });
  256 |       const results = [];
  257 |       for (const state of [
  258 |         "queued",
  259 |         "preparing",
  260 |         "step 0",
  261 |         "step 1",
  262 |         "step 2",
  263 |         "step 3",
  264 |         "step 4",
  265 |         "decoding",
  266 |         "complete",
  267 |         "cancelling",
  268 |         "cancelled",
  269 |         "failed",
  270 |         "interrupted",
  271 |         "removed",
  272 |       ]) {
  273 |         await page
  274 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  275 |           .click();
  276 |         for (const count of [1, 2, 3]) {
  277 |           await page
  278 |             .getByRole("button", {
  279 |               name: `Preview ${count} image${count > 1 ? "s" : ""}`,
  280 |               exact: true,
  281 |             })
  282 |             .click();
  283 |           await expect(page.locator(".image-frame")).toHaveCount(count);
  284 |         }
  285 |         await settle(page);
  286 |         expect(
  287 |           await page.evaluate(
  288 |             () => document.documentElement.scrollWidth <= innerWidth,
  289 |           ),
  290 |         ).toBe(true);
  291 |         const scan = await new AxeBuilder({ page }).analyze();
  292 |         const violations = scan.violations.filter((v) =>
  293 |           ["critical", "serious"].includes(v.impact ?? ""),
  294 |         );
  295 |         expect(violations).toEqual([]);
  296 |         results.push({ state, count: 3, violations });
  297 |         await page.screenshot({
  298 |           path: `${dir}/${state.replace(" ", "-")}-${width}-${theme}-${browserName}-fake.png`,
  299 |           fullPage: true,
  300 |         });
  301 |       }
  302 |       await writeFile(
  303 |         `${dir}/axe-${width}-${theme}-${browserName}.json`,
  304 |         JSON.stringify(results, null, 2),
  305 |       );
  306 |     });
  307 | 
  308 | for (const mode of ["always", "system"] as const)
  309 |   test(`image develop and progress motion respects ${mode}`, async ({
  310 |     page,
  311 |   }) => {
  312 |     await page.emulateMedia({
  313 |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  314 |     });
  315 |     await page.goto("/design?chat-images");
  316 |     if (mode === "always")
  317 |       await page.getByRole("button", { name: "Reduce motion" }).click();
  318 |     await expect(page.locator(".image-progress")).toHaveCount(2);
  319 |     expect(
  320 |       await page
  321 |         .locator(".image-develop i,.image-progress i")
  322 |         .evaluateAll((nodes) =>
  323 |           nodes.every((node) => {
  324 |             const css = getComputedStyle(node);
  325 |             return (
  326 |               css.animationName === "none" &&
  327 |               css.transitionDuration
  328 |                 .split(",")
  329 |                 .every((n) => parseFloat(n) === 0)
  330 |             );
  331 |           }),
```