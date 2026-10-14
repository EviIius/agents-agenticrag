# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> long answer completes beyond 90 seconds; idle timeout keeps partial
- Location: tests/chat.spec.ts:112:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/token1499/)
Expected: visible
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByText(/token1499/) with timeout 180000ms
  - waiting for getByText(/token1499/)
  - Test ended.

```

```yaml
- complementary:
  - button "Collapse sidebar"
  - text: Atelier
  - link "New chat":
    - /url: /
  - navigation "Chat history":
    - textbox "Search history":
      - /placeholder: Search chats…
    - text: ⌘K
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
      - link "Images":
        - /url: /images
    - region "Folders":
      - heading "Folders" [level=2]
      - button "New folder"
      - paragraph: No folders yet
    - paragraph: Today
    - 'link "#long:1500 #slow:10"':
      - /url: /c/8c9ff660b9fc49a3ad53054b6bc010e5
    - img "Generating response"
    - 'button "Actions for #long:1500 #slow:10"'
    - 'link "#long:350 #slow:10"':
      - /url: /c/cb9fcdca030f4ab280db01b89b2e71e2
    - 'button "Actions for #long:350 #slow:10"'
    - 'link "#long:500 #slow:50"':
      - /url: /c/ba00052fb37a4582a25f7c0ac4151695
    - 'button "Actions for #long:500 #slow:50"'
    - link "Hello from the browser":
      - /url: /c/769d5fff2e6545afb69adfdae96c0ec3
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/9de2b8171849489ea745dcb0c9d0fa50
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/e8c3d3d3c09944409ffe00641c1106a0
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/3e82a012d29142b5b73d30a840c85063
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/263b2bad88744ad686b027a4efa6ed08
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/a2295491f4d84344a63e8cf5ed5b962d
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/d75f4154c53e4a2dabbd4b50c53711a4
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/c78a9a55f2f54ded8cae2fe5fb9e5ef9
    - button "Actions for Hello from the browser"
  - button "Settings"
- main:
  - button "Choose model": fake-chat Fake runtime
  - text: "#long:1500 #slow:10"
  - button "Chat controls"
  - 'button "Actions for #long:1500 #slow:10"'
  - status: Generating response
  - log "Conversation":
    - article "user message":
      - heading "You said" [level=2]
      - paragraph: "#long:1500 #slow:10"
      - button "Copy message":
        - status
      - button "Edit message"
    - article "assistant message":
      - heading "fake-chat replied" [level=2]
      - paragraph: fake-chat
      - status
      - paragraph: token0 token1 token2 token3 token4 token5 token6 token7 token8 token9 token10 token11 token12 token13 token14 token15 token16 token17 token18 token19 token20 token21 token22 token23 token24 token25 token26 token27 token28 token29 token30 token31 token32 token33 token34 token35 token36 token37 token38 token39 token40 token41 token42 token43 token44 token45 token46 token47 token48 token49 token50 token51 token52 token53 token54 token55 token56 token57 token58 token59 token60 token61 token62 token63 token64 token65 token66 token67 token68 token69 token70 token71 token72 token73 token74 token75 token76 token77 token78 token79 token80 token81 token82 token83 token84 token85 token86 token87 token88 token89 token90 token91 token92 token93 token94 token95 token96 token97 token98 token99 token100 token101 token102 token103 token104 token105 token106 token107 token108 token109 token110 token111 token112 token113 token114 token115 token116 token117 token118 token119 token120 token121 token122 token123 token124 token125 token126 token127 token128 token129 token130 token131 token132 token133 token134 token135 token136 token137 token138 token139 token140 token141 token142 token143 token144 token145 token146 token147 token148 token149 token150 token151 token152 token153 token154 token155 token156 token157 token158 token159 token160 token161 token162 token163 token164 token165 token166 token167 token168 token169 token170 token171 token172 token173
  - form "Message":
    - textbox "Message fake-chat":
      - /placeholder: Message fake-chat…
    - button "Add attachment"
    - button "Web search": Search
    - button "Create image": Image
    - button "Library" [disabled]
    - button "Choose Library collections"
    - img "21 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin"
    - button "Stop generating"
