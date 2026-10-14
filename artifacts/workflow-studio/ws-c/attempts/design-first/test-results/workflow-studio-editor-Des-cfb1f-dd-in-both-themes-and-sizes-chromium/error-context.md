# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-editor.spec.ts >> Design catalogue exposes every editing panel and Quick add in both themes and sizes
- Location: tests/workflow-studio-editor.spec.ts:522:1

# Error details

```
Error: 390/light/cards

expect(received).toEqual(expected) // deep equality

- Expected  -  1
+ Received  + 52

- Array []
+ Array [
+   Object {
+     "description": "Ensure elements that have scrollable content are accessible by keyboard in Safari",
+     "help": "Scrollable region must have keyboard access",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/scrollable-region-focusable?application=playwright",
+     "id": "scrollable-region-focusable",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "focusable-content",
+             "impact": "serious",
+             "message": "Element should have focusable content",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "focusable-element",
+             "impact": "serious",
+             "message": "Element should be focusable",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element should have focusable content
+   Element should be focusable",
+         "html": "<div class=\"flex flex-1 flex-wrap items-start gap-6 overflow-y-auto p-6\">",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           ".items-start",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.keyboard",
+       "wcag2a",
+       "wcag211",
+       "wcag213",
+       "TTv5",
+       "TT4.a",
+       "EN-301-549",
+       "EN-9.2.1.1",
+       "EN-9.2.1.3",
+       "RGAAv4",
+       "RGAA-7.3.2",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic [ref=f8e2]:
  - main [ref=f8e4]:
    - generic [ref=f8e5]:
      - generic [ref=f8e6]:
        - button "Open sidebar" [ref=f8e7] [cursor=pointer]
        - button "Choose model" [ref=f8e9] [cursor=pointer]:
          - generic [aria-hidden] [ref=f8e10]: ●
          - generic [ref=f8e11]: fake-chat
      - generic [ref=f8e12]:
        - button "Chat controls" [ref=f8e13] [cursor=pointer]
        - button "Chat actions" [ref=f8e14] [cursor=pointer]
    - generic [ref=f8e16]:
      - generic [ref=f8e17]:
        - paragraph [ref=f8e18]: Workflow Studio · fake runtime states
        - button "light" [ref=f8e19] [cursor=pointer]
        - button "dark" [ref=f8e20] [cursor=pointer]
        - button "canvas" [ref=f8e21] [cursor=pointer]
        - button "empty" [ref=f8e22] [cursor=pointer]
        - button "selected" [ref=f8e23] [cursor=pointer]
        - button "problems" [ref=f8e24] [cursor=pointer]
        - button "conflict" [ref=f8e25] [cursor=pointer]
        - button "outline" [ref=f8e26] [cursor=pointer]
        - button "non-nestable" [ref=f8e27] [cursor=pointer]
        - button "settings" [ref=f8e28] [cursor=pointer]
        - button "run-inputs" [ref=f8e29] [cursor=pointer]
        - button "cards" [ref=f8e30] [cursor=pointer]
        - button "home-cards" [ref=f8e31] [cursor=pointer]
        - button "quick-add" [ref=f8e32] [cursor=pointer]
        - button "setup-start" [ref=f8e33] [cursor=pointer]
        - button "setup-generate" [ref=f8e34] [cursor=pointer]
        - button "setup-transcribe" [ref=f8e35] [cursor=pointer]
        - button "setup-clean_transcript" [ref=f8e36] [cursor=pointer]
        - button "setup-generate_image" [ref=f8e37] [cursor=pointer]
        - button "setup-review" [ref=f8e38] [cursor=pointer]
        - button "setup-output" [ref=f8e39] [cursor=pointer]
      - generic [ref=f8e40]:
        - generic [ref=f8e41]:
          - paragraph [ref=f8e42]: Start
          - generic [ref=f8e44]:
            - generic [ref=f8e49]:
              - generic [ref=f8e50]: Start
              - generic [ref=f8e51]: Start
            - paragraph [ref=f8e52]: "Inputs: Image brief"
            - generic [ref=f8e53]: start.brief
        - generic [ref=f8e55]:
          - paragraph [ref=f8e56]: Generate text
          - generic [ref=f8e58]:
            - generic [ref=f8e64]:
              - generic [ref=f8e65]: Draft image prompt
              - generic [ref=f8e66]: Generate text
            - paragraph [ref=f8e67]: Workflow default
            - generic [ref=f8e68]: draft.text
        - generic [ref=f8e70]:
          - paragraph [ref=f8e71]: Approve or edit
          - generic [ref=f8e73]:
            - generic [ref=f8e80]:
              - generic [ref=f8e81]: Check the prompt
              - generic [ref=f8e82]: Approve or edit
            - paragraph [ref=f8e83]: "Review {{draft.text}} · editable"
            - generic [ref=f8e84]: review.value
        - generic [ref=f8e86]:
          - paragraph [ref=f8e87]: Create images
          - generic [ref=f8e89]:
            - generic [ref=f8e96]:
              - generic [ref=f8e97]: Create images
              - generic [ref=f8e98]: Create images
            - paragraph [ref=f8e99]: 1 image · FLUX.2 klein
            - generic [ref=f8e100]:
              - generic [ref=f8e101]: images.images
              - generic [ref=f8e102]: images.prompt
        - generic [ref=f8e103]:
          - paragraph [ref=f8e104]: Save results
          - generic [ref=f8e106]:
            - generic [ref=f8e113]:
              - generic [ref=f8e114]: Save results
              - generic [ref=f8e115]: Save results
            - paragraph [ref=f8e116]: Markdown, JSON · 2 items
        - generic [ref=f8e118]:
          - generic [ref=f8e122]:
            - generic [ref=f8e123]: Transcribe recording
            - generic [ref=f8e124]: Transcribe recording
          - paragraph [ref=f8e125]: "{{start.recording}}"
          - generic [ref=f8e126]:
            - generic [ref=f8e127]: transcript.transcript
            - generic [ref=f8e128]: transcript.text
            - generic [ref=f8e129]: "+3"
        - generic [ref=f8e131]:
          - generic [ref=f8e137]:
            - generic [ref=f8e138]: Clean up transcript
            - generic [ref=f8e139]: Clean up transcript
          - paragraph [ref=f8e140]: Disabled · skipped when the workflow runs
          - generic [ref=f8e141]: clean.text
  - region "Notifications alt+T"
```

