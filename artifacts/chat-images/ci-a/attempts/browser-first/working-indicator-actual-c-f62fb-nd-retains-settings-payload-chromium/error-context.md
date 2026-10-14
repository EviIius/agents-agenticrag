# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: working-indicator.spec.ts >> actual chat stream prioritizes stages, batches reasoning, collapses on text and retains settings payload
- Location: tests/working-indicator.spec.ts:220:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: apiRequestContext.post: Target page, context or browser has been closed
```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic:
      - complementary [aria-hidden]:
        - generic:
          - generic:
            - button
            - generic: Atelier
            - link:
              - /url: /
          - navigation:
            - generic:
              - textbox:
                - /placeholder: Search chats…
              - generic: ⌘K
            - navigation:
              - generic:
                - link:
                  - /url: /workflows
                  - text: Workflows
              - generic:
                - link:
                  - /url: /images
                  - text: Images
            - region:
              - generic:
                - heading [level=2]: Folders
                - button
              - paragraph: No folders yet
            - generic:
              - paragraph: Today
              - generic:
                - link:
                  - /url: /c/4a10a8e17945435b8b172cad1b5c6b7d
                  - text: "#think #long:100 #slow:1 #stall:30 Synthetic ticker check"
                - button
          - generic:
            - button: Settings
      - main:
        - generic [aria-hidden]:
          - generic:
            - button:
              - generic [aria-hidden]: ●
              - generic: fake-reasoning
              - generic: Fake runtime
          - generic: "#think #long:100 #slow:1 #stall:30 Synthetic ticker check"
          - button
          - button
        - status [aria-hidden]: Generating response
        - log "Conversation":
          - generic:
            - article "user message":
              - heading "You said" [level=2]
              - generic:
                - paragraph: "#think #long:100 #slow:1 #stall:30 Synthetic ticker check"
              - generic:
                - generic:
                  - generic:
                    - button "Copy message":
                      - status
                    - button "Edit message"
            - article "assistant message":
              - heading "fake-reasoning replied" [level=2]
              - paragraph: fake-reasoning
              - generic:
                - generic:
                  - button "Searched the web · 0 sources · 0.0 s"
              - generic:
                - button "Thought for 0 s" [expanded]
                - region "Model reasoning": An original synthetic thought. Newest reasoning stays literal <tag>.
              - generic:
                - status
                - generic:
                  - paragraph: Synthetic streamed answer
              - button "0 sources"
        - generic [aria-hidden]:
          - button [aria-hidden]
          - generic:
            - form:
              - textbox:
                - /placeholder: Message fake-reasoning…
              - generic:
                - button
                - button:
                  - generic: Search
                - button:
                  - generic: Image
                - generic:
                  - button [disabled]:
                    - generic: Library
                  - button
                - button:
                  - generic: Think
                - generic:
                  - generic:
                    - button
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - banner [ref=e3]:
      - heading "Settings" [level=2] [ref=e4]
      - button "Close settings" [ref=e5] [cursor=pointer]
    - paragraph [ref=e6]: Local models · your preferences
    - generic [ref=e7]:
      - navigation "Settings sections" [ref=e8]:
        - button "Connections" [ref=e9] [cursor=pointer]
        - button "Models" [ref=e10] [cursor=pointer]
        - button "Presets" [ref=e11] [cursor=pointer]
        - button "Web search" [ref=e12] [cursor=pointer]
        - button "Library" [ref=e13] [cursor=pointer]
        - button "Transcription" [ref=e14] [cursor=pointer]
        - button "Appearance" [active] [ref=e15] [cursor=pointer]
        - button "Data" [ref=e16] [cursor=pointer]
        - button "Shortcuts" [ref=e17] [cursor=pointer]
        - button "About" [ref=e18] [cursor=pointer]
      - region "Appearance" [ref=e19]:
        - heading "Appearance" [level=2] [ref=e20]
        - group "Theme" [ref=e21]:
          - generic [ref=e23]:
            - button "System" [pressed] [ref=e24] [cursor=pointer]
            - button "Light" [ref=e25] [cursor=pointer]
            - button "Dark" [ref=e26] [cursor=pointer]
        - group "Answer font" [ref=e27]:
          - generic [ref=e29]:
            - button "Serif · Newsreader" [pressed] [ref=e30] [cursor=pointer]
            - button "Sans · Geist" [ref=e31] [cursor=pointer]
        - group "Text size" [ref=e32]:
          - generic [ref=e34]:
            - button "S" [ref=e35] [cursor=pointer]
            - button "M" [pressed] [ref=e36] [cursor=pointer]
            - button "L" [ref=e37] [cursor=pointer]
        - group "Status words" [ref=e38]:
          - generic [ref=e40]:
            - button "playful" [pressed] [ref=e41] [cursor=pointer]
            - button "plain" [ref=e42] [cursor=pointer]
        - generic [ref=e43]:
          - text: Reduce motion
          - combobox "Reduce motion" [ref=e44] [cursor=pointer]:
            - generic: Follow system
          - status [ref=e45]: Brief animations are enabled.
        - generic [ref=e46]:
          - generic [ref=e47]: What should Atelier call you?
          - textbox "What should Atelier call you?" [ref=e48]:
            - /placeholder: Your name (optional)
```

