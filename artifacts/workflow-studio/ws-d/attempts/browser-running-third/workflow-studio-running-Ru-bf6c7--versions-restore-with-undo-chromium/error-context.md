# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Run from here uses saved outputs, rejects changed settings, and versions restore with undo
- Location: tests/workflow-studio-running.spec.ts:189:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Close Inspector', exact: true })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - button "Expand sidebar" [ref=e7] [cursor=pointer]
        - link "New chat" [ref=e8] [cursor=pointer]:
          - /url: /
        - button "Search chats" [ref=e9] [cursor=pointer]
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e12] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e13] [cursor=pointer]:
              - /url: /images
        - button "Settings" [ref=e15] [cursor=pointer]
    - main [ref=e16]:
      - generic [ref=e17]:
        - generic [ref=e18]:
          - link "Back to Workflows" [ref=e19] [cursor=pointer]:
            - /url: /workflows
            - generic [ref=e22]: Workflows
          - generic [ref=e23]: /
          - button "Synthetic running workflow" [ref=e24] [cursor=pointer]
          - status [ref=e25]: Saved
          - button "Undo" [ref=e27] [cursor=pointer]
          - button "Redo" [disabled]
          - button "Workflow menu" [ref=e28] [cursor=pointer]
          - button "Run" [ref=e29] [cursor=pointer]
        - generic [ref=e30]:
          - complementary "Blocks" [ref=e31]:
            - textbox "Search blocks" [ref=e36]
            - generic [ref=e37]:
              - group [ref=e38]:
                - generic "Inputs" [ref=e39] [cursor=pointer]
                - button "Start" [ref=e40] [cursor=pointer]
              - group [ref=e43]:
                - generic "AI" [ref=e44] [cursor=pointer]
                - button "Generate text" [ref=e45] [cursor=pointer]
                - button "Classify" [disabled] [ref=e48]
              - group [ref=e51]:
                - generic "Knowledge" [ref=e52] [cursor=pointer]
                - button "Search the web" [disabled] [ref=e53]
                - button "Search my files" [disabled] [ref=e56]
                - button "Read a document" [disabled] [ref=e59]
              - group [ref=e62]:
                - generic "Media" [ref=e63] [cursor=pointer]
                - button "Transcribe recording" [ref=e64] [cursor=pointer]
                - button "Clean up transcript" [ref=e67] [cursor=pointer]
                - button "Create images" [ref=e70] [cursor=pointer]
              - group [ref=e73]:
                - generic "Logic" [ref=e74] [cursor=pointer]
                - button "If / else" [disabled] [ref=e75]
                - button "Compose text" [disabled] [ref=e78]
              - group [ref=e81]:
                - generic "Review" [ref=e82] [cursor=pointer]
                - button "Approve or edit" [ref=e83] [cursor=pointer]
                - button "Pick favorites" [ref=e86] [cursor=pointer]
              - group [ref=e89]:
                - generic "Output" [ref=e90] [cursor=pointer]
                - button "Save results" [ref=e91] [cursor=pointer]
            - button "Note" [ref=e95] [cursor=pointer]
          - generic "Workflow canvas" [ref=e98]:
            - application [ref=e99]:
              - generic [ref=e101]:
                - generic:
                  - generic:
                    - img:
                      - group "Connection from Start to Draft image prompt"
                    - img:
                      - group "Connection from Create images to Save results" [ref=e102] [cursor=pointer]
                    - img:
                      - group "Connection from Draft image prompt to Create images" [ref=e105] [cursor=pointer]
                  - generic:
                    - generic [ref=e108]:
                      - button "Insert on connection e_start_draft" [ref=e109] [cursor=pointer]
                      - button "Delete connection e_start_draft" [ref=e110] [cursor=pointer]
                    - generic [ref=e111]:
                      - button "Insert on connection e_images_save" [ref=e112] [cursor=pointer]
                      - button "Delete connection e_images_save" [ref=e113] [cursor=pointer]
                    - generic [ref=e114]:
                      - button "Insert on connection e_direct" [ref=e115] [cursor=pointer]
                      - button "Delete connection e_direct" [ref=e116] [cursor=pointer]
                  - generic:
                    - group "Start block ‘Start’, 1 of 4" [ref=e117]:
                      - generic [ref=e120]:
                        - generic [ref=e121]:
                          - generic [ref=e125]:
                            - generic [ref=e126]: Start
                            - generic [ref=e127]: Start
                          - button "Actions for Start" [ref=e128] [cursor=pointer]
                        - paragraph [ref=e129]: "Inputs: Image brief"
                        - generic [ref=e130]: start.brief
                    - group "Generate text block ‘Draft image prompt’, 2 of 4" [ref=e133]:
                      - generic [ref=e137]:
                        - generic [ref=e138]:
                          - generic [ref=e143]:
                            - generic [ref=e144]: Draft image prompt
                            - generic [ref=e145]: Generate text
                          - button "Actions for Draft image prompt" [ref=e146] [cursor=pointer]
                        - paragraph [ref=e147]: fake-chat
                        - generic [ref=e148]: draft.text
                    - group "Create images block ‘Create images’, 3 of 4" [ref=e151]:
                      - generic [ref=e155]:
                        - generic [ref=e156]:
                          - generic [ref=e162]:
                            - generic [ref=e163]: Create images
                            - generic [ref=e164]: Create images
                          - button "Actions for Create images" [ref=e165] [cursor=pointer]
                        - paragraph [ref=e166]: 1 image · FLUX.2 klein
                        - generic [ref=e167]:
                          - generic [ref=e168]: images.images
                          - generic [ref=e169]: images.prompt
                    - group "Save results block ‘Save results’, 4 of 4" [ref=e171]:
                      - generic [ref=e175]:
                        - generic [ref=e176]:
                          - generic [ref=e182]:
                            - generic [ref=e183]: Save results
                            - generic [ref=e184]: Save results
                          - button "Actions for Save results" [ref=e185] [cursor=pointer]
                        - paragraph [ref=e186]: Markdown, JSON · 2 items
              - img "Mini Map" [ref=e188]
              - link "React Flow attribution" [ref=e194] [cursor=pointer]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - paragraph [ref=e195]: Drag blocks from the left, or hover a connection and press +
            - generic [ref=e196]:
              - button "Zoom out" [ref=e197] [cursor=pointer]
              - button "Zoom 100%" [ref=e198] [cursor=pointer]: 100%
              - button "Zoom in" [ref=e199] [cursor=pointer]
              - button "Fit view" [ref=e200] [cursor=pointer]
              - button "Tidy up" [ref=e201] [cursor=pointer]
              - button "Outline view" [ref=e202] [cursor=pointer]
              - button "Canvas actions" [ref=e203] [cursor=pointer]
        - button "Import workflow JSON" [ref=e204]
  - region "Notifications alt+T"