# Test source

```ts
  474 |     );
  475 |     detached.id = "n_detached";
  476 |     detached.key = "detached";
  477 |     detached.title = "Synthetic detached";
  478 |     branched.nodes.push(detached);
  479 |     await put(branched);
  480 |     await page.reload();
  481 |     await expect(
  482 |       page.getByText(
  483 |         "Part of this workflow is easier to change on a larger screen. Settings still open here.",
  484 |       ),
  485 |     ).toBeVisible();
  486 |     await expect(
  487 |       page.getByRole("button", { name: "Insert after Start", exact: true }),
  488 |     ).toBeDisabled();
  489 |     await page
  490 |       .getByRole("button", {
  491 |         name: "Actions for Synthetic detached",
  492 |         exact: true,
  493 |       })
  494 |       .tap();
  495 |     await expect(
  496 |       page.getByRole("menuitem", { name: "Duplicate", exact: true }),
  497 |     ).toHaveAttribute("aria-disabled", "true");
  498 |     await expect(
  499 |       page.getByRole("menuitem", { name: "Delete", exact: true }),
  500 |     ).toHaveAttribute("aria-disabled", "true");
  501 |     await page.keyboard.press("Escape");
  502 |     await page
  503 |       .getByRole("button", {
  504 |         name: "Configure Synthetic detached",
  505 |         exact: true,
  506 |       })
  507 |       .tap();
  508 |     await page
  509 |       .getByRole("textbox", { name: "Block name", exact: true })
  510 |       .fill("Synthetic edited on phone");
  511 |     await page
  512 |       .getByRole("button", { name: "Close Inspector", exact: true })
  513 |       .tap();
  514 |     await saved(page);
  515 |     expect(
  516 |       (await def(request, d.id)).graph.nodes.find((n) => n.id === detached.id)!
  517 |         .title,
  518 |     ).toBe("Synthetic edited on phone");
  519 |   });
  520 | });
  521 | 
  522 | test("Design catalogue exposes every editing panel and Quick add in both themes and sizes", async ({
  523 |   page,
  524 |   request,
  525 |   browserName,
  526 | }) => {
  527 |   test.setTimeout(240000);
  528 |   await request.patch("/api/settings", {
  529 |     data: { "appearance.reduce_motion": "system" },
  530 |   });
  531 |   const states = [
  532 |     "empty",
  533 |     "selected",
  534 |     "problems",
  535 |     "conflict",
  536 |     "outline",
  537 |     "non-nestable",
  538 |     "settings",
  539 |     "run-inputs",
  540 |     "cards",
  541 |     "home-cards",
  542 |     "quick-add",
  543 |     ...[
  544 |       "start",
  545 |       "generate",
  546 |       "transcribe",
  547 |       "clean_transcript",
  548 |       "generate_image",
  549 |       "review",
  550 |       "output",
  551 |     ].map((k) => "setup-" + k),
  552 |   ];
  553 |   const results = [];
  554 |   await mkdir(dir, { recursive: true });
  555 |   for (const width of [390, 1440]) {
  556 |     await page.setViewportSize({ width, height: 900 });
  557 |     for (const theme of ["light", "dark"]) {
  558 |       for (const state of states) {
  559 |         await page.goto(`/design?studio&state=${state}`);
  560 |         await expect(
  561 |           page.getByText("Workflow Studio · fake runtime states"),
  562 |         ).toBeVisible();
  563 |         await page.evaluate(
  564 |           (v) => (document.documentElement.dataset.theme = v),
  565 |           theme,
  566 |         );
  567 |         await settle(page);
  568 |         const scan = await new AxeBuilder({ page }).analyze();
  569 |         expect(
  570 |           scan.violations.filter((v) =>
  571 |             ["serious", "critical"].includes(v.impact ?? ""),
  572 |           ),
  573 |           `${width}/${theme}/${state}`,
> 574 |         ).toEqual([]);
      |           ^ Error: 390/light/cards
  575 |         expect(
  576 |           await page.evaluate(
  577 |             () => document.documentElement.scrollWidth <= innerWidth,
  578 |           ),
  579 |           `${width}/${theme}/${state} overflow`,
  580 |         ).toBe(true);
  581 |         results.push({ width, theme, state, seriousCritical: 0 });
  582 |         await page.screenshot({
  583 |           path: `${dir}/design-${state}-${width}-${theme}-${browserName}-fake.png`,
  584 |         });
  585 |       }
  586 |     }
  587 |   }
  588 |   await writeFile(
  589 |     `${dir}/axe-design-${browserName}.json`,
  590 |     JSON.stringify(results, null, 2),
  591 |   );
  592 | });
  593 | 
```