# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Failed image block retries without repeating the finished text and shows paused notification
- Location: tests/workflow-studio-running.spec.ts:363:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Open', exact: true })
    - locator resolved to <button class="" data-button="true" data-action="true">Open</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not stable
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not stable
    - retrying click action
      - waiting 100ms
    - waiting for element to be visible, enabled and stable
    - element is not stable
  7 × retrying click action
      - waiting 500ms
      - waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <li tabindex="0" data-index="0" class="font-sans" data-front="true" data-styled="true" data-mounted="true" data-swiped="false" data-visible="true" data-sonner-toast="" data-promise="false" data-removed="false" data-swiping="false" data-expanded="false" data-swipe-out="false" data-x-position="right" data-dismissible="true" data-y-position="bottom">…</li> intercepts pointer events
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting 500ms
    - waiting for element to be visible, enabled and stable
  - element was detached from the DOM, retrying

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
          - link "New chat" [ref=f1e9]:
            - /url: /
        - navigation "Chat history" [ref=f1e10]:
          - generic [ref=f1e11]:
            - textbox "Search history" [ref=f1e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=f1e13]:
            - link "Workflows" [ref=f1e15]:
              - /url: /workflows
              - text: Workflows
              - img "A workflow is waiting for you" [ref=f1e20]
            - link "Images" [ref=f1e22]:
              - /url: /images
          - region "Folders" [ref=f1e28]:
            - generic [ref=f1e29]:
              - heading "Folders" [level=2] [ref=f1e30]
              - button "New folder" [ref=f1e31] [cursor=pointer]
            - paragraph [ref=f1e32]: No folders yet
          - generic [ref=f1e33]:
            - paragraph [ref=f1e34]: Today
            - generic [ref=f1e35]:
              - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e36]:
                - /url: /c/78dfff0c58a147cdb904d912e6418ca1
              - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e37] [cursor=pointer]
          - generic [ref=f1e39]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e40]:
              - /url: /c/200c64474f5e41aea3eb06b93beb5c1e
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e41] [cursor=pointer]
          - generic [ref=f1e43]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e44]:
              - /url: /c/c87275f5ec6f4b31ac57c5cec32aa6c5
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e45] [cursor=pointer]
          - generic [ref=f1e47]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e48]:
              - /url: /c/f38528a5dbf04318b4fdaa6679422124
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e49] [cursor=pointer]
          - generic [ref=f1e51]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e52]:
              - /url: /c/c4d06558f2654d6b93146c8c562ae251
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e53] [cursor=pointer]
          - generic [ref=f1e55]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e56]:
              - /url: /c/eead6a1825af4114a80cb05f2507ccb9
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e57] [cursor=pointer]
          - generic [ref=f1e59]:
            - link "Synthetic budget request" [ref=f1e60]:
              - /url: /c/c368de1ff23848c89791bb4969bd572b
            - button "Actions for Synthetic budget request" [ref=f1e61] [cursor=pointer]
          - generic [ref=f1e63]:
            - link "Summarize this recording." [ref=f1e64]:
              - /url: /c/483ac52728554d8e97b9a65cb6b66e0a
            - button "Actions for Summarize this recording." [ref=f1e65] [cursor=pointer]
          - generic [ref=f1e67]:
            - link "#think Review this interface" [ref=f1e68]:
              - /url: /c/1d6e6efddceb4cbaa6f379779a908a67
            - 'button "Actions for #think Review this interface" [ref=f1e69] [cursor=pointer]'
          - generic [ref=f1e71]:
            - link "#think Review this interface" [ref=f1e72]:
              - /url: /c/559e8e2918b34616b544558e6788359c
            - 'button "Actions for #think Review this interface" [ref=f1e73] [cursor=pointer]'
          - generic [ref=f1e75]:
            - link "#think Review this interface" [ref=f1e76]:
              - /url: /c/c6d659ba20394675a7be3a8f8a4981e6
            - 'button "Actions for #think Review this interface" [ref=f1e77] [cursor=pointer]'
          - generic [ref=f1e79]:
            - link "#think Review this interface" [ref=f1e80]:
              - /url: /c/cc34ad21e739497585b1b84adfc7c38b
            - 'button "Actions for #think Review this interface" [ref=f1e81] [cursor=pointer]'
          - generic [ref=f1e83]:
            - link "Synthetic renamed checkpoint" [ref=f1e84]:
              - /url: /c/f8d2d81ae6f642a38ea97ca0dd361232
            - button "Actions for Synthetic renamed checkpoint" [ref=f1e85] [cursor=pointer]
          - generic [ref=f1e87]:
            - link "Synthetic server-default request" [ref=f1e88]:
              - /url: /c/aaaa10c7cc574800b0e6be62934798d8
            - button "Actions for Synthetic server-default request" [ref=f1e89] [cursor=pointer]
          - generic [ref=f1e91]:
            - link "Synthetic explicit None" [ref=f1e92]:
              - /url: /c/1fe65727c765455a8102f85c41903333
            - button "Actions for Synthetic explicit None" [ref=f1e93] [cursor=pointer]
          - generic [ref=f1e95]:
            - link "Synthetic preset request 1440 webkit" [ref=f1e96]:
              - /url: /c/88467288370c4b5a9e9a2a32f616dedd
            - button "Actions for Synthetic preset request 1440 webkit" [ref=f1e97] [cursor=pointer]
          - generic [ref=f1e99]:
            - link "Synthetic preset request 390 webkit" [ref=f1e100]:
              - /url: /c/ba1fd30b079c456d8f9059bf078c6514
            - button "Actions for Synthetic preset request 390 webkit" [ref=f1e101] [cursor=pointer]
          - generic [ref=f1e103]:
            - 'link "#long:100 #slow:10" [ref=f1e104]':
              - /url: /c/ee5d79733f944da9bf682d2ec6e682f1
            - 'button "Actions for #long:100 #slow:10" [ref=f1e105] [cursor=pointer]'
          - generic [ref=f1e107]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e108]:
              - /url: /c/72b3604a2ccd411ab67d9e724dd72e77
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e109] [cursor=pointer]
          - generic [ref=f1e111]:
            - 'link "#long:50 #slow:10" [ref=f1e112]':
              - /url: /c/95adabf493f541e88b53bf8d75aa517d
            - 'button "Actions for #long:50 #slow:10" [ref=f1e113] [cursor=pointer]'
          - generic [ref=f1e115]:
            - link "Parameter payload 1440 webkit" [ref=f1e116]:
              - /url: /c/54fcd5e4693b48a4ad04a5fed8005825
            - button "Actions for Parameter payload 1440 webkit" [ref=f1e117] [cursor=pointer]
          - generic [ref=f1e119]:
            - link "Parameter payload 390 webkit" [ref=f1e120]:
              - /url: /c/07725752f8d14ffa9c92665c631d304d
            - button "Actions for Parameter payload 390 webkit" [ref=f1e121] [cursor=pointer]
          - generic [ref=f1e123]:
            - link "Synthetic mobile request" [ref=f1e124]:
              - /url: /c/0d565efda1274f4ea7fd48e6089b583c
            - button "Actions for Synthetic mobile request" [ref=f1e125] [cursor=pointer]
          - generic [ref=f1e127]:
            - link "Context payload 1440 true webkit" [ref=f1e128]:
              - /url: /c/6c72a0f7c31d4e1ab7243b52f900edb5
            - button "Actions for Context payload 1440 true webkit" [ref=f1e129] [cursor=pointer]
          - generic [ref=f1e131]:
            - link "Context payload 1440 false webkit" [ref=f1e132]:
              - /url: /c/74d5d7f9dcf8428281c1e9b1242f77db
            - button "Actions for Context payload 1440 false webkit" [ref=f1e133] [cursor=pointer]
          - generic [ref=f1e135]:
            - link "Context payload 390 true webkit" [ref=f1e136]:
              - /url: /c/58695fb30a0b440d8e506b026a9a591b
            - button "Actions for Context payload 390 true webkit" [ref=f1e137] [cursor=pointer]
          - generic [ref=f1e139]:
            - link "Context payload 390 false webkit" [ref=f1e140]:
              - /url: /c/e4d8a68f86b14dc4b5e679bf3f2b8229
            - button "Actions for Context payload 390 false webkit" [ref=f1e141] [cursor=pointer]
          - generic [ref=f1e143]:
            - link "#lib Synthetic empty scope" [ref=f1e144]:
              - /url: /c/d6d02b01bdf24585848cf2565fc9e4f2
            - 'button "Actions for #lib Synthetic empty scope" [ref=f1e145] [cursor=pointer]'
          - generic [ref=f1e147]:
            - link "#lib What does the invented handbook say?" [ref=f1e148]:
              - /url: /c/48a3c6c992ea496f891ede4fc3986fba
            - 'button "Actions for #lib What does the invented handbook say?" [ref=f1e149] [cursor=pointer]'
          - generic [ref=f1e151]:
            - link "#lib What does the invented handbook say?" [ref=f1e152]:
              - /url: /c/202f33e6cb774e9785819eeb39ceef32
            - 'button "Actions for #lib What does the invented handbook say?" [ref=f1e153] [cursor=pointer]'
          - generic [ref=f1e155]:
            - link "#lib What does the invented handbook say?" [ref=f1e156]:
              - /url: /c/bbdf09dab64445748e28206f7aa36e07
            - 'button "Actions for #lib What does the invented handbook say?" [ref=f1e157] [cursor=pointer]'
          - generic [ref=f1e159]:
            - link "#lib What does the invented handbook say?" [ref=f1e160]:
              - /url: /c/39be0d564eb9495a83ec747b6ec7fbaa
            - 'button "Actions for #lib What does the invented handbook say?" [ref=f1e161] [cursor=pointer]'
          - generic [ref=f1e163]:
            - link "Synthetic mobile handoff request" [ref=f1e164]:
              - /url: /c/122dc70cdfdd4e2fb16b828f683287c7
            - button "Actions for Synthetic mobile handoff request" [ref=f1e165] [cursor=pointer]
          - generic [ref=f1e167]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=f1e168]:
              - /url: /c/856e4a4f547a4be0958b444bd8f6adbb
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=f1e169] [cursor=pointer]
          - generic [ref=f1e171]:
            - link "Synthetic handoff history 44" [ref=f1e172]:
              - /url: /c/a06b8e4623414a0e8dd12c63ef387ee3
            - button "Actions for Synthetic handoff history 44" [ref=f1e173] [cursor=pointer]
          - generic [ref=f1e175]:
            - link "Synthetic handoff history 43" [ref=f1e176]:
              - /url: /c/1edd6dd77aaa477c8ae81fddc7d80e50
            - button "Actions for Synthetic handoff history 43" [ref=f1e177] [cursor=pointer]
          - generic [ref=f1e179]:
            - link "Synthetic handoff history 42" [ref=f1e180]:
              - /url: /c/6d1f619d074843529b495209a2363d00
            - button "Actions for Synthetic handoff history 42" [ref=f1e181] [cursor=pointer]
          - generic [ref=f1e183]:
            - link "Synthetic handoff history 41" [ref=f1e184]:
              - /url: /c/2afa7a0e58fc45bdbfa3b56a665f55d3
            - button "Actions for Synthetic handoff history 41" [ref=f1e185] [cursor=pointer]
          - generic [ref=f1e187]:
            - link "Synthetic handoff history 40" [ref=f1e188]:
              - /url: /c/cd470d377af6430ca50d9c698a01ed02
            - button "Actions for Synthetic handoff history 40" [ref=f1e189] [cursor=pointer]
          - generic [ref=f1e191]:
            - link "Synthetic handoff history 39" [ref=f1e192]:
              - /url: /c/a312193938804982afb68fde3b17f9ff
            - button "Actions for Synthetic handoff history 39" [ref=f1e193] [cursor=pointer]
          - generic [ref=f1e195]:
            - link "Synthetic handoff history 38" [ref=f1e196]:
              - /url: /c/1ee60b4e33d54f2392e78e466b47c579
            - button "Actions for Synthetic handoff history 38" [ref=f1e197] [cursor=pointer]
          - generic [ref=f1e199]:
            - link "Synthetic handoff history 37" [ref=f1e200]:
              - /url: /c/782c5d3ff91a41bbba826b91cf70b386
            - button "Actions for Synthetic handoff history 37" [ref=f1e201] [cursor=pointer]
          - generic [ref=f1e203]:
            - link "Synthetic handoff history 36" [ref=f1e204]:
              - /url: /c/424ba9c9203f4cbeb6f2fdab9ad3fff7
            - button "Actions for Synthetic handoff history 36" [ref=f1e205] [cursor=pointer]
          - generic [ref=f1e207]:
            - link "Synthetic handoff history 35" [ref=f1e208]:
              - /url: /c/6acae93cf54143e0be9e89d2dd909c4d
            - button "Actions for Synthetic handoff history 35" [ref=f1e209] [cursor=pointer]
          - generic [ref=f1e211]:
            - link "Synthetic handoff history 34" [ref=f1e212]:
              - /url: /c/fe8ce7ec49674a928fc9473e0d87d1ce
            - button "Actions for Synthetic handoff history 34" [ref=f1e213] [cursor=pointer]
          - generic [ref=f1e215]:
            - link "Synthetic handoff history 33" [ref=f1e216]:
              - /url: /c/af76ceec2f674e6882004094910f6539
            - button "Actions for Synthetic handoff history 33" [ref=f1e217] [cursor=pointer]
          - generic [ref=f1e219]:
            - link "Synthetic handoff history 32" [ref=f1e220]:
              - /url: /c/ead8fae49b8c4d76be8094c00187746e
            - button "Actions for Synthetic handoff history 32" [ref=f1e221] [cursor=pointer]
          - generic [ref=f1e223]:
            - link "Synthetic handoff history 31" [ref=f1e224]:
              - /url: /c/f17067b2882d45e08a94407249a6443b
            - button "Actions for Synthetic handoff history 31" [ref=f1e225] [cursor=pointer]
          - generic [ref=f1e227]:
            - link "Synthetic handoff history 30" [ref=f1e228]:
              - /url: /c/7a639dafa0114ea58fe407058ac7c83c
            - button "Actions for Synthetic handoff history 30" [ref=f1e229] [cursor=pointer]
          - generic [ref=f1e231]:
            - link "Synthetic handoff history 29" [ref=f1e232]:
              - /url: /c/f567256e76cc4fbe9d8e93f84caca445
            - button "Actions for Synthetic handoff history 29" [ref=f1e233] [cursor=pointer]
          - paragraph [ref=f1e235]: Loading more chats…
        - button "Settings" [ref=f1e237] [cursor=pointer]
    - main [ref=f1e238]:
      - generic [ref=f1e239]:
        - button "Choose model" [ref=f1e241] [cursor=pointer]:
          - generic [aria-hidden] [ref=f1e242]: ●
          - generic [ref=f1e243]: fake-chat
          - generic [ref=f1e244]: Fake runtime
        - button "Chat controls" [ref=f1e245] [cursor=pointer]
      - generic [ref=f1e246]:
        - heading "Good morning" [level=1] [ref=f1e247]
        - generic [ref=f1e248]:
          - form "Message" [ref=f1e249]:
            - generic [ref=f1e250]:
              - button "Open transcript for Synthetic-workflow.wav" [ref=f1e252] [cursor=pointer]:
                - generic [ref=f1e253]: Synthetic-workflow.wav
                - status [ref=f1e254]: 1:15 · 16 words · ≈29 tokens
              - button "Recording actions for Synthetic-workflow.wav" [ref=f1e255] [cursor=pointer]
            - textbox "Message fake-chat" [ref=f1e256]:
              - /placeholder: Message fake-chat…
            - generic [ref=f1e257]:
              - button "Add attachment" [ref=f1e258] [cursor=pointer]
              - button "Web search" [disabled] [ref=f1e259] [cursor=pointer]:
                - generic [ref=f1e260]: Search
              - button "Create image" [ref=f1e261] [cursor=pointer]:
                - generic [ref=f1e262]: Image
              - generic [ref=f1e263]:
                - button "Library" [disabled] [ref=f1e264] [cursor=pointer]
                - button "Choose Library collections" [ref=f1e266] [cursor=pointer]
              - generic [ref=f1e267]:
                - img "29 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=f1e268]
                - generic [ref=f1e272]:
                  - button "Send message" [disabled]
          - generic [ref=f1e273]:
            - button "Summarize" [ref=f1e274] [cursor=pointer]
            - button "Action items" [ref=f1e275] [cursor=pointer]
            - button "Decisions" [ref=f1e276] [cursor=pointer]
        - paragraph [ref=f1e277]: Your models. Your Mac.
  - region "Notifications alt+T"
