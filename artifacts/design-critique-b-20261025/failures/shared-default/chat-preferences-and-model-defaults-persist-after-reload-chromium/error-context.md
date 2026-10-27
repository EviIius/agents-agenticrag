# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> preferences and model defaults persist after reload
- Location: tests/chat.spec.ts:260:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('button', { name: 'Choose model' })
Expected substring: "fake-chat"
Received string:    "○fake-reasoningFake runtime"
Timeout: 5000ms

Call log:
  - Expect "toContainText" getByRole('button', { name: 'Choose model' }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Choose model' })
    14 × locator resolved to <button data-slot="button" data-size="default" data-variant="ghost" aria-label="Choose model" title="Not loaded · loads on send" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-accent hover:tex…>…</button>
       - unexpected value "○fake-reasoningFake runtime"

```

```yaml
- button "Choose model": fake-reasoning
```

# Test source

```ts
  173 |       requestAnimationFrame(frame);
  174 |     };
  175 |     requestAnimationFrame(frame);
  176 |   });
  177 |   await send(page, "#long:300 #slow:100");
  178 |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  179 |   await page.evaluate(() => {
  180 |     (window as unknown as { frames: number[] }).frames.length = 0;
  181 |   });
  182 |   await expect(page.getByText(/token299/)).toBeVisible();
  183 |   const times = await page.evaluate(
  184 |     () => (window as unknown as { frames: number[] }).frames,
  185 |   );
  186 |   await mkdir(dir, { recursive: true });
  187 |   await writeFile(
  188 |     `${dir}/frames-${test.info().project.name}.json`,
  189 |     JSON.stringify(times),
  190 |   );
  191 |   if (cdp) {
  192 |     const finished = new Promise<string>((resolve, reject) =>
  193 |       cdp.once("Tracing.tracingComplete", (event) =>
  194 |         event.stream
  195 |           ? resolve(event.stream)
  196 |           : reject(new Error("Chrome trace stream missing")),
  197 |       ),
  198 |     );
  199 |     await cdp.send("Tracing.end");
  200 |     const handle = await finished;
  201 |     let trace = "";
  202 |     for (;;) {
  203 |       const part = await cdp.send("IO.read", { handle });
  204 |       trace += part.data;
  205 |       if (part.eof) break;
  206 |     }
  207 |     await cdp.send("IO.close", { handle });
  208 |     await writeFile(`${dir}/streaming-chromium-trace.json.gz`, gzipSync(trace));
  209 |   }
  210 |   const sorted = times.filter((n) => n < 100).sort((a, b) => a - b);
  211 |   expect(sorted[Math.floor(sorted.length * 0.5)]).toBeLessThan(20);
  212 | });
  213 | 
  214 | test("first-token render delay under 150ms", async ({ page, request }) => {
  215 |   await page.addInitScript(() => {
  216 |     const listener = new MutationObserver(() => {
  217 |       if (
  218 |         document
  219 |           .querySelector('[aria-label="assistant message"] .prose-answer')
  220 |           ?.textContent?.includes("Fake")
  221 |       ) {
  222 |         (window as unknown as { firstRendered: number }).firstRendered =
  223 |           performance.timeOrigin + performance.now();
  224 |         listener.disconnect();
  225 |       }
  226 |     });
  227 |     listener.observe(document, {
  228 |       subtree: true,
  229 |       childList: true,
  230 |       characterData: true,
  231 |     });
  232 |   });
  233 |   await send(page, "first-token-latency-check");
  234 |   await expect(
  235 |     page.getByText("Fake runtime reply.", { exact: false }),
  236 |   ).toBeVisible();
  237 |   const at = await page.evaluate(
  238 |     () => (window as unknown as { firstRendered: number }).firstRendered,
  239 |   );
  240 |   const state = await (
  241 |     await request.get("http://127.0.0.1:18080/tests/state")
  242 |   ).json();
  243 |   const first = state.first_tokens.findLast(
  244 |     (r: { prompt: string; at_ms: number }) =>
  245 |       r.prompt === "first-token-latency-check",
  246 |   );
  247 |   const delay = at - first.at_ms;
  248 |   expect(delay).toBeGreaterThanOrEqual(0);
  249 |   expect(delay).toBeLessThan(150);
  250 |   await writeFile(
  251 |     `${dir}/first-token-${test.info().project.name}.json`,
  252 |     JSON.stringify({
  253 |       runtime_first_ms: first.at_ms,
  254 |       ui_first_ms: at,
  255 |       delay_ms: delay,
  256 |     }),
  257 |   );
  258 | });
  259 | 
  260 | test("preferences and model defaults persist after reload", async ({
  261 |   page,
  262 |   request,
  263 | }) => {
  264 |   const initial = await (await request.get("/api/settings")).json();
  265 |   const models = await (await request.get("/api/models")).json();
  266 |   const model = models.find(
  267 |     (item: { model_id: string }) => item.model_id === "fake-chat",
  268 |   );
  269 |   await page.setViewportSize({ width: 390, height: 844 });
  270 |   await page.goto("/");
  271 |   await expect(
  272 |     page.getByRole("button", { name: "Choose model" }),
> 273 |   ).toContainText("fake-chat");
      |     ^ Error: expect(locator).toContainText(expected) failed
  274 |   await page.keyboard.press("Control+,");
  275 |   const settings = page.getByRole("dialog", { name: "Settings" });
  276 |   await settings
  277 |     .getByRole("button", { name: "Appearance", exact: true })
  278 |     .click();
  279 |   await settings
  280 |     .getByPlaceholder("Your name (optional)")
  281 |     .fill("Preference test");
  282 |   await settings.getByRole("button", { name: "Sans · Geist" }).click();
  283 |   await expect
  284 |     .poll(
  285 |       async () => (await (await request.get("/api/settings")).json()).user_name,
  286 |     )
  287 |     .toBe("Preference test");
  288 |   await settings.getByRole("button", { name: "Models", exact: true }).click();
  289 |   await settings
  290 |     .getByRole("button", { name: "Parameters and context" })
  291 |     .first()
  292 |     .click();
  293 |   await settings
  294 |     .getByRole("switch", { name: "Use model default for Temperature" })
  295 |     .click();
  296 |   await settings
  297 |     .getByRole("spinbutton", { name: "Temperature", exact: true })
  298 |     .fill("0.35");
  299 |   await settings
  300 |     .getByRole("button", { name: "Save as model defaults" })
  301 |     .click();
  302 |   await expect
  303 |     .poll(async () => {
  304 |       const catalog = await (
  305 |         await request.get("/api/models?include_hidden=true")
  306 |       ).json();
  307 |       return catalog.find(
  308 |         (item: { model_id: string }) => item.model_id === "fake-chat",
  309 |       ).params_defaults.temperature;
  310 |     })
  311 |     .toBe(0.35);
  312 |   await settings.locator('section[aria-label="Models"]').evaluate((element) => {
  313 |     element.scrollTop = 0;
  314 |   });
  315 |   expect(
  316 |     await settings
  317 |       .locator('section[aria-label="Models"]')
  318 |       .evaluate((element) => element.scrollWidth <= element.clientWidth),
  319 |   ).toBeTruthy();
  320 |   await settle(page);
  321 |   await page.screenshot({
  322 |     path: `${dir}/settings-models-390-light-fake-runtime.png`,
  323 |   });
  324 |   await page.reload();
  325 |   await expect(
  326 |     page.getByRole("heading", { name: /Preference test/ }),
  327 |   ).toBeVisible();
  328 |   expect(
  329 |     await page.evaluate(() => document.documentElement.dataset.answerFont),
  330 |   ).toBe("sans");
  331 |   await page.locator(".composer textarea").fill("model-default-payload-check");
  332 |   await page.getByRole("button", { name: "Send message" }).click();
  333 |   await expect(
  334 |     page.getByText("Fake runtime reply.", { exact: false }),
  335 |   ).toBeVisible();
  336 |   const captures = (
  337 |     await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  338 |   ).captures;
  339 |   const payload = captures.findLast(
  340 |     (item: { messages?: { content: string }[] }) =>
  341 |       item.messages?.at(-1)?.content === "model-default-payload-check",
  342 |   );
  343 |   expect(payload.options.temperature).toBe(0.35);
  344 |   expect(payload.options).not.toHaveProperty("top_p");
  345 |   await request.put("/api/models/prefs", {
  346 |     data: {
  347 |       connection_id: model.connection_id,
  348 |       model_id: model.model_id,
  349 |       params: {},
  350 |     },
  351 |   });
  352 |   await request.patch("/api/settings", {
  353 |     data: {
  354 |       user_name: initial.user_name,
  355 |       "appearance.font": initial["appearance.font"] ?? "serif",
  356 |     },
  357 |   });
  358 | });
  359 | 
```