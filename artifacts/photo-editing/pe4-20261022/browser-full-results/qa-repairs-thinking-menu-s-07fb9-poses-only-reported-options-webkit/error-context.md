# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: qa-repairs.spec.ts >> thinking menu says Model default and exposes only reported options
- Location: tests/qa-repairs.spec.ts:169:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator:  getByRole('menuitemradio', { name: 'Model default', exact: true })
Expected: "Model default"
Received: "Default"
Timeout:  5000ms

Call log:
  - Expect "toHaveText" getByRole('menuitemradio', { name: 'Model default', exact: true }) with timeout 5000ms
  - waiting for getByRole('menuitemradio', { name: 'Model default', exact: true })
    14 × locator resolved to <div tabindex="-1" aria-checked="true" role="menuitemradio" data-state="checked" title="Model default" aria-label="Model default" data-orientation="vertical" data-radix-collection-item="" data-slot="dropdown-menu-radio-item" class="relative flex cursor-default items-center gap-2 rounded-sm py-1.5 pr-2 pl-8 text-sm outline-hidden select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:…>…</div>
       - unexpected value "Default"

```

```yaml
- menuitemradio "Model default" [checked]: Default
```

# Test source

```ts
  90  |   };
  91  |   let loaded = true;
  92  |   const ejected: string[] = [];
  93  |   await page.route("**/api/models?include_hidden=true", (route) =>
  94  |     route.fulfill({ json: [...regular, { ...embedding, loaded }] }),
  95  |   );
  96  |   await page.route("**/api/models/unload", async (route) => {
  97  |     ejected.push(route.request().postDataJSON().model_id);
  98  |     loaded = false;
  99  |     await route.fulfill({ json: { ok: true } });
  100 |   });
  101 |   await request.patch("/api/settings", {
  102 |     data: {
  103 |       default_connection_id: connection.id,
  104 |       default_model_id: "fake-chat",
  105 |     },
  106 |   });
  107 |   await page.goto("/");
  108 |   await page.keyboard.press("Control+Comma");
  109 |   // Open the actual app settings through the sidebar on both desktop and phone.
  110 |   if (
  111 |     !(await page
  112 |       .getByRole("dialog", { name: "Settings", exact: true })
  113 |       .isVisible())
  114 |   ) {
  115 |     const open = page.getByRole("button", {
  116 |       name: "Open sidebar",
  117 |       exact: true,
  118 |     });
  119 |     if (await open.isVisible()) await open.click();
  120 |     await page.getByRole("button", { name: "Settings", exact: true }).click();
  121 |   }
  122 |   const dialog = page.getByRole("dialog", { name: "Settings", exact: true });
  123 |   await dialog.getByRole("button", { name: "Models", exact: true }).click();
  124 |   const card = dialog.locator("div.rounded-lg").filter({
  125 |     has: page.getByRole("heading", {
  126 |       name: "Synthetic Library embedding",
  127 |       exact: true,
  128 |     }),
  129 |   });
  130 |   await expect(
  131 |     card.getByRole("button", { name: "Eject", exact: true }),
  132 |   ).toBeEnabled();
  133 |   expect(ejected).toEqual([]);
  134 |   await card.getByRole("button", { name: "Eject", exact: true }).click();
  135 |   await expect(card).toContainText("Not loaded");
  136 |   expect(ejected).toEqual(["fake-embedding"]);
  137 |   await mkdir("../artifacts/qa-roadmap/repair-1/browser", { recursive: true });
  138 |   await page.screenshot({
  139 |     path: `../artifacts/qa-roadmap/repair-1/browser/embedding-ejected-${test.info().project.name}-fake.png`,
  140 |   });
  141 | });
  142 | 
  143 | test("long-thinking guidance starts at a minute and Stop reply uses cancellation without an answer claim", async ({
  144 |   page,
  145 | }) => {
  146 |   await page.clock.install();
  147 |   await page.goto("/design?indicator");
  148 |   await page
  149 |     .getByRole("button", { name: "Preview Thinking", exact: true })
  150 |     .click();
  151 |   const warning = page.getByTestId("long-thinking");
  152 |   await expect(warning).toHaveCount(0);
  153 |   await page.clock.fastForward(59000);
  154 |   await expect(warning).toHaveCount(0);
  155 |   await page.clock.fastForward(2000);
  156 |   await expect(warning).toBeVisible();
  157 |   await expect(warning).toContainText("does not guarantee a better answer");
  158 |   await mkdir("../artifacts/qa-roadmap/repair-1/browser", { recursive: true });
  159 |   await page.screenshot({
  160 |     path: `../artifacts/qa-roadmap/repair-1/browser/long-thinking-${test.info().project.name}-fake.png`,
  161 |   });
  162 |   await warning
  163 |     .getByRole("button", { name: "Stop reply", exact: true })
  164 |     .click();
  165 |   await expect(warning).toHaveCount(0);
  166 |   await expect(page.locator('[data-streaming="true"]')).toHaveCount(0);
  167 | });
  168 | 
  169 | test("thinking menu says Model default and exposes only reported options", async ({
  170 |   page,
  171 |   request,
  172 | }) => {
  173 |   const connection = (await (await request.get("/api/connections")).json())[0];
  174 |   await request.patch("/api/settings", {
  175 |     data: {
  176 |       default_connection_id: connection.id,
  177 |       default_model_id: "fake-reasoning",
  178 |       auto_title: false,
  179 |     },
  180 |   });
  181 |   await page.goto("/");
  182 |   await expect(
  183 |     page.getByRole("button", { name: "Choose model", exact: true }),
  184 |   ).toContainText("fake-reasoning");
  185 |   await page.getByRole("button", { name: "Tools", exact: true }).click();
  186 |   const option = page.getByRole("menuitemradio", {
  187 |     name: "Model default",
  188 |     exact: true,
  189 |   });
> 190 |   await expect(option).toHaveText("Model default");
      |                        ^ Error: expect(locator).toHaveText(expected) failed
  191 |   await expect(option).toHaveAttribute("aria-checked", "true");
  192 |   await expect(
  193 |     page.getByRole("menuitemradio", { name: "High", exact: true }),
  194 |   ).toHaveCount(0);
  195 |   await page.getByRole("menuitemradio", { name: "On", exact: true }).click();
  196 |   await expect(
  197 |     page.getByRole("menuitemradio", { name: "On", exact: true }),
  198 |   ).toHaveAttribute("aria-checked", "true");
  199 |   await option.click();
  200 |   await expect(option).toHaveAttribute("aria-checked", "true");
  201 | });
  202 | 
  203 | test("thinking elapsed excludes retrieval and its Stop reply cancels the active run once", async ({
  204 |   page,
  205 |   request,
  206 | }) => {
  207 |   await page.clock.install();
  208 |   const connection = (await (await request.get("/api/connections")).json())[0];
  209 |   await request.patch("/api/settings", {
  210 |     data: { auto_title: false, "web.default_on": false },
  211 |   });
  212 |   const chat = await (
  213 |     await request.post("/api/chats", {
  214 |       data: {
  215 |         connection_id: connection.id,
  216 |         model_id: "fake-reasoning",
  217 |         web_enabled: false,
  218 |       },
  219 |     })
  220 |   ).json();
  221 |   await page.addInitScript(() => {
  222 |     const Native = window.EventSource;
  223 |     window.EventSource = class extends EventTarget {
  224 |       constructor(url: string | URL, options?: EventSourceInit) {
  225 |         super();
  226 |         if (!/^\/api\/runs\/[^/]+\/events$/.test(String(url)))
  227 |           return new Native(url, options);
  228 |         Object.assign(window, { qaRunEvents: this });
  229 |       }
  230 |       close() {}
  231 |     } as unknown as typeof EventSource;
  232 |   });
  233 |   await page.route(`**/api/chats/${chat.id}/messages`, async (route) => {
  234 |     const response = await route.fetch();
  235 |     const body = await response.json();
  236 |     body.assistant_message.created_at = new Date(
  237 |       Date.now() - 120000,
  238 |     ).toISOString();
  239 |     body.assistant_message.stats = {
  240 |       ...body.assistant_message.stats,
  241 |       ttft_ms: 120000,
  242 |     };
  243 |     await route.fulfill({ response, json: body });
  244 |   });
  245 |   let runId: string | undefined;
  246 |   let cancels = 0;
  247 |   page.on("request", (r) => {
  248 |     if (r.method() === "POST" && /\/api\/runs\/[^/]+\/cancel$/.test(r.url()))
  249 |       cancels++;
  250 |   });
  251 |   try {
  252 |     await page.goto(`/c/${chat.id}`);
  253 |     await page
  254 |       .locator(".composer textarea")
  255 |       .fill("#think #long:100 #slow:1 #stall:120 Synthetic cancellation");
  256 |     const accepted = page.waitForResponse(
  257 |       (r) =>
  258 |         r.request().method() === "POST" &&
  259 |         r.url().endsWith(`/api/chats/${chat.id}/messages`),
  260 |     );
  261 |     await page
  262 |       .getByRole("button", { name: "Send message", exact: true })
  263 |       .click();
  264 |     runId = (await (await accepted).json()).run_id;
  265 |     await expect
  266 |       .poll(() =>
  267 |         page.evaluate(() =>
  268 |           Boolean(
  269 |             (window as unknown as { qaRunEvents?: EventTarget }).qaRunEvents,
  270 |           ),
  271 |         ),
  272 |       )
  273 |       .toBe(true);
  274 |     await page.evaluate(() => {
  275 |       (
  276 |         window as unknown as { qaRunEvents: EventTarget }
  277 |       ).qaRunEvents.dispatchEvent(
  278 |         new MessageEvent("reasoning.delta", {
  279 |           data: JSON.stringify({ text: "Synthetic ongoing reasoning." }),
  280 |         }),
  281 |       );
  282 |     });
  283 |     await expect(page.locator(".thought-ticker")).toBeVisible();
  284 |     await expect(page.getByTestId("long-thinking")).toHaveCount(0);
  285 |     await page.clock.fastForward(61000);
  286 |     const warning = page.getByTestId("long-thinking");
  287 |     await expect(warning).toBeVisible();
  288 |     const stopped = page.waitForResponse(
  289 |       (r) =>
  290 |         r.url().endsWith(`/runs/${runId}/cancel`) &&
```