```

# Test source

```ts
  307 |   await configureStudioBlock(page, "Draft image prompt");
  308 |   await page.getByRole("tab", { name: "Output", exact: true }).click();
  309 |   await expect(page.locator(".wf-panel-body").last()).toContainText(
  310 |     "Block test",
  311 |   );
  312 | });
  313 | 
  314 | test("Favorites select actual image outputs and saved run uses an immutable canvas snapshot", async ({
  315 |   page,
  316 |   request,
  317 |   browserName,
  318 | }) => {
  319 |   const d = await create(request, { review: false, count: 2, pick: true });
  320 |   const run = await start(request, d);
  321 |   await page.goto(`/workflows/${d.id}?run=1`);
  322 |   await expect(
  323 |     page.getByRole("region", { name: "Pick favorites" }),
  324 |   ).toBeVisible();
  325 |   await page
  326 |     .getByRole("button", { name: "Pick result 2", exact: true })
  327 |     .click();
  328 |   await page
  329 |     .getByRole("button", { name: "Keep favorites", exact: true })
  330 |     .click();
  331 |   await done(page);
  332 |   const completed = await (
  333 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  334 |   ).json();
  335 |   expect(completed.results[0].items[0].value[0].id).toBe(
  336 |     completed.nodes.n_images.output.images[1].id,
  337 |   );
  338 |   const changed: Doc = structuredClone(d.graph);
  339 |   changed.nodes[0].position.x += 300;
  340 |   await request.put(`/api/workflows/defs/${d.id}`, {
  341 |     data: {
  342 |       name: d.name,
  343 |       description: d.description,
  344 |       icon: d.icon,
  345 |       graph: changed,
  346 |       version: d.version,
  347 |     },
  348 |   });
  349 |   await page.goto(`/workflows/${d.id}/runs/${run.id}`);
  350 |   await expect(
  351 |     page.getByText("The current workflow has changed.", { exact: false }),
  352 |   ).toBeVisible();
  353 |   await expect(page.locator(".wf-canvas")).toHaveAttribute(
  354 |     "aria-label",
  355 |     "Read-only workflow canvas",
  356 |   );
  357 |   await expect(
  358 |     page.getByRole("region", { name: "Workflow results" }),
  359 |   ).toBeVisible();
  360 |   await shot(page, `run-view-${browserName}`);
  361 | });
  362 | 
  363 | test("Failed image block retries without repeating the finished text and shows paused notification", async ({
  364 |   page,
  365 |   request,
  366 | }) => {
  367 |   const d = await create(request, { review: false });
  368 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  369 |   image.config.prompt = `Synthetic image ${d.id} #fail-once`;
  370 |   const saved = await (
  371 |     await request.put(`/api/workflows/defs/${d.id}`, {
  372 |       data: {
  373 |         name: d.name,
  374 |         description: d.description,
  375 |         icon: d.icon,
  376 |         graph: d.graph,
  377 |         version: d.version,
  378 |       },
  379 |     })
  380 |   ).json();
  381 |   await start(request, saved);
  382 |   await page.goto(`/workflows/${d.id}?run=1`);
  383 |   await expect(page.locator('.wf-block[data-run="failed"]')).toContainText(
  384 |     "Image could not be completed or validated",
  385 |   );
  386 |   await expect(
  387 |     page.getByRole("button", { name: "Retry block", exact: true }),
  388 |   ).toBeVisible();
  389 |   await page.getByRole("button", { name: "Retry block", exact: true }).click();
  390 |   await done(page);
  391 |   const recovered = await (
  392 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  393 |   ).json();
  394 |   expect(recovered.items[0].nodes.n_draft.attempt).toBe(1);
  395 |   expect(recovered.items[0].nodes.n_images.attempt).toBe(2);
  396 |   const paused = await create(request, { review: true });
  397 |   await page.goto("/");
  398 |   await start(request, paused);
  399 |   await expect(
  400 |     page.getByRole("button", { name: "Open", exact: true }),
  401 |   ).toBeVisible();
  402 |   await expect(
  403 |     page.locator(
  404 |       'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
  405 |     ),
  406 |   ).toBeVisible();
> 407 |   await page.getByRole("button", { name: "Open", exact: true }).click();
      |                                                                 ^ Error: locator.click: Test timeout of 45000ms exceeded.
  408 |   await expect(
  409 |     page.getByRole("textbox", { name: "Review result", exact: true }),
  410 |   ).toBeVisible();
  411 |   await page.getByRole("button", { name: "Reject", exact: true }).click();
  412 |   await done(page);
  413 | });
  414 | 
  415 | test("Full application lifecycle restart preserves completed blocks and resumes unfinished work", async ({
  416 |   page,
  417 |   request,
  418 |   browserName,
  419 | }) => {
  420 |   const d = await create(request, { review: false });
  421 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  422 |   image.config.prompt = "Synthetic restart image #restart";
  423 |   const saved = await (
  424 |     await request.put(`/api/workflows/defs/${d.id}`, {
  425 |       data: {
  426 |         name: d.name,
  427 |         description: d.description,
  428 |         icon: d.icon,
  429 |         graph: d.graph,
  430 |         version: d.version,
  431 |       },
  432 |     })
  433 |   ).json();
  434 |   const run = await start(request, saved);
  435 |   await page.goto(`/workflows/${d.id}?run=1`);
  436 |   await expect(page.locator('.wf-block[data-run="running"]')).toContainText(
  437 |     "Create images",
  438 |   );
  439 |   expect(
  440 |     (await request.post(`${fakeAppURL}/tests/restart-lifecycle`)).ok(),
  441 |   ).toBe(true);
  442 |   await page.reload();
  443 |   await expect(
  444 |     page.getByRole("button", { name: "Retry unfinished steps", exact: true }),
  445 |   ).toBeVisible();
  446 |   const interrupted = await (
  447 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  448 |   ).json();
  449 |   expect(interrupted.state).toBe("interrupted");
  450 |   expect(interrupted.nodes.n_draft.state).toBe("complete");
  451 |   await page
  452 |     .getByRole("button", { name: "Retry unfinished steps", exact: true })
  453 |     .click();
  454 |   await done(page);
  455 |   const recovered = await (
  456 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  457 |   ).json();
  458 |   expect(recovered.nodes.n_draft.attempt).toBe(1);
  459 |   expect(recovered.nodes.n_draft.output).toEqual(
  460 |     interrupted.nodes.n_draft.output,
  461 |   );
  462 |   expect(recovered.nodes.n_images.attempt).toBe(2);
  463 |   await shot(page, `restart-recovered-${browserName}`);
  464 | });
  465 | 
  466 | for (const width of [390, 1440])
  467 |   for (const theme of ["dark", "light"])
  468 |     test(`Run design states ${width} ${theme}`, async ({
  469 |       page,
  470 |       browserName,
  471 |     }) => {
  472 |       const results = [];
  473 |       await page.setViewportSize({ width, height: 900 });
  474 |       for (const state of [
  475 |         "run-running",
  476 |         "run-paused",
  477 |         "run-complete",
  478 |         "run-failed",
  479 |         "run-interrupted",
  480 |         "run-reused",
  481 |         "run-skipped",
  482 |         "pick-paused",
  483 |         "block-test",
  484 |         "setup-pick",
  485 |       ]) {
  486 |         await page.goto("/design?studio");
  487 |         await page.getByRole("button", { name: theme, exact: true }).click();
  488 |         await page.getByRole("button", { name: state, exact: true }).click();
  489 |         await settle(page);
  490 |         const scan = await new AxeBuilder({ page }).analyze();
  491 |         expect(
  492 |           scan.violations.filter((v) =>
  493 |             ["serious", "critical"].includes(v.impact ?? ""),
  494 |           ),
  495 |           `${state} ${width} ${theme}`,
  496 |         ).toEqual([]);
  497 |         results.push({ width, theme, state, seriousCritical: 0 });
  498 |         await shot(page, `${state}-${width}-${theme}-${browserName}`);
  499 |       }
  500 |       await mkdir(dir, { recursive: true });
  501 |       await writeFile(
  502 |         `${dir}/axe-states-${width}-${theme}-${browserName}.json`,
  503 |         JSON.stringify(results, null, 2),
  504 |       );
  505 |     });
  506 | test("Run activity stops for system and Always reduced motion", async ({
  507 |   page,
```