```

# Test source

```ts
  140 |   const run = await start(request, d);
  141 |   await page.goto(`/workflows/${d.id}?run=1`);
  142 |   await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  143 |   const text = page.locator(".wf-stream-preview").first();
  144 |   await expect(text).toContainText("token");
  145 |   const before = await text.innerText();
  146 |   await expect.poll(() => text.innerText()).not.toBe(before);
  147 |   await expect(
  148 |     page.getByRole("button", { name: "Following run", exact: true }),
  149 |   ).toHaveAttribute("aria-pressed", "true");
  150 |   await page.getByRole("button", { name: "Zoom out", exact: true }).click();
  151 |   await expect(
  152 |     page.getByRole("button", { name: "Resume following run", exact: true }),
  153 |   ).toHaveAttribute("aria-pressed", "false");
  154 |   await shot(page, `stream-${browserName}`);
  155 |   let detailReads = 0;
  156 |   page.on("request", (r) => {
  157 |     if (r.url().endsWith(`/runs/${run.id}/v2`)) detailReads++;
  158 |   });
  159 |   await page.context().setOffline(true);
  160 |   await page.waitForTimeout(350);
  161 |   await page.context().setOffline(false);
  162 |   await expect(page.locator('.wf-block[data-run="paused"]')).toContainText(
  163 |     "Waiting for you",
  164 |   );
  165 |   await expect(page.locator(".wf-stream-preview").first()).toContainText(
  166 |     "token15",
  167 |   );
  168 |   expect(detailReads).toBeLessThanOrEqual(1);
  169 |   await expect(
  170 |     page.getByRole("button", { name: "Following run", exact: true }),
  171 |   ).toHaveAttribute("aria-pressed", "true");
  172 |   await page
  173 |     .getByRole("textbox", { name: "Review result" })
  174 |     .fill("Synthetic approved blue circle");
  175 |   await page.getByRole("button", { name: "Approve", exact: true }).click();
  176 |   await done(page);
  177 |   await expect(page.locator('.wf-block[data-run="complete"]')).toHaveCount(
  178 |     d.graph.nodes.length,
  179 |   );
  180 |   const snapshot = await (
  181 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  182 |   ).json();
  183 |   expect(snapshot.nodes.n_review.output.value).toBe(
  184 |     "Synthetic approved blue circle",
  185 |   );
  186 |   await shot(page, `complete-${browserName}`);
  187 | });
  188 | 
  189 | test("Run from here uses saved outputs, rejects changed settings, and versions restore with undo", async ({
  190 |   page,
  191 |   request,
  192 |   browserName,
  193 | }) => {
  194 |   const d = await create(request, { review: false });
  195 |   const first = await start(request, d);
  196 |   await page.goto(`/workflows/${d.id}?run=1`);
  197 |   await done(page);
  198 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  199 |   await configureStudioBlock(page, "Create images");
  200 |   await page
  201 |     .locator(".wf-inspector")
  202 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  203 |     .click();
  204 |   await page
  205 |     .getByRole("menuitem", { name: "Run from here", exact: true })
  206 |     .click();
  207 |   await page
  208 |     .getByRole("button", { name: "Run from here", exact: true })
  209 |     .click();
  210 |   await done(page);
  211 |   await expect(page.locator('.wf-block[data-run="reused"]')).toContainText([
  212 |     "Start",
  213 |     "Draft image prompt",
  214 |   ]);
  215 |   const all = await (
  216 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  217 |   ).json();
  218 |   const second = all.items[0];
  219 |   expect(second.id).not.toBe(first.id);
  220 |   expect(second.nodes.n_draft.reused_from).toBe(first.id);
  221 |   expect(second.nodes.n_draft.attempt).toBe(0);
  222 |   await shot(page, `reused-${browserName}`);
  223 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  224 |   await configureStudioBlock(page, "Draft image prompt");
  225 |   await page
  226 |     .getByRole("textbox", { name: "Prompt", exact: true })
  227 |     .fill("Synthetic changed prompt");
  228 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  229 |   await configureStudioBlock(page, "Create images");
  230 |   await page
  231 |     .locator(".wf-inspector")
  232 |     .getByRole("button", { name: "Actions for Create images", exact: true })
  233 |     .click();
  234 |   await expect(
  235 |     page.getByRole("menuitem", { name: "Run from here", exact: true }),
  236 |   ).toBeDisabled();
  237 |   await page.keyboard.press("Escape");
  238 |   await page
  239 |     .getByRole("button", { name: "Close Inspector", exact: true })
> 240 |     .click();
      |      ^ Error: locator.click: Test timeout of 45000ms exceeded.
  241 |   await page
  242 |     .getByRole("button", { name: "Workflow menu", exact: true })
  243 |     .click();
  244 |   await page.getByRole("menuitem", { name: "Versions", exact: true }).click();
  245 |   const version = page.locator(".wf-version").last();
  246 |   await version.getByRole("textbox").fill("Synthetic named version");
  247 |   await version.getByRole("button", { name: "Save name", exact: true }).click();
  248 |   await expect(version).toContainText("Synthetic named version");
  249 |   await version.getByRole("button", { name: "Restore", exact: true }).click();
  250 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  251 |   await page.getByRole("button", { name: "Undo", exact: true }).click();
  252 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  253 |   const restored = await (
  254 |     await request.get(`/api/workflows/defs/${d.id}`)
  255 |   ).json();
  256 |   expect(
  257 |     restored.graph.nodes.find((n: { kind: string }) => n.kind === "generate")
  258 |       .config.prompt,
  259 |   ).toBe("Synthetic changed prompt");
  260 | });
  261 | 
  262 | test("Single block tests use explicit samples and remain outside recent history after reload", async ({
  263 |   page,
  264 |   request,
  265 | }) => {
  266 |   const d = await create(request, { review: false });
  267 |   await page.goto(`/workflows/${d.id}`);
  268 |   await configureStudioBlock(page, "Draft image prompt");
  269 |   await page
  270 |     .locator(".wf-inspector")
  271 |     .getByRole("button", {
  272 |       name: "Actions for Draft image prompt",
  273 |       exact: true,
  274 |     })
  275 |     .click();
  276 |   await page
  277 |     .getByRole("menuitem", { name: "Test this block", exact: true })
  278 |     .click();
  279 |   await page
  280 |     .getByRole("textbox", { name: "Sample start.brief", exact: true })
  281 |     .fill("Synthetic test brief");
  282 |   await page.getByRole("button", { name: "Test block", exact: true }).click();
  283 |   await done(page);
  284 |   await page.reload();
  285 |   await done(page);
  286 |   await expect(page.locator(".wf-run-card")).toContainText(
  287 |     "Draft image prompt",
  288 |   );
  289 |   const list = await (
  290 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  291 |   ).json();
  292 |   expect(list.items).toEqual([]);
  293 |   const tests = await (
  294 |     await request.get(`/api/workflows/defs/${d.id}/tests?node_id=n_draft`)
  295 |   ).json();
  296 |   expect(tests).toHaveLength(1);
  297 |   expect(tests[0].mode).toBe("test");
  298 |   expect(tests[0].nodes.n_images.attempt).toBe(0);
  299 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  300 |   await configureStudioBlock(page, "Draft image prompt");
  301 |   await page.getByRole("tab", { name: "Output", exact: true }).click();
  302 |   await expect(page.locator(".wf-panel-body").last()).toContainText(
  303 |     "Block test",
  304 |   );
  305 | });
  306 | 
  307 | test("Favorites select actual image outputs and saved run uses an immutable canvas snapshot", async ({
  308 |   page,
  309 |   request,
  310 |   browserName,
  311 | }) => {
  312 |   const d = await create(request, { review: false, count: 2, pick: true });
  313 |   const run = await start(request, d);
  314 |   await page.goto(`/workflows/${d.id}?run=1`);
  315 |   await expect(
  316 |     page.getByRole("region", { name: "Pick favorites" }),
  317 |   ).toBeVisible();
  318 |   await page
  319 |     .getByRole("button", { name: "Pick result 2", exact: true })
  320 |     .click();
  321 |   await page
  322 |     .getByRole("button", { name: "Keep favorites", exact: true })
  323 |     .click();
  324 |   await done(page);
  325 |   const completed = await (
  326 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  327 |   ).json();
  328 |   expect(completed.results[0].items[0].value[0].id).toBe(
  329 |     completed.nodes.n_images.output.images[1].id,
  330 |   );
  331 |   const changed: Doc = structuredClone(d.graph);
  332 |   changed.nodes[0].position.x += 300;
  333 |   await request.put(`/api/workflows/defs/${d.id}`, {
  334 |     data: {
  335 |       name: d.name,
  336 |       description: d.description,
  337 |       icon: d.icon,
  338 |       graph: changed,
  339 |       version: d.version,
  340 |     },
```