# Test source

```ts
  259 |   const emit = async (type: string, data: unknown) =>
  260 |     page.evaluate(
  261 |       ({ type, data }) =>
  262 |         (
  263 |           window as unknown as {
  264 |             syntheticRunEvent: (type: string, data: unknown) => void;
  265 |           }
  266 |         ).syntheticRunEvent(type, data),
  267 |       { type, data },
  268 |     );
  269 |   let runId: string | undefined;
  270 |   try {
  271 |     await page.goto(`/c/${chat.id}`);
  272 |     await page
  273 |       .locator(".composer textarea")
  274 |       .fill("#think #long:100 #slow:1 #stall:30 Synthetic ticker check");
  275 |     const accepted = page.waitForResponse(
  276 |       (r) =>
  277 |         r.request().method() === "POST" &&
  278 |         r.url().endsWith(`/api/chats/${chat.id}/messages`),
  279 |     );
  280 |     await page
  281 |       .getByRole("button", { name: "Send message", exact: true })
  282 |       .click();
  283 |     const response = await accepted;
  284 |     expect(response.ok()).toBe(true);
  285 |     runId = (await response.json()).run_id;
  286 |     await expect(line(page)).toHaveCount(1);
  287 |     await emit("run.queued", { position: 2 });
  288 |     await expect(word(page)).toContainText("#2 in line");
  289 |     await emit("run.started", { model_loaded: false });
  290 |     await expect(word(page)).toContainText("Loading");
  291 |     await emit("search.reading", {
  292 |       url: "https://example.org/one",
  293 |       title: "Synthetic source",
  294 |     });
  295 |     await expect(word(page)).toHaveText("Reading 1 page");
  296 |     await emit("search.done", { sources: [], timings: {} });
  297 |     await emit("reasoning.delta", { text: "An original synthetic thought.\n" });
  298 |     await emit("reasoning.delta", {
  299 |       text: "Newest reasoning stays literal <tag>.",
  300 |     });
  301 |     await expect(page.locator(".thought-ticker")).toHaveText(
  302 |       "…An original synthetic thought. Newest reasoning stays literal <tag>.",
  303 |     );
  304 |     await expect(
  305 |       page.getByRole("button", { name: "Show thinking" }),
  306 |     ).toBeVisible();
  307 |     await emit("text.delta", { text: "Synthetic streamed answer" });
  308 |     await expect(
  309 |       page.getByText("Synthetic streamed answer", { exact: true }),
  310 |     ).toBeVisible();
  311 |     await expect(line(page)).toHaveCount(0);
  312 |     const done = page.getByRole("button", { name: /Thought for/ });
  313 |     await done.click();
  314 |     await expect(
  315 |       page.getByRole("region", { name: "Model reasoning" }),
  316 |     ).toHaveText(
  317 |       "An original synthetic thought.\nNewest reasoning stays literal <tag>.",
  318 |     );
  319 |     const writes: unknown[] = [];
  320 |     page.on("request", (r) => {
  321 |       if (r.method() === "PATCH" && r.url().endsWith("/api/settings"))
  322 |         writes.push(r.postDataJSON());
  323 |     });
  324 |     await page
  325 |       .getByRole("button", { name: "Choose model", exact: true })
  326 |       .click();
  327 |     await page
  328 |       .getByRole("button", { name: "Manage models…", exact: true })
  329 |       .click();
  330 |     const settings = page.getByRole("dialog", {
  331 |       name: "Settings",
  332 |       exact: true,
  333 |     });
  334 |     await settings
  335 |       .getByRole("button", { name: "Appearance", exact: true })
  336 |       .click();
  337 |     await settings.getByRole("button", { name: "Plain", exact: true }).click();
  338 |     await expect(
  339 |       settings.getByRole("button", { name: "Plain", exact: true }),
  340 |     ).toHaveAttribute("aria-pressed", "true");
  341 |     await page.waitForTimeout(500);
  342 |     expect(writes).toEqual([]);
  343 |     expect(
  344 |       await page.evaluate(() => localStorage.getItem("workbench-status-words")),
  345 |     ).toBe("plain");
  346 |     await settings
  347 |       .getByRole("button", { name: "Sans · Geist", exact: true })
  348 |       .click();
  349 |     await expect.poll(() => writes.length).toBe(1);
  350 |     expect(writes[0]).toMatchObject({ "appearance.font": "sans" });
  351 |     expect(Object.keys(writes[0] as object)).not.toContain(
  352 |       "appearance.status_words",
  353 |     );
  354 |     await mkdir(dir, { recursive: true });
  355 |     await writeFile(
  356 |       `${dir}/settings-payload-${test.info().project.name}.json`,
  357 |       JSON.stringify(writes, null, 2),
  358 |     );
> 359 |   } finally {
      |                              ^ Error: apiRequestContext.post: Target page, context or browser has been closed
  360 |     if (runId) await request.post(`/api/runs/${runId}/cancel`);
  361 |     await request.delete(`/api/chats/${chat.id}`);
  362 |     await request.patch("/api/settings", {
  363 |       data: { "appearance.font": "serif" },
  364 |     });
  365 |   }
  366 | });
  367 | 
```