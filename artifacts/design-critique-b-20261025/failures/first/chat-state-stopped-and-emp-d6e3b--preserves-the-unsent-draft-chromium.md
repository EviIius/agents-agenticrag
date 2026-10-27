# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> stopped and empty replies are visible, Continue names its parent and preserves the unsent draft
- Location: web/tests/chat-state.spec.ts:188:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('alert')
Expected substring: "Synthetic rejected continuation"
Received string:    "Something went wrong. Try again."
Timeout: 5000ms

Call log:
  - Expect "toContainText" getByRole('alert') with timeout 5000ms
  - waiting for getByRole('alert')
    14 × locator resolved to <p role="alert" class="mb-3 text-sm text-danger">Something went wrong. Try again.</p>
       - unexpected value "Something went wrong. Try again."

```

```yaml
- alert: Something went wrong. Try again.
```

# Test source

```ts
  160 |   expect(bodies[1]).not.toHaveProperty("reference_id");
  161 |   await expect(
  162 |     page.locator('[data-slot="image-turn"]').last().locator("img.is-loaded"),
  163 |   ).toBeVisible();
  164 |   await page.route(
  165 |     `**/api/chats/${chat.id}/image-references/from-job`,
  166 |     (route) =>
  167 |       route.fulfill({
  168 |         status: 404,
  169 |         contentType: "application/json",
  170 |         body: JSON.stringify({
  171 |           error: { code: "not_found", message: "Synthetic source unavailable" },
  172 |         }),
  173 |       }),
  174 |   );
  175 |   await page
  176 |     .getByRole("textbox", { name: "Image prompt" })
  177 |     .fill("An edit that cannot find its source");
  178 |   await page.getByRole("button", { name: "Edit image", exact: true }).click();
  179 |   await expect(page.getByRole("alert")).toContainText(
  180 |     "Synthetic source unavailable",
  181 |   );
  182 |   expect(bodies).toHaveLength(2);
  183 |   await expect(page.getByRole("textbox", { name: "Image prompt" })).toHaveValue(
  184 |     "An edit that cannot find its source",
  185 |   );
  186 | });
  187 | 
  188 | test("stopped and empty replies are visible, Continue names its parent and preserves the unsent draft", async ({
  189 |   page,
  190 |   request,
  191 | }) => {
  192 |   const { connection, chat } = await setup(request);
  193 |   const model = {
  194 |     connection_id: connection.id,
  195 |     model_id: "fake-chat",
  196 |     display_name: "fake-chat",
  197 |   };
  198 |   const rows = [
  199 |     {
  200 |       id: "stopped-synthetic",
  201 |       chat_id: chat.id,
  202 |       role: "assistant",
  203 |       status: "stopped",
  204 |       content: "I'd begin",
  205 |       model,
  206 |       created_at: chat.created_at,
  207 |     },
  208 |     {
  209 |       id: "empty-synthetic",
  210 |       chat_id: chat.id,
  211 |       parent_id: "stopped-synthetic",
  212 |       role: "assistant",
  213 |       status: "complete",
  214 |       content: "",
  215 |       reasoning: "Synthetic reasoning without a final answer",
  216 |       model,
  217 |       created_at: chat.created_at,
  218 |     },
  219 |   ];
  220 |   await page.route(`**/api/chats/${chat.id}`, (route) =>
  221 |     route.fulfill({
  222 |       contentType: "application/json",
  223 |       body: JSON.stringify({
  224 |         chat: { ...chat, current_leaf_id: "empty-synthetic" },
  225 |         messages: rows,
  226 |       }),
  227 |     }),
  228 |   );
  229 |   let body: Record<string, unknown> | undefined;
  230 |   await page.route(`**/api/chats/${chat.id}/messages`, (route) => {
  231 |     body = route.request().postDataJSON();
  232 |     return route.fulfill({
  233 |       status: 503,
  234 |       contentType: "application/json",
  235 |       body: JSON.stringify({
  236 |         error: {
  237 |           code: "unavailable",
  238 |           message: "Synthetic rejected continuation",
  239 |         },
  240 |       }),
  241 |     });
  242 |   });
  243 |   await page.goto(`/c/${chat.id}`);
  244 |   const stopped = page.locator('[data-message-id="stopped-synthetic"]');
  245 |   const empty = page.locator('[data-message-id="empty-synthetic"]');
  246 |   await expect(stopped.locator('[data-slot="reply-outcome"]')).toContainText(
  247 |     "Stopped",
  248 |   );
  249 |   await expect(
  250 |     stopped.getByRole("button", { name: "Retry", exact: true }),
  251 |   ).toHaveCount(1);
  252 |   await expect(
  253 |     stopped.getByRole("button", { name: "Regenerate answer", exact: true }),
  254 |   ).toHaveCount(0);
  255 |   await expect(empty.locator('[data-slot="reply-outcome"]')).toContainText(
  256 |     "No answer",
  257 |   );
  258 |   await page.locator(".composer textarea").fill("An unsent draft");
  259 |   await stopped.getByRole("button", { name: "Continue", exact: true }).click();
> 260 |   await expect(page.getByRole("alert")).toContainText(
      |                                         ^ Error: expect(locator).toContainText(expected) failed
  261 |     "Synthetic rejected continuation",
  262 |   );
  263 |   expect(body).toMatchObject({
  264 |     content: "Continue your previous answer.",
  265 |     parent_id: "stopped-synthetic",
  266 |     attachment_ids: [],
  267 |   });
  268 |   await expect(page.locator(".composer textarea")).toHaveValue(
  269 |     "An unsent draft",
  270 |   );
  271 |   await expect(stopped).toContainText("I'd begin");
  272 | });
  273 | 
  274 | test("one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save", async ({
  275 |   page,
  276 |   request,
  277 | }) => {
  278 |   const { connection, chat } = await setup(request);
  279 |   await request.put("/api/models/prefs", {
  280 |     data: {
  281 |       connection_id: connection.id,
  282 |       model_id: "fake-chat",
  283 |       params: { reasoning: "on" },
  284 |       context_length: 16384,
  285 |     },
  286 |   });
  287 |   await request.patch(`/api/chats/${chat.id}`, {
  288 |     data: { params: { reasoning: "off" } },
  289 |   });
  290 |   let patches = 0,
  291 |     failed = false;
  292 |   page.on("request", (req) => {
  293 |     if (req.method() === "PATCH" && req.url().endsWith(`/api/chats/${chat.id}`))
  294 |       patches++;
  295 |   });
  296 |   await page.route("**/api/models/prefs", (route) => {
  297 |     if (!failed && route.request().postDataJSON().params) {
  298 |       failed = true;
  299 |       return route.fulfill({
  300 |         status: 503,
  301 |         contentType: "application/json",
  302 |         body: JSON.stringify({
  303 |           error: { code: "unavailable", message: "Synthetic defaults failure" },
  304 |         }),
  305 |       });
  306 |     }
  307 |     return route.continue();
  308 |   });
  309 |   await page.goto(`/c/${chat.id}`);
  310 |   await page
  311 |     .getByRole("button", { name: "Chat controls", exact: true })
  312 |     .click();
  313 |   const controls = page.getByRole("region", { name: "Chat controls" });
  314 |   await expect(
  315 |     controls.getByRole("combobox", { name: "Reasoning" }),
  316 |   ).toHaveCount(0);
  317 |   await controls
  318 |     .getByRole("switch", {
  319 |       name: "Use model default for Temperature",
  320 |       exact: true,
  321 |     })
  322 |     .click();
  323 |   await controls
  324 |     .getByRole("spinbutton", { name: "Temperature", exact: true })
  325 |     .fill("0.4");
  326 |   await controls
  327 |     .locator("summary")
  328 |     .filter({ hasText: "Every chat with this model" })
  329 |     .click();
  330 |   await controls
  331 |     .getByRole("switch", {
  332 |       name: "Use model default for Model Top K",
  333 |       exact: true,
  334 |     })
  335 |     .click();
  336 |   await controls
  337 |     .getByRole("spinbutton", { name: "Model Top K", exact: true })
  338 |     .fill("23");
  339 |   await controls
  340 |     .getByRole("spinbutton", { name: "Context length" })
  341 |     .fill("8192");
  342 |   const save = controls.getByRole("button", {
  343 |     name: "Save settings",
  344 |     exact: true,
  345 |   });
  346 |   await save.click();
  347 |   await expect(
  348 |     page.getByText("Synthetic defaults failure", { exact: true }),
  349 |   ).toBeVisible();
  350 |   await expect(save).toBeEnabled();
  351 |   expect(patches).toBe(1);
  352 |   expect(
  353 |     (await (await request.get(`/api/chats/${chat.id}`)).json()).chat.params,
  354 |   ).toEqual({ temperature: 0.4, reasoning: "off" });
  355 |   await save.click();
  356 |   await expect(save).toContainText("Saved");
  357 |   expect(patches).toBe(1);
  358 |   const models = await (await request.get("/api/models")).json();
  359 |   const updated = models.find(
  360 |     (m: { model_id: string }) => m.model_id === "fake-chat",
```