- region "Notifications alt+T"
```

# Test source

```ts
  22  |       await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
  23  |       await page.addInitScript(
  24  |         (value) => localStorage.setItem("workbench-theme", value),
  25  |         theme,
  26  |       );
  27  |       await send(page, "Hello from the browser");
  28  |       await expect(
  29  |         page.getByText("Fake runtime reply.", { exact: false }),
  30  |       ).toBeVisible();
  31  |       await expect(
  32  |         page.getByRole("button", { name: "Stop generating" }),
  33  |       ).not.toBeVisible();
  34  |       expect(
  35  |         await page.evaluate(
  36  |           () => document.documentElement.scrollWidth <= innerWidth,
  37  |         ),
  38  |       ).toBeTruthy();
  39  |       const thread = await page.getByTestId("thread").boundingBox(),
  40  |         composer = await page.getByTestId("composer-row").boundingBox();
  41  |       expect(thread!.y + thread!.height).toBeLessThanOrEqual(composer!.y + 1);
  42  |       await mkdir(dir, { recursive: true });
  43  |       await settle(page);
  44  |       await page.screenshot({
  45  |         path: `${dir}/chat-${width}-${theme}-fake-runtime.png`,
  46  |       });
  47  |       await settle(page);
  48  |       const result = await new AxeBuilder({ page }).analyze();
  49  |       expect(
  50  |         result.violations.filter((v) =>
  51  |           ["serious", "critical"].includes(v.impact ?? ""),
  52  |         ),
  53  |       ).toEqual([]);
  54  |       await page.reload();
  55  |       await expect(
  56  |         page
  57  |           .getByRole("article", { name: "user message" })
  58  |           .getByText("Hello from the browser", { exact: true }),
  59  |       ).toBeVisible();
  60  |     });
  61  | test("Stop persists partial text and closes runtime connection", async ({
  62  |   page,
  63  |   request,
  64  | }) => {
  65  |   const before = (
  66  |     await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  67  |   ).disconnected;
  68  |   await send(page, "#long:500 #slow:50");
  69  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  70  |   await page.getByRole("button", { name: "Stop generating" }).click();
  71  |   await expect(
  72  |     page.locator(".meta").filter({ hasText: /stopped/i }),
  73  |   ).toBeVisible();
  74  |   await expect
  75  |     .poll(
  76  |       async () =>
  77  |         (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
  78  |           .disconnected,
  79  |     )
  80  |     .toBeGreaterThan(before);
  81  |   const text = await page.locator(".prose-answer").innerText();
  82  |   await page.reload();
  83  |   await expect(page.locator(".prose-answer")).toHaveText(text);
  84  | });
  85  | test("close tab and reopen after 20 seconds resumes exactly", async ({
  86  |   page,
  87  |   context,
  88  |   request,
  89  | }) => {
  90  |   test.setTimeout(65000);
  91  |   await send(page, "#long:350 #slow:10");
  92  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  93  |   const url = page.url();
  94  |   await page.close();
  95  |   await new Promise((resolve) => setTimeout(resolve, 20000));
  96  |   const reopened = await context.newPage();
  97  |   await reopened.goto(url);
  98  |   await expect(
  99  |     reopened.getByRole("button", { name: "Stop generating" }),
  100 |   ).toBeVisible();
  101 |   await expect(
  102 |     reopened.getByRole("button", { name: "Stop generating" }),
  103 |   ).not.toBeVisible({ timeout: 25000 });
  104 |   const data = await (
  105 |     await request.get("/api/chats/" + url.split("/").pop())
  106 |   ).json();
  107 |   expect(await reopened.locator(".prose-answer").innerText()).toBe(
  108 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  109 |       .content,
  110 |   );
  111 | });
  112 | test("long answer completes beyond 90 seconds; idle timeout keeps partial", async ({
  113 |   page,
  114 |   request,
  115 | }) => {
  116 |   test.skip(
  117 |     test.info().project.name !== "chromium",
  118 |     "Run the real-time timeout gate once",
  119 |   );
  120 |   test.setTimeout(240000);
  121 |   await send(page, "#long:1500 #slow:10");
> 122 |   await expect(page.getByText(/token1499/)).toBeVisible({ timeout: 180000 });
      |                                             ^ Error: expect(locator).toBeVisible() failed
  123 |   await expect(
  124 |     page.getByRole("button", { name: "Stop generating" }),
  125 |   ).not.toBeVisible();
  126 |   const url = page.url();
  127 |   const data = await (
  128 |     await request.get("/api/chats/" + url.split("/").pop())
  129 |   ).json();
  130 |   expect(
  131 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  132 |       .status,
  133 |   ).toBe("complete");
  134 |   expect(
  135 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  136 |       .stats.total_ms,
  137 |   ).toBeGreaterThan(150000);
  138 |   await send(page, "#stall:70");
  139 |   await expect(
  140 |     page.getByText("The model stopped responding. The partial answer is kept."),
  141 |   ).toBeVisible({ timeout: 75000 });
  142 |   const id = page.url().split("/").pop();
  143 |   const error = await (await request.get("/api/chats/" + id)).json();
  144 |   expect(
  145 |     error.messages.findLast((m: { role: string }) => m.role === "assistant")
  146 |       .error.code,
  147 |   ).toBe("idle_timeout");
  148 |   expect(
  149 |     error.messages.findLast((m: { role: string }) => m.role === "assistant")
  150 |       .content.length,
  151 |   ).toBeGreaterThan(0);
  152 | });
  153 | test("100 tokens/s render frame trace", async ({ page }) => {
  154 |   const cdp =
  155 |     test.info().project.name === "chromium"
  156 |       ? await page.context().newCDPSession(page)
  157 |       : null;
  158 |   if (cdp)
  159 |     await cdp.send("Tracing.start", {
  160 |       categories: "devtools.timeline,blink.user_timing",
  161 |       transferMode: "ReturnAsStream",
  162 |     });
  163 |   await page.addInitScript(() => {
  164 |     const times: number[] = [];
  165 |     (window as unknown as { frames: number[] }).frames = times;
  166 |     let previous = performance.now();
  167 |     const frame = (now: number) => {
  168 |       times.push(now - previous);
  169 |       previous = now;
  170 |       requestAnimationFrame(frame);
  171 |     };
  172 |     requestAnimationFrame(frame);
  173 |   });
  174 |   await send(page, "#long:300 #slow:100");
  175 |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  176 |   await page.evaluate(() => {
  177 |     (window as unknown as { frames: number[] }).frames.length = 0;
  178 |   });
  179 |   await expect(page.getByText(/token299/)).toBeVisible();
  180 |   const times = await page.evaluate(
  181 |     () => (window as unknown as { frames: number[] }).frames,
  182 |   );
  183 |   await mkdir(dir, { recursive: true });
  184 |   await writeFile(
  185 |     `${dir}/frames-${test.info().project.name}.json`,
  186 |     JSON.stringify(times),
  187 |   );
  188 |   if (cdp) {
  189 |     const finished = new Promise<string>((resolve, reject) =>
  190 |       cdp.once("Tracing.tracingComplete", (event) =>
  191 |         event.stream
  192 |           ? resolve(event.stream)
  193 |           : reject(new Error("Chrome trace stream missing")),
  194 |       ),
  195 |     );
  196 |     await cdp.send("Tracing.end");
  197 |     const handle = await finished;
  198 |     let trace = "";
  199 |     for (;;) {
  200 |       const part = await cdp.send("IO.read", { handle });
  201 |       trace += part.data;
  202 |       if (part.eof) break;
  203 |     }
  204 |     await cdp.send("IO.close", { handle });
  205 |     await writeFile(`${dir}/streaming-chromium-trace.json.gz`, gzipSync(trace));
  206 |   }
  207 |   const sorted = times.filter((n) => n < 100).sort((a, b) => a - b);
  208 |   expect(sorted[Math.floor(sorted.length * 0.5)]).toBeLessThan(20);
  209 | });
  210 | 
  211 | test("first-token render delay under 150ms", async ({ page, request }) => {
  212 |   await page.addInitScript(() => {
  213 |     const listener = new MutationObserver(() => {
  214 |       if (
  215 |         document
  216 |           .querySelector('[aria-label="assistant message"] .prose-answer')
  217 |           ?.textContent?.includes("Fake")
  218 |       ) {
  219 |         (window as unknown as { firstRendered: number }).firstRendered =
  220 |           performance.timeOrigin + performance.now();
  221 |         listener.disconnect();
  222 |